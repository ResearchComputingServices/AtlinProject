from abc import ABC, abstractmethod
from inspect import currentframe, getframeinfo
import requests
import urllib
import logging
import json
from jsonschema import validate
from . import atlin_schemas as schemas
import time
from uuid import uuid4, UUID

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
            response = requests.delete(url, params=params, headers=headers, json=body)
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
            response=requests.put(url=url, headers=headers, params=params, json=body)
            return response
        except Exception as e:
            logging.error(f"{__name__}, line {getframeinfo(currentframe()).lineno}: {e}")
            raise e
    
    def _request_post(self, url, headers, params, body):
        try: 
            logging.debug(f"Making a post request.\nurl: {url}\nheaders: {headers}\nparams: {params}\ndata: {body}")
            response=requests.post(url=url, headers=headers, params=params, json=body)
            return response
        except Exception as e:
            logging.error(f"{__name__}, line {getframeinfo(currentframe()).lineno}: {e}")
            raise e
        
    def _job_set_fields(self, job_uid, fields: json = None):
        encoded_url = f"{self.url_api}job/{job_uid}"
        return self._request_put(encoded_url, self._header_json, None, fields)
    
    def job_create(self,
                user_uid,
                token_uid,
                job_status,
                social_platform,
                job_tag = [],
                output_path = '',
                job_message = '',
                job_detail = {}):
        #TODO
        if job_status not in self._job_status.valid_values:
            raise ValueError(f"{job_status} is not a valid status ({', '.join(self._job_status.valid_values)})")
        
        if social_platform not in self._job_platforms.valid_values:
            raise ValueError(f"{social_platform} is not a valid social platform ({', '.join(self._job_platforms.valid_values)})")
        
        if not isinstance(job_tag, list):
            raise TypeError(f"{job_tag} should be a list of strings.")
        job_tag = ",".join(job_tag)
        
        body = dict(
            user_uid = user_uid,
            token_uid = token_uid,
            job_status = job_status,
            social_platform = social_platform,
            job_tag = job_tag,
            output_path = output_path,
            job_message = job_message,
            job_detail = job_detail,
        )
        
        encoded_url = f"{self.url_api}job"
        return self._request_post(encoded_url, self._header_json, None, body=body)
        
        # raise NotImplementedError()
        # encoded_url = f"{self.url_api}job"
        # print(locals())
        # return self._request_post(encoded_url, self._header_json, None, )
    
    def job_update(self, job_uid, data):
        encoded_url = f"{self.url_api}job/{job_uid}"
        return self._request_put(encoded_url, None, None, data)
        
    
    def job_delete(self, job_uid):
        encoded_url = f"{self.url_api}job/{job_uid}"
        return self._request_delete(encoded_url, None, None, None)
    
    def job_get(self, user_uid: list = None, social_platform: list = None, job_status: list =None):
        params = dict()
        loc = locals()
        
        for var in ["user_uid", "social_platform", "job_status"]:
            if loc[var] is not None:
                if not isinstance(loc[var], list):
                    raise TypeError(f"{loc[var]} should be a list.")
                params[var] = ",".join(loc[var])
        
        if params == {}:
            params = None
        
        encoded_url = f"{self.url_api}job"
        return self._request_get(encoded_url, self._header_json, params)
    
    def job_get_by_uid(self, job_uid):
        encoded_url = f"{self.url_api}job/{job_uid}"
        return self._request_get(encoded_url, None, None)
    
    def job_set_status(self, job_uid, job_status):
        if job_status not in self._job_status.valid_values:
            raise ValueError(f"Invalid status: {job_status}. Valid status are: {JobStatus.valid_values}")
        encoded_url = f"{self.url_api}job/status/{job_uid}"
        body = dict(job_status=job_status)
        return self._request_put(encoded_url, None, None, body)
    
    def token_get(self,
                  user_uid : str = None,
                  social_platform: str = None, 
                  token_uid: str = None):
        params = None
        if token_uid is None:
            params={}
            if user_uid is not None: 
                params["user_uid"] = user_uid
            if social_platform is not None: 
                params["social_platform"] = social_platform
            if params == {}:
                params = None
            encoded_url = f"{self.url_api}token"
        else:
            encoded_url = f"{self.url_api}token/{token_uid}"
        return self._request_get(encoded_url, self._header_json, params=params)

    def token_update(self, token_uid: str, token_details: dict):
        encoded_url = f"{self.url_api}token/{token_uid}"
        return self._request_put(encoded_url, None, None, token_details)
    
    def token_delete(self, token_uid: str):
        encoded_url = f"{self.url_api}token/{token_uid}"
        return self._request_delete(encoded_url, None, None, None)
    
    def token_create(self, user_uid:str, token_details: dict):
        encoded_url = f"{self.url_api}token"
        return self._request_post(encoded_url, None, None, token_details)
    
    def token_set_quota(self, token_uid, social_platform: str, token_quota: int):
        encoded_url = f"{self.url_api}token/quota/{token_uid}"
        if social_platform not in JobPlatform().valid_values:
            raise ValueError(f"invalid social platform {social_platform}. Valid values are {','.join(JobPlatform().valid_values)}")
        body = dict(token_quota = token_quota, social_platform = social_platform)
        return self._request_put(encoded_url, self._header_json, None, body=body)
    
    
    
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
        return schema
           
class AtlinReddit(AtlinBase):
    def __init__(self, domain: str):
        super().__init__(domain)
    
    def job_get_detail_schema(self, **kwargs):
        schemas.schema_jobs_job_detail_get("REDDIT", None)
        
    