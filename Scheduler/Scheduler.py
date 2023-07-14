import concurrent.futures
import time

import sys
sys.path.insert(0, '../')
from AtlinAPI.AtlinAPI.atlin import *

from Utils import  *

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
    jobHandleDict ={REDDIT_JOB  : RedditInterface,
                    CRAWL_JOB   : CrawlerInterface,
                    TWITTER_JOB : DummyInterface,
                    YOUTUBE_JOB : YouTubeInterface}
        
    #########################################################################
    # CONSTRUCTOR
    #########################################################################
    
    def __init__(   self,
                    dataBaseDomain = "http://localhost:5000",
                    waitTime = 60):
        
        self.waitTime_ = waitTime
   
        self.keepRunning_ = True
        
        # ToDo: Connect to the data base API
        self.atlin_ = AtlinReddit(dataBaseDomain)
        
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
                jobType = jobJSON['jobType']
            
                if jobType in self.jobHandleDict.keys():
                     # start a process that will execute the correct script
                    executor.submit(self.jobHandleDict[jobType],
                                    jobJSON) 
                else:
                    print('[ERROR]: Unknown Job Type: ', jobType)
            
            # this allows the context manager to return before each process is finished
            # which means the scheduler is free to go back and check for other new jobs
            executor.shutdown(wait=False)

        return

    ############################################################################################
    # This function checks the data base for any rows in the JobsTable which has a job
    # status set to CREATED
    def checkDataBaseForNewJobs(self):
        
        # request all the "created"
        listOfJobJSON =  self.atlin_.get_jobs(job_status=[JobStatus.create()])
                      
        return listOfJobJSON

    ############################################################################################
    # This function checks the data base for any rows in the JobsTable which has a job
    # status set to READY
    def CheckOnWaitingJobs(self) -> None:
        
        # request all the "created"
        listOfWaitingJobJSON =  self.atlin_.get_jobs(job_status=[JobStatus().paused])
        
        for job in listOfWaitingJobJSON:
            job = job    

    ############################################################################################
    # This function checks for any sort of exit conditions
    def checkExit(self):
        print('CheckExit')
        
        return True
     
    #########################################################################
    # PUBLIC FUNCTIONS
    #########################################################################
       
    ############################################################################################
    # This is the main loop for the job scheduler
    def Run(self):
                
        while self.keepRunning_:
            
            # ToDo: Get all waiting jobs and check to see if any can be set to created
            # ToDo: I think the job status should be ready not created
            self.CheckOnWaitingJobs()
            
            # This function will check the database for news and return a list of dictionaries with
            # the row ID of the new job
            listOfJobJSON = self.checkDataBaseForNewJobs()

            if len(listOfJobJSON) > 0:               
                # This function will submit the jobs to be run on seperate processes
                self.submitJobs(listOfJobJSON)
                
            time.sleep(WAIT_TIME)
            
            # check if some type of exit condition has been set
            self.checkExit()


##############################################################################################################
if __name__ == '__main__':
    
    js = JobScheduler(waitTime=5)
    
    js.Run()
    
