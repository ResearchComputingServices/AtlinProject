from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()
sys.path.insert(0, BASE_DIR)

import logging

from requests import Response

import concurrent.futures
import time
from typing import Callable, List
import signal

from atlin_api.atlin_api import Atlin, JobStatus
import Config as config

from ToolInterfaces.ToolInterface import genericInterface

class JobScheduler:
    """The Job Scheduler checks the DB for jobs which can be run and runs them.
    
    """

    def __init__(   self,
                    dataBaseDomain = config.ATLIN_API_ADDRESS,
                    wait_Time = 60):

        self._wait_time = wait_Time

        self._keep_running = True

        self._atlin_session = Atlin(dataBaseDomain)

        self._job_handle_dict = {}

        self._logger = logging.getLogger('Scheduler')

        signal.signal(signal.SIGINT, self._handler_sig_int)

    #~~~~~~~~~~~~~~~~~~~~~ PRIVATE FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _submit_jobs(   self,
                        list_of_job_jsons : List[any]) -> None:
        """ This function will take in a list of dictionarys which describe a j
        ob and creates seperate threads to run them

        Args:
            list_of_job_jsons (List[any]): list of jobs to submit
        """

        self._logger.info('Submitting jobs')

        # TODO: it would be nice to confirm that the items in the list
        # are dictionaries with the correct key-value pairs

        # Create a context manager to handle the opening/closing of processes
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for job_json in list_of_job_jsons:                          
                # get the data from the job dictionary
                job_type = job_json['social_platform']

                if job_type in self._job_handle_dict.keys():
                    # start a process that will execute the correct script
                    executor.submit(genericInterface,
                                    self._job_handle_dict[job_type],
                                    job_json)
                else:
                    self._logger.error('Unknown Job Type: %s',{job_type})

            # this allows the context manager to return before each process is finished
            # which means the scheduler is free to go back and check for other new jobs
            executor.shutdown(wait=False)

        return

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _handler_sig_int(self,
                         sig, 
                         frame) -> None:
        """Handle receiving SIGINT signal

        Args:
            sig (_type_): _description_
            frame (_type_): _description_
        """

        self._logger.info('Handling SIGINT')
        self._clear_running_jobs()
        sys.exit(0)

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_jobs(self,
                 job_status: JobStatus) -> Response:
        """ Handle API request for jobs with status = jobStatus

        Args:
            jobStatus (JobStatus): _description_

        Returns:
            _type_: _description_
        """

        response = None

        # request all the "created"
        try:
            response = self._atlin_session.job_get(job_status=[job_status])
        except Exception as e:
            self._logger.error(e)
            raise e

        return response

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _set_job_status(self,
                        job_uid : str,
                        job_status : JobStatus) -> None:
        """

        Args: Sets status of job with id 'job_uid' to 'status
            job_uid (str): _description_
            job_status (JobStatus): _description_

        Raises:
            e: _description_
        """
        try:        
            self._atlin_session.job_set_status(job_uid, job_status)
        except Exception as e:
            self._logger.error(e)
            raise e

        return

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_currently_used_tokens(self) -> list:
        """
        Helper function that returns a list of currently used token_uids
        """
        used_token_ids = []

        try:
            running_jobs_list = self._get_jobs(JobStatus().running).json()

            for job in running_jobs_list:
                used_token_ids.append(job['token_uid'])

        except Exception as e:
            self._logger.error(e)
            raise e
        return used_token_ids

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_potentially_runnable_jobs(self) -> list:
        """ Merges the created and paused jobs and returns a list sort by age (oldest to youngest) 

        Raises:
            e: _description_

        Returns:
            list: _description_
        """
        potentially_runnable_jobs = []

        try:
            created_jobs = self._get_jobs(JobStatus().created).json()
            paused_jobs = self._get_jobs(JobStatus().paused).json()

            potentially_runnable_jobs = created_jobs + paused_jobs

            potentially_runnable_jobs.sort(key= lambda job: job['create_date'])

        except Exception as e:
            self._logger.error(e)
            raise e

        return potentially_runnable_jobs

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _clear_running_jobs(self):
        """
        Clears out all running jobs from the database and sets there status to FAILED. This
        function is executed before the scheduler starts it's main loop and when handling SIGINT
        """
        try:
            running_jobs_list = self._get_jobs(JobStatus().running).json()

            for job in running_jobs_list:
                self._set_job_status(job['job_uid'], JobStatus().failed)

        except Exception as e:
            self._logger.error(e)
            raise e

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_runnable_jobs_from_db(self) -> list:
        """This function compares rows in the jobs table with the status CREATED with those that are 
        currently status RUNNING. If the token_uid of a CREATED job is not currenly used by a 
        RUNNING job it is added to the returned list.
        Raises:
            e: _description_

        Returns:
            list: _description_
        """
        runnable_jobs = []

        try:
            self._logger.info('Checking for runnable jobs')
            potentially_runnable_jobs = self._get_potentially_runnable_jobs()
            used_token_ids = self._get_currently_used_tokens()

            # for job in createdJobs:
            for job in potentially_runnable_jobs:
                if job['token_uid'] not in used_token_ids:
                    runnable_jobs.append(job)   
                    used_token_ids.append(job['token_uid'])

            self._logger.info('%d runnable job(s) found',len(runnable_jobs))

        except Exception as e:
            self._logger.error(e)
            raise e

        return runnable_jobs

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _get_jobs_from_db(self) -> None:
        """This function checks the data base for any rows in the JobsTable which has a job
        status set to CREATED

        Raises:
            e: _description_
        """
        try:
            runnable_jobs = self._get_runnable_jobs_from_db()

            # This function will submit the jobs to be run on seperate processes
            if len(runnable_jobs) > 0:
                self._submit_jobs(runnable_jobs)

        except Exception as e:
            self._logger.error(e)
            raise e

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def _check_exit(self):
        """ This function checks for any sort of exit conditions
        """
        self._logger.info('Check for exit conditions')

        self._keep_running = True

    #~~~~~~~~~~~~~~~~~~~~~~~ PUBLIC FUNCTIONS~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    def add_job_type( self,
                    job_type : str,
                    tool_func_point : Callable) -> None:

        """Add a new job type, and the ToolInterface to run it
    
        Raises:
            TypeError: _description_
        """

        if callable(tool_func_point):
            self._job_handle_dict[job_type] = tool_func_point
            self._logger.info('Handler for job type %s added.',job_type)
        else:
            self._logger.error('AddJobType: argument \'toolFunctionPoint\' not a callable type')
            raise TypeError

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    
    def run(self):
        """This is the main loop for the job scheduler
        """                
        # Clear out jobs in DB which are stuck on 'running'
        self._clear_running_jobs()

        while self._keep_running:

            # This function will check the database for news and return a list of dictionaries with
            # the row ID of the new job
            self._get_jobs_from_db()

            # check if some type of exit condition has been set
            self._check_exit()

            # don't spam the API
            self._logger.info(f'Sleep for %d seconds...',self._wait_time)
            time.sleep(self._wait_time)
