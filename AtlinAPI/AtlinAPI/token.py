from abc import ABC, abstractmethod, abstractproperty
from uuid import UUID, uuid4
import json
from . import atlin_schemas as schemas



class Token(ABC):
    _required_keys = [
        "token_name",
        "token_uid",
        "user_uid",
        "token_tag",
        "social_platform",
        "token_detail"
    ]
    
    def __init__(self, data: json = None):
        if data is not None:
            self.from_json(data)
    
    def _verify_token_details(self):
        self.verify_token_details(self.token_detail)
        
    def verify_token_details(self, value):
        if not all(key in value.keys() for key in self.required_token_details().keys()):
            raise ValueError(f"Missing token key. Required keys are: {self.required_token_details().keys()}")
     
    def _validate_uid(self, value):
        try:
            UUID(str(value))
        except Exception as e:
            raise ValueError(f"{value } is not a valid uuid")
    
    @property
    @abstractmethod
    def required_token_details(self):
        raise NotImplementedError()
    
    @property
    def token_name(self):
        return getattr(self, '_token_name', "")
    
    @token_name.setter
    def token_name(self, value):
        if not isinstance(value,str):
            raise TypeError("value shoud be a string")
        setattr(self, "_token_name", value)
        
    @property
    def token_uid(self):
        if getattr(self, "_token_uid", None) is None:
            setattr(self, "_token_uid", str(uuid4()))
        return getattr(self, "_token_uid")

    @token_uid.setter
    def token_uid(self, value):
        self._validate_uid(value)
        setattr(self, "_token_uid", value)
     
    @property
    def user_uid(self):
        id = getattr(self, "_user_uid", None)
        if id is None:
           raise ValueError(f"Invalid user id: {id}") 
        return id
        
    @user_uid.setter
    def user_uid(self, value):
        self._validate_uid(value)
        setattr(self, "_user_uid", value)    
    
    @property
    def token_tag(self):
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
        val = getattr(self, "_social_platform", "")
        if val not in schemas._valid_social_platforms:
            raise ValueError("'{val}' is not a valid platform.")
        return val
    
    @social_platform.setter
    def social_platform(self, value):
        if value not in schemas._valid_social_platforms:
            raise ValueError(f"'{value}' is not a valid social_platform")
        setattr(self, "_social_platform", value)
    
    @property
    def token_detail(self):
        return getattr(self, "_token_detail", dict())
    
    @token_detail.setter
    def token_detail(self, value: dict):
        if not isinstance(value, dict):
            raise TypeError(f"token_detail should be a dictionary")
        self.verify_token_details(value)
        setattr(self, "_token_detail", value)
        
    def from_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        
        if not all(key in data.keys() for key in self._required_keys):
            raise ValueError(f"Missing key. Required keys are {self._required_keys()}")
        
        for key in self._required_keys:
            setattr(self, key, data[key])
        
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def to_dict(self):
        out = dict()
        for key in self._required_keys:
            out[key] = getattr(self, key)
        self._verify_token_details()
        return out 


class YoutubeToken(Token):
    def __init__(self, data: json = None):
        super().__init__(data)
        self.social_platform = "YOUTUBE"
    
    def required_token_details(self):
        return dict(
            api_token=str,
            token_quota=int,
            modify_date = str,
        )
        
    # def verify_token_details(self, token_details):
    #     if not all(key in token_details.keys() for key in self._required_token_structure.keys()):
    #         raise ValueError(f"Missing token key. Required keys are: {self._required_token_structure.keys()}")

class RedditToken(Token):
    def __init__(self, data: json = None):
        super().__init__(data)
        self.social_platform = "REDDIT"
    
    def required_token_details(self):
        dict(
            client_id = str,
            secret_token = str,
            username = str,
            password = str,
            token_quota = int,
            modify_date = str,
        )
        
    # def verify_token_details(self, token_details):
    #     if not all(key in token_details.keys() for key in self._required_token_structure.keys()):
    #         raise ValueError(f"Missing token key. Required keys are: {self._required_token_structure.keys()}")
        
        
if __name__ == "__main__":
    token = YoutubeToken()
    token.user_uid = str(uuid4())
    token_details = dict(api_token=str(uuid4()), token_quota=100, modified_quota_timestamp="")
    token.token_detail = token_details
    print(token.to_json())
    token2 = YoutubeToken(token.to_json())
    print(token2.to_json())
    pass