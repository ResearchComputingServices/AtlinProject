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

        atlin.job_update(   job_uid = jobJSON['job_uid'],
                            data = jobJSON)
        
    except Exception as e:
        logger.debug(e)    
    
    return

####################################################################################################
#
####################################################################################################

def UpdateJobMsg(jobJSON, job_msg) -> None:
            
    return

####################################################################################################
#
####################################################################################################
def GenerateOutputDirectory(jobJSON) -> str:
    
    job_uid = jobJSON['job_uid']
    
    #Check if the main output directory exists, it if doesn't create it.
    if not os.path.isdir(config.MAIN_OUTPUT_DIR):
        os.mkdir(config.MAIN_OUTPUT_DIR)
    
    # generate the job specific output directory    
    output_path = os.path.join(config.MAIN_OUTPUT_DIR, job_uid)

    #Check if the output directory exists, it if doesn't create it.
    if not os.path.isdir(output_path):
        os.mkdir(output_path)

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
####################################################################################################
def checkKeyword(jobDictDB):
    
    keywords = ''
    getposts = 1
    
    if 'keyword_list' in jobDictDB.keys():
        keywords = jobDictDB['keyword_list']
        getposts = 0
    
    return keywords, getposts

####################################################################################################
#
####################################################################################################
def checkGetComments(jobDictDB):
    getcomments = 1
    if jobDictDB['scrape_comments'] == 'false':
        getcomments = 0
        
    return getcomments

####################################################################################################
#
#################################################################################################### 
def getSubredditJobDict(jobDictDB):
    
    sort_by, time_frame = decodeSortOption(jobDictDB['sort_option'])
        
    keywords, getposts = checkKeyword(jobDictDB)
   
    getcomments = checkGetComments(jobDictDB)
   
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : sort_by,
                REDDIT_JOB_DETAIL_TIME_FRAME : time_frame,  
                REDDIT_JOB_DETAIL_N : int(jobDictDB['response_count']), 
                REDDIT_JOB_DETAIL_SUBREDDIT: jobDictDB['subreddit_list'],
                REDDIT_JOB_DETAIL_USER: '',
                REDDIT_JOB_DETAIL_POST: ['', ''],
                REDDIT_JOB_DETAIL_KEYWORD: keywords,
                REDDIT_JOB_DETAIL_GETPOSTS: getposts,
                REDDIT_JOB_DETAIL_COMMENTS: getcomments}

    return jobDict

####################################################################################################
#
####################################################################################################
def getPostJobDict(jobDictDB):
    
    sort_by, time_frame =decodeSortOption(jobDictDB['sort_option'])
    getcomments = checkGetComments(jobDictDB)
    
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : sort_by,
                REDDIT_JOB_DETAIL_TIME_FRAME : time_frame,  
                REDDIT_JOB_DETAIL_N : 0,  # this type of request does not need an N value
                REDDIT_JOB_DETAIL_SUBREDDIT: '',
                REDDIT_JOB_DETAIL_USER: '',
                REDDIT_JOB_DETAIL_POST: [jobDictDB['subreddit_name'], jobDictDB['post_list']],
                REDDIT_JOB_DETAIL_KEYWORD: '',
                REDDIT_JOB_DETAIL_GETPOSTS: 1-getcomments,
                REDDIT_JOB_DETAIL_COMMENTS: getcomments}
    
    return jobDict

####################################################################################################
#
####################################################################################################
def getUserJobDict(jobDictDB):
    
    sort_by, time_frame =decodeSortOption(jobDictDB['sort_option'])
    getcomments = checkGetComments(jobDictDB)
    
    jobDict = { REDDIT_JOB_DETAIL_SORT_BY : sort_by,
                REDDIT_JOB_DETAIL_TIME_FRAME : time_frame,  
                REDDIT_JOB_DETAIL_N : int(jobDictDB['response_count']), 
                REDDIT_JOB_DETAIL_SUBREDDIT: '',
                REDDIT_JOB_DETAIL_USER: jobDictDB['username_list'],
                REDDIT_JOB_DETAIL_POST: ['', ''],
                REDDIT_JOB_DETAIL_KEYWORD: '',
                REDDIT_JOB_DETAIL_GETPOSTS: 1-getcomments,
                REDDIT_JOB_DETAIL_COMMENTS: getcomments}

    return jobDict

####################################################################################################
#
####################################################################################################
def getJobDict(jobJSON) -> dict:
    
    logger = logging.getLogger('RedditInterface')
    jobDict = None

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
        logger.error(e)
        
    return jobDict

####################################################################################################
# save the scraped data to a output folder previously generated.
####################################################################################################
def SaveResponses(jobJSON, listOfResponses) -> bool:
    
    success_flag = False
    
    folderPath = jobJSON['output_path']
    
    # check if the file path exists and is accessbile then write the listOfResponses_ to the file
    if os.path.exists(folderPath):          
        filename = jobJSON['job_name']+'.json'
        
        filePath = os.path.join(folderPath, filename)
        file = open(filePath, "w")
        
        if len(listOfResponses) == 0:
            file.write('No data found matching scraping criteria.')
        
        else:
            for responseJSON in listOfResponses:
                dict = responseJSON['data']
                
                for key in dict.keys():                        
                    file.write(str(key)+' : ' + str(dict[key]) + '\n')
            
                file.write(RESPONSE_BREAK+'\n')
        
        file.close()     
        
        success_flag = True   
            
    return success_flag

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
    logger.info('JobJSON from DB: \n', jobJSON)
    
    # the credientals  and job details from the JOB_JSON object    
    jobDict = getJobDict(jobJSON)
    
    if jobDict != None:
        logger.info('jobDict:', jobDict)
    
        credentialsDict = getCredentialsDict(jobJSON)
    
        # create an output directory to store the collected data in
        output_path = GenerateOutputDirectory(jobJSON)
        
        UpdateOutputPath(jobJSON, output_path)
        
        # connect to reddit API
        session = RedditAPISession(credentialsDict) 
            
        # execute the job as defined by the jobDict
        if session.HandleJobDict(jobDict):
            logger.info('Job completed: SUCCESS.')    
            
            if SaveResponses(jobJSON, session.GetResponses()):
                logger.info('Job saved.')
                jobStatus = JobStatus().success
            else:
                logging.error('Unable to save job.')
                jobStatus = JobStatus().failed
            
            # update quota used
            quotaUsed = session.GetNumberOfRequests()
            UpdateQuota(jobJSON, quotaUsed)

        else:
            logger.error('Job completed: FAILED.')
        
        # update the job_message with the message returned form RedditAPISession
        UpdateJobMsg(jobJSON, session.get_job_msg())        
        
        # disconnect from the reddit API
        session.End()
        logger.info('session ENDED.')

    return jobStatus
 
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