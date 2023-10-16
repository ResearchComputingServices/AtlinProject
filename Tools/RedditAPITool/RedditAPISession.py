import argparse
import requests
import logging
import os
import uuid
from pathlib import Path
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()
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
    # CONSTRUCTOR
    #########################################################################
    
    def __init__(   self,
                    credientalsDict = {}):
        
        # initialize logger
        username = credientalsDict['username']
        self.logger_ = logging.getLogger(f'RedditAPISession {username}' )  
        self.logger_.info('Reddit API Session logger initialized.')
             
        # Initialize members
        
        self.credientalsDict_ = credientalsDict
            
        self.header_ = {}
    
        self.params_ = {}
    
        self.listOfResponses_ = []
    
        self.numRequest_ = 0
        
        self.OAuthSuccessful_ = self.generateAuthentifiedHeader()
       
        if self.OAuthSuccessful_:  
            self.logger_.info('Account successfully authenticated')               
        else:
            self.logger_.error('Unable to authenticate account')    

    #########################################################################
    # PRIVATE FUNCTIONS
    #########################################################################

    def generateAuthentifiedHeader( self,
                                    headerKey = DEFAULT_HEADER_KEY,
                                    headerValue = DEFAULT_HEADER_VALUE) -> bool:
        
        successFlag = False
                      
        # note that CLIENT_ID refers to 'personal use script' and SECRET_TOKEN to 'token'
        auth = requests.auth.HTTPBasicAuth( self.credientalsDict_[CRED_CLIENT_ID_KEY],
                                            self.credientalsDict_[CRED_SECRET_TOKEN_KEY])
        
        # setup our header info, which gives reddit a brief description of our app
        self.header_[headerKey] =  headerValue

        # send our request for an OAuth token
        resp = requests.post(   REDDIT_OAUTH_POST, 
                                auth=auth, 
                                data=self.credientalsDict_, 
                                headers=self.header_)
        if resp.status_code == 200:
                       
            successFlag = True
               
            # convert response to JSON and get access_token value
            TOKEN = resp.json()[REDDIT_OAUTH_KEY]

            # add authorization to our headers dictionary
            self.header_[REDDUT_AUTHEN_KEY] = f"bearer {TOKEN}"

        return successFlag

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
        urlString = API_BASE + 'r/'+jobDict['subreddit']+'/'+jobDict['sortBy']
               
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
        self.params_['sort'] = jobDict['sortBy']
        self.params_['limit'] = jobDict['n']
        self.params_['t'] = jobDict['timeFrame']
       
    ####################################################################################################
    # This function checks a response for an error. If there is an error than the error code and any
    # error text is displayed. If HALT is True than the script waits for the user to hit enter
    ####################################################################################################
    def check4ResponseError(self, resp, HALT = False):
           
        retFlag = False
                          
        if 'error' in resp.keys():  
            self.logger_.error('Error Code:', resp['error'])

            if 'error_description' in resp.keys():
                self.logger_.error('Error Msg:',resp['error_description'])
            
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
        
        self.logger_.info(urlString)
        self.logger_.info( self.params_)
        self.logger_.info( self.header_)
        
        sucessFlag = False
                    
        responseList = []

        if numResultsRequested > MAX_NUM_RESPONSES_TOTAL:
            numResultsRequested = MAX_NUM_RESPONSES_TOTAL

        # calculate floor division
        performNumRequests = numResultsRequested // MAX_NUM_RESPONSES_PER_REQUEST
        if performNumRequests == 0:
            performNumRequests = 1
                      
        afterID = ''   
        for i in range(0, performNumRequests):

            self.params_['after'] = afterID        
       
            try:
                
                response = requests.get(url=urlString,
                                        headers = self.header_,
                                        params = self.params_,
                                        timeout= REQUEST_GET_TIMEOUT)
                                               
                if response.status_code == 200:
                    
                    sucessFlag = True
                    respJSON = response.json()
                    
                    if isinstance(respJSON, list):
                        respJSON = respJSON[0]
                    
                    for resp in respJSON['data']['children']:                     
                        responseList.append(resp) 
  
                    if len(respJSON['data']['children']) > 0:
                        afterID = respJSON['data']['children'][-1]['data']['name']
                         
            except Exception as e:
                self.logger_.error(e)
                sucessFlag = False
           

        # Store the results in the correct member
        self.listOfResponses_ = responseList

        # Store thenumber of requests made so # of request per minute can be monitored
        self.numRequest_ = performNumRequests
        
        return sucessFlag
    
    ####################################################################################################
    # This function handles 'subreddit' type jobs
    def handleSubRedditJob(self, jobDict) -> bool:
        
        self.logger_.info('handleSubRedditJob')  
        
        successFlag = False
        
        if not self.OAuthSuccessful_:
            self.logger_.error('Account was not authenticated.')              
        elif jobDict['getposts'] == 1: 
            self.logger_.info('getSubredditPosts')
            successFlag = self.getSubredditPosts(jobDict)
        elif len(jobDict['keyword']) > 0:
            self.logger_.info('getSubredditKeywordSearch')
            successFlag = self.getSubredditKeywordSearch(jobDict)
        else:
            self.logger_.warning('No ACTION specified for subreddit')  
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
            self.logger_.warning('No ACTION specified for user')
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
            self.logger_.error(e)
            successFlag = False
        
        return successFlag
        
    ####################################################################################################
    # This function performs the API call which is described in the jobDict dictionary.
    def HandleJobDict(self, jobDict) -> None:      
                   
        self.logger_.info(jobDict)        
             
        successFlag = False
        
        self.extractParams(jobDict)
                
        # This block of code calls the API command which is described in the jobDict          
        if jobDict['subreddit'] != '':
            successFlag = self.handleSubRedditJob(jobDict)        
        elif jobDict['user'] != '':
            successFlag = self.handleUserJob(jobDict)       
        elif jobDict['post'][0] !=  '' and jobDict['post'][1] != '':
            successFlag = self.handlePostJob(jobDict)
        else:
            self.logger_.warning('No ITEM ID specified.')  
        
        return successFlag
    
    ####################################################################################################
    # Get number of requests sent for the last job
    def SaveResponses(self,
                      jobJSON) -> bool:
        
        successFlag = False
        
        folderPath = jobJSON['output_path']
        
        # check if the file path exists and is accessbile then write the listOfResponses_ to the file
        if os.path.exists(folderPath):          
            filename = jobJSON['job_name']+'.json'
            
            filePath = os.path.join(folderPath, filename)
            file = open(filePath, "w")
           
            listOrResponses = self.GetResponses()
            for responseJSON in listOrResponses:
                
                dict = responseJSON['data']
                  
                for key in dict.keys():
                    
                    if key not in POST_KEYS_OF_INTEREST:
                        continue        
                        
                    file.write(str(key)+' : ' + str(dict[key]) + '\n')
                
                file.write(RESPONSE_BREAK)
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
    def End(self):
        # TODO: do stuff here to end the session cleanly
       
        return 
        

