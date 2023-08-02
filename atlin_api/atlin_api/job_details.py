'''JobDetail'''
from abc import ABC
import logging

logger = logging.getLogger("JobDetail")

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
