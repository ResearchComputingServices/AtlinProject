"""Module used to call requests and build the data structures."""
from abc import ABC
from inspect import currentframe, getframeinfo
import logging
import json

# from uuid import uuid4, UUID
import requests


class JobStatus:
    """Job Status"""

    valid_values = ["CREATED", "RUNNING", "PAUSED", "FAILED", "SUCCESS"]
    created = "CREATED"
    running = "RUNNING"
    paused = "PAUSED"
    failed = "FAILED"
    success = "SUCCESS"


class JobPlatform:
    """Job Platform"""

    valid_values = ["YOUTUBE", "REDDIT"]
    youtube = "YOUTUBE"
    reddit = "REDDIT"


class AtlinBase(ABC):
    """Atlin Base used by Youtube and Reddit."""

    _timeout = 5

    def __init__(self, domain: str):
        self._domain = domain if domain[-1] == "/" else f"{domain}/"
        self._apipath = "api/v1/"
        self._job_status = JobStatus()
        self._job_platforms = JobPlatform()
        self._header_json = {"Content-Type": "application/json"}

    @property
    def url_api(self):
        """The url of the api"""
        return f"{self._domain}{self._apipath}"

    # @abstractmethod
    # def job_get_detail_schema(self, **kwargs):
    #     '''job_get_detail_schema will be deprecated.'''

    def _request_delete(self, url, headers, params, body):
        try:
            logging.debug(
                "Making a delete request.\nurl: %s\nheaders: %s\nparams: %s",
                url,
                headers,
                params,
            )
            response = requests.delete(
                url, params=params, headers=headers, json=body, timeout=self._timeout
            )
            return response
        except Exception as exception:
            logging.error("%s %s: %s", __file__, __name__, exception)
            raise exception

    def _request_get(self, url, headers, params):
        try:
            logging.debug(
                f"Making a get request.\nurl: {url}\nheaders:"
                + f" {headers}\nparams: {params}"
            )
            response = requests.get(
                url=url, headers=headers, params=params, timeout=self._timeout
            )
            return response
        except Exception as exception:
            logging.error("%s %s: %s", __file__, __name__, exception)
            raise exception

    def _request_put(self, url, headers, params, body):
        try:
            logging.debug(
                f"Making a put request.\nurl: {url}\nheaders: "
                + f"{headers}\nparams: {params}\ndata: {body}"
            )
            response = requests.put(
                url=url,
                headers=headers,
                params=params,
                json=body,
                timeout=self._timeout,
            )
            return response
        except Exception as exception:
            logging.error(
                "%s, line %s: %s",
                __name__,
                getframeinfo(currentframe()).lineno,
                exception,
            )
            raise exception

    def _request_post(self, url, headers, params, body):
        try:
            logging.debug(
                "Making a post request.\nurl: %sn"
                + "headers: %s\nparams: %s\ndata: %s",
                url,
                headers,
                params,
                body,
            )
            response = requests.post(
                url=url,
                headers=headers,
                params=params,
                json=body,
                timeout=self._timeout,
            )
            return response
        except Exception as exception:
            logging.error(
                "%s, line %s: %s",
                __name__,
                getframeinfo(currentframe()).lineno,
                exception,
            )
            raise exception

    def _job_set_fields(self, job_uid, fields: json = None):
        encoded_url = f"{self.url_api}job/{job_uid}"
        return self._request_put(encoded_url, self._header_json, None, fields)

    def job_create(
        self,
        *,
        user_uid,
        token_uid,
        job_status,
        social_platform,
        job_tag=None,
        output_path="",
        job_message="",
        job_detail=None,
    ):
        """Create a job"""
        if job_status not in self._job_status.valid_values:
            raise ValueError(
                f"{job_status} is not a valid status ({', '.join(self._job_status.valid_values)})"
            )

        if social_platform not in self._job_platforms.valid_values:
            raise ValueError(
                f"{social_platform} is not a valid social platform"
                + f"({', '.join(self._job_platforms.valid_values)})"
            )

        if job_tag is None:
            job_tag = []
        if not isinstance(job_tag, list):
            raise TypeError(f"{job_tag} should be a list of strings.")
        job_tag = ",".join(job_tag)

        body = {
            "user_uid": user_uid,
            "token_uid": token_uid,
            "job_status": job_status,
            "social_platform": social_platform,
            "job_tag": job_tag,
            "output_path": output_path,
            "job_message": job_message,
            "job_detail": job_detail,
        }

        encoded_url = f"{self.url_api}job"
        return self._request_post(encoded_url, self._header_json, None, body=body)

    def job_update(self, job_uid, data):
        """Updates a job"""
        encoded_url = f"{self.url_api}job/{job_uid}"
        return self._request_put(encoded_url, None, None, data)

    def job_delete(self, job_uid):
        """Deletes a job given a job_uid"""
        encoded_url = f"{self.url_api}job/{job_uid}"
        return self._request_delete(encoded_url, None, None, None)

    def job_get(
        self,
        *,
        user_uid: list = None,
        social_platform: list = None,
        job_status: list = None,
    ):
        """get jobs"""
        params = {}

        for varname, var in zip(
            ["user_uid", "social_platform", "job_status"],
            [user_uid, social_platform, job_status],
        ):
            if var is not None:
                if not isinstance(var, list):
                    raise TypeError(f"{var} should be a list.")
                params[varname] = ",".join(var)

        if not params:
            params = None

        encoded_url = f"{self.url_api}job"
        return self._request_get(encoded_url, self._header_json, params)

    def job_get_by_uid(self, job_uid):
        """Get job by job_uid"""
        encoded_url = f"{self.url_api}job/{job_uid}"
        return self._request_get(encoded_url, None, None)

    def job_set_status(self, job_uid, job_status):
        """Set job status"""
        if job_status not in self._job_status.valid_values:
            raise ValueError(
                f"Invalid status: {job_status}. Valid status are: {JobStatus.valid_values}"
            )
        encoded_url = f"{self.url_api}job/status/{job_uid}"
        body = dict(job_status=job_status)
        return self._request_put(encoded_url, None, None, body)

    def token_get(
        self,
        *,
        user_uid: str = None,
        social_platform: str = None,
        token_uid: str = None,
    ):
        """get token"""
        params = None
        if token_uid is None:
            params = {}
            if user_uid is not None:
                params["user_uid"] = user_uid
            if social_platform is not None:
                params["social_platform"] = social_platform
            if not params:
                params = None
            encoded_url = f"{self.url_api}token"
        else:
            encoded_url = f"{self.url_api}token/{token_uid}"
        return self._request_get(encoded_url, self._header_json, params=params)

    def token_update(self, token_uid: str, token_details: dict):
        """update token"""
        encoded_url = f"{self.url_api}token/{token_uid}"
        return self._request_put(encoded_url, None, None, token_details)

    def token_delete(self, token_uid: str):
        """Delete token by token_uid"""
        encoded_url = f"{self.url_api}token/{token_uid}"
        return self._request_delete(encoded_url, None, None, None)

    def token_create(self, *, token_details: dict):
        """create token given with token_details"""
        encoded_url = f"{self.url_api}token"
        return self._request_post(encoded_url, None, None, token_details)

    def token_set_quota(self, token_uid, social_platform: str, token_quota: int):
        """Set token quota"""
        encoded_url = f"{self.url_api}token/quota/{token_uid}"
        if social_platform not in JobPlatform().valid_values:
            raise ValueError(
                f"invalid social platform {social_platform}. "
                + f"Valid values are {','.join(JobPlatform().valid_values)}"
            )
        body = dict(token_quota=token_quota, social_platform=social_platform)
        return self._request_put(encoded_url, self._header_json, None, body=body)


class Atlin(AtlinBase):
    """Atlin"""


class AtlinYoutube(AtlinBase):
    """Atlin Youtube"""


class AtlinReddit(AtlinBase):
    """Atlin Reddit"""
