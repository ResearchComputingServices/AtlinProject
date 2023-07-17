import logging
from Scheduler.Utils import *

import sys
sys.path.insert(0, BASE_DIR)

from Tools.RedditAPITool.RedditAPISession import RedditAPISession

from AtlinAPI.AtlinAPI.atlin import *

####################################################################################################
#
####################################################################################################
def RedditInterface(jobJSON):

    # TODO: This is a place holder function for now
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
    print('RUNNING REDDIT JOB')
    print(jobJSON)
    print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~',flush=True)

    # # TODO: For some reason logging is causing the new processes to fail
    # # logging.info('PERFORMING JOBS:')
    # # logging.info(jobJSON)

    # # the credientals  and job detailsfrom the JOB_JSON object    
    # jobDict = jobJSON.JobJSON
    # credentialsDict = jobJSON.credentialsDict
    
    # # connect to reddit API
    # session = RedditAPISession(credentialsDict) 
    
    # # TODO: the session should return how much quota was used and the status of the job (sucess/fail)
    # # execute the job as defined by the jobDict
    # session.HandleJobDict(jobDict) 
    
    # # disconnect from the reddit API
    # session.End()
            
    return  JobStatus().success
 