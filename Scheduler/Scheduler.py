import logging
from logging.handlers import RotatingFileHandler
import concurrent.futures
import time
from itertools import repeat
from pathlib import Path
from typing import Callable, List
import sys
import signal

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()
sys.path.insert(0, BASE_DIR)

#from AtlinAPI.AtlinAPI.atlin import *
from atlin_api.atlin_api import *

from Scheduler.Utils import  *
import Config as config
from ToolInterfaces.ToolInterface import genericInterface
from ToolInterfaces.RedditAPIInterface import RedditInterface
from ToolInterfaces.CrawlerInterface import CrawlerInterface
from ToolInterfaces.YouTubeInterface import YouTubeInterface

##############################################################################################################
# CLASS DEFINITION: Job Scheduler
##############################################################################################################

class JobScheduler:

    #########################################################################
    # CONSTRUCTOR
    #########################################################################
    
    def __init__(   self,
                    dataBaseDomain = config.ATLIN_API_ADDRESS,
                    waitTime = 60):
        
        self.waitTime_ = waitTime
   
        self.keepRunning_ = True
        
        self.atlin_ = Atlin(dataBaseDomain)

        self.jobHandleDict = {}

        self.logger_ = logging.getLogger('Scheduler')
        
        signal.signal(signal.SIGINT, self._handlerSIGINT)
                    
    #########################################################################
    # PRIVATE FUNCTIONS
    #########################################################################
   
    ############################################################################################
    # This function will take in a list of dictionarys which describe a job and creates seperate
    # threads to run them
    ############################################################################################
    def _submitJobs(self, 
                    listOfJobJSON : List[any]):
        
        self.logger_.info('Submitting jobs')

        # TODO: it would be nice to confirm that the items in the list are dictionaries with the correct key-value pairs

        # Create a context manager to handle the opening/closing of processes
        with concurrent.futures.ProcessPoolExecutor() as executor:
            for jobJSON in listOfJobJSON:                                          
                # get the data from the job dictionary    
                jobType = jobJSON['social_platform']
            
                if jobType in self.jobHandleDict.keys():
                    # start a process that will execute the correct script
                    executor.submit(genericInterface,
                                    self.jobHandleDict[jobType],
                                    jobJSON)                     
                else:
                    self.logger_.error(f'Unknown Job Type: {jobType}')
            
            # this allows the context manager to return before each process is finished
            # which means the scheduler is free to go back and check for other new jobs
            executor.shutdown(wait=False)

        return
    
    ############################################################################################
    # Handle receiving SIGINT signal
    ############################################################################################
    def _handlerSIGINT(self,sig, frame):
        self.logger_.info('Handling SIGINT')
        
        self._clearRunningJobs()
        
        sys.exit(0)

    ############################################################################################
    # Handle API request for jobs with status = jobStatus
    ############################################################################################
    def _getJobs(self,
                 jobStatus: JobStatus):
        response = None
        
        # request all the "created"
        try:
            response = self.atlin_.job_get(job_status=[jobStatus])
        except Exception as e:
            self.logger_.error(e)  

        return response

    ####################################################################################################
    # Sets status of job with id 'job_uid' to 'status
    ############################################################################################
    def _setJobStatus(  self,
                        job_uid, 
                        job_status) -> None:
        
        try:        
            self.atlin_.job_set_status(job_uid, job_status)
        except Exception as e:
            self.logger_.error(e)  
        
        return 

    ############################################################################################
    # Helper function that returns a list of currently used token_uids
    ############################################################################################
    def _getCurrentlyUsedTokenIDs(self) -> list:
        
        usedTokenIDs = []
        
        try:
            runningJobsList = self._getJobs(JobStatus().running).json()
        
            for job in runningJobsList:
                usedTokenIDs.append(job['token_uid'])
        
        except Exception as e:
            self.logger_.error(f'_getCurrentlyUsedTokenIDs: {e}')
        
        return usedTokenIDs

    ############################################################################################
    # Merges the created and paused jobs and returns a list sort by age (oldest to youngest) 
    ############################################################################################
    def _getPotentiallyRunnableJobs(self) -> list:
        potentiallyRunnableJobs = []
        
        try:
            createdJobs = self._getJobs(JobStatus().created).json()
            pausedJobs = self._getJobs(JobStatus().paused).json()
        
            potentiallyRunnableJobs = createdJobs + pausedJobs
                   
            potentiallyRunnableJobs.sort(key= lambda job: job['create_date'])
                
        except Exception as e:
            self.logger_.error(f'_getCurrentlyUsedTokenIDs: {e}')
                    
        return potentiallyRunnableJobs
    
    ############################################################################################
    # Clears out all running jobs from the database and sets there status to FAILED. This is
    # function is executed before the scheduler starts it's main loop.
    ############################################################################################
    def _clearRunningJobs(self):
                        
        try:
            runningJobsList = self._getJobs(JobStatus().running).json()
        
            for job in runningJobsList:
                self._setJobStatus(job['job_uid'], JobStatus().failed)     
        
        except Exception as e:
            self.logger_.error(e)
        
    ############################################################################################
    # This function compares rows in the jobs table with the status CREATED with those that are 
    # currently status RUNNING. If the token_uid of a CREATED job is not currenly used by a 
    # RUNNING job it is added to the returned list.
    ############################################################################################
    def _checkDataBaseForRunnableJobs(self) -> list:
        
        runnableJobs = []
        
        try:
            self.logger_.info('Checking for runnable jobs')
            potentiallyRunnableJobs = self._getPotentiallyRunnableJobs()
            usedTokenIDs = self._getCurrentlyUsedTokenIDs()
            
            # for job in createdJobs:
            for job in potentiallyRunnableJobs:
                if job['token_uid'] not in usedTokenIDs:
                    runnableJobs.append(job)   
                    usedTokenIDs.append(job['token_uid'])
                    
            self.logger_.info(f'{len(runnableJobs)} runnable job(s) found')
             
        except Exception as e:
            self.logger_.error(f'_checkDataBaseForRunnableJobs: {e}')
              
        return runnableJobs
    
    ############################################################################################
    # This function checks the data base for any rows in the JobsTable which has a job
    # status set to CREATED
    ############################################################################################
    def _checkDataBaseForJobsToSubmit(self) -> None:
        
        try:
            runnableJobs = self._checkDataBaseForRunnableJobs()
                      
            # This function will submit the jobs to be run on seperate processes
            if len(runnableJobs) > 0:
                self._submitJobs(runnableJobs)
               
        except Exception as e:
            self.logger_.error(f'_checkDataBaseForJobsToSubmit: {e}')
                                   
    ############################################################################################
    # This function checks for any sort of exit conditions
    ############################################################################################
    def _checkExit(self):
        self.logger_.info('Check for exit conditions')
        
        self.keepRunning_ = True
     
    #########################################################################
    # PUBLIC FUNCTIONS
    #########################################################################
    
    ############################################################################################
    # Add a new job type, and the ToolInterface to run it
    ############################################################################################
    def AddJobType( self,
                    jobType : str,
                    toolFunctionPoint : Callable) -> None:

        if callable(toolFunctionPoint):
            self.jobHandleDict[jobType] = toolFunctionPoint
            self.logger_.info(f'Handler for job type {jobType} added.')
        else:
            self.logger_.error('AddJobType: argument \'toolFunctionPoint\' not a callable type')
            raise TypeError
               
    ############################################################################################
    # This is the main loop for the job scheduler
    ############################################################################################
    def Run(self):
                
        # Clear out jobs in DB which are stuck on 'running'
        self._clearRunningJobs()
                
        while self.keepRunning_:
            
            # This function will check the database for news and return a list of dictionaries with
            # the row ID of the new job
            self._checkDataBaseForJobsToSubmit()

            # check if some type of exit condition has been set
            self._checkExit()

            # don't spam the API
            self.logger_.info(f'Sleep for {self.waitTime_} seconds...')
            time.sleep(self.waitTime_)           


##############################################################################################################

if __name__ == '__main__':
       
    logging.basicConfig(
        level=logging.DEBUG,
        format='%(asctime)s %(levelname)s %(filename)s %(funcName)s(%(lineno)d) %(message)s',
        handlers=[
            RotatingFileHandler(
                f"log_data_fetcher_{time.strftime('%y%m%d_%H%M')}.log",
                mode='a',
                maxBytes=5*1024*1024,
                backupCount=2,
                encoding=None,
                delay=0,
            ),
            #logging.FileHandler(f"log_data_fetcher_{time.strftime('%y%m%d_%H%M')}.log"),
            logging.StreamHandler(),
        ])
       
    js = JobScheduler(waitTime=WAIT_TIME)
    
    js.AddJobType('REDDIT', RedditInterface)
    js.AddJobType('YOUTUBE', YouTubeInterface)
    js.AddJobType('CRAWL', CrawlerInterface)
    
    js.Run()
    
