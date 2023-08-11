import logging
import concurrent.futures
import time
from itertools import repeat
from pathlib import Path
from typing import Callable, List
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()
sys.path.insert(0, BASE_DIR)

#from AtlinAPI.AtlinAPI.atlin import *
from atlin_api.atlin_api import *

from Scheduler.Utils import  *

from ToolInterfaces.ToolInterface import genericInterface
from ToolInterfaces.RedditAPIInterface import RedditInterface
from ToolInterfaces.CrawlerInterface import CrawlerInterface
from ToolInterfaces.YouTubeInterface import YouTubeInterface

##############################################################################################################
# CLASS DEFINITION: Job Scheduler
##############################################################################################################

class JobScheduler:

    #########################################################################
    # MEMBER(S)
    #########################################################################   
    atlin_ = None 
    
    keepRunning_ = True
    waitTime_ = 60 # the number of seconds to wait before checking for new jobs
     
    # This dictionary connects job type flags to the tool which handles them
    jobHandleDict = {}
    
    # logger
    logger_ = None
     
    #########################################################################
    # CONSTRUCTOR
    #########################################################################
    
    def __init__(   self,
                    dataBaseDomain = "http://localhost:6010",
                    waitTime = 60):
        
        self.waitTime_ = waitTime
   
        self.keepRunning_ = True
        
        self.atlin_ = Atlin(dataBaseDomain)

        logging.basicConfig(level=logging.INFO)
        self.logger_ = logging.getLogger(__name__)
                    
    #########################################################################
    # PRIVATE FUNCTIONS
    #########################################################################
   
    ############################################################################################
    # This function will take in a list of dictionarys which describe a job and creates seperate
    # threads to run them
    def _submitJobs(self, 
                    listOfJobJSON : List[any]):

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
                    print('[ERROR]: Unknown Job Type: ', jobType)
            
            # this allows the context manager to return before each process is finished
            # which means the scheduler is free to go back and check for other new jobs
            executor.shutdown(wait=False)

        return

    ############################################################################################
    # Handle API request for job with status == CREATED
    def _getJobs(self,
                 jobStatus: JobStatus):
        response = None
        
        # request all the "created"
        try:
            response = self.atlin_.job_get(job_status=[jobStatus])
        except Exception as e:
            self.logger_.error(e)  
            print('ERROR: _getJobs: ',e)    

        return response

    ############################################################################################
    # Helper function that returns a list of currently used token_uids
    def _getCurrentlyUsedTokenIDs(self) -> list:
        
        usedTokenIDs = []
        
        try:
            runningJobsList = self._getJobs(JobStatus().running).json()
        
            for job in runningJobsList:
                usedTokenIDs.append(job['token_uid'])
        
        except Exception as e:
            self.logger_.error(e)
            print('ERROR: _getCurrentlyUsedTokenIDs: ', e) 
        
        return usedTokenIDs

    ############################################################################################
    # Merges the created and paused jobs and returns a list sort by age (oldest to youngest) 
    def _getPotentiallyRunnableJobs(self) -> list:
        potentiallyRunnableJobs = []
        
        try:
            createdJobs = self._getJobs(JobStatus().created).json()
            pausedJobs = self._getJobs(JobStatus().paused).json()
        
            potentiallyRunnableJobs = createdJobs + pausedJobs
                   
            potentiallyRunnableJobs.sort(key= lambda job: job['create_date'])
                
        except Exception as e:
            self.logger_.error(e)
            print('ERROR: _getCurrentlyUsedTokenIDs: ', e) 
        
        return potentiallyRunnableJobs
        

    ############################################################################################
    # This function compares rows in the jobs table with the status CREATED with those that are 
    # currently status RUNNING. If the token_uid of a CREATED job is not currenly used by a 
    # RUNNING job it is added to the returned list.
    def _checkDataBaseForRunnableJobs(self) -> list:
        
        runnableJobs = []
        
        try:
            # createdJobs = self._getJobs(JobStatus().created).json()
            potentiallyRunnableJobs = self._getPotentiallyRunnableJobs()
            usedTokenIDs = self._getCurrentlyUsedTokenIDs()
            
            # for job in createdJobs:
            for job in potentiallyRunnableJobs:
                if job['token_uid'] not in usedTokenIDs:
                    runnableJobs.append(job)   
                    usedTokenIDs.append(job['token_uid'])
             
        except Exception as e:
            self.logger_.error(e)
            print('ERROR: _checkDataBaseForRunnableJobs: ', e) 
            
        return runnableJobs
    
    ############################################################################################
    # This function checks the data base for any rows in the JobsTable which has a job
    # status set to CREATED
    def _checkDataBaseForJobsToSubmit(self) -> None:
        
        try:
            runnableJobs = self._checkDataBaseForRunnableJobs()
                      
            # This function will submit the jobs to be run on seperate processes
            self._submitJobs(runnableJobs)
               
        except Exception as e:
            self.logger_.error(e)
            print('ERROR: _checkDataBaseForJobsToSubmit: ', e) 
                       
    ############################################################################################
    # This function checks for any sort of exit conditions
    def _checkExit(self):
        logging.info('CheckExit')
        
        return True
     
    #########################################################################
    # PUBLIC FUNCTIONS
    #########################################################################
    
    ############################################################################################
    # Add a new job type, and the ToolInterface to run it
    def AddJobType( self,
                    jobType : str,
                    toolFunctionPoint : Callable) -> None:

        if callable(toolFunctionPoint):
            self.jobHandleDict[jobType] = toolFunctionPoint
        else:
            logging.error('AddJobType: argument \'toolFunctionPoint\' not a callable type')
            raise TypeError
                
    ############################################################################################
    # This is the main loop for the job scheduler
    def Run(self):
                
        while self.keepRunning_:
            
            # This function will check the database for news and return a list of dictionaries with
            # the row ID of the new job
            self.logger_.info('Checking jobs ready...')
            self._checkDataBaseForJobsToSubmit()
            
            # don't spam the API
            time.sleep(self.waitTime_)
            
            # check if some type of exit condition has been set
            self._checkExit()

##############################################################################################################

if __name__ == '__main__':
        
    js = JobScheduler(waitTime=WAIT_TIME)
    
    js.AddJobType('REDDIT', RedditInterface)
    js.AddJobType('YOUTUBE', YouTubeInterface)
    js.AddJobType('CRAWL', CrawlerInterface)
    
    js.Run()
    
