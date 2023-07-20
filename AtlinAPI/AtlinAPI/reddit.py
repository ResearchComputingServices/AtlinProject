import json
from typing import Any 

class RedditJobDetails:
    _valid_sortby = ["top", "new", "hot"]
    _valid_timeframe = ["all", "year","month", "week", "today", "now"]
    
    def __init__(self, data: json = None):
        if data is not None:
            self.from_json(data)
        
    def __repr__(self) -> str:
        return self.to_json()
    
    @property
    def sort_by(self):
        return getattr(self, "_sort_by", self._valid_sortby[0])
    
    @sort_by.setter
    def sort_by(self, value):
        if value not in self._valid_sortby:
            raise ValueError(f"'{value}' is not a valid sortby value")
        setattr(self,"_sort_by", value)

    @property
    def timeframe(self):
        return getattr(self, "_timeframe", self._valid_timeframe[0])
    
    @timeframe.setter
    def timeframe(self, value):
        if value not in self._valid_timeframe:
            raise ValueError(f"'{value}' is not a valid timeframe.")
        setattr(self, "_timeframe", value)
    
    @property
    def n(self):
        return getattr(self, "_n", 5)

    @n.setter
    def n(self, value):
        if not isinstance(value, int):
            raise TypeError("n should be an integer")
        _n = value
    
    @property
    def subreddit(self):
        return getattr(self, "_subreddit", "")
    
    @subreddit.setter
    def subreddit(self, value):
        self._check_string(value)
        setattr(self, "_subreddit", value)
    
    @property
    def user(self):
        return getattr(self, "_user", "")
    
    @user.setter
    def user(self, value):
        self._check_string(value)
        setattr(self, "_user", value)
    
    @property
    def post(self):
        return getattr(self, "_post", "")
    
    @post.setter
    def post(self, value):
        self._check_string(value)
        setattr(self, "_post", value)
    
    @property
    def keyword(self):
        return getattr(self, "_keyword", "")
    
    @keyword.setter
    def keyword(self, value):
        self._check_string(value)
        setattr(self, "_keyword", value)
    
    @property
    def getposts(self):
        return getattr(self, "_getposts", "")
    
    @getposts.setter
    def getposts(self, value):
        self._check_string(value)
        setattr(self, "_getposts", value)
    
    @property
    def getcomments(self):
        return getattr(self, "_getcomments", "")
    
    @getcomments.setter
    def getcomments(self, value):
        self._check_string(value)
        setattr(self, "_getcomments", value)
    
    def _check_string(self, value):
        if not isinstance(value, str):
            raise ValueError(f"'{value}' should be a string.")
    
    def _mapkeys(self, key) -> str:
        mapping = {"sortBy": "sort_by"}
        
        if key in mapping.keys():
            return mapping[key]
        else:
            return key
        
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def from_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)
        required_keys = ['sortBy', 'timeframe', 'n', 'subreddit', 'user', 'post', 'keyword', 'getposts', 'getcomments']
        if not all(key in required_keys for key in data.keys()):
            raise ValueError(f"data should contain these fields: {', '.join(required_keys)}")
        for key in required_keys:
            setattr(self, self._mapkeys(key), data[key])
        
    def to_dict(self):
        return dict(
            sortBy = self.sort_by,
            timeframe = self.timeframe,
            n = self.n,
            subreddit = self.subreddit,
            user = self.user,
            post = self.post,
            keyword = self.keyword,
            getposts = self.getposts,
            getcomments = self.getcomments,
        )
    
    
        
if __name__ == "__main__":
    jobd = RedditJobDetails()
    
    jobd.sort_by = "new"
    print(jobd.to_json())
    newjobd = RedditJobDetails(jobd.to_json())
    print(newjobd.to_json())
    pass
    