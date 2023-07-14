from abc import ABC, abstractmethod
from inspect import currentframe, getframeinfo
import requests
import urllib
import logging
import json
from jsonschema import validate
from . import atlin_schemas as schemas

logging.basicConfig(level=logging.DEBUG)

class JobStatus:
    def __init__(self) -> None:
        for item in schemas._valid_job_status:
            setattr(self, item.lower(), item)
        self.valid_values = schemas._valid_job_status

class JobPlatform:
    def __init__(self):
        for item in schemas._valid_social_platforms:
            setattr(self, item.lower(), item)
        self.valid_values = schemas._valid_social_platforms

class AtlinBase(ABC):
    def __init__(self, 
                 domain: str):
        self._domain = domain if domain[-1] == '/' else f"{domain}/"
        self._apipath = "api/v1/"
        self._job_status = JobStatus()
        self._job_platforms = JobPlatform()
        self._header_json  = {"Content-Type": "application/json"}
    
    @property
    def url_api(self):
        return f"{self._domain}{self._apipath}"
    
    @abstractmethod
    def job_get_detail_schema(self, **kwargs):
        pass
    
    def _request_delete(self, url, headers, params, body):
        try:
            logging.debug(f"Making a delete request.\nurl: {url}\nheaders: {headers}\nparams: {params}")
            response = requests.delete(url, params=params, headers=headers, data=body)
            return response
        except Exception as e:
            logging.error(f"{__file__} {__name__}: {e}")
            raise e
            
    def _request_get(self, url, headers, params):
        try: 
            logging.debug(f"Making a get request.\nurl: {url}\nheaders: {headers}\nparams: {params}")
            response = requests.get(url=url, headers= headers, params=params )
            return response
        except Exception as e:
            logging.error(f"{__file__} {__name__}: {e}")
            raise e
        
    def _request_put(self, url, headers, params, body):
        try: 
            logging.debug(f"Making a put request.\nurl: {url}\nheaders: {headers}\nparams: {params}\ndata: {body}")
            response=requests.put(url=url, headers=headers, params=params, data=body)
            return response
        except Exception as e:
            logging.error(f"{__name__}, line {getframeinfo(currentframe()).lineno}: {e}")
            raise e
        
    def _job_set_fields(self, job_uid, fields: json = None):
        headers = {"Content-Type": "application/json"}
        # schema = self.get_job_detail_schema()
        # validate(fields, schema=schema)
        encoded_url = f"{self.url_api}jobs/{job_uid}"
        return self._request_put(encoded_url, headers, None, fields)
    
    def job_delete(self, job_uid):
        encoded_url = f"{self.url_api}/jobs/{job_uid}"
        return self._request_delete(encoded_url, None, None, None)
    
    def job_set_status(self, job_uid, status):
        if status not in self._job_status.valid_values:
            raise ValueError(f"Invalid status: {status}. Valid status are: {JobStatus.valid_values}")
        body = dict(job_status=status)
        return self._job_set_fields(job_uid, body)

    def job_get_fields(self, job_uid, fields):
        encoded_url = f"{self.url_api}jobs/{job_uid}"
        self._request_get(encoded_url, None, fields)
        
    def jobs_get(self, job_status: list = None):
        encoded_url = f"{self.url_api}jobs"
        return self._request_get(encoded_url, None, job_status)
    
    def token_get_quota(self, token_uid):
        encoded_url = f"{self.url_api}tokens/{token_uid}"
        return self._request_get(encoded_url, None, dict(token_quota=None))

    def token_set_quota(self, token_uid, token_quota: int):
        encoded_url = f"{self.url_api}tokens/{token_uid}"
        return self._request_put(encoded_url, self._header_json, None, dict(token_quota=token_quota))
    
    
    
class Atlin(AtlinBase):
    def __init__(self, domain: str):
        super().__init__(domain)
        
    def job_get_detail_schema(self, **kwargs):
        raise NotImplementedError("Atlin")

class AtlinYoutube(AtlinBase):
    def __init__(self, domain: str):
        super().__init__(domain)
    
    def job_get_detail_schema(self, **kwargs):
        if "job_status"in kwargs.keys():
            job_status = kwargs["job_status"]
            if job_status not in self._job_status.valid_values:
                raise ValueError(f"{job_status} not in {self._job_status.valid_values}")
        else:
            job_status = self._job_status.created
        
        
        
        schema = schemas.schema_jobs_job_detail_get(self._job_platform.youtube, job_status)
        # if job_status == JobStatus.running:
        #     schema = {
        #         "type": "object",
        #         "properties" : {
        #             "current_quota": {"type": "number"},
        #             "quota_exceeded": {"type": "boolean"},
        #             "api_key_valid" : {"type": "boolean"},
        #             "videos_ids" : {"type": "array"},
        #             "comments_count" : {"type": "object"},
        #             "actions" : {"type": "array"},
        #             "all_videos_retrieved" : {"type": "boolean"},
        #             "all_comments_retrieved" : {"type": "boolean"},
        #             "error" : {"type": "boolean"},
        #             "error_description" : {"type": "string"},
        #         },
        #         "required": [],
        #     }
            
            
class AtlinReddit(AtlinBase):
    def __init__(self, domain: str):
        super().__init__(domain)
    
    def job_get_detail_schema(self, **kwargs):
        schemas.schema_jobs_job_detail_get("REDDIT", None)
        
    