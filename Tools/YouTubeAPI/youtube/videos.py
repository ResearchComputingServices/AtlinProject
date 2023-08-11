import logging
import traceback
import datetime
import Tools.YouTubeAPI.youtube.config as config
from Tools.YouTubeAPI.youtube.utils import is_quota_exceeded
from Tools.YouTubeAPI.youtube.utils import is_api_key_valid
from Tools.YouTubeAPI.youtube.utils import get_HTTP_error_msg
from Tools.YouTubeAPI.youtube.utils import preprocess_string
from Tools.YouTubeAPI.youtube.utils import convert_to_local_zone
from Tools.YouTubeAPI.youtube.utils import log_format
from googleapiclient.errors import HttpError

logger = logging.getLogger('youtube.videos')

class Videos:
    def __init__(self, youtube):
        logger.debug("Initializing Videos object.")
        self._youtube = youtube
        self.video_records = {}
    
    def get_videos_by_id(self, ids: list):
        logger.debug(f"get_videos_by_id: ids {ids}")
    
    def get_videos_for_file(self, file):
        logger.debug(f"get_videos_for_file: file {file}")


    # *****************************************************************************************************
    # This function retrieves videos metadata for a list of ids
    # *****************************************************************************************************
    def get_videos_metadata(self, videos_ids):

        if len(videos_ids) == 0:
            return {}

        videos_response = None
        try:
            # Request videos metadata
            videos_request = self._youtube.service.videos().list(
                part="contentDetails,snippet,statistics",
                maxResults=config.MAX_VIDEOS_PER_REQUEST,
                id=','.join(videos_ids)
            )
            # Update quote_usage
            self._youtube.state.update_quota_usage(config.UNITS_VIDEOS_LIST)
            videos_response = videos_request.execute()

        except HttpError as error:
            self._youtube.state.quota_exceeded = is_quota_exceeded(error)
            self._youtube.state.api_key_valid = is_api_key_valid(error)

            msg = get_HTTP_error_msg(error)
            st = log_format("get_videos_metadata", msg)
            logger.error(st)
            self._youtube.state.set_error_description(True, msg)

        except:
            ex = traceback.format_exc()
            st = log_format("get_videos_metadata", ex)
            logger.error(st)
            self._youtube.state.set_error_description(True, st)

        return videos_response

    # *****************************************************************************************************
    # *****************************************************************************************************
    def get_videos_and_videocreators(self, ids):

        msg = f"get_videos_and_videocreators for ids: {ids}"
        st = log_format("get_videos_and_videocreators", msg)
        logger.debug(st)

        self.video_records = {}
        slicing = True
        start = 0
        original_videos_ids = ids



        # Add action to state
        self._youtube.state.add_action(config.ACTION_RETRIEVE_VIDEOS)
        self._youtube.state.all_videos_retrieved = False    ### ====> Check where are we actually using this variable
        self._youtube.state.videos_ids =ids

        try:
            while (slicing):
                # The cost of retrieving videos and channels
                retrieving_cost = config.UNITS_VIDEOS_LIST + config.UNITS_CHANNELS_LIST

                # Check if there is available quote
                if self._youtube.state.under_quota_limit(retrieving_cost):
                    end = start + config.MAX_VIDEOS_PER_REQUEST
                    if end >= len(original_videos_ids):
                        end = len(original_videos_ids)
                        slicing = False

                    videos_ids = original_videos_ids[start:end]
                    videos_response = self.get_videos_metadata(videos_ids)

                    if not videos_response:
                        break

                    if (len(videos_response['items'])==0):
                        #The API key is valid but the response came empty from the server.
                        #Probably a invalid input (id, url etc)
                        if self._youtube.state.api_key_valid:
                            st = log_format("get_videos_and_videocreators", "Response from YouTube server was empty. Check input request (e.g., IDs, url, etc)")
                            logger.warning(st)
                            self._youtube.state.set_error_description(True, st)
                        break

                    # Get ids from channels (videos' creators)
                    channels_ids = []
                    for item in videos_response['items']:
                        id = item["snippet"].get("channelId", None)
                        if id!=None:
                            channels_ids.append(id)

                    channels_ids = set(channels_ids)
                    self._youtube.channels.get_channels_metadata(channels_ids)
                    self.join_videos_creators(videos_response,self._youtube.channels.channel_records)

                    start = end

                    #Save videos ids of videos missing to retrievd
                    self._youtube.state.videos_ids = original_videos_ids[start:len(original_videos_ids)]
                else:
                    slicing = False
                    self._youtube.state.quota_exceeded = True
        except:
            ex = traceback.format_exc()
            st = log_format("get_videos_and_videocreators",ex)
            logger.error(st)
            self._youtube.state.set_error_description(True,st)


        # All videos have been retrieved
        if start >= len(original_videos_ids):
            self._youtube.state.remove_action(config.ACTION_RETRIEVE_VIDEOS)
            self._youtube.state.set_all_retrieved(config.ALL_VIDEOS_RETRIEVED, True)

        return self.video_records



    # *****************************************************************************************************
    # This function creates a dictionary that combines a video's and its creator (a channel) metadata
    # The video's metadata is sent in the parameter item
    # The information of the channel is located in channel_records which is a dictionary of channel's metadata
    # This dictionary will be used to create a record on the output excel file
    # *****************************************************************************************************
    def create_video_and_creator_dict(self, item, channels_records):

        try:
            now = datetime.datetime.now()
            current_datetime_str = now.strftime("%Y-%m-%d, %H:%M:%S")
            videoId = item.get("id", "N/A")

            title = ""
            if "snippet" in item:
                title = preprocess_string(item["snippet"].get("title", "N/A"))
                publishedDate = convert_to_local_zone(item["snippet"].get("publishedAt", None))
                description = preprocess_string(item["snippet"].get("description", "N/A"))
                channelId = item["snippet"].get("channelId", "N/A")

            url = "youtu.be/" + videoId

            if "statistics" in item:
                views = item["statistics"].get("viewCount", "N/A")
                likes = item["statistics"].get("likeCount", "N/A")
                favoriteCount = item["statistics"].get("favoriteCount", "N/A")
                commentsCount = item["statistics"].get("commentCount", "N/A")

            if "contentDetails" in item:
                duration = item["contentDetails"].get("duration", "N/A")

            channel_info = None
            if channels_records:
                try:
                    channel_info = channels_records[channelId]
                except:
                    channel_info = None

            metadata = {
                "videoId": videoId,
                "video_title": title,
                "video_url": url,
                "video_publishedAt": publishedDate,
                "video_scrappedAt": current_datetime_str,
                "video_duration": duration,
                "video_views": views,
                "video_likes": likes,
                "video_favoriteCount": favoriteCount,
                "video_commentsCount": commentsCount,
                "video_description": description,
                "video_Transcript Language": "",
                "video_Transcript Type": "",
                "video_Downloaded Transcript": "",
                "video_channelId": channelId
            }
            metadata.update(channel_info)
        except:
            ex = traceback.format_exc()
            st = log_format("create_video_and_creator_dict", ex)
            logger.error(st)
            self._youtube.state.set_error_description(True, st)

            metadata = {
                "videoId": "",
                "video_title": "",
                "video_url": "",
                "video_publishedAt": "",
                "video_scrappedAt": "",
                "video_duration": "",
                "video_views": "",
                "video_likes": "",
                "video_favoriteCount": "",
                "video_commentsCount": "",
                "video_description": "",
                "video_channelId": "",
                "video_Transcript Language": "",
                "video_Transcript Type": "",
                "video_Downloaded Transcript": ""
            }

        return metadata

    # *****************************************************************************************************
    # *****************************************************************************************************
    def join_videos_creators(self, videos_response, channel_records):
        # Merge video and channel info in only one dictionary
        for item in videos_response['items']:
            metadata = self.create_video_and_creator_dict(item, channel_records)
            self.video_records[metadata["videoId"]] = metadata



    # *****************************************************************************************************
    # *****************************************************************************************************
    def get_video_id_from_url(self, url):
        url = url.strip()
        video_id = ""
        index = url.find("v=")
        if index >= 0:
            video_id = url[index + 2:]
        else:
            msg = f"{url} is not a valid url. "
            st = log_format("get_video_id_from_url", msg)
            logger.error(st)
        return video_id


