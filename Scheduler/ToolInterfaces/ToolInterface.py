import logging
import time

from Scheduler.Utils import *

from atlin_api.atlin_api import *

import sys
sys.path.insert(0, BASE_DIR)


####################################################################################################
# This function will continue to attempt to update the status of a job until sucessful (code 200)
def updateJobStatus(job_uid, status) -> None:
    
    logger = logging.getLogger('genericInterface')
       
    # Set up connection to database
    atlin = Atlin("http://localhost:6010")

    statusCode = atlin.job_set_status(job_uid, status).status_code
    
    while statusCode != 200:
        logger.warning('updateJobStatus: Failed to update status. Attempting again')
        statusCode = atlin.job_set_status(job_uid, status).status_code
        time.sleep(1)

    return

####################################################################################################
# A Generic Tool Interface which ensures the job status is updated correctly
def genericInterface(toolFunctionPointer, jobJSON):

    job_uid = jobJSON['job_uid']
                   
    # Set the job status to "RUNNING"
    updateJobStatus(job_uid, JobStatus().running)
 
    # Make call to tool
    jobCompleteStatus = toolFunctionPointer(jobJSON)
    
    # update job status to as either SUCCESS or FAILURE
    updateJobStatus(job_uid, jobCompleteStatus)
     
    return  
