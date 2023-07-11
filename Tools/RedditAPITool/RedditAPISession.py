import argparse
import requests
import logging

from RedditUtils import *

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
        
        # Check if there was an error message returned
        self.check4ResponseError(resp.json(), True)
        
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
    def exctractParams(self,
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
            
            resp = requests.get(url=urlString,
                                headers = self.header_,
                                params = self.params_,
                                timeout=REQUEST_GET_TIMEOUT)
 
            respDict = resp.json()
            if isinstance(respDict,list):
                respDict = resp.json()[0]               

            responseList.append(respDict) 

            if not self.check4ResponseError(respDict):
                if len(respDict['data']['children']) > 0:
                    afterID = respDict['data']['children'][-1]['data']['name']

        return responseList
    
    ####################################################################################################
    # This function handles 'subreddit' type jobs
    def handleSubRedditJob(self, jobDict):
        listOfResponseJSON = [] 
        
        if jobDict['getposts'] == 1: 
            listOfResponseJSON = self.getSubredditPosts(jobDict)
        elif len(jobDict['keyword']) > 0:
            listOfResponseJSON = self.getSubredditKeywordSearch(  jobDict)
        else:
            logging.warning('[WARNING]: HandlejobDict: No ACTION specified for subreddit',flush=True)  
                
        return listOfResponseJSON    
    
    ####################################################################################################
    # This function handles 'user' type jobs
    def handleUserJob(self, jobDict):
        listOfResponseJSON = [] 
        
        if jobDict['getposts'] == 1:
            listOfResponseJSON = self.getUserPosts(jobDict)
        elif jobDict['getcomments'] == 1:
            listOfResponseJSON = self.getUserComments(jobDict)
        else:
            logging.warning('[WARNING]: HandlejobDict: No ACTION specified for user',flush=True)
        
        return listOfResponseJSON    
    
    ####################################################################################################
    # This function handles 'post' type jobs
    def handlePostJob(self, jobDict):
        listOfResponseJSON = [] 
        
        listOfResponseJSON = self.getCommentsFromPost(jobDict)
        
        return listOfResponseJSON 
        
    ####################################################################################################
    # This function performs the API call which is described in the jobDict dictionary.
    def HandleJobDict(self, jobDict):
        self.exctractParams(jobDict)
        
        # All the get functions will return a JSON data structure containing the results
        listOfResponseJSON = [] 
  
        # This block of code calls the API command which is described in the jobDict          
        if jobDict['subreddit'] != None:
            listOfResponseJSON = self.handleSubRedditJob(jobDict)
        elif jobDict['user'] != None:
            listOfResponseJSON =self.handleUserJob(jobDict)       
        elif  jobDict['post'] != None:
            listOfResponseJSON = self.handlePostJob(jobDict)
        else:
            logging.warning('[WARNING]: HandlejobDict: No ITEM ID specified.',flush=True)  
            
        return listOfResponseJSON
    
    ####################################################################################################
    #
    def End():
        # TODO: do stuff here to end the session cleanly
        logging.debug('END SESSION')
        
        return 
        

##############################################################################################################
# This code defines the command interface including the todo: webInterface, and command line interface 
##############################################################################################################

# TODO: Change --getPosts and --getComments so they dont require arguments (nrgs = 0?)
# TODO: Check if --post --getComments returns all comments
# TODO: add functionality for saving the data to a file
# TODO: add functionality for printing retrieved data to the screen

# Example command line calls:
# python RedditAPISession.py --subreddit 'python' --getposts 1
# python RedditAPISession.py --subreddit 'python' --keyword ide
# python RedditAPISession.py --user pmz --getcomments 1
# python RedditAPISession.py --user pmz --getposts 1
# python RedditAPISession.py --post 13e5oxw --getcomments 1

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
    listOfResponsesJSON = session.HandleJobDict(jobDict)   
          
    #now do something with thre responses
    numResponses = 0
    for responseJSON in listOfResponsesJSON:
        numResponses += len(responseJSON['data']['children'])
        for aPost in responseJSON['data']['children']:
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ POST DATA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            #DisplayDict(aPost['data'], COMMENT_KEYS_OF_INTEREST)
            DisplayDict(aPost['data'], POST_KEYS_OF_INTEREST)
            input()    
    
# API call to:
# 1. get user credentials from the User Table
# 2. update an entry in the Job Table (status, location of output file)
            