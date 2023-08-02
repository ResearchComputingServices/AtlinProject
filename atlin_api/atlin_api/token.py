'''Tokens'''
from abc import ABC, abstractmethod
from uuid import UUID, uuid4
import json
from .atlin import JobPlatform


class Token(ABC):
    """token"""

    _required_keys = [
        "token_name",
        "token_uid",
        "user_uid",
        "token_tag",
        "social_platform",
        "token_detail",
    ]

    def __init__(self, data: json = None):
        if data is not None:
            self.from_json(data)

    def _verify_token_details(self):
        self.verify_token_details(self.token_detail)

    def verify_token_details(self, value):
        """verify token details"""
        if not all(key in value.keys() for key in self.required_token_details().keys()):
            raise ValueError(
                f"Missing token key. Required keys are: {self.required_token_details().keys()}"
            )

    def _validate_uid(self, value):
        try:
            UUID(str(value))
        except ValueError as exc:
            raise exc

    @abstractmethod
    def required_token_details(self):
        """required token details: a dict with keys and types"""
        raise NotImplementedError()

    @property
    def token_name(self):
        """token name"""
        return getattr(self, "_token_name", "")

    @token_name.setter
    def token_name(self, value):
        if not isinstance(value, str):
            raise TypeError("value shoud be a string")
        setattr(self, "_token_name", value)

    @property
    def token_uid(self):
        """token uid"""
        if getattr(self, "_token_uid", None) is None:
            setattr(self, "_token_uid", str(uuid4()))
        return getattr(self, "_token_uid")

    @token_uid.setter
    def token_uid(self, value):
        self._validate_uid(value)
        setattr(self, "_token_uid", value)

    @property
    def user_uid(self):
        """user uid"""
        uid = getattr(self, "_user_uid", None)
        if uid is None:
            raise ValueError(f"Invalid user uid: {uid}")
        return uid

    @user_uid.setter
    def user_uid(self, value):
        self._validate_uid(value)
        setattr(self, "_user_uid", value)

    @property
    def token_tag(self):
        """token tag"""
        return getattr(self, "_token_tag", "")

    @token_tag.setter
    def token_tag(self, value: list):
        if isinstance(value, str):
            setattr(self, "_token_tag", value)
        elif isinstance(value, list):
            setattr(self, "_token_tag", ",".join(value))
        else:
            raise TypeError("token_tag should be either str or list.")

    @property
    def social_platform(self):
        """social platform"""
        val = getattr(self, "_social_platform", "")
        if val not in JobPlatform.valid_values:
            raise ValueError("'{val}' is not a valid platform.")
        return val

    @social_platform.setter
    def social_platform(self, value):
        if value not in JobPlatform.valid_values:
            raise ValueError(f"'{value}' is not a valid social_platform")
        setattr(self, "_social_platform", value)

    @property
    def token_detail(self):
        """token detail"""
        return getattr(self, "_token_detail", dict())

    @token_detail.setter
    def token_detail(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError(
                f"token_detail should be a dictionary but {type(value)} was provided"
            )
        self.verify_token_details(value)
        setattr(self, "_token_detail", value)

    def from_json(self, data):
        """from json"""
        if isinstance(data, str):
            data = json.loads(data)

        if not all(key in data.keys() for key in self._required_keys):
            raise ValueError(f"Missing key. Required keys are {self._required_keys}")

        for key in self._required_keys:
            setattr(self, key, data[key])

    def to_json(self):
        """to_json"""
        return json.dumps(self.to_dict())

    def to_dict(self):
        """to dict"""
        out = dict()
        for key in self._required_keys:
            out[key] = getattr(self, key)
        self._verify_token_details()
        return out


class YoutubeToken(Token):
    """YouTube token"""

    def __init__(self, data: json = None):
        super().__init__(data)
        self.social_platform = JobPlatform.youtube

    def required_token_details(self):
        """required token details"""
        return {
            "api_token": str,
            "token_quota": int,
            "modify_date": str,
        }


class RedditToken(Token):
    """reddit token"""

    def __init__(self, data: json = None):
        super().__init__(data)
        self.social_platform = JobPlatform.reddit

    def required_token_details(self):
        return {
            "client_id": str,
            "secret_token": str,
            "username": str,
            "password": str,
            "token_quota": int,
            "modify_date": str,
        }


def token_filter_by_keyword(data: list, keyword: str, value: str):
    """filter data by keywords and values"""
    out = []
    for datadict in data:
        if isinstance(datadict, dict):
            if keyword in datadict.keys():
                if datadict[keyword] == value:
                    out.append(datadict)
    return out
