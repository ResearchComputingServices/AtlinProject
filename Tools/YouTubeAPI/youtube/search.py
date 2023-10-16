import logging
import traceback
import Tools.YouTubeAPI.youtube.config as config
from Tools.YouTubeAPI.youtube.utils import log_format
from googleapiclient.errors import HttpError
from Tools.YouTubeAPI.youtube.utils import is_quota_exceeded
from Tools.YouTubeAPI.youtube.utils import get_HTTP_error_msg

logger = logging.getLogger('youtube.search')


class Search(object):
    def __init__(self, youtube, query=None, numberOfVideos=None) -> None:
        logger.debug("Initializing Search Object.")
        self._youtube = youtube
        self.query = query
        self.videos_ids = []

    # *****************************************************************************************************
    # This function executes a search on youtube (similar to the one in youtube search bar) to retrieves
    # the videos that match the query given as a paramter.
    # The search is based on relevance to the query
    # *****************************************************************************************************
    def __get_videos_id_by_query(self, query, maxNumberVideos):
        nextPageToken = None
        videos_ids = []

        maxResults = config.MAX_SEARCH_RESULTS_PER_REQUEST

        if maxNumberVideos < maxResults:
            maxResults = maxNumberVideos

        count = 0
        #search_finished = False
        try:
            while True:
                video_channels_request = self._youtube.service.search().list(
                    part="snippet",
                    q=query,
                    type="video",
                    maxResults=maxResults,
                    order="relevance",
                    pageToken=nextPageToken

                )

                self._youtube.state.update_quota_usage(config.UNITS_SEARCH_LIST)
                response_videos_channels = video_channels_request.execute()

                # Obtain video_id for each video in the response
                for item in response_videos_channels['items']:
                    videoId = item["id"].get("videoId", "N/A")
                    if videoId!="N/A":
                        videos_ids.append(videoId)
                    count = count + 1

                nextPageToken = response_videos_channels.get('nextPageToken')
                if not nextPageToken or count >= maxNumberVideos:
                    #search_finished = True
                    break;

        except HttpError as error:
            self._youtube.state.quota_exceeded = is_quota_exceeded(error)

            msg = get_HTTP_error_msg(error)
            st = log_format("__get_videos_id_by_query", msg)
            logger.error(st)
            msg = "HTTP Error on searching videos by a query. Check the query format."
            self._youtube.state.set_error_description(True, msg)


        except:
            ex = traceback.format_exc()
            st = log_format("__get_videos_id_by_query", ex)
            logger.error(st)
            msg = "Error on searching videos by a query. Check the query format."
            self._youtube.state.set_error_description(True, msg)

        #if search_finished:
        #    self._youtube.state.remove_action(config.ACTION_QUERY_SEARCH)
        #    self._youtube.state.query = ""
        #    self._youtube.state.num_videos = 0

        return videos_ids


    # *****************************************************************************************************
    # *****************************************************************************************************
    def get_videos_id_by_query(self, query, maxNumberVideos=None):

        try:
            videos_ids = []
            videos_with_quota = self._youtube.state.number_of_items_with_quota(config.UNITS_SEARCH_LIST,
                                                                               config.MAX_SEARCH_RESULTS_PER_REQUEST)



            if (not maxNumberVideos) or (maxNumberVideos < 0) or (maxNumberVideos > config.MAX_VIDEOS_TO_RETRIEVE):
               maxNumberVideos = config.DEFAULT_VIDEOS_TO_RETRIEVE

            self._youtube.state.num_videos = maxNumberVideos
            #self._youtube.state.add_action(config.ACTION_QUERY_SEARCH)
            #self._youtube.state.query = query

            if (maxNumberVideos > videos_with_quota):
                msg = "There is not enough quota to perform the search."
                st = log_format("get_videos_id_by_query", msg)
                logger.warning(st)
                self._youtube.state.quota_exceeded = True
                self.videos_ids = videos_ids
                return videos_ids

            videos_ids = self.__get_videos_id_by_query(query, maxNumberVideos)
            videos_ids = list(set(videos_ids))
            self.videos_ids = videos_ids



        except:
            ex = traceback.format_exc()
            st = log_format("get_videos_id_by_query", ex)
            logger.error(st)
            st = "Error on retrieving videos'ids by a query. "
            self._youtube.state.set_error_description(True, st)

        return videos_ids






