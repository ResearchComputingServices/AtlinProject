import logging

BASE_DIR ='/home/nickshiell/Documents/Work/SocialMediaAPIInterface/SocialMediaAPIInterface/'

#from Scheduler.Utils import *

import sys
sys.path.insert(0, BASE_DIR)

from Tools.RedditAPITool.RedditAPISession import RedditAPISession
from AtlinAPI.AtlinAPI import *

####################################################################################################
#
####################################################################################################

def UpdateQuota(jobJSON, quotaUsed) -> None:
    atlin = AtlinReddit("http://localhost:6010")

    token_uid = jobJSON['token_uid']
    
    token = atlin.token_get(token_uid=token_uid )

    return

####################################################################################################
#
####################################################################################################
def getCredentialsDict(token_uid) -> dict:
    atlin = AtlinReddit("http://localhost:6010")
    
    tokenReturn = {}
     
    try :
        response = atlin.token_get(token_uid=token_uid)
        if response.status_code == 200:
            tokenReturn = response.json['token_details']
            
    except Exception as e:
        print(e)
        
    
    return tokenReturn

####################################################################################################
#
####################################################################################################
def RedditInterface(jobJSON):

    logging.info('RedditInterface: Preforming Reddit job:')
    logging.info(jobJSON)

    # the credientals  and job details from the JOB_JSON object    
    jobDict = jobJSON['job_detail']
   
    # TODO: put this back in when integration complete
    #credentialsDict = getCredentialsDict(jobJSON['token_uid'])
    
    # TODO: get rid of this when integration complete
    credientalsDict = {}
    credientalsDict['grant_type'] = 'password'
    credientalsDict['CLIENT_ID'] = '_-W7ANd6UN4EXexvgHn8DA'
    credientalsDict['SECRET_TOKEN'] = 'kpBdT1f-nRHM_kxdBzmxoOnDo_96FA'
    credientalsDict['username'] = 'nickshiell'
    credientalsDict['password'] =  'Q!w2e3r4'
    
    # connect to reddit API
    session = RedditAPISession(credientalsDict) 
    
    # the return value
    jobStatus = None
    
    # execute the job as defined by the jobDict
    if session.HandleJobDict(jobDict):
    
        # TODO: Get the correct folder path
        save_path = str('./') 
        session.SaveResponses(save_path)    

        # TODO: Update the quota
        #quotaUsed = session.GetNumberOfRequests()
        #UpdateQuota(jobJSON, quotaUsed)

        # update the returned job status
        jobStatus = JobStatus().success
    
    else:
        jobStatus = JobStatus().failure
    
    # disconnect from the reddit API
    session.End()
    
    # TODO: Remove this line when integration is complete
    jobStatus = JobStatus().success
    return  jobStatus
 
 
 #############################################################################################
 # Test Code:
if __name__ == '__main__':     

    dataBaseDomain = "http://localhost:6010"
    atlin = AtlinReddit(dataBaseDomain)

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