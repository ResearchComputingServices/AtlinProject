class RedditConstants:
    """ Constants defined for the RedditAPISession Class and it's commandline interface.

    """

    LOGGER_FORMAT_STR = '%(asctime)s %(levelname)s %(filename)s %(funcName)s(%(lineno)d) %(message)s'

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

    REQUEST_TIMEOUT = 5

    MAX_NUM_RESPONSES_TOTAL = 1000

    MAX_NUM_RESPONSES_PER_REQUEST = 100

    CATEGORY_TOP = 'top'
    CATEGORY_NEW = 'new'
    CATEGORY_HOT = 'hot'
    CATEGORY_RISING = 'rising'

    REDDIT_CATEGORIES = [   CATEGORY_TOP,
                            CATEGORY_NEW,
                            CATEGORY_HOT,
                            CATEGORY_RISING]

    TIME_FRAME_NOW = 'now'
    TIME_FRAME_TODAY = 'today'
    TIME_FRAME_WEEK = 'week'
    TIME_FRAME_MONTH = 'month'
    TIME_FRAME_YEAR = 'year'
    TIME_FRAME_ALL = 'all'

    REDDIT_TIME_FRAMES = [  TIME_FRAME_NOW,
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

    REDDIT_SORT_BY = [  SORT_BY_RELAVANCE,
                        SORT_BY_HOT,
                        SORT_BY_TOP,
                        SORT_BY_NEW,
                        SORT_BY_MOST_COMMENTS]


    JOB_TYPE_KEYWORD = 'keyword'
    JOB_TYPE_POSTS = 'posts'
    JOB_TYPE_COMMENTS = 'comments'

    REDDIT_JOB_TYPES = [JOB_TYPE_KEYWORD,
                        JOB_TYPE_POSTS,
                        JOB_TYPE_COMMENTS]

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
    REDDIT_JOB_DETAIL_N = 'n'
    REDDIT_JOB_DETAIL_SUBREDDIT = 'subreddit'
    REDDIT_JOB_DETAIL_USER = 'user'
    REDDIT_JOB_DETAIL_POST = 'post'
    REDDIT_JOB_DETAIL_KEYWORD = 'keyword'
    REDDIT_JOB_DETAIL_GETPOSTS = 'getposts'
    REDDIT_JOB_DETAIL_COMMENTS = 'getcomments'

    RESPONSE_BREAK = '============================================================================='

    # Command line arguement strings
    CL_ARG_SORT_BY_KEY = 'sortBy'
    CL_ARG_SORT_BY_HELP = 'options: top, hot, new'
    CL_ARG_SORT_BY_DEFAULT = 'hot'

    CL_ARG_TIME_FRAME_KEY = 'timeFrame'
    CL_ARG_TIME_FRAME_HELP = 'options: now, today, week, month, year, all'
    CL_ARG_TIME_FRAME_DEFAULT = 'all'

    CL_ARG_N_KEY = 'n'
    CL_ARG_N_HELP = 'Number of repsones to request (max 1000)'
    CL_ARG_N_DEFAULT = '5'

    CL_ARG_SUBREDDIT_KEY = 'subreddit'
    CL_ARG_SUBREDDIT_HELP = 'Name of subreddit to scrape'
    CL_ARG_SUBREDDIT_DEFAULT = ''

    CL_ARG_USER_KEY = 'user'
    CL_ARG_USER_HELP = 'Name of user to scrape'
    CL_ARG_USER_DEFAULT = ''

    CL_ARG_POST_KEY = 'post'
    CL_ARG_POST_HELP = 'Post SUBREDDIT and ID to scrape'
    CL_ARG_POST_DEFAULT = ['','']

    CL_ARG_KEYWORD_KEY = 'keyword'
    CL_ARG_KEYWORD_HELP = 'search subreddit for keyword'
    CL_ARG_KEYWORD_DEFAULT = ''

    CL_ARG_GET_POSTS_KEY = 'getposts'
    CL_ARG_GET_POSTS_HELP = 'Return posts from  SUBREDDIT or USER'
    CL_ARG_GET_POSTS_DEFAULT = 0

    CL_ARG_GET_COMMENTS_KEY = 'getcomments'
    CL_ARG_GET_COMMENTS_HELP = 'Return posts from  POST or USER'
    CL_ARG_GET_COMMENTS_DEFAULT = 0

    CL_ARG_CRED_FP_KEY = 'cred'
    CL_ARG_CRED_FP_HELP = 'location to reddit credientials'
    CL_ARG_CRED_FP_DEFAULT = './cred.json'
