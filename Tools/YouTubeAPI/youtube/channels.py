import logging
import Tools.YouTubeAPI.youtube.config as config
import traceback
from Tools.YouTubeAPI.youtube.utils import is_quota_exceeded
from Tools.YouTubeAPI.youtube.utils import preprocess_string
from Tools.YouTubeAPI.youtube.utils import get_HTTP_error_msg
from Tools.YouTubeAPI.youtube.utils import log_format
from googleapiclient.errors import HttpError

logger = logging.getLogger('youtube.channels')

class Channels:
    def __init__(self, youtube) -> None:
        logger.debug("Initializing Channels object")
        self._youtube = youtube
        self.channel_records = {}

    # *****************************************************************************************************
    # This function retrieves the channels' metadata for each channel in channel_ids
    # The metadata is returned as a dictionary of dictionaries
    # *****************************************************************************************************
    def get_channels_metadata(self, channel_ids):

        if len(channel_ids) == 0:
                return {}

        channel_records = {}
        try:
            # Request all channels
            channels_request = self._youtube.service.channels().list(
                part="contentDetails,id,snippet,statistics,status,topicDetails",
                id=','.join(channel_ids),
                maxResults=config.MAX_CHANNELS_PER_REQUEST,
            )

            # Update quote usage
            self._youtube.state.update_quota_usage(config.UNITS_CHANNELS_LIST)
            channels_response = channels_request.execute()
            channel_records = self.channel_response_to_dict(channels_response)
        except HttpError as error:
            self._youtube.state.quota_exceeded = is_quota_exceeded(error)

            msg = get_HTTP_error_msg(error)
            st = log_format("get_videos_metadata", msg)
            logger.error(st)
            self._youtube.state.set_error_description(True, msg)

        except:
            ex = traceback.format_exc()
            st = log_format("get_videos_metadata", ex)
            logger.error(st)
            st = "Error on getting channel's metadata."
            self._youtube.state.set_error_description(True, st)

        self.channel_records = channel_records
        return channel_records

    # *****************************************************************************************************
    # This function creates a dictionary with a channel's metadata (send it as parameter).
    # This dictionary will be used to create a record on the output excel file
    # *****************************************************************************************************
    def create_channel_dict(self, item):
        try:
            record = {}
            record["channelId"] = item["id"]
            if "snippet" in item:
                record["channel_title"] = preprocess_string(item["snippet"].get("title", "NA"))
                record["channel_description"] = preprocess_string(item["snippet"].get("description", "NA"))
                record["channel_url"] = "www.youtube.com/channel/" + item["id"]
                record["channel_JoinDate"] = item["snippet"].get("publishedAt", "NA")
                record["channel_country"] = item["snippet"].get("country", "NA")

            if "statistics" in item:
                record["channel_viewCount"] = item["statistics"].get("viewCount", "NA")
                record["channel_subscriberCount"] = item["statistics"].get("subscriberCount", "NA")
                record["channel_videoCount"] = item["statistics"].get("videoCount", "NA")
        except:
            ex = traceback.format_exc()
            st = log_format("create_channel_dict", ex)
            logger.error(st)
            st = "Error on creating a channels dictionary.ff"
            self._youtube.state.set_error_description(True, st)

        return record

    # *****************************************************************************************************
    # *****************************************************************************************************
    def channel_response_to_dict(self, channels_response):
        records = {}
        for item in channels_response["items"]:   
            record = self.create_channel_dict(item)
            records[item["id"]] = record

        return records


