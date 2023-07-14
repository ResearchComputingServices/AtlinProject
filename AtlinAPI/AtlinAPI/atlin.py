from abc import ABC, abstractmethod
from inspect import currentframe, getframeinfo
import requests
import urllib
import logging
import json
from jsonschema import validate
from . import atlin_schemas as schemas

logging.basicConfig(level=logging.DEBUG)

####################################################################################################
#
####################################################################################################

# ToDO: define class members before they are use
# ToDO: use "hints" to show expected arg types, and function return type

class JobStatus:
    def __init__(self) -> None:
        for item in schemas._valid_job_status:
            setattr(self, item.lower(), item)
        self.valid_values = schemas._valid_job_status

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class JobPlatform:
    def __init__(self):
        for item in schemas._valid_social_platforms:
            setattr(self, item.lower(), item)
        self.valid_values = schemas._valid_social_platforms

# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class Atlin(ABC):
    def __init__(self, 
                 domain: str):
        self._domain = domain if domain[-1] == '/' else f"{domain}/"
        self._apipath = "api/v1/"
    
    
    # ----------------------------------------------------------------------------------------------
    
    @property
    def url_api(self):
        return f"{self._domain}{self._apipath}"
        
    @abstractmethod
    def get_job_detail_schema(self, **kwargs):
        pass
    
    # ---------------------------------------------------------------------------------------------
    # ToDo: function should return True/False?
    # ToDo: only one return statement at the end of the func
    def _request_get(self, 
                     url, 
                     headers, 
                     params):
        try: 
            response = requests.get(url=url, 
                                    headers=headers, 
                                    params=params )
            return response
        except Exception as e:
            logging.error(f"{__file__} {__name__}: {e}")
            raise e
    
    # ---------------------------------------------------------------------------------------------
        
    def _request_put(self, 
                     url, 
                     headers, 
                     params, 
                     body):
        try: 
            logging.debug(f"Making a put request.\nurl: {url}\nheaders: {headers}\nparams: {params}\ndata: {body}")
            response=requests.put(url=url, headers=headers, params=params, data=body)
            return response
        except Exception as e:
            logging.error(f"{__name__}, line {getframeinfo(currentframe()).lineno}: {e}")
            raise e
    
    # ---------------------------------------------------------------------------------------------
        
    def _set_job_fields(self, 
                        job_uid, 
                        fields: json = {},):
        
        headers = {"Content-Type": "application/json"}
        # schema = self.get_job_detail_schema()
        # validate(fields, schema=schema)
        encoded_url = f"{self.url_api}jobs/{job_uid}"
        
        # Call next funtion in sequence
        return self._request_put(url = encoded_url, 
                                 headers = headers, 
                                 params = None, 
                                 body = fields)
    
    # ---------------------------------------------------------------------------------------------
    
    def set_job_status(self, 
                       job_uid, 
                       status):
        
        # Raise Exception if status invalid
        if status not in JobStatus().valid_values:
            raise ValueError(f"Invalid status: {status}. Valid status are: {JobStatus.valid_values}")
        
        # Create the Request Body
        body = dict(job_status=status)
        
        # Call next function in sequence
        return self._set_job_fields(job_uid = job_uid, 
                                    fields = body)

    # ---------------------------------------------------------------------------------------------

    def get_jobs_fields(self, 
                        job_uid, 
                        fields):
        
        # url for specific job with primary key "job_uid"
        encoded_url = f"{self.url_api}jobs/{job_uid}"
        
        self._request_get(url=encoded_url, 
                          headers=None, 
                          params=fields)
        
    # ---------------------------------------------------------------------------------------------    
    
    def get_jobs(self, 
                 job_status: list = None):
        
        # url at base of job resource
        encoded_url = f"{self.url_api}jobs"
        
        return self._request_get(url=encoded_url, 
                                 headers=None, 
                                 params=job_status)
            
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

class AtlinYoutube(Atlin):
    def __init__(self, domain: str):
        super().__init__(domain)
    
    def get_job_detail_schema(self, **kwargs):
        if "job_status"in kwargs.keys():
            job_status = kwargs["job_status"]
        else:
            job_status = JobStatus.created
        
        if job_status not in JobStatus.valid_values:
            raise ValueError(f"{job_status} not in {JobStatus.valid_values}")
        
        if job_status == JobStatus.running:
            schema = {
                "type": "object",
                "properties" : {
                    "current_quota": {"type": "number"},
                    "quota_exceeded": {"type": "boolean"},
                    "api_key_valid" : {"type": "boolean"},
                    "videos_ids" : {"type": "array"},
                    "comments_count" : {"type": "object"},
                    "actions" : {"type": "array"},
                    "all_videos_retrieved" : {"type": "boolean"},
                    "all_comments_retrieved" : {"type": "boolean"},
                    "error" : {"type": "boolean"},
                    "error_description" : {"type": "string"},
                },
                "required": [],
            }         
    
# ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
            
class AtlinReddit(Atlin):
    def __init__(self, 
                 domain: str):
        input(domain)
        super().__init__(domain)
    
    def get_job_detail_schema(self, **kwargs):
        schemas.schema_jobs_job_detail_get("REDDIT", None)
        
    