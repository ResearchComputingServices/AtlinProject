import logging
import traceback
import datetime
import emoji
from bs4 import BeautifulSoup
from googleapiclient.errors import HttpError
import Tools.YouTubeAPI.youtube.config as config
from Tools.YouTubeAPI.youtube.utils import is_quota_exceeded
from Tools.YouTubeAPI.youtube.utils import preprocess_string
from Tools.YouTubeAPI.youtube.utils import remove_prefix_url
from Tools.YouTubeAPI.youtube.utils import log_format
from Tools.YouTubeAPI.youtube.utils import get_HTTP_error_msg

logger = logging.getLogger('youtube.comments')

class Comments(object):
    def __init__(self, youtube) -> None:
        logger.debug("Initializing Comments object.")
        self._youtube = youtube
        self.comments_records = {}

    # *****************************************************************************************************
    # This function gets a comment (a string) which contains html tags and/or html characters and
    # returns a string without them
    # *****************************************************************************************************
    def soupify_comment(self, comment):
        soup = BeautifulSoup(comment, 'html.parser')
        return soup.get_text()

    # *****************************************************************************************************
    # This functions gets a comment (a string) and replaces the emojis with the emoji name and  the prefix
    # "emoji_"
    # *****************************************************************************************************
    def demojize_comment(self, comment):
        return emoji.demojize(comment, delimiters=(" emoji_", " "))


    # *****************************************************************************************************
    # *****************************************************************************************************
    # *****************************************************************************************************
    # This function retrieves the replies for a comment (parent_id)
    # *****************************************************************************************************
    def get_comment_replies(self, parent_id):

        nextPageToken = None
        list = []
        try:
            while True:
                 # List maxResults videos in a playlist
                requestCommentsList = self._youtube.service.comments().list(
                    part='id,snippet',
                    parentId=parent_id,
                    maxResults=config.MAX_REPLIES_PER_REQUEST,
                    # textFormat='plainText',
                    pageToken=nextPageToken
                )
                self._youtube.state.update_quota_usage(config.UNITS_COMMENTS_LIST)
                responseCommentsList = requestCommentsList.execute()
                list.extend(responseCommentsList['items'])
                nextPageToken = responseCommentsList.get('nextPageToken')
                if not nextPageToken:
                    break;
        except:
            ex = traceback.format_exc()
            st = log_format("get_comment_replies", ex)
            logger.error(st)
            #self._youtube.state.set_error_description(True, st)
            list = []

        return list

    # *****************************************************************************************************
    # *****************************************************************************************************
    def create_comment_and_commenter_dict(self, records, item, commentsCount, comment_number, channelId_commenters):
        now = datetime.datetime.now()
        current_datetime_str = now.strftime("%Y-%m-%d, %H:%M:%S")

        count = len(records) + 1

        metadata = {
            "id": "",
            "type": "",
            "Recipient (video or comment)": "",
            "video url": "",
            "comment": "",
            "likeCount": "",
            "publishedAt": "",
            "scrappedAt": "",
            "totalReplyCount": "",
            "authorDisplayName": "",
            "authorProfileImageUrl": "",
            "authorChannelId": "",
            "authorChannelUrl": "",
            "totalComments": commentsCount,
            "comment #": comment_number,
        }

        if "snippet" in item:
            try:
                metadata["id"] = item["id"]
                metadata["type"] = "Comment"
                metadata["Recipient (video or comment)"] = item["snippet"].get("videoId", "")
                # url = "https://youtu.be/" + item["snippet"].get("videoId","")
                url = "youtu.be/" + item["snippet"].get("videoId", "")
                metadata["video url"] = url
                # metadata["original_comment"] = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay","") #debug only
                comment = item["snippet"]["topLevelComment"]["snippet"].get("textDisplay", "")
                if len(comment) > 0:
                    comment = self.soupify_comment(comment)
                    comment = self.demojize_comment(comment)
                metadata["comment"] = preprocess_string(comment)
                metadata["authorDisplayName"] = preprocess_string(
                    item["snippet"]["topLevelComment"]["snippet"].get("authorDisplayName", ""))
                metadata["authorProfileImageUrl"] = remove_prefix_url(
                    item["snippet"]["topLevelComment"]["snippet"].get("authorProfileImageUrl", ""))
                commenter_channel_id = item["snippet"]["topLevelComment"]["snippet"]["authorChannelId"].get("value", "")
                metadata["authorChannelId"] = commenter_channel_id
                metadata["authorChannelUrl"] = remove_prefix_url(
                    item["snippet"]["topLevelComment"]["snippet"].get("authorChannelUrl", ""))
                metadata["likeCount"] = item["snippet"]["topLevelComment"]["snippet"].get("likeCount", "")
                metadata["publishedAt"] = item["snippet"]["topLevelComment"]["snippet"].get("publishedAt", "")
                metadata["scrappedAt"] = current_datetime_str
                totalReplies = item["snippet"].get("totalReplyCount", "0")
                metadata["totalReplyCount"] = totalReplies
                records[count] = metadata

                if commenter_channel_id != "":
                    channelId_commenters.append(commenter_channel_id)

                if "replies" in item:

                    copy_replies = True
                    if len(item["replies"]["comments"]) < int(totalReplies):
                        replies_retrieving_cost = self._youtube.state.total_requests_cost(int(totalReplies),config.MAX_REPLIES_PER_REQUEST, config.UNITS_COMMENTS_LIST)

                        # We only retrieve replies if we have enough quote
                        # These calls are difficult to estimate in advance, since we don't know for which videos we will
                        # actually get all the replies in the first call.
                        if self._youtube.state.under_quota_limit(replies_retrieving_cost):
                            replies = self.get_comment_replies(item["id"])
                            # We actually obtained more replies than the first call
                            if len(replies) > 0 and len(replies) > len(item["replies"]["comments"]):
                                copy_replies = False

                    if copy_replies:
                        replies = item["replies"]["comments"]

                    for reply in replies:
                        comment_number = comment_number + 1
                        metadata = {}
                        count = count + 1
                        metadata["id"] = reply["id"]
                        metadata["type"] = "Reply"
                        metadata["Recipient (video or comment)"] = reply["snippet"].get("parentId", "")
                        # metadata["original_comment"] = reply["snippet"].get("textDisplay", "")  #debug only
                        comment = reply["snippet"].get("textDisplay", "")
                        if len(comment) > 0:
                            comment = self.soupify_comment(comment)
                            comment = self.demojize_comment(comment)
                        metadata["comment"] = preprocess_string(comment)
                        commenter_channel_id = reply["snippet"]["authorChannelId"].get("value", "")
                        metadata["authorChannelId"] = commenter_channel_id
                        metadata["authorChannelUrl"] = remove_prefix_url(reply["snippet"].get("authorChannelUrl", ""))
                        metadata["authorDisplayName"] = preprocess_string(reply["snippet"].get("authorDisplayName", ""))
                        metadata["authorProfileImageUrl"] = remove_prefix_url(
                            reply["snippet"].get("authorProfileImageUrl", ""))
                        metadata["likeCount"] = reply["snippet"].get("likeCount", "")
                        metadata["publishedAt"] = reply["snippet"].get("publishedAt", "")
                        metadata["scrappedAt"] = current_datetime_str
                        metadata["totalReplyCount"] = "N/A"
                        metadata["video url"] = ""
                        metadata["totalComments"] = commentsCount
                        metadata["comment #"] = comment_number

                        if commenter_channel_id != "":
                            channelId_commenters.append(commenter_channel_id)

                        records[count] = metadata
            except:
                ex = traceback.format_exc()
                st = log_format("create_comment_and_commenter_dict", ex)
                logger.error(st)
        else:
            records[count] = metadata

        return records, channelId_commenters

    # ***********************************************************************************************************************
    # TThis function retrieves all comments, its replies and its commenters ids (channel id) for a single
    # video given as a parameter (video_id)
    # The commenters ids (channels ids) are retuned into a list of commenters
    # ***********************************************************************************************************************
    def _get_single_video_comments_and_commenters(self, video_id, commentsCount, records=None, commenters_ids=None):

        if not records:
            records = {}

        if commentsCount == 0 or commentsCount == 'N/A':
            return records, commenters_ids

        nextPageToken = None
        count = 0

        try:
            fully_retrieved = True
            while True:
                #Check to see if we have quota to retrieve video's comments
                if not self._youtube.state.under_quota_limit(config.UNITS_COMMENTS_THREADS_LIST):
                    fully_retrieved = False
                    break

                # List maxResults videos in a playlist
                requestCommentsList = self._youtube.service.commentThreads().list(
                    part='id,snippet,replies',
                    videoId=video_id,
                    maxResults=config.MAX_COMMENTS_PER_REQUEST,
                    # textFormat='plainText',
                    pageToken=nextPageToken
                )

                self._youtube.state.update_quota_usage(config.UNITS_COMMENTS_THREADS_LIST)
                responseCommentsList = requestCommentsList.execute()


                for item in responseCommentsList['items']:
                    count = count + 1
                    before = len(records)
                    records, commenters_ids = self.create_comment_and_commenter_dict(records, item, commentsCount, count, commenters_ids)
                    replies = len(records) - before - 1
                    count = count + replies
                    nextPageToken = responseCommentsList.get('nextPageToken')

                if not nextPageToken:
                    break;
        except HttpError as error:
            self._youtube.state.quota_exceeded = is_quota_exceeded(error)

            msg = get_HTTP_error_msg(error)
            st = log_format("_get_single_video_comments_and_commenters", msg)
            logger.error(st)
            self._youtube.state.set_error_description(True, msg)
            fully_retrieved = False

        except:
            ex = traceback.format_exc()
            st = log_format("_get_single_video_comments_and_commenters", ex)
            logger.error(st)
            #self._youtube.state.set_error_description(True, st)
            fully_retrieved = False

        return records, commenters_ids, fully_retrieved

    # ***********************************************************************************************************************
    # TThis function retrieves all comments, its replies and its commenters ids (channel id) for a single
    # video given as a parameter (video_id)
    # The commenters ids (channels ids) are retuned into a list of commenters
    # ***********************************************************************************************************************
    def get_single_video_comments_and_commenters(self, video_id, video_id_comments_count, records=None, commenters_ids=None):

        #Estimate the cost of retrieving all comments and the commenters information for a single video
        comments_cost = self._youtube.state.total_requests_cost(video_id_comments_count,
                                                                config.MAX_COMMENTS_PER_REQUEST,
                                                                config.UNITS_COMMENTS_LIST)

        commenters_cost = self._youtube.state.total_requests_cost(video_id_comments_count,
                                                                  config.MAX_CHANNELS_PER_REQUEST,
                                                                  config.UNITS_CHANNELS_LIST)

        fully_retrieved = False

        # We do not have enough quote to retrieve the comments for this video along with its commenter's info
        if self._youtube.state.under_quota_limit(comments_cost + commenters_cost):
            ex = "Fetching comments for video: " + video_id
            st = log_format("get_single_video_comments_and_commenters", ex)
            logger.debug(st)

            records, commenters_ids, fully_retrieved = self._get_single_video_comments_and_commenters(video_id,
                                                                                                       video_id_comments_count,
                                                                                                       records,
                                                                                                       commenters_ids)

        return records, commenters_ids, fully_retrieved


    # *****************************************************************************************************
    # *****************************************************************************************************
    def get_commenters_info(self, commenters_ids, channel_records):


        #Remove ids for which info has already been retrieved
        id_list = commenters_ids
        for id in id_list:
            if id in channel_records.keys():
                commenters_ids.remove(id)

        # Retrieving commenter's info
        slicing = True
        start = 0


        while (slicing):
            end = start + config.MAX_CHANNELS_PER_REQUEST
            if end > len(commenters_ids):
                end = len(commenters_ids)
                slicing = False

            channels_ids = set(commenters_ids[start:end])
            r = self._youtube.channels.get_channels_metadata(channels_ids)
            if self._youtube.state.quota_exceeded:
                break
            channel_records.update(r)
            start = end

        return channel_records

    # *****************************************************************************************************
    # This function removes from a list the videos form whom the cost of retrieving all its comments
    # superpases the available quote
    # It also removes videos with zero or N/A comments
    # *****************************************************************************************************
    def filter_videos_by_comments_count(self, comments_count_original):
        comments_count = {}
        for video_id, total_comments in comments_count_original.items():
            if not (total_comments == '0' or total_comments == 'N/A'):
                cost = self._youtube.state.total_requests_cost(int(total_comments), config.MAX_COMMENTS_PER_REQUEST,
                                                 config.UNITS_COMMENTS_LIST)
                # if cost < 10000:
                if cost <  config.UNITS_QUOTA_LIMIT:
                    comments_count[video_id] = int(total_comments)
                else:
                    msg  = "Video {} has {} comments. It cannot be retrieved with current quota. ".format(video_id,total_comments)
                    st = log_format("filter_videos_by_comments_count", msg)
                    logger.warning(st)

                    # Save to file to notify user - TO DO
        return comments_count

    # *****************************************************************************************************
    # This function retrieves the total comments (including replies) for a list of videos ids
    # *****************************************************************************************************
    def _get_comments_count(self, videos_ids):

        comments_count = {}
        slice = True
        start = 0
        while (slice):
            end = start + config.MAX_JOIN_VIDEOS_IDS
            if end > len(videos_ids):
                end = len(videos_ids)
                slice = False

            ids = videos_ids[start:end]
            try:
                videos_request = self._youtube.service.videos().list(
                    part="statistics",
                    id=','.join(ids)
                )

                self._youtube.state.update_quota_usage(config.UNITS_VIDEOS_LIST)
                videos_response = videos_request.execute()
                r = {}
                for item in videos_response['items']:
                    if "statistics" in item:
                        id = item["id"]
                        commentsCount = item["statistics"].get("commentCount", "N/A")
                        r[id] = commentsCount

                comments_count.update(r)
            except HttpError as error:
                self._youtube.state.quota_exceeded = is_quota_exceeded(error)
            except:
                ex = traceback.format_exc()
                st = log_format("_get_comments_count", ex)
                logger.error(st)
                #self._youtube.state.set_error_description(True, st)

            start = end

        return comments_count

    # *****************************************************************************************************
    # This funtion retrieves the # of comments for a list of videos ids
    # Returns a dictionary list where the key is the video id.
    # Sorts the list (by default) from min to max number of comments
    # *****************************************************************************************************
    def get_comments_count(self, videos_ids):

        logger.debug(f"Comments:get_comments_for_ids: ids {videos_ids}")

        try:
            # Cost of retrieving videos' stats (to get the # of comments)
            cost = self._youtube.state.total_requests_cost(len(videos_ids), config.MAX_VIDEOS_PER_REQUEST, config.UNITS_VIDEOS_LIST)
            if not self._youtube.state.under_quota_limit(cost):
                #There is not enough quote to retrieve all the comments count
                self._youtube.state.quota_exceeded = True
                return

            # Obtain the total comments per video_id
            videos_comments_count_original = self._get_comments_count(videos_ids)

            # Remove the un-retrievable videos, i.e., videos for we cannot retrieve their comments with the
            # full available quota (the cost of retrieving the comments overpasses the 10,000 units)
            # It also removes videos with zero or N/A comments
            videos_comments_count = self.filter_videos_by_comments_count(videos_comments_count_original)

            #Update the videos_id only with the videos that we can actually retrieve
            videos_ids = list(videos_comments_count.keys())


            self._youtube.state.videos_ids = videos_ids
            self._youtube.state.comments_count = videos_comments_count
        except:
            ex = traceback.format_exc()
            st = log_format("get_comments_count", ex)
            logger.error(st)
            #self._youtube.state.set_error_description(True, st)

        return

    # *****************************************************************************************************
    # *****************************************************************************************************
    def clean_comments_count_dict(self, videos_ids):
        new_dict = {}
        try:
            for id in videos_ids:
                d={}
                if id in self._youtube.state.comments_count.keys():
                    value = self._youtube.state.comments_count[id]
                    d[id] = value
                    new_dict.update(d)
        except:
            ex = traceback.format_exc()
            st = log_format("clean_comments_count_dict", ex)
            logger.error(st)
            #self._youtube.state.set_error_description(True, st)
            return None

        return new_dict

    # *****************************************************************************************************
    # This function retrieves all comments, its replies and its commenters ids (channel id) for a list of
    # videos given as a parameter (videos_id)
    # *****************************************************************************************************
    def get_comments_and_commenters(self, videos_ids):

        channel_records = {}
        records = {}
        start = 0

        self._youtube.state.add_action(config.ACTION_RETRIEVE_COMMENTS)
        self._youtube.state.all_comments_retrieved= False
        self._youtube.state.videos_ids = videos_ids


        # Retrieve the number of comments per video (if not preivously retrieved)
        #and discard the videos where the cost of retrieval exceeds the maximum quota
        if len(self._youtube.state.comments_count)==0:
            self.get_comments_count(videos_ids)
            if not len(self._youtube.state.comments_count):
                #We have to raise an exception to let the user/scheduler we cannot run the request with the available quota
                ex = "There is not enough quota to run the request."
                st = log_format("get_comments_and_commenters", ex)
                logger.warning(st)
                self._youtube.state.quota_exceeded=True
                return records

        #Update the videos ids to retrieve after removing videos with too many comments that cannot be retrieved
        #The variable self._youtube.state.videos_ids got updated in self.get_comments_count
        videos_ids = self._youtube.state.videos_ids

        while (start < len(videos_ids)):
            try:
                commenters_ids = []
                inc = 0

                #Loop to retrieve comments for at most 50 videos at the time
                #We are requesting channel info (commenters_ids) after and the limit is config.MAX_CHANNELS_PER_REQUEST
                fully_retrieved = True
                while (len(commenters_ids) < config.MAX_CHANNELS_PER_REQUEST) and (start + inc < len(videos_ids)) and fully_retrieved:
                    video_id = videos_ids[start + inc]
                    video_id_comments_count = self._youtube.state.comments_count[video_id]
                    records, commenters_ids, fully_retrieved = self.get_single_video_comments_and_commenters(video_id, video_id_comments_count, records, commenters_ids)
                    commenters_ids = list(set(commenters_ids))
                    inc = inc + 1


                #Stop if there is not enough quota to continue retrieving comments
                if not fully_retrieved or self._youtube.state.quota_exceeded:
                    # The videos's comments were not fully retrieved because we run out of quota
                    ex = "Run out of quota."
                    st = log_format("get_comments_and_commenters", ex)
                    logger.warning(st)
                    self._youtube.state.quota_exceeded = True
                    break

                #REVISIT THIS CONDITION!!!
                if len(records) == 0 or len(commenters_ids) == 0:
                    return records

                # Check that we have quota to retrieve commenters
                commenters_cost = self._youtube.state.total_requests_cost(len(commenters_ids), config.MAX_CHANNELS_PER_REQUEST, config.UNITS_CHANNELS_LIST)
                if not self._youtube.state.under_quota_limit(commenters_cost):
                    ex = "There is not enough quota to continue retrieving comments."
                    st = log_format("get_comments_and_commenters", ex)
                    logger.warning(st)
                    self._youtube.state.quota_exceeded = True
                    break

                # Retrieving commenter's info
                channel_records = self.get_commenters_info(commenters_ids, channel_records)

                #Check if we didn't run out of quota while retrieving channel's commenters
                if self._youtube.state.quota_exceeded:
                    break

                #Update comments with commenter info
                for key, item in records.items():
                    try:
                        channel_id_commenter = item["authorChannelId"]
                        channel_info = channel_records[channel_id_commenter]
                        item.update(channel_info)
                    except:
                        ex1 = traceback.format_exc()
                        ex2 = 'Error getting commenters metadata: ' + channel_id_commenter
                        st = log_format("get_comments_and_commenters", ex1 + ex2)
                        logger.warning(st)

                start = start + inc
                #Keep in the state only the videos ids missing to process
                #In case we run out of quota
                self._youtube.state.videos_ids = videos_ids[start:len(videos_ids)]
            except:
                ex = traceback.format_exc()
                st = log_format("get_comments_count", ex)
                logger.error(st)
                #self._youtube.state.set_error_description(True, st)

        if start >= len(videos_ids):
            self._youtube.state.remove_action(config.ACTION_RETRIEVE_COMMENTS)
            self._youtube.state.set_all_retrieved(config.ALL_COMMENTS_RETRIEVED, True)
        else:
            new_dict = self.clean_comments_count_dict(self._youtube.state.videos_ids)
            if new_dict != None or len(new_dict)>0:
                self._youtube.state.comments_count = new_dict

        self.comments_records = records

        return records
