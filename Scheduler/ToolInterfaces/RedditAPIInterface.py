import logging
# from Scheduler.Utils import *

# from AtlinAPI.AtlinAPI.atlin import *

# import sys
# sys.path.insert(0, BASE_DIR)

# from Tools.RedditAPITool.RedditAPISession import RedditAPISession

# ####################################################################################################
# #
# ####################################################################################################
# def PerformRedditAPICall(jobJSON):
    
#     listOfResponsesJSON = []

#     # the credientals  and job detailsfrom the JOB_JSON object    
#     jobDict = jobJSON.JobJSON
#     credentialsDict = jobJSON.credentialsDict
    
#     # connect to reddit API
#     session = RedditAPISession(credentialsDict) 
    
#     # execute the job as defined by the jobDict
#     listOfResponsesJSON = session.HandleJobDict(jobDict) 
    
#     # disconnect from the reddit API
#     session.End()
            
#     return listOfResponsesJSON

# ####################################################################################################
# #
# ####################################################################################################
# def RedditInterface(jobJSON):
   
#     logging.info('PERFORMING JOBS:',flush=True)
#     logging.info(jobJSON,flush=True)
   
#     # Set up connection to database
#     atlin = AtlinReddit("http://localhost:5000")
   
   
#     job_uid = jobJSON['job_uid']
#     # Set the job status to "RUNNING"
#     atlin.set_job(job_uid, JobStatus().running)

#     # make the reddit API call
#     listOfResponsesJSON = PerformRedditAPICall(jobJSON)

#     # TODO: this should be handled by the tool.
#     # save the output to a file
#     # filePath = SaveOutput(listOfResponsesJSON)
  
#     # update job status to "DONE" 
#     atlin.set_job(job_uid, JobStatus().done)


#     return  

def RedditInterface(jobJSON):
   
    logging.info('PERFORMING JOBS:',flush=True)
    logging.info(jobJSON,flush=True)
   
    return 