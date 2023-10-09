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
    
    atlin.token_set_quota(token_uid, 'REDDIT', quotaUsed)

    return

####################################################################################################
#
####################################################################################################

def UpdateOutputPath(jobJSON, output_path) -> None:
    
    logger = logging.getLogger('RedditInterface')
    
    try:
        atlin = Atlin(config.ATLIN_API_ADDRESS)

        jobJSON['output_path'] = output_path
        jobJSON['job_status'] = "RUNNING"

        atlin.job_update(job_uid = jobJSON['job_uid'],
                        data = jobJSON)
    except Exception as e:
        logger.debug(e)    
    
    return

####################################################################################################
#
####################################################################################################
def GenerateOutputDirectory(jobJSON) -> str:
    
    job_uid = jobJSON['job_uid']
    output_path = os.path.join(config.MAIN_OUTPUT_DIR, job_uid)

    #Check if the output directory exists, it if doesn't create it.
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

    UpdateOutputPath(jobJSON, output_path)

    return output_path   
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
def initializeJobDict() -> dict:
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : 'new',
                REDDIT_JOB_DETAIL_TIME_FRAME : 'all',  
                REDDIT_JOB_DETAIL_N : 5, 
                REDDIT_JOB_DETAIL_SUBREDDIT: 'canada',
                REDDIT_JOB_DETAIL_USER: '',
                REDDIT_JOB_DETAIL_POST: ['', ''],
                REDDIT_JOB_DETAIL_KEYWORD: '',
                REDDIT_JOB_DETAIL_GETPOSTS: 1,
                REDDIT_JOB_DETAIL_COMMENTS: 0}

    return jobDict

####################################################################################################
#
####################################################################################################
def decodeSortOption(sort_option: str) -> str:
    sort_string = ''
    
    if sort_option == 'TOP_TODAY.':
        sort_string = 'top/?t=day'
    elif sort_option == 'TOP_WEEK.':
        sort_string = 'top/?t=week'
    elif sort_option == 'TOP_MONTH.':
        sort_string = 'top/?t=month'
    elif sort_option == 'TOP_YEAR.':
        sort_string = 'top/?t=year'
    elif sort_option == 'TOP_ALL.':
        sort_string = 'top/?t=all'
    elif sort_option == 'BEST.':
        sort_string = 'hot'
    else:
        sort_string = 'new'
    
    return sort_string

####################################################################################################
#
# 'job_detail': {
#       'job_submit': {
#           'post_list': '', 
#           'option_type': 'SUBREDDIT', 
#           'sort_option': 'TOP_TODAY', 
#           'scrape_option': 'BASIC', 
#           'username_list': '', 
#           'response_count': '5', 
#           'subreddit_list': 'canada', 
#           'subreddit_name': '', 
#           'scrape_comments': 'false'}},
#################################################################################################### 
def getSubredditJobDict(jobDictDB):
    
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : decodeSortOption(jobDictDB['sort_option']),
                REDDIT_JOB_DETAIL_TIME_FRAME : 'all',  
                REDDIT_JOB_DETAIL_N : int(jobDictDB['response_count']), 
                REDDIT_JOB_DETAIL_SUBREDDIT: jobDictDB['subreddit_list'],
                REDDIT_JOB_DETAIL_USER: '',
                REDDIT_JOB_DETAIL_POST: ['', ''],
                REDDIT_JOB_DETAIL_KEYWORD: jobDictDB['keyword_list'],
                REDDIT_JOB_DETAIL_GETPOSTS: 1,
                REDDIT_JOB_DETAIL_COMMENTS: 0}
    
    return jobDict

