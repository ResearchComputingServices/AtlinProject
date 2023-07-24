#Requests quotes
#From https://developers.google.com/youtube/v3/determine_quota_cost
#Check regularly for updates.
#We only include the ones we are using

#resource	method	cost
#activities   list	1
#channels     list	1
#comments     list	1
#commentThreads list	1
#playlistItems  list	1
#playlists      list	1
#search         list	100
#videos         list	1


UNITS_ACTIVITIES_LIST = 1
UNITS_CHANNELS_LIST = 1
UNITS_COMMENTS_LIST = 1
UNITS_COMMENTS_THREADS_LIST = 1
UNITS_PLAYLIST_ITEMS_LIST = 1
UNITS_PLAYLIST_LIST = 1
UNITS_SEARCH_LIST = 100
UNITS_VIDEOS_LIST = 1
UNITS_QUOTA_LIMIT = 350

MAX_JOIN_VIDEOS_IDS = 50
MAX_CHANNELS_PER_REQUEST = 50
MAX_COMMENTS_PER_REQUEST = 100
MAX_REPLIES_PER_REQUEST = 100
MAX_VIDEOS_PER_REQUEST= 50
MAX_PLAYLISTITEMS_PER_REQUEST = 50
MAX_SEARCH_RESULTS_PER_REQUEST = 50
DEFAULT_VIDEOS_TO_RETRIEVE = 200
MAX_VIDEOS_TO_RETRIEVE = 500
MAX_PAGES_SEARCHES = 10   #Each page of 50 results (500 units at most)

ACTION_QUERY_SEARCH = "query_search"
ACTION_RETRIEVE_VIDEOS = "retrieve_videos"
ACTION_RETRIEVE_COMMENTS = "retrieve_comments"
ACTION_CREATE_NETWORK = "create_network"
ACTION_RETRIEVE_CHANNELS_METADATA = "retrieve_channels_metadata"
ACTION_RETRIEVE_CHANNELS_ACTIVITY = "retrieve_channels_activity"
ACTION_RETRIEVE_CHANNELS_ALL_VIDEOS = "retrieve_channels_all_videos"

ALL_VIDEOS_RETRIEVED = "all_videos_retrieved"
ALL_COMMENTS_RETRIEVED = "all_comments_retrieved"

TEST_VIDEO_ID = "ZU_wbPigVRI"
#TEST_VIDEO_ID = "hola"

SAFETY_BACKUP = 100
RETRY_REQUESTS_ATTEMPT = 3