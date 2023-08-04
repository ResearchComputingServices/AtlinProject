import logging
from pathlib import Path
import sys
import time

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()
sys.path.insert(0, BASE_DIR)

from Tools.RedditAPITool.RedditAPISession import RedditAPISession
from Tools.RedditAPITool.RedditUtils import *
from atlin_api.atlin_api import *

####################################################################################################
#
####################################################################################################

def UpdateQuota(jobJSON, quotaUsed) -> None:
    atlin = Atlin("http://localhost:6010")

    token_uid = jobJSON['token_uid']
    
    token = atlin.token_get(token_uid=token_uid )

    return

####################################################################################################
# This function handles the get request and any associated errors
####################################################################################################
def getCredentialsDictFromDB(jobJSON) -> dict:

    atlin = Atlin("http://localhost:6010")

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
# { 'sortBy': 'new', 
#   'timeFrame': 'all', 
#   'n': 1, 
#   'subreddit': 'canada', 
#   'user': '', 
#   'post': ['', ''], 
#   'keyword': '', 
#   'getposts': 1, 
#   'getcomments': 0}
# {
#   "job_submit": {
#     "actions": [
#       "KEYWORD"
#     ],
#     "post_list": "",
#     "option_type": "POST",
#     "sort_option": "TOP",
#     "keyword_list": "maple",
#     "response_count": "10",
#     "subreddit_list": "Canada"
#   }
# }
####################################################################################################
def getJobDict(jobJSON) -> dict:
    
    jobDictDB = jobJSON['job_detail']['job_submit']
    
    print(jobDictDB)

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
def RedditInterface(jobJSON):
   
    # TODO: remove this after dev
    logging.info('\n\n\n HERE HERE HERE \n\n\n')

    logging.info('RedditInterface: Preforming Reddit job:')
    
    # the credientals  and job details from the JOB_JSON object    
    jobDict = getJobDict(jobJSON)
    logging.info('RedditInterface:', jobDict)
    
    credentialsDict = getCredentialsDict(jobJSON)
    
    logging.info('RedditInterface: credentialsDict RECIEVED')
    
    # connect to reddit API
    session = RedditAPISession(credentialsDict) 
    logging.info('RedditInterface: RedditAPISession started.')
    
    # the return value
    jobStatus = None
    
    # execute the job as defined by the jobDict
    if session.HandleJobDict(jobDict):
        
        logging.info('RedditInterface: RedditAPISession Job completed.')
        # TODO: Get the correct folder path
        save_path = str('./')  
        if session.SaveResponses(save_path)    :
            logging.info('RedditInterface: Data saved.')
        else:
            logging.info('RedditInterface: Unable to save data.')

        # TODO: Update the quota
        #quotaUsed = session.GetNumberOfRequests()
        #UpdateQuota(jobJSON, quotaUsed)

        # update the returned job status
        jobStatus = JobStatus().success
    
    else:
        jobStatus = JobStatus().failure
        logging.info('RedditInterface: RedditAPISession Job FAILED.')
    
    # disconnect from the reddit API
    session.End()

    return  jobStatus
 
#############################################################################################
# Test Code:
if __name__ == '__main__':     

    dataBaseDomain = "http://localhost:6010"
    
    atlin = Atlin(dataBaseDomain)

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