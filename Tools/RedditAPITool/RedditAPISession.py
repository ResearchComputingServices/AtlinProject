import argparse
import requests
import logging
import os
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()

import sys
sys.path.insert(0, BASE_DIR)

from RedditAPITool.RedditUtils import *

####################################################################################################
# Objects which are passed back as children in the response to a GET request contain objects.
# Each object has a unique name made up of a TYPE and an ID36 id. The TYPE is one of the following:
#
#   t1_	    Comment
#   t2_	    Account
#   t3_	    Link
#   t4_	    Message
#   t5_	    Subreddit
#   t6_	    Award

##############################################################################################################
# CLASS DEFINITION: RedditInterface 
##############################################################################################################

class RedditAPISession:

    #########################################################################
    # MEMBER(S)
    #########################################################################
    
    header_ = {}
    
    params_ = {}
    
    listOfResponses_ = []
    
    numRequest_ = 0
    
    #########################################################################
    # CONSTRUCTOR(S)
    #########################################################################
    
    def __init__(   self,
                    credientalsDict = {}):
        
        self.credientalsDict_ = credientalsDict
            
        self.generateAuthentifiedHeader()
        
    #########################################################################
    # PRIVATE FUNCTIONS
    #########################################################################

    def generateAuthentifiedHeader( self,
                                    headerKey = 'User-Agent',
                                    headerValue = 'MyAPI/0.0.1'):
               
        # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
        auth = requests.auth.HTTPBasicAuth( self.credientalsDict_['CLIENT_ID'],
                                            self.credientalsDict_['SECRET_TOKEN'])
        
        # setup our header info, which gives reddit a brief description of our app
        self.header_[headerKey] =  headerValue

        # send our request for an OAuth token
        resp = requests.post(   'https://www.reddit.com/api/v1/access_token', # TODO: Make this a CONST somewhere
                                auth=auth, 
                                data=self.credientalsDict_, 
                                headers=self.header_)
                
        # convert response to JSON and get access_token value
        TOKEN = resp.json()['access_token']

        # add authorization to our headers dictionary
        self.header_['Authorization'] = f"bearer {TOKEN}"

    ####################################################################################################
    # This function returns the comments for a given post
    #################################################################################################### 
    def getCommentsFromPost(self,
                            jobDict):

        urlString = API_BASE + 'r/'+jobDict['post'][0]+'/comments/'+jobDict['post'][1]
                    
        return self.requestGet(urlString=urlString,
                               numResultsRequested = jobDict['n'])

    ####################################################################################################
    # This function returns all comments/replies from a given user
    ####################################################################################################
    def getUserComments(self,
                        jobDict):
    
        # Construct the urlSring for the GET request
        urlString = API_BASE + 'user/'+jobDict['user']+'/comments'
        
        # Submit Request  
        return self.requestGet( urlString=urlString,
                                numResultsRequested = jobDict['n'])

    ####################################################################################################
    # This function returns all comments/replies from a given user
    ####################################################################################################
    def getUserPosts(   self, 
                        jobDict):
        # Construct the urlSring for the GET request
        urlString = API_BASE + 'user/' + jobDict['user'] + '/submitted' 
        
        # Submit Request        
        return self.requestGet(urlString=urlString,
                               numResultsRequested = jobDict['n'])
    
    ####################################################################################################
    # This function returns the top (numResponses) posts in the subreddit (subRedditName)
    ####################################################################################################
    def getSubredditPosts(  self,
                            jobDict):
        # Construct the urlSring for the GET request
        urlString = RedditUtils.API_BASE + 'r/'+jobDict['subreddit']+'/'+jobDict['sortBy']
               
        # Submit Request
        return self.requestGet(urlString=urlString,
                               numResultsRequested = jobDict['n'])

    ####################################################################################################
    # This function does a keyword search of a subreddit
    ####################################################################################################
    def getSubredditKeywordSearch(  self, 
                                    jobDict):
        
        # Construct the urlSring for the GET request
        urlString = API_BASE + 'r/'+jobDict['subreddit'] + '/search/'
        
        # Construct the params for the GET request
        self.params_['q'] = jobDict['keyword']
        self.params_['restrict_sr'] = True
                
        # Submit Request
        return self.requestGet( urlString= urlString,
                                numResultsRequested = jobDict['n'])
    
    ####################################################################################################
    # This function
    ####################################################################################################
    def extractParams(  self,
                        jobDict):

        self.params_['sortBy'] = jobDict['sortBy']
        self.params_['limit'] = jobDict['n']
        self.params_['t'] = jobDict['timeFrame']
       
    ####################################################################################################
    # This function checks a response for an error. If there is an error than the error code and any
    # error text is displayed. If HALT is True than the script waits for the user to hit enter
    ####################################################################################################
    def check4ResponseError(self, resp, HALT = False):
           
        retFlag = False
                          
        if 'error' in resp.keys():  
            logging.error('Error Code:', resp['error'])

            if 'error_description' in resp.keys():
                logging.error('Error Msg:',resp['error_description'])
            
            if HALT:    
                input('Press ENTER to continue...')

            retFlag = True

        return retFlag
            
    ####################################################################################################
    # This function performs a GET call from requests as defined by it's arguments
    ####################################################################################################
    def requestGet(self,
                   urlString,
                   numResultsRequested):
        
        sucessFlag = False
                    
        responseList = []

        if numResultsRequested > RedditUtils.MAX_NUM_RESPONSES_TOTAL:
            numResultsRequested = RedditUtils.MAX_NUM_RESPONSES_TOTAL

        # calculate floor division
        performNumRequests = numResultsRequested // RedditUtils.MAX_NUM_RESPONSES_PER_REQUEST
        if performNumRequests == 0:
            performNumRequests = 1
                      
        afterID = ''   
        for i in range(0, performNumRequests):

            self.params_['after'] = afterID        
                        
            try:
                response = requests.get(url=urlString,
                                    headers = self.header_,
                                    params = self.params_,
                                    timeout=RedditUtils.REQUEST_GET_TIMEOUT)

                if response.status_code == 200:
                    
                    sucessFlag = True
                    respJSON = response.json()
                                    
                    for resp in respJSON['data']['children']:                     
                        responseList.append(resp) 

                        
                    if len(respJSON['data']['children']) > 0:
                        afterID = respJSON['data']['children'][-1]['data']['name']
                         
            except Exception as e:
                print(e)
           

        # Store the results in the correct member
        self.listOfResponses_ = responseList

        # Store thenumber of requests made so # of request per minute can be monitored
        self.numRequest_ = performNumRequests
        
        return sucessFlag
    
    ####################################################################################################
    # This function handles 'subreddit' type jobs
    def handleSubRedditJob(self, jobDict) -> bool:
        
        successFlag = None
              
        if jobDict['getposts'] == 1: 
            successFlag = self.getSubredditPosts(jobDict)
        elif len(jobDict['keyword']) > 0:
            successFlag = self.getSubredditKeywordSearch(  jobDict)
        else:
            logging.warning('[WARNING]: HandlejobDict: No ACTION specified for subreddit',flush=True)  
            successFlag = False
            
        return successFlag
                    
    ####################################################################################################
    # This function handles 'user' type jobs
    def handleUserJob(self, jobDict) -> bool:
        
        successFlag = None
        
        if jobDict['getposts'] == 1:
            successFlag = self.getUserPosts(jobDict)
        elif jobDict['getcomments'] == 1:
            successFlag = self.getUserComments(jobDict)
        else:
            logging.warning('[WARNING]: HandlejobDict: No ACTION specified for user',flush=True)
            successFlag = False
        
        return successFlag
    ####################################################################################################
    # This function handles 'post' type jobs
    def handlePostJob(self, jobDict) -> bool:
        
        successFlag = None
        try:
            self.getCommentsFromPost(jobDict)          
            successFlag = True
        except:
            successFlag = False
        
        return successFlag
        
    ####################################################################################################
    # This function performs the API call which is described in the jobDict dictionary.
    def HandleJobDict(self, jobDict) -> None:
        
        successFlag = False
        
        self.extractParams(jobDict)
                
        # This block of code calls the API command which is described in the jobDict          
        if jobDict['subreddit'] != None:
            successFlag = self.handleSubRedditJob(jobDict)
        
        elif jobDict['user'] != None:
            successFlag = self.handleUserJob(jobDict)       
            
        elif  jobDict['post'] != None:
            successFlag = self.handlePostJob(jobDict)
        else:
            logging.warning('[WARNING]: HandlejobDict: No ITEM ID specified.')  
        
        return successFlag
    
    ####################################################################################################
    # Get number of requests sent for the last job
    def SaveResponses(self,
                      folderPath : str) -> bool:
        
        successFlag = False
        
        # check if the file path exists and is accessbile then write the listOfResponses_ to the file
        if os.path.exists(folderPath):          
            filename = str(uuid.uuid1())+'.json'
            
            filePath = os.path.join(folderPath, filename)
            file = open(filePath, "w")
            
            listOrResponses = self.GetResponses()
            for responseJSON in listOrResponses:
                
                file.write(str(responseJSON['data']))
            
            file.close()     
            
            successFlag = True   
            
        return successFlag
    
    ####################################################################################################
    # Get the list of responses from the last Request
    def GetResponses(self) -> list:
        return self.listOfResponses_
           
    ####################################################################################################
    # Get number of requests sent for the last job
    def GetNumberOfRequests(self) -> int:
        return self.numRequest_
       
    ####################################################################################################
    #
    def End(arg1):
        # TODO: do stuff here to end the session cleanly
        logging.debug('END SESSION')
        
        return 
        

