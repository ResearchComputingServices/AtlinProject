import json

class YoutubeJobDetailsSubmit:
    _required_fields = ["option_type","option_value","actions","video_count"]
    def __init__(self,
                 option_type = None,
                 option_value = None,
                 actions = None,
                 video_count = None):
        loc = locals()
        for key in self._required_fields:
            if loc[key] is not None:
                setattr(self, key, loc[key])
        
    @property
    def option_type(self):
        return getattr(self, "_option_type", "QUERY")

    @option_type.setter
    def option_type(self, value):
        valid_values = ["VIDEO", "PLAYLIST", "QUERY", "FILE"]
        if value not in valid_values:
            raise ValueError(f"{value} is not valid. Valid values are {', '.join(valid_values)}")
        self._option_type = value
    
    @property
    def option_value(self):
        return getattr(self, "_option_value", "")

    @option_value.setter
    def option_value(self, value):
        self._option_value = value

    @property
    def actions(self):
        return getattr(self, "_actions", ["METADATA"])
    
    @actions.setter
    def actions(self, value):
        if not isinstance(value, list):
            raise TypeError("Should be of type list")
        valid_values =  ["METADATA", "COMMENTS"]
        if not all(key in valid_values for key in value):
            raise ValueError(f"Contains invalid value. Valid values are: {', '.join(valid_values)}")
        self._actions = value
    
    @property
    def video_count(self):
        return getattr(self, "_video_count", 5)

    @video_count.setter
    def video_count(self, value):
        if not isinstance(value, int):
            raise TypeError(f"value should be an integer.")
        self._video_count = value
    
    def to_dict(self):
        out = dict()
        try:
            for varname in self._required_fields:
                out[varname] = getattr(self, varname)
        except Exception as exc:
            raise e
        return out
    
    def to_json(self):
        '''to json'''
        return json.dumps(self.to_dict())
    
    def from_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)

        if not all (field in data.keys() for field in self._required_fields):
            raise ValueError(f"data should contain fields: {', '.join(self._required_fields)}")
        
        for var in self._required_fields:
            setattr(self, var, data[var])
        
class YoutubeJobDetailsResume:
    _required_fields = {
        "current_quota" : 1000, 
        "quota_exceeded": True,
        "api_key_valid" : True,
        "videos_ids" :[],
        "comments_count" : {},
        "actions" : [],
        "all_videos_retrieved" : True,
        "all_comments_retrieved" : True,
        "error"  : True,
        "error_description" : "",
    }
    
    def __init__(self):
        for key in self._required_fields.keys():
            setattr(self, key, self._required_fields[key])
    
    def to_dict(self):
        '''to dict'''
        out = {}
        for key in self._required_fields.keys():
            out[key] = getattr(self, key)
        return out
    
    def to_json(self):
        '''to json'''
        return json.dumps(self.to_dict())

    def from_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)
            
        if not all(key in data.keys() for key in self._required_fields.keys()):
            raise ValueError(f"Missing key. Required keys: {', '.join(self._required_fields.keys())}")
        for key in self._required_fields.keys():
            setattr(self, key, data[key])
        
class YoutubeJobDetails:
    _required_fields = ["job_name", "job_submit", "job_resume"]
    
    def __init__(self,
                 job_name: str = '',
                 job_submit: YoutubeJobDetailsSubmit = YoutubeJobDetailsSubmit(),
                 job_resume: YoutubeJobDetailsResume = YoutubeJobDetailsResume(),
                 data: dict = None) -> None:
        
        self.job_name = job_name
        self.job_submit = job_submit
        self.job_resume = job_resume
        
        if data is not None:
            self.from_json(data)
        
        
    def from_json(self, data):
        if isinstance(data, str):
            data = json.loads(data)
            
        if not all(key in data.keys() for key in self._required_fields):
            raise ValueError(f"missing required value. Required values: {', '.join(self._required_fields)}")
        setattr(self, "job_name", data['job_name'])
        self.job_submit.from_json(data['job_submit'])
        self.job_resume.from_json(data['job_resume'])
            
    def to_json(self):
        return json.dumps(self.to_dict())
    
    def to_dict(self):
        return {
            'job_name': self.job_name,
            'job_submit': self.job_submit if isinstance(self.job_submit, dict) else self.job_submit.to_dict(),
            'job_resume': self.job_resume if isinstance(self.job_resume,dict) else self.job_resume.to_dict(),
        }

if __name__ == "__main__":
    
    job_submit = YoutubeJobDetailsSubmit()
    print(job_submit.to_json())
    
    job_submit.from_json({"option_type": "VIDEO", "option_value": "", "actions": ["COMMENTS"], "video_count": 5})
    print(job_submit.to_json())
    
    job_resume = YoutubeJobDetailsResume()
    print(job_resume.to_json())
    
    job_resume.from_json(json.loads('{"current_quota": 1234, "quota_exceeded": true, "api_key_valid": true, "videos_ids": [], "comments_count": {}, "actions": [], "all_videos_retrieved": true, "all_comments_retrieved": true, "error": true, "error_description": ""}'))
    print(job_resume.to_json())
    
    jobd = YoutubeJobDetails()
    print(jobd.to_json())
    
    jobd.from_json(json.loads(jobd.to_json()))
    
    jobd.from_json(json.dumps(
        dict(
            job_name = "testjob",
            job_submit= job_submit.to_json(),
            job_resume = job_resume.to_json(),
        )
    ))
    
    