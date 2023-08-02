"""Test Atlin classes and methods."""
import json
from json.decoder import JSONDecodeError
from uuid import uuid4
import logging
from atlin_api import JobStatus, JobPlatform, Atlin, YoutubeToken
from atlin_api import YoutubeJobDetails
from atlin_api import Job

logging.basicConfig(level=logging.ERROR)


# valid values from test database
USER_UID = "b1d93700-aee5-4eca-939d-cf8b866f2be4"
# USER_UID = "b1d93700-aee5-4eca-939d-cf8b866f2be7"
# job_uid = "9ef8b11b-0d51-4303-ada0-111ed9f6fbaa"
# token_uid = "dc3b1d6d-cbb9-41e5-8713-c7620bbbc21f"


atlin = Atlin("http://localhost:6010")

token_yt = YoutubeToken()

token_yt.user_uid = USER_UID
token_yt.token_name = "Main token"

token_details_yt = {
    "api_token": str(uuid4()),
    "token_quota": 100,
    "modify_date": "",
}

token_yt.token_detail = token_details_yt

logging.info("YouTube token:\n%s", json.dumps(token_yt.to_dict(), indent=2))

response = atlin.token_create(token_details=token_yt.to_dict())
response.raise_for_status()
if response.status_code == 201:
    try:
        token_yt.from_json(response.json())
        logging.info("updated token:\n%s", json.dumps(token_yt.to_dict(), indent=2))
    except JSONDecodeError as exc:
        logging.error("invalid json response: %s", response.content)
        raise


response = atlin.token_get(user_uid=USER_UID)
response.raise_for_status()
if response:
    logging.debug("returned %s tokens for user %s", len(response.json()), USER_UID)


response = atlin.token_get(token_uid=token_yt.token_uid)
response.raise_for_status()
if response:
    logging.debug("returned token for id %s\n%s", token_yt.token_uid, response.json())


response = atlin.token_get(social_platform="YOUTUBE")
response.raise_for_status()
if response:
    logging.debug("got %s tokens for social_platform 'YOUTUBE'", len(response.json()))


token_yt.token_name = "New token name"
response = atlin.token_update(token_yt.token_uid, token_yt.to_dict())
response.raise_for_status()
if response:
    try:
        token_yt.from_json(response.json())
        logging.debug("Token name updated to '%s'", token_yt.token_name)
    except Exception as exc:
        logging.error("Could not update token details from json")
        raise exc

# Example of token deletion at the end.

TOKEN_QUOTA = 9213
response = atlin.token_set_quota(
    token_yt.token_uid, token_yt.social_platform, TOKEN_QUOTA
)
response.raise_for_status()
if response:
    try:
        assert response.json()["token_detail"]["token_quota"] == TOKEN_QUOTA
        logging.info(response.json())
    except JSONDecodeError as exc:
        logging.error(
            "token_set_quota did not return a json object.\n%s", response.content
        )
        raise exc


def extract_jobs(_response):
    """Extract jobs from response"""
    _jobs = []
    if _response.status_code == 200:
        _jobs = _response.json()
    return _jobs


def print_jobs(_jobs):
    """Print jobs"""
    for _job in _jobs:
        logging.debug(json.dumps(_job, indent=2))


# POST create a job
youtube_job_details = YoutubeJobDetails()

response = atlin.job_create(
    user_uid=USER_UID,
    token_uid=token_yt.token_uid,
    job_status=JobStatus.created,
    social_platform=JobPlatform.youtube,
    job_tag=["tag1", "tag2"],
    job_detail=youtube_job_details.to_dict()
)
response.raise_for_status()
if response:
    try:
        logging.debug("Job with uid %s created.",response.json()['job_uid'])
        logging.debug("%s", json.dumps(response.json(), indent=2))
        job = Job(response.json())
    except JSONDecodeError as exc:
        logging.error(
            "token_set_quota did not return a json object.\n%s", response.content
        )
        raise exc
    except Exception as exc:
        raise exc

# GET all the jobs in the database .
response = atlin.job_get()
print_jobs(extract_jobs(response))
response.raise_for_status()

# GET only jobs with job_status = "CREATED"
response = atlin.job_get(job_status=[JobStatus.created])
print_jobs(extract_jobs(response))
response.raise_for_status()

# GET only jobs with job_status = "CREATED" or "PAUSED"
response = atlin.job_get(job_status=[JobStatus.created, JobStatus.paused])
print_jobs(extract_jobs(response))
jobs = extract_jobs(response)
response.raise_for_status()

# GET job  by job_uid
# http://localhost:6010/api/v1/job/9978d901-96e6-4a80-bfec-3a7dd87d81ad
response = atlin.job_get_by_uid(jobs[0]["job_uid"])
response.raise_for_status()

print_jobs(extract_jobs(response))

job = Job(response.json())

# PUT - update the status of a job to running
response = atlin.job_set_status(job.job_uid, JobStatus.running)
job.from_json(response.json())
response.raise_for_status()

# PUT - update job
job.output_path = "/var/data"
response = atlin.job_update(job.job_uid, job.to_dict())
response.raise_for_status()
if response:
    job.from_json(response.json())

# GET - get quota
response = atlin.token_get(token_uid=job.token_uid)
response.raise_for_status()
if response.status_code == 200:
    try:
        quota = response.json()["token_detail"]["token_quota"]
    except AttributeError as exc:
        logging.debug("Could not fetch token quota. %s", exc)
        raise exc

# PUT - set quota
response = atlin.token_set_quota(job.token_uid, job.social_platform, 300)
response.raise_for_status()

response = atlin.token_delete(job.token_uid)
if response:
    logging.debug("Deleted token with token id %s", token_yt.token_uid)
response.raise_for_status()

# DEL - delete a job
response = atlin.job_delete(job.job_uid)
if response:
    logging.debug("Deleted job with job_uid '%s'", job.job_uid)
response.raise_for_status()