##############################################################################################################
# This code defines the command interface including the todo: webInterface, and command line interface 
##############################################################################################################

# TODO: Change --getPosts and --getComments so they dont require arguments (nrgs = 0?)
# TODO: Check if --post --getComments returns all comments
# TODO: add functionality for printing retrieved data to the screen

# Example command line calls:
#python RedditAPISession.py --subreddit 'canada' --getposts 1 --n 1 --sortBy new
def ExtractCommandLineArgs() :
    parser = argparse.ArgumentParser()

    # Optional Argument.

    # Return options
    parser.add_argument('--sortBy',default='top')
    parser.add_argument('--timeFrame',default='all')
    parser.add_argument('--n', type=int,default=RedditUtils.MAX_NUM_RESPONSES_TOTAL)

    # Items
    items = parser.add_mutually_exclusive_group(required=True)
    items.add_argument('--subreddit',default='')
    items.add_argument('--user',default='')
    items.add_argument('--post',nargs=2,default=['',''])

    # Actions
    actions = parser.add_mutually_exclusive_group(required=True)
    actions.add_argument('--keyword',default='',help='Search the given SUBREDDIT for KEYWORD')
    actions.add_argument('--getposts',type=int,default=0,choices=[0,1],help='Return posts from  SUBREDDIT or USER')
    actions.add_argument('--getcomments',type=int,default=0,choices=[0,1],help='Return posts from  POST or USER')

    args = parser.parse_args()
       
    return vars(args)

##############################################################################################################
# This code tests the above class using the command line interface
##############################################################################################################
if __name__ == '__main__':
    
    credientalsDict = {}

        
    session = RedditAPISession(credientalsDict)
    
    # turn the list of command line args into a dictionary
    jobDict = ExtractCommandLineArgs()    
    
    # collect all the responses generated by the RedditInterface named session
    if session.HandleJobDict(jobDict):
  
        #now do something with thre responses
        numResponses = 0
        for responseJSON in session.GetResponses():
            print(responseJSON)
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ POST DATA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            RedditUtils.DisplayDict(responseJSON['data'], RedditUtils.POST_KEYS_OF_INTEREST)
            input()    
    
           