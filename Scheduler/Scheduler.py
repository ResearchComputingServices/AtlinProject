import concurrent.futures
import time
from itertools import repeat

import sys
sys.path.insert(0, '../')
from AtlinAPI.AtlinAPI.atlin import *

from Utils import  *

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
    dataBaseConnection_ = None
    dataBaseFilePath_ = None
    
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
        
        # ToDo: Connect to the data base API
        self.atlin_ = AtlinReddit(dataBaseDomain)
    
        logging.basicConfig(level=logging.INFO)    
        self.logger_ = logging.getLogger(__name__)
                    
    #########################################################################
    # PRIVATE FUNCTIONS
    #########################################################################
   
    ############################################################################################
    # This function will take in a list of dictionarys which describe a job and creates seperate
    # threads to run them
    def submitJobs(self, 
                   listOfJobJSON):

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
    def _getNewJobs(self):
        response = None
        
        # request all the "created"
        try:
            response = self.atlin_.job_get(job_status=[JobStatus().created])
        except Exception as e:
            self.logger_.error(e)  
            print('ERROR: _getNewJobs: ',e)    

        return response

    ############################################################################################
    # This function checks the data base for any rows in the JobsTable which has a job
    # status set to CREATED
    def checkDataBaseForNewJobs(self) -> None:
        
        try:
            response = self._getNewJobs()
    
            # This function will submit the jobs to be run on seperate processes
            self.submitJobs(response.json())
               
        except Exception as e:
            self.logger_.error(e)
            print('ERROR: checkDataBaseForNewJobs: ', e) 

    ############################################################################################
    # This function checks the data base for any rows in the JobsTable which has a job
    # status set to READY
    def CheckOnWaitingJobs(self) -> None:
        
        # request all the "created"
        response = None
        try:
            response = self.atlin_.job_get(job_status=[JobStatus().paused])         
        except Exception as e:
            self.logger_.error(e)
            print('ERROR: CheckOnWaitingJobs: ',e)
            
        # TODO: Fill in the code here to change waiting jobs to ready jobs
           
    ############################################################################################
    # This function checks for any sort of exit conditions
    def checkExit(self):
        print('CheckExit')
        
        return True
     
    #########################################################################
    # PUBLIC FUNCTIONS
    #########################################################################
    
    ############################################################################################
    # Add a new job type, and the ToolInterface to run it
    def AddJobType( self,
                    jobType : str,
                    toolFunctionPoint) -> None:

        self.jobHandleDict[jobType] = toolFunctionPoint
    
    
    ############################################################################################
    # This is the main loop for the job scheduler
    def Run(self):
                
        while self.keepRunning_:
            
            # ToDo: Get all waiting jobs and check to see if any can be set to created
            # ToDo: I think the job status should be ready not created
            self.logger_.info('Checking jobs waiting...')
            self.CheckOnWaitingJobs()
            
            # This function will check the database for news and return a list of dictionaries with
            # the row ID of the new job
            self.logger_.info('Checking jobs ready...')
            self.checkDataBaseForNewJobs()
            
            
            time.sleep(WAIT_TIME)
            
            # check if some type of exit condition has been set
            self.checkExit()


##############################################################################################################
if __name__ == '__main__':
        
    js = JobScheduler(waitTime=5)
    
    js.AddJobType('reddit', RedditInterface)
    # js.AddJobType('youtube', YouTubeInterface)
    # js.AddJobType('crawl', CrawlerInterface)
    
    js.Run()
    
