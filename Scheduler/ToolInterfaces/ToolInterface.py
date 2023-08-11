import logging
import time

from Scheduler.Utils import *

from atlin_api.atlin_api import *

import sys
sys.path.insert(0, BASE_DIR)


####################################################################################################
# This function will continue to attempt to update the status of a job until sucessful (code 200)
def updateJobStatus(job_uid, status) -> None:
    
    logging.debug('updateJobStatus: Updating status: ' + job_uid)
    
    # Set up connection to database
    atlin = Atlin("http://localhost:6010")

    statusCode = atlin.job_set_status(job_uid, status).status_code
    
    while statusCode != 200:
        logging.warning('updateJobStatus: Failed to update status. attepting again')
        statusCode = atlin.job_set_status(job_uid, status).status_code
        time.sleep(1)

    logging.debug('updateJobStatus: Updating status complete')

    return

####################################################################################################
#
def genericInterface(toolFunctionPointer, jobJSON):

    job_uid = jobJSON['job_uid']
   
    logging.info('genericInterface: Starting job: ' + job_uid)
                
    # Set the job status to "RUNNING"
    updateJobStatus(job_uid, JobStatus().running)
 
    # Make call to tool
    jobCompleteStatus = toolFunctionPointer(jobJSON)
    
    # update job status to as either SUCCESS or FAILURE
    updateJobStatus(job_uid, jobCompleteStatus)
    
    logging.info('genericInterface: Finished Job: ' + job_uid)
 
    return  
