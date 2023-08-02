"""Job related classes"""
from abc import ABC
import json
from json.decoder import JSONDecodeError
import os
import logging
from uuid import UUID, uuid4
from .youtube import YoutubeJobDetails
from .atlin import JobStatus, JobPlatform


logger = logging.getLogger("Job")


class Job:
    """Job encodes and decodes the job structure"""

    _required_fields = {
        "job_uid": str,
        "user_uid": str,
        "token_uid": str,
        "job_name": str,
        "job_tag": str,
        "job_status": str,
        "social_platform": str,
        "create_date": str,
        "modify_date": str,
        "complete_date": str,
        "output_path": str,
        "job_message": str,
        "job_detail": str,
    }

    def __init__(self, data: dict = None) -> None:
        if data is not None:
            self.from_json(data)

    def _validate_string(self, varname, value):
        if not isinstance(value, str):
            raise TypeError(f"value of {varname} should be of type string")

    def _validate_uid(self, value):
        UUID(value)

    def _get_date(self):
        # TODO
        return ""

    @property
    def job_uid(self):
        """unique id of a job. It is being sent, but values are changed by the backend."""
        return getattr(self, "_job_uid", str(uuid4()))

    @job_uid.setter
    def job_uid(self, value):
        self._validate_uid(value)
        setattr(self, "_job_uid", value)

    @property
    def user_uid(self):
        """unique id of the user"""
        return getattr(self, "_user_uid", str(uuid4()))

    @user_uid.setter
    def user_uid(self, value):
        self._validate_uid(value)
        setattr(self, "_user_uid", value)

    @property
    def token_uid(self):
        """unique id of token"""
        return getattr(self, "_token_uid", str(uuid4))

    @token_uid.setter
    def token_uid(self, value):
        self._validate_uid(value)
        setattr(self, "_token_uid", value)

    @property
    def job_name(self):
        """name of the job"""
        return getattr(self, "_job_name", "")

    @job_name.setter
    def job_name(self, value):
        if value is None:
            value = ""
        self._validate_string("job_name", value)
        setattr(self, "_job_name", value)

    @property
    def job_tag(self):
        """job tag"""
        return getattr(self, "_job_tag", "")

    @job_tag.setter
    def job_tag(self, value: list[str]):
        if isinstance(value, list):
            value = ",".join(value)
        setattr(self, "_job_tag", value)

    @property
    def job_status(self):
        """job status"""
        return getattr(self, "_job_status", "CREATED")

    @job_status.setter
    def job_status(self, value: str):
        if value not in JobStatus.valid_values:
            raise ValueError(
                f"'{value}' is not a valid job status."
                + f"Valid status are: {', '.join(JobStatus.valid_values)}"
            )
        setattr(self, "_job_status", value)

    @property
    def social_platform(self):
        """social platform"""
        return getattr(self, "_social_platform", "YOUTUBE")

    @social_platform.setter
    def social_platform(self, value):
        if value not in JobPlatform.valid_values:
            raise ValueError(
                f"'{value}' is not a valid social_platform."
                + f"Valid values are: {', '.join(JobPlatform.valid_values)}"
            )
        setattr(self, "_social_platform", value)

    @property
    def create_date(self):
        "date created"
        return getattr(self, "_create_date", self._get_date())

    @create_date.setter
    def create_date(self, value):
        setattr(self, "_create_date", value)

    @property
    def modify_date(self):
        """modify date"""
        return getattr(self, "_modify_date", self._get_date())

    @modify_date.setter
    def modify_date(self, value):
        setattr(self, "_modify_date", value)

    @property
    def complete_date(self):
        """complete date"""
        return getattr(self, "_complete_date", "")

    @complete_date.setter
    def complete_date(self, value):
        # TODO validate date
        setattr(self, "_complete_date", value)

    @property
    def output_path(self):
        """output path"""
        return getattr(self, "_output_path", "")

    @output_path.setter
    def output_path(self, value):
        if not isinstance(value, str):
            raise TypeError(f"output_path should be a string, not a {type(value)}")
        if value != "":
            if not os.path.exists(value):
                logger.warning("output_path %s does not exist", value)
        setattr(self, "_output_path", value)

    @property
    def job_message(self):
        """job message"""
        return getattr(self, "_job_message", "")

    @job_message.setter
    def job_message(self, value):
        self._validate_string("job_message", value)
        setattr(self, "_job_message", value)

    @property
    def job_detail(self):
        """job_detail"""
        return getattr(self, "_job_detail", {})

    @job_detail.setter
    def job_detail(self, value):
        if isinstance(value, str):
            try:
                value = json.loads(value)
            except JSONDecodeError as exception:
                logger.error("could not decode json for %s", value)
                raise exception
        elif isinstance(value, dict):
            pass
        else:
            # try to convert the job details if it is an object
            try:
                value = value.to_dict()
            except AttributeError as exc:
                logger.warning(
                    "Tried to convert object to dictionary without success. %s", exc
                )

        if self.social_platform == "YOUTUBE":
            value = YoutubeJobDetails(data=value)
        elif self.social_platform == "REDDIT":
            raise NotImplementedError("Reddit job details not implemented.")

        setattr(self, "_job_detail", value)

    def to_dict(self):
        """convert object to dictionary"""
        if isinstance(self.job_detail, dict):
            job_detail = self.job_detail
        else:
            try:
                job_detail = self.job_detail.to_dict()
            except Exception as exc:
                logger.error("to_dict: Invalid job_detail")
                raise exc

        return {
            'job_uid': getattr(self, "job_uid"),
            'user_uid': getattr(self, "user_uid"),
            'token_uid': getattr(self, "token_uid"),
            'job_name': getattr(self, "job_name"),
            'job_tag': getattr(self, "job_tag"),
            'job_status': getattr(self, "job_status"),
            'social_platform': getattr(self, "social_platform"),
            'create_date': getattr(self, "create_date"),
            'modify_date': getattr(self, "modify_date"),
            'complete_date': getattr(self, "complete_date"),
            'output_path': getattr(self, "output_path"),
            'job_message': getattr(self, "job_message"),
            'job_detail': job_detail,
        }

    def to_json(self):
        """convert object to json"""
        return json.dumps(self.to_dict())

    def from_json(self, data):
        """populates all variables from json data"""
        if not all(key in data.keys() for key in self._required_fields):
            raise ValueError("Missing Key!")

        if isinstance(data, str):
            data = json.loads(data)

        for key in data.keys():
            setattr(self, key, data[key])