####################################################################################################
#
# 'job_detail': {
#         'job_submit': {
#             'post_list': '173bygx\n    ', 
#             'option_type': 'POST', 
#             'sort_option': 'BEST', 
#             'keyword_list': '', 
#             'scrape_option': '', 
#             'username_list': '', 
#             'response_count': '', 
#             'subreddit_list': '', 
#             'subreddit_name': 'canada', 
#             'scrape_comments': ''}
#             }, 
####################################################################################################
def getPostJobDict(jobDictDB):
    
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : decodeSortOption(jobDictDB['sort_option']),
                REDDIT_JOB_DETAIL_TIME_FRAME : 'all',  
                REDDIT_JOB_DETAIL_N : int(jobDictDB['response_count']), 
                REDDIT_JOB_DETAIL_SUBREDDIT: '',
                REDDIT_JOB_DETAIL_USER: '',
                REDDIT_JOB_DETAIL_POST: [jobDictDB['subreddit_list'], jobDictDB['post_list']],
                REDDIT_JOB_DETAIL_KEYWORD: '',
                REDDIT_JOB_DETAIL_GETPOSTS: 1,
                REDDIT_JOB_DETAIL_COMMENTS: 0}
    
    return jobDict

####################################################################################################
#
# 'job_detail': {
#       'job_submit': {
#           'post_list': '', 
#           'option_type': 'USER', 
#           'sort_option': 'BEST', 
#           'keyword_list': '', 
#           'scrape_option': '', 
#           'username_list': 'DonSalaam', 
#           'response_count': '5', 
#           'subreddit_list': '', 
#           'subreddit_name': '', 
#           'scrape_comments': 'false'}}
####################################################################################################
def getUserJobDict(jobDictDB):
    
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : decodeSortOption(jobDictDB['sort_option']),
                REDDIT_JOB_DETAIL_TIME_FRAME : 'all',  
                REDDIT_JOB_DETAIL_N : int(jobDictDB['response_count']), 
                REDDIT_JOB_DETAIL_SUBREDDIT: '',
                REDDIT_JOB_DETAIL_USER: jobDictDB['username_list'],
                REDDIT_JOB_DETAIL_POST: ['', ''],
                REDDIT_JOB_DETAIL_KEYWORD: '',
                REDDIT_JOB_DETAIL_GETPOSTS: 1,
                REDDIT_JOB_DETAIL_COMMENTS: 0}

    return jobDict

####################################################################################################
#
####################################################################################################

def getJobDict(jobJSON) -> dict:
    
    logger = logging.getLogger('RedditInterface')
    try:
        jobDict = initializeJobDict()
            
        jobDictDB = jobJSON['job_detail']['job_submit']
        job_type = jobDictDB['option_type']
        
        if job_type == 'SUBREDDIT':
            jobDict = getSubredditJobDict(jobDictDB) 
        elif job_type == 'POST':
            jobDict = getPostJobDict(jobDictDB) 
        elif job_type == 'USER':
            jobDict = getUserJobDict(jobDictDB) 
        else:
            logger.info(f'Unknown option_type: {job_type}')
    except Exception as e:
        logger.info(e)
        
    return jobDict

####################################################################################################
#
####################################################################################################
def RedditInterface(jobJSON):
   
    logger = logging.getLogger('RedditInterface')
     
    job_uid = jobJSON['job_uid']
    logger.info(f'Preforming Reddit job: {job_uid}')
    
    # the credientals  and job details from the JOB_JSON object    
    logger.info('Constructing jobDict')
    jobDict = getJobDict(jobJSON)
    logger.info('RedditInterface jobDict:', jobDict)
    
    logger.info('Waiting for credentials')
    credentialsDict = getCredentialsDict(jobJSON)
    logger.info('credentialsDict RECIEVED')
    
    # create an output directory to store the collected data in
    GenerateOutputDirectory(jobJSON)
    logger.info('Output directory generated')
    
    # connect to reddit API
    session = RedditAPISession(credentialsDict) 
    logger.info('RedditAPISession started.')
    
    # the return value
    jobStatus = None
    
    # execute the job as defined by the jobDict
    if session.HandleJobDict(jobDict):
                
        if session.SaveResponses(jobJSON):
            logging.info('RedditInterface: Data saved.')
        else:
            logging.info('RedditInterface: Unable to save data.')

        # update quota used
        quotaUsed = session.GetNumberOfRequests()
        UpdateQuota(jobJSON, quotaUsed)

        # update the returned job status
        jobStatus = JobStatus().success
        
        logger.info('RedditAPISession Job completed SUCCESSFULLY.')
    else:
        jobStatus = JobStatus().failed
        logger.info('RedditInterface Job completed FAILED.')
    
    # disconnect from the reddit API
    session.End()
    logger.info('RedditInterface: session ENDED.')

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