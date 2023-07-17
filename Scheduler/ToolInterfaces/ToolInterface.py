import logging
import time

from Scheduler.Utils import *

from AtlinAPI.AtlinAPI.atlin import *

import sys
sys.path.insert(0, BASE_DIR)


def UpdateJobStatus(job_uid, status) -> None:
    
    # Set up connection to database
    atlin = AtlinReddit("http://localhost:6010")
    
    statusCode = 404
    
    while statusCode != 200:
        response = atlin.job_set_status(job_uid, status)
        statusCode = response.status_code
        time.sleep(1)

    return

####################################################################################################
#
####################################################################################################
def genericInterface(toolFunctionPointer, jobJSON):
         
    # For some reason the logging it not working  
    # logging.info('PERFORMING JOBS:',flush=True)
    # logging.info(jobJSON,flush=True)
           
    job_uid = jobJSON['job_uid']
    
    # Set the job status to "RUNNING"
    UpdateJobStatus(job_uid, JobStatus().running)
 
    # Make call to tool
    jobCompleteStatus = toolFunctionPointer(jobJSON)
    
    # update job status to as either SUCCESS or FAILURE
    UpdateJobStatus(job_uid, jobCompleteStatus)
 
    return  
