"""Reddit related classes."""

import json
import logging

logger = logging.getLogger("RedditJobDetails")


class RedditJobDetails:
    """Reddit Job Details class."""

    _valid_option_type = ["POST", "SUBREDDIT", "USER"]
    _valid_sort_option = ["TOP", "HOT", "NEW"]
    _valid_timeframe = ["all", "year", "month", "week", "today", "now"]
    _valid_actions = ["POST", "COMMENT", "KEYWORD"]

    def __init__(self, data: json = None):
        if data is not None:
            self.from_json(data)

    def __repr__(self) -> str:
        return self.to_json()

    def _validate_value(self, value, property_name, primary_type, secondary_type):
        """auxiliary method to validate types."""
        if not isinstance(value, primary_type):
            raise TypeError(
                f"{property_name} should be a {primary_type}, but {type(value)} was provided."
            )
        for val in value:
            if not isinstance(val, secondary_type):
                raise TypeError(
                    f'{property_name} should be a {primary_type} of'+ \
                    f'{secondary_type}, but {type(val)} was provided.'
                )

    @property
    def option_type(self):
        """option type"""
        return getattr(self, "_option_type", self._valid_option_type[0])

    @option_type.setter
    def option_type(self, value: str):
        if value not in self._valid_option_type:
            raise ValueError(
                f'Invalid option type {value}. Valid options: {", ".join(self._valid_option_type)}'
            )
        setattr(self, "_option_type", value)

    @property
    def post_list(self):
        '''post list'''
        return getattr(self, "_post_list", [])

    @post_list.setter
    def post_list(self, value: list[str]):
        self._validate_value(value, "post_list", list, str)
        setattr(self, "_post_list", value)

    @property
    def subreddit_list(self):
        """list of subreddits"""
        return getattr(self, "_subreddit_list", [])

    @subreddit_list.setter
    def subreddit_list(self, value: list[str]):
        """list of strings"""
        self._validate_value(value, "subreddit_list", list, str)
        setattr(self, "_subreddit_list", value)

    @property
    def keyword_list(self):
        """list of keywords"""
        return getattr(self, "_keyword_list", [])

    @keyword_list.setter
    def keyword_list(self, value: list[str]):
        self._validate_value(value, "keyword_list", list, str)
        setattr(self, "_keyword_list", value)

    @property
    def username_list(self):
        """list of usernames"""
        return getattr(self, "_username_list", [])

    @username_list.setter
    def username_list(self, value: list[str]):
        self._validate_value(value, "username_list", list, str)
        setattr(self, "_username_list", value)

    @property
    def sort_option(self):
        """sort_option key"""
        return getattr(self, "_sort_option", self._valid_sort_option[0])

    @sort_option.setter
    def sort_option(self, value):
        if not isinstance(value, str):
            raise TypeError(
                f"sort_option should be a string, but {type(value)} was provided."
            )
        if value not in self._valid_sort_option:
            raise ValueError(
                f'{value} is not a valid value. Valid values are:'+ \
                '{", ".join(self._valid_sort_option)}'
            )
        setattr(self, "_sort_option", value)

    @property
    def actions(self):
        """actions"""
        return getattr(self, "_actions", self._valid_actions[0])

    @actions.setter
    def actions(self, value):
        if not isinstance(value, str):
            raise TypeError(
                f"actions should be a string, but {type(value)} was provided."
            )
        if value not in self._valid_actions:
            raise ValueError(
                f'{value} is not a valid value. Valid values are: {", ".join(self._valid_actions)}'
            )
        setattr(self, "_actions", value)

    @property
    def response_count(self):
        """response count"""
        return getattr(self, "_response_count", 500)

    @response_count.setter
    def response_count(self, value: int):
        if not isinstance(value, int):
            raise TypeError(
                f"response_count should be an integer, but {type(value)} was provided."
            )
        setattr(self, "_response_count", value)

    def to_json(self):
        """to json"""
        return json.dumps(self.to_dict())

    def from_json(self, data):
        """from json"""
        if isinstance(data, str):
            data = json.loads(data)
        required_keys = [
            "option_type",
            "post_list",
            "subreddit_list",
            "keyword_list",
            "username_list",
            "sort_option",
            "actions",
            "response_count",
        ]
        for key in required_keys:
            if key not in data.keys():
                logger.debug("%s was not provided.", key)
            else:
                setattr(self, key, data[key])

    def to_dict(self):
        """convert to dictionary"""
        return {
            "job_submit": {
                "option_type": self.option_type,
                "post_list": self.post_list,
                "subreddit_list": self.subreddit_list,
                "keyword_list": self.keyword_list,
                "username_list": self.username_list,
                "sort_option": self.sort_option,
                "actions": self.actions,
                "response_count": self.response_count,
            }
        }


if __name__ == "__main__":
    jobd = RedditJobDetails()
    print(jobd.to_json())
    newjobd = RedditJobDetails(jobd.to_json())
    print(newjobd.to_json())