##############################################################################################################
# This code defines the command interface including the todo: webInterface, and command line interface 
##############################################################################################################

# TODO: Change --getPosts and --getComments so they dont require arguments (nrgs = 0?)
# TODO: Check if --post --getComments returns all comments
# TODO: add functionality for printing retrieved data to the screen

# Example command line calls:
# python RedditAPISession.py --subreddit canada --getposts 1 --n 1 --sortBy new
# python RedditAPISession.py --subreddit canada --keyword maple --n 1 --sortBy top
# python RedditAPISession.py --post canada 176zyp4 --getcomments 1
def ExtractCommandLineArgs() :
    parser = argparse.ArgumentParser()

    # Optional Argument.

    # Return options
    parser.add_argument('--sortBy',default='top')
    parser.add_argument('--timeFrame',default='all')
    parser.add_argument('--n', type=int,default=MAX_NUM_RESPONSES_TOTAL)

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
    
    logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s %(levelname)s %(filename)s %(funcName)s(%(lineno)d) %(message)s',
    handlers=[
        logging.StreamHandler(),
    ])

    
    credientalsDict = {}
    credientalsDict['grant_type'] = 'password'
    credientalsDict['CLIENT_ID'] = '_-W7ANd6UN4EXexvgHn8DA'
    credientalsDict['SECRET_TOKEN'] = 'kpBdT1f-nRHM_kxdBzmxoOnDo_96FA'
    credientalsDict['username'] = 'nickshiell'
    credientalsDict['password'] =  'Q!w2e3r4'
        
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
            DisplayDict(responseJSON['data'], POST_KEYS_OF_INTEREST)
            input()    
    
           