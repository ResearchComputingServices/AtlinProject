import logging
import sys
import traceback
from googleapiclient.errors import HttpError
import Tools.YouTubeAPI.youtube.config as config
from Tools.YouTubeAPI.youtube.utils import is_quota_exceeded
from Tools.YouTubeAPI.youtube.utils import get_HTTP_error_msg
from Tools.YouTubeAPI.youtube.utils import log_format

logger = logging.getLogger('youtube.playlist')


class Playlist(object):
    def __init__(self, youtube) -> None:
        logger.debug("Initializing Playlist Object")
        self._youtube = youtube
        self.id = ""
        self.title = ""
        self.videos_ids = []

    # *****************************************************************************************************
    # Gets the id of a playslit from the url
    # *****************************************************************************************************
    def get_playlist_id(self,url):

        id = None
        index = url.find("list=")
        if index >= 0:
            id = url[index + 5:]
            self.id = id
        else:
            msg = f"{url} is not a valid playlist url. "
            st = log_format("get_playlist_id", msg)
            logger.error(st)
            self._youtube.state.set_error_description(True, st)


        return id

    # *****************************************************************************************************
    # This function returns the title of the playlist given as argument
    # *****************************************************************************************************
    def get_playlist_title(self):

        msg = f"Get playlist title for: {self.id}"
        st = log_format("get_playlist_title", msg)
        logger.debug(st)


        if self.id==None:
            return

        title = None

        try:
            request = self._youtube.service.playlists().list(
                id=self.id,
                part='snippet'
            )
            self._youtube.state.update_quota_usage(config.UNITS_PLAYLIST_LIST)
            response = request.execute()

            for item in response['items']:
                title = item["snippet"].get("title", "playlist")
        except HttpError as error:
            self._youtube.state.quota_exceeded = is_quota_exceeded(error)

            msg = get_HTTP_error_msg(error)
            st = log_format("get_playlist_title", msg)
            logger.error(st)
            self._youtube.state.set_error_description(True, msg)

        except:
            ex = traceback.format_exc()
            st = log_format("get_playlist_title", ex)
            logger.error(st)
            self._youtube.state.set_error_description(True, st)

        self.title = title


    # *****************************************************************************************************
    # This function retrieves the videos ids for a playlist id in the class
    # *****************************************************************************************************
    def _get_playlist_videos_ids(self, playlistId=None):

        msg = f"Get videos ids in playlist: {self.id} or {playlistId}"
        st = log_format("_get_playlist_videos_ids", msg)
        logger.debug(st)

        if playlistId==None and self.id==None:
            return

        if playlistId!=None:
            self.id = playlistId

        nextPageToken = None
        pages = 0
        videos_ids = []
        try:
            while True:
                if self._youtube.state.under_quota_limit(config.UNITS_PLAYLIST_ITEMS_LIST):
                    # List maxResults videos in a playlist
                    requestVideosList = self._youtube.service.playlistItems().list(
                        part='contentDetails,snippet',
                        playlistId=self.id,
                        maxResults=config.MAX_PLAYLISTITEMS_PER_REQUEST,  # max is 50
                        pageToken=nextPageToken
                    )
                    self._youtube.state.update_quota_usage(config.UNITS_PLAYLIST_ITEMS_LIST)
                    responseVideosList = requestVideosList.execute()
                    nextPageToken = responseVideosList.get('nextPageToken')

                    # Obtain video_id for each video in the response
                    for item in responseVideosList['items']:
                        videoId = item['contentDetails'].get('videoId',None)
                        if videoId and ('videoPublishedAt' in item['contentDetails']):  # For some reason the API is bringing "ghost" videos in the playlist
                            videos_ids.append(videoId)

                    pages = pages + 1
                    if not nextPageToken:
                        break
                else:
                    self._youtube.state.quota_exceeded = True
                    st = log_format("_get_playlist_videos_ids","Out of quota")
                    logger.error(st)
                    self._youtube.state.set_error_description(True, msg)
                    break

        except HttpError as error:
            self._youtube.state.quota_exceeded = is_quota_exceeded(error)
            msg = get_HTTP_error_msg(error)
            st = log_format("_get_playlist_videos_ids", msg)
            logger.error(st)
            self._youtube.state.set_error_description(True, msg)
        except:
            ex = traceback.format_exc()
            st = log_format("_get_playlist_videos_ids", ex)
            logger.error(st)
            self._youtube.state.set_error_description(True, st)

        self.videos_ids = list(set(videos_ids))
        return self.videos_ids



    # *****************************************************************************************************
    # *****************************************************************************************************
    def get_playlist_videos_ids(self, url=None, playlistId=None):

        #At least one parameter should be provided
        if url==None and playlistId==None:
            return None

        if url!=None:
            id = self.get_playlist_id(url)
            if id:
                self.get_playlist_title()  # Not necessary for the request, but it could be useful to have.
                self._get_playlist_videos_ids()

        if playlistId!=None:
            self.playlist._get_playlist_videos_ids()