class JobDetail(ABC):
    """holds the base structure for jobdetails"""

    def __init__(
        self, *, job_name: str = None, job_submit: dict = None, job_resume: dict = None
    ) -> None:
        if job_name is not None:
            setattr(self, "job_name", job_name)
        if job_submit is not None:
            setattr(self, "job_submit", job_submit)
        if job_resume is not None:
            setattr(self, "job_resume", job_resume)

    @property
    def job_name(self):
        """job name"""
        return getattr(self, "_job_name", "")

    @job_name.setter
    def job_name(self, value):
        if not isinstance(value, str):
            raise TypeError(
                f"job_name should be a string, but {type(value)} was provided."
            )
        setattr(self, "_job_name", value)

    @property
    def job_details(self):
        """job details"""
        return getattr(self, "_job_details", {})

    @job_details.setter
    def job_details(self, value):
        if isinstance(value, dict):
            setattr(self, "_job_details", value)
        else:
            try:
                setattr(self, "_job_details", value.to_dict())
            except AttributeError as exc:
                logger.error(("Could not convert value to dictionary. %s}", value))
                raise exc

    @property
    def job_resume(self):
        """job resume"""
        return getattr(self, "_job_resume", {})

    @job_resume.setter
    def job_resume(self, value):
        if isinstance(value, dict):
            setattr(self, "_job_details", value)
        else:
            try:
                setattr(self, "_job_details", value.to_dict())
            except AttributeError as exc:
                logger.error(("Could not convert value to dictionary. %s}", value))
                raise exc
