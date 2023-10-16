import logging
import traceback
import math
import Tools.YouTubeAPI.youtube.config as config
import pickle
import os
from Tools.YouTubeAPI.youtube.utils import get_fullpath
from Tools.YouTubeAPI.youtube.utils import log_format

logger = logging.getLogger('youtube.state')


class State(object):
    def __init__(self, youtube, current_quota) -> None:
        logger.debug("Initializing State object.")
        self._youtube = youtube
        self.current_quota = current_quota
        self.quota_exceeded = False
        self.api_key_valid = True
        self.videos_ids = []
        self.comments_count = {}
        #self.query = ""
        #self.num_videos = 0
        self.actions = []
        self.all_videos_retrieved = False
        self.all_comments_retrieved = False
        self.error = False
        self.error_description = ""

    def add_action(self, action):
        if action and action not in self.actions:
            self.actions.append(action)

    def remove_action(self, action=None, all=None):
        if action and action in self.actions:
            self.actions.remove(action)
        if all:
            self.actions = []

    def total_requests_cost(self, total_items, items_per_request, units_request):
        number_of_requests = math.ceil(total_items / items_per_request)
        total_cost = number_of_requests * units_request
        return total_cost

    def under_quota_limit(self, cost=None):
        if not cost:
            cost = 0
        under = True
        if (self.current_quota + cost) > (config.UNITS_QUOTA_LIMIT - config.SAFETY_BACKUP):
            under = False
        return under

    def update_quota_usage(self, value):
        self.current_quota = self.current_quota + value

    def set_all_retrieved(self, field, value):
        if field == config.ALL_VIDEOS_RETRIEVED:
            self.all_videos_retrieved = value

        if field == config.ALL_COMMENTS_RETRIEVED:
            self.all_comments_retrieved = value

    def number_of_items_with_quota(self, units_per_request, items_per_request):
        quote_available = ((config.UNITS_QUOTA_LIMIT - config.SAFETY_BACKUP) - self.current_quota)
        number_of_requests = math.floor(quote_available / units_per_request)
        total_items = items_per_request * number_of_requests
        return total_items

    def set_error_description(self, value, msg):
        self.error = value
        self.error_description = msg


    def _state_to_dict(self):

        state_dict ={}

        state_dict["current_quota"] = self.current_quota
        state_dict["quota_exceeded"] = self.quota_exceeded
        state_dict["api_key_valid"] = self.api_key_valid
        state_dict["videos_ids"] = self.videos_ids
        state_dict["comments_count"] = self.comments_count
        #state_dict["query"] = self.query
        #state_dict["num_videos"] = self.num_videos
        state_dict["actions"] = self.actions
        state_dict["all_videos_retrieved"] = self.all_videos_retrieved
        state_dict["all_comments_retrieved"] = self.all_comments_retrieved
        state_dict["error"] = self.error
        state_dict["error_description"] = self.error_description


        return state_dict

    def from_dict_to_state(self, state_dict):
        try:
            self.current_quota = state_dict.get("current_quota",0)
            self.quota_exceeded = state_dict.get("quota_exceeded",False)
            self.api_key_valid = state_dict.get("api_key_valid",True)
            self.videos_ids = state_dict.get("videos_ids",[])
            self.comments_count = state_dict.get("comments_count",{})
            #self.query = state_dict.get("query","")
            #self.num_videos = state_dict.get("num_videos", 0)
            self.actions = state_dict.get("actions", [])
            self.all_videos_retrieved = state_dict.get("all_videos_retrieved",False)
            self.all_comments_retrieved = state_dict.get("all_comments_retrieved",False)
            self.error = state_dict.get("error",False)
            self.error_description = state_dict.get("error_description",False)
        except:
            ex = traceback.format_exc()
            st = log_format("from_dict_to_state", ex)
            logger.error(st)
            st = "Error on saving the job state."
            self._youtube.state.set_error_description(True, st)


    def save_state_to_file(self, directory, name):
        state_dict = self._state_to_dict()
        filename_path = get_fullpath(directory, name)
        with open(filename_path, 'wb') as file:
            pickle.dump(state_dict, file)

    def load_state_from_file(self, directory, name):
        try:
            file = get_fullpath(directory, name)
            if os.path.exists(file):
                with open(file, 'rb') as f:
                    obj = pickle.load(f)
        except:
            obj = None
        return obj

    def add_actions_to_state(self, actions):
        if "METADATA" in actions:
            self.add_action(config.ACTION_RETRIEVE_VIDEOS)

        if "COMMENT" in actions:
            self.add_action(config.ACTION_RETRIEVE_COMMENTS)



