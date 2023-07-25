from googleapiclient.discovery import build
from .setup_logger import logger
from .comments import Comments
from .videos import Videos
from .channels import Channels
from .state import State
from .playlist import Playlist
from .search import Search
from .utils import get_ids_from_file
from .utils import log_format
import Tools.YouTubeAPI.youtube.config as config
import sys
import traceback

class Youtube:
    def __init__(self, api_key, current_quota=None) -> None:
        logger.debug("Initializing YouTube object.")

        self._apikey = api_key
        self.service = self.__build_service_api_key()
        self.items = {}
        self.comments = Comments(self)
        self.videos = Videos(self)
        self.channels = Channels(self)
        self.playlist = Playlist(self)
        self.search = Search(self)

        if not current_quota:
            current_quota = 0

        self.state = State(self,current_quota)

        #self.__test_service()

    def login(self):
        logger.debug(f"Should login using the api_key {self._apikey}")


    # *****************************************************************************************************
    # Builds a service for the YouTube Data API using an API Key
    # This is the simplest form of authentication and it is available only to retrieve public information
    # *****************************************************************************************************
    def __build_service_api_key(self):
        service = None
        try:
            if self._apikey:
                # Builds a service object. In this case, the service is youtube api, version v3, with the api_key
                service= build('youtube', 'v3', developerKey=self._apikey)
                logger.debug(f"YouTube Service Initialized")
        except:
            logger.critical("YouTube Service couldn't be created.")
        return service

    # *****************************************************************************************************
    # *****************************************************************************************************
    def __test_service(self):
        video_id= config.TEST_VIDEO_ID
        info = self.videos.get_videos_and_videocreators([video_id])
        if not self.state.api_key_valid or self.state.quota_exceeded:
            self.service = None
        self.state.set_error_description(False,"")
        return info

    # *****************************************************************************************************
    # This function retrieves the metadata for a video and its creator (a channel)
    # *****************************************************************************************************
    def get_video_metadata_for_url(self, url):

        response = None
        msg = f"{url}"
        st = log_format("get_video_metadata_for_url", msg)
        logger.debug(st)

        video_id = self.videos.get_video_id_from_url(url)
        if len(video_id)>0:
            response = self.videos.get_videos_and_videocreators([video_id])
        else:
            self.state.set_error_description(True,f"{url} is not a valid url.")

        return response

    # *****************************************************************************************************
    # This function retrieves the metadata for a video and its creator (a channel)
    # *****************************************************************************************************
    def get_video_comments_for_url(self, url):

        response = None
        msg = f"{url}"
        st = log_format("get_video_comments_for_url", msg)
        logger.debug(st)

        video_id = self.videos.get_video_id_from_url(url)
        if len(video_id) > 0:
            response = self.comments.get_comments_and_commenters([video_id])
        else:
            self.state.set_error_description(True, f"{url} is not a valid url.")

        return response

    # *****************************************************************************************************
    # This function retrieves the videos' metadata and creators for all the videos on the playlist given as argument
    # *****************************************************************************************************
    def get_videos_metadata_from_playlist(self, url):

        response = None
        msg = f"{url}"
        st = log_format("get_video_metadata_from_playlist", msg)
        logger.debug(st)

        self.playlist.get_playlist_videos_ids(url)
        if len(self.playlist.videos_ids) > 0:  # Need to report the error in case we didn't get the data
            response = self.videos.get_videos_and_videocreators(self.playlist.videos_ids)

        return response

    # **********************************************************************************************************
    # This function extracts a list of videos ids from an excel file (The excel file must contain the column
    # videoId with the videos' ids)
    # Once extracted this list, the function then calls the function get_videos_and_videocreators to retrieve
    # the videos and its creators' metadata.
    # ***********************************************************************************************************
    def get_videos_metadata_from_file(self, filename):
        try:
            # Load file
            videos_ids = get_ids_from_file(filename, "videoId")
            if videos_ids:
                # Get data from YouTube API
                self.videos.get_videos_and_videocreators(videos_ids)
            else:
                logger.debug("Video's ids couldn't be retrieved. Check input file.")
        except:
            logger.debug("Error on get_videos_from_file")
            logger.debug(sys.exc_info()[0])
            logger.debug(traceback.print_exc())

    # **********************************************************************************************************
    # This function extracts a list of videos ids from an excel file (The excel file must contain the column
    # videoId with the videos' ids)
    # Once extracted this list, the function then calls the function get_videos_and_videocreators to retrieve
    # the videos and its creators' metadata.
    # ***********************************************************************************************************
    def get_videos_comments_from_file(self, filename):
        try:
            # Load file
            videos_ids = get_ids_from_file(filename, "videoId")
            if videos_ids:
                # Get data from YouTube API
                self.comments.get_comments_and_commenters(videos_ids)
            else:
                logger.debug("Video's ids couldn't be retrieved. Check input file.")
        except:
            logger.debug("Error on get_videos_from_file")
            logger.debug(sys.exc_info()[0])
            logger.debug(traceback.print_exc())


    # *****************************************************************************************************
    # This function retrieves the videos' comments and commenters for all the videos on the playlist given as argument
    # *****************************************************************************************************
    def get_videos_comments_from_playlist(self, url):
        response = None
        self.playlist.get_playlist_videos_ids(url)
        if len(self.playlist.videos_ids) > 0:  # Need to report the error in case we didn't get the data
            response = self.comments.get_comments_and_commenters(self.playlist.videos_ids)
        return response

    # *****************************************************************************************************
    # This function retrieves the videos' metadata and creators for all the videos on the playlist given as argument
    # *****************************************************************************************************
    def get_videos_metadata_from_query(self, query, maxNumberVideos=None):
        response = None
        self.search.get_videos_id_by_query(query, maxNumberVideos)
        if self.search.videos_ids and len(self.search.videos_ids) > 0:
            response = self.videos.get_videos_and_videocreators(self.search.videos_ids)
        return response

    # *****************************************************************************************************
    # This function retrieves the videos' metadata and creators for all the videos on the playlist given as argument
    # *****************************************************************************************************
    def get_videos_comments_from_query(self, query, maxNumberVideos=None):
        response = None
        self.search.get_videos_id_by_query(query, maxNumberVideos)
        if self.search.videos_ids and len(self.search.videos_ids) > 0:
            response = self.comments.get_comments_and_commenters(self.search.videos_ids)
        return response










