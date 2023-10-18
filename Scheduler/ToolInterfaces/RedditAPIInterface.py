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

    # Make the get request to the API
    atlin = Atlin(config.ATLIN_API_ADDRESS)
    response = ''
    try :          
        response = atlin.token_get( user_uid=jobJSON['user_uid'],
                                    social_platform=jobJSON['social_platform'],
                                    token_uid=jobJSON['token_uid'])
    except Exception as e:
        logging.error(e)

    # extract the token_details from the response if successful
    tokenReturn = {}
    if response.status_code == 200:  
        tokenReturn = response.json()['token_detail']
    else:
        logging.warning('API get request failed with error code:', response.status_code)

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
    sort_by_str = ''
    time_frame_str = ''
        
    if sort_option == 'TOP_TODAY':
        sort_by_str = 'top'
        time_frame_str = 'day'
    elif sort_option == 'TOP_WEEK':
        sort_by_str = 'top'
        time_frame_str = 'week'
    elif sort_option == 'TOP_MONTH':
        sort_by_str = 'top'
        time_frame_str = 'month'
    elif sort_option == 'TOP_YEAR':
        sort_by_str = 'top'
        time_frame_str = 'year'
    elif sort_option == 'TOP_ALL':
        sort_by_str = 'top'
        time_frame_str = 'all'
    elif sort_option == 'BEST':
        sort_by_str = 'hot'
        time_frame_str = ''
    elif sort_option == 'KEYWORD':
        sort_by_str = ''
        time_frame_str = ''
    else:
        sort_by_str = 'new'
        time_frame_str = ''
    
    return sort_by_str, time_frame_str

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
    
    sort_by, time_frame =decodeSortOption(jobDictDB['sort_option'])
    
    keywords = ''
    getposts = 1
    if 'keyword_list' in jobDictDB.keys():
        keywords = jobDictDB['keyword_list']
        getposts = 0
        
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : sort_by,
                REDDIT_JOB_DETAIL_TIME_FRAME : time_frame,  
                REDDIT_JOB_DETAIL_N : int(jobDictDB['response_count']), 
                REDDIT_JOB_DETAIL_SUBREDDIT: jobDictDB['subreddit_list'],
                REDDIT_JOB_DETAIL_USER: '',
                REDDIT_JOB_DETAIL_POST: ['', ''],
                REDDIT_JOB_DETAIL_KEYWORD: keywords,
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
    
    sort_by, time_frame =decodeSortOption(jobDictDB['sort_option'])
    
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : sort_by,
                REDDIT_JOB_DETAIL_TIME_FRAME : time_frame,  
                REDDIT_JOB_DETAIL_N : 0,  # this type of request does not need an N value
                REDDIT_JOB_DETAIL_SUBREDDIT: '',
                REDDIT_JOB_DETAIL_USER: '',
                REDDIT_JOB_DETAIL_POST: [jobDictDB['subreddit_name'], jobDictDB['post_list']],
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
    
    sort_by, time_frame =decodeSortOption(jobDictDB['sort_option'])
    
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : sort_by,
                REDDIT_JOB_DETAIL_TIME_FRAME : time_frame,  
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
        jobDict = None
        
    return jobDict

####################################################################################################
#
####################################################################################################
def RedditInterface(jobJSON):
   
    # the return value
    jobStatus =  JobStatus().failed
   
    # initialize logger
    logger = logging.getLogger('RedditInterface')
     
    job_uid = jobJSON['job_uid']
    logger.info(f'Preforming Reddit job: {job_uid}')
    logger.info(jobJSON)
    
    # the credientals  and job details from the JOB_JSON object    
    logger.info('Constructing jobDict')
    jobDict = getJobDict(jobJSON)
    if jobDict != None:
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