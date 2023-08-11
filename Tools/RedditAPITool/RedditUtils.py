from colorama import Fore, Back, Style

####################################################################################################
# GLOBAL CONSTANTS
####################################################################################################

API_BASE = 'https://oauth.reddit.com/'

POST_KEYS_OF_INTEREST = [   'subreddit',
                            'selftext',
                            'author_fullname',
                            'title','downs',
                            'name',
                            'upvote_ratio',
                            'ups',
                            'score',
                            'created',
                            'view_count',
                            'id',
                            'author',
                            'num_comments',
                            'created_utc',
                            'num_crossposts']

COMMENT_KEYS_OF_INTEREST = [    'subreddit_id',
                                'subreddit', 	
                                'replies',
                                'id',
                                'author', 	
                                'parent_id', 	
                                'score', 	
                                'author_fullname', 	
                                'body', 	
                                'name', 	
                                'body_html', 	
                                'created', 	
                                'link_id', 	
                                'controversiality', 	
                                'depth', 	
                                'ups'] 	

REQUEST_GET_TIMEOUT = 5

MAX_NUM_RESPONSES_TOTAL = 1000

MAX_NUM_RESPONSES_PER_REQUEST = 100

CATEGORY_TOP = 'top'
CATEGORY_NEW = 'new'
CATEGORY_HOT = 'hot'
CATEGORY_RISING = 'rising'

REDDIT_CATEGORIES = [CATEGORY_TOP,
                     CATEGORY_NEW,
                     CATEGORY_HOT,
                     CATEGORY_RISING]

TIME_FRAME_NOW = 'now'
TIME_FRAME_TODAY = 'today'
TIME_FRAME_WEEK = 'week'
TIME_FRAME_MONTH = 'month'
TIME_FRAME_YEAR = 'year'
TIME_FRAME_ALL = 'all'

REDDIT_TIME_FRAMES = [TIME_FRAME_NOW,
                      TIME_FRAME_TODAY,
                      TIME_FRAME_WEEK,
                      TIME_FRAME_MONTH,
                      TIME_FRAME_YEAR,
                      TIME_FRAME_ALL]

SORT_BY_RELAVANCE = 'relevance'
SORT_BY_HOT = 'hot'
SORT_BY_TOP = 'top'
SORT_BY_NEW = 'new'
SORT_BY_MOST_COMMENTS = 'comments'

REDDIT_SORT_BY = [SORT_BY_RELAVANCE,
                  SORT_BY_HOT,
                  SORT_BY_TOP,
                  SORT_BY_NEW,
                  SORT_BY_MOST_COMMENTS]

CRED_USERNAME_KEY = 'username'
CRED_PASSWORD_KEY = 'password'
CRED_CLIENT_ID_KEY = 'CLIENT_ID'
CRED_SECRET_TOKEN_KEY = 'SECRET_TOKEN'
CRED_GRANT_TYPE_KEY = 'grant_type' 
CRED_GRANT_TYPE_VALUE = 'password' 
          
DEFAULT_HEADER_KEY = 'User-Agent'
DEFAULT_HEADER_VALUE = 'MyAPI/0.0.1'  
REDDIT_OAUTH_POST = 'https://www.reddit.com/api/v1/access_token' 

REDDIT_OAUTH_KEY = 'access_token'     
REDDUT_AUTHEN_KEY = 'Authorization'      

REDDIT_JOB_DETAIL_SORT_BY ='sortBy' 
REDDIT_JOB_DETAIL_TIME_FRAME = 'timeFrame' 
REDDIT_JOB_DETAIL_N = 'n', 
REDDIT_JOB_DETAIL_SUBREDDIT = 'subreddit'
REDDIT_JOB_DETAIL_USER = 'user', 
REDDIT_JOB_DETAIL_POST = 'post', 
REDDIT_JOB_DETAIL_KEYWORD = 'keyword', 
REDDIT_JOB_DETAIL_GETPOSTS = 'getposts', 
REDDIT_JOB_DETAIL_COMMENTS = 'getcomments'
    
####################################################################################################
# This function removed the 'type' code at the front of a reddit ID36
####################################################################################################
def ExtractID36(str):
    
    id36 = None
    
    strSplit = str.split('_')
    
    if len(strSplit) == 2:
        id36 = strSplit[1]
    
    return id36

####################################################################################################
# This function prints the contents of a dictionary outwith colours
####################################################################################################
def DisplayDict(dict, keysOfInterest = None):
    
    for key in dict.keys():
        
        if keysOfInterest != None and key not in keysOfInterest:
            continue        
            
        value = str(dict[key])

        if len(value) > 100:
            value = value[:100]
       
        print(Fore.RED + key, Fore.WHITE+':',value)
        
####################################################################################################
# This function returns replies to a comment 
####################################################################################################
def ExtractRepliesFromComment(comment):
        
    replies = {}
    
    if 'replies' in comment.keys():
        replies = comment['replies']
                
        for reply in replies['data']['children']:
            print('~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ REPLY DATA ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~')
            DisplayDict(reply['data'], COMMENT_KEYS_OF_INTEREST)
            input()


    return replies