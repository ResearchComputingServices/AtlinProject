import logging
from pathlib import Path
import sys
import os

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()
sys.path.insert(0, BASE_DIR)

from Tools.RedditAPITool.RedditAPISession import RedditAPISession
from Tools.RedditAPITool.RedditUtils import *
from atlin_api.atlin_api import *
import Config as config

####################################################################################################
#
####################################################################################################

def UpdateQuota(jobJSON, quotaUsed) -> None:
    atlin = Atlin(config.ATLIN_API_ADDRESS)

    token_uid = jobJSON['token_uid']
    
    token = atlin.token_get(token_uid=token_uid )

    return

####################################################################################################
#
####################################################################################################

def UpdateOutputPath(jobJSON, output_path) -> None:
    atlin = Atlin(config.ATLIN_API_ADDRESS)

    jobJSON['output_path'] = output_path

    atlin.job_update(job_uid = jobJSON['job_uid'],
                     data = jobJSON.to_dict())
        
    return

####################################################################################################
# This function handles the get request and any associated errors
####################################################################################################
def getCredentialsDictFromDB(jobJSON) -> dict:

    atlin = Atlin(config.ATLIN_API_ADDRESS)

    tokenReturn = {}
    try :          
        response = atlin.token_get( user_uid=jobJSON['user_uid'],
                                    social_platform=jobJSON['social_platform'],
                                    token_uid=jobJSON['token_uid'])
        
        if response.status_code == 200:
            tokenReturn = response.json()['token_detail']
        else:
            logging.warning('RedditAPIInderface::getCredentialsDictFromDB: failed error code:', response.status_code)
    except Exception as e:
        logging.error('getCredentialsDictFromDB:', e)

    return tokenReturn


####################################################################################################
# This function gets the credientials dict from the database and reforms it into what 
# the tool needs
####################################################################################################
def getCredentialsDict(jobJSON) -> dict:
    logging.info('getCredentialsDict: START')
    
    logging.info('getCredentialsDict: Sending API Get Request for creds')   
    tokenDB = getCredentialsDictFromDB(jobJSON)
    logging.info('getCredentialsDict: Received')   

    tokenDict = {   CRED_USERNAME_KEY : tokenDB['username'],
                    CRED_PASSWORD_KEY : tokenDB['password'],
                    CRED_CLIENT_ID_KEY : tokenDB['client_id'],
                    CRED_SECRET_TOKEN_KEY : tokenDB['secret_token'],
                    CRED_GRANT_TYPE_KEY : CRED_GRANT_TYPE_VALUE}

    logging.info('getCredentialsDict: DONE')   
    
    return tokenDict

####################################################################################################
#
####################################################################################################
def getJobDict(jobJSON) -> dict:
    
    jobDictDB = jobJSON['job_detail']['job_submit']
    
    # TODO: Figure out why some keys are not working out (ie ones in quotes)    
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : jobDictDB['sort_option'].lower(),
                REDDIT_JOB_DETAIL_TIME_FRAME : 'all',  
                'n' : int(jobDictDB['response_count']), 
                REDDIT_JOB_DETAIL_SUBREDDIT: jobDictDB['subreddit_list'],
                'user': '',
                'post': ['', ''],
                'keyword': jobDictDB['keyword_list'],
                'getposts': 0,
                REDDIT_JOB_DETAIL_COMMENTS: 0}
    
    if jobDictDB['option_type'] == "POST":
        jobDict['getposts'] = 1

    return jobDict

####################################################################################################
#
####################################################################################################
def GenerateOutputDirectory(jobJSON) -> str:
    
    job_uid = jobJSON['job_uid']
    
    output_path = os.path.join(os.getcwd(), job_uid)

    #Check if the output directory exists, it if doesn't create it.
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    UpdateOutputPath(jobJSON, output_path)

    return output_path   

####################################################################################################
#
####################################################################################################
def RedditInterface(jobJSON):
   
    logger = logging.getLogger('RedditInterface')
     
    job_uid = jobJSON['job_uid']
    logger.info(f'Preforming Reddit job: {job_uid}')
    
    # the credientals  and job details from the JOB_JSON object    
    jobDict = getJobDict(jobJSON)
    logger.info('RedditInterface jobDict:', jobDict)
    
    credentialsDict = getCredentialsDict(jobJSON)
    logger.info('credentialsDict RECIEVED')
    
    # create an output directory to store the collected data in
    GenerateOutputDirectory(jobJSON)
    
    # connect to reddit API
    session = RedditAPISession(credentialsDict) 
    logger.info('RedditAPISession started.')
    
    # the return value
    jobStatus = None
    
    # execute the job as defined by the jobDict
    if session.HandleJobDict(jobDict):
        
        logger.info('RedditAPISession Job completed.')
        
        if session.SaveResponses(jobJSON['output_path']):
            logging.info('RedditInterface: Data saved.')
        else:
            logging.info('RedditInterface: Unable to save data.')

        # TODO: Update the quota
        #quotaUsed = session.GetNumberOfRequests()
        #UpdateQuota(jobJSON, quotaUsed)

        # update the returned job status
        jobStatus = JobStatus().success
    
    else:
        jobStatus = JobStatus().failed
        logger.info('RedditInterface: RedditAPISession Job FAILED.')
    
    # disconnect from the reddit API
    session.End()

    return  jobStatus
 
#############################################################################################
# Test Code:
if __name__ == '__main__':     

    atlin = Atlin(config.ATLIN_API_ADDRESS)

    response = atlin.job_get_by_uid('9978d901-96e6-4a80-bfec-3a7dd87d81ab')
    
    aRedditJob = RedditJobDetails()
    aRedditJob.subreddit = 'canada'
    aRedditJob.getposts = '1'
    aRedditJob.n = 100
    
    print(aRedditJob.to_dict())

    myToken = RedditToken()

    myToken.social_platform = 'reddit'
    myToken.token_uid

    #RedditInterface(jobJSON)