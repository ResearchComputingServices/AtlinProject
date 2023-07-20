from AtlinAPI import JobStatus, JobPlatform, AtlinYoutube, YoutubeToken
from AtlinAPI import YoutubeJobDetails
from AtlinAPI import Job

import json

job_status = JobStatus()
job_platform = JobPlatform()

# valid values from test database
user_uid = "b1d93700-aee5-4eca-939d-cf8b866f2be4"
# job_uid = "9ef8b11b-0d51-4303-ada0-111ed9f6fbaa"
# token_uid = "dc3b1d6d-cbb9-41e5-8713-c7620bbbc21f"


atlin = AtlinYoutube("http://localhost:6010")

token_yt = YoutubeToken()

token_yt.user_uid = user_uid
token_yt.token_name = "Main token"

token_details_yt = dict(
    api_token = "api_token_sample",
    token_quota = 100,
    modify_date = "",
)

token_yt.token_detail = token_details_yt

print(token_yt.to_json())

response = atlin.token_create(token_yt.token_uid, token_yt.to_dict())

if response.status_code == 201:
    token_yt.from_json(response.json())
    print(token_yt.to_dict())
else: 
    raise response.raise_for_status()

response = atlin.token_get(user_uid = user_uid)
if response:
    print(f"returned {len(response.json())} tokens for user {user_uid}")
response.raise_for_status()

response = atlin.token_get(token_uid = token_yt.token_uid)
if response:
    print(f"returned token for id {token_yt.token_uid}\n{response.json()}")
response.raise_for_status()

response = atlin.token_get(social_platform="YOUTUBE")
if response:
    print(f"got {len(response.json())} tokens for social_platform 'YOUTUBE'")
response.raise_for_status()

token_yt.token_name = "New token name"
response = atlin.token_update(token_yt.token_uid, token_yt.to_dict())
if response.ok:
    token_yt.from_json(response.json())
    print(f"Token name updated to '{token_yt.token_name}'")
response.raise_for_status()

# Example of token deletion at the end.

response = atlin.token_set_quota(token_yt.token_uid, token_yt.social_platform, 9213)
if response:
    print(response.json())
response.raise_for_status()

def extract_jobs(response):
    jobs = []
    if response.status_code == 200:
        jobs = response.json()
    return jobs 

def print_jobs(jobs):
    for job in jobs:
        print(json.dumps(job, indent=2))


# POST create a job
youtube_job_details = YoutubeJobDetails()

response = atlin.job_create(
    user_uid = user_uid,
    token_uid = token_yt.token_uid,
    job_status = job_status.created,
    social_platform = job_platform.youtube,
    job_tag = ["tag1", "tag2"],
    job_detail = youtube_job_details.to_dict(),
    # token_uid,
    # job_status.created,
    # job_platform.youtube,
    )
if response:
    print(f"Job with uid {response.json()['job_uid']} created.")
    print(json.dumps(response.json(), indent=2))
    job = Job(response.json())
response.raise_for_status()

# GET all the jobs in the database .
response = atlin.job_get()
print_jobs( extract_jobs(response))
response.raise_for_status()

# GET only jobs with job_status = "CREATED"
response = atlin.job_get(job_status =[job_status.created])
print_jobs( extract_jobs(response))
response.raise_for_status()

# GET only jobs with job_status = "CREATED" or "PAUSED" 
response = atlin.job_get(job_status =[job_status.created, job_status.paused])
print_jobs( extract_jobs(response))
jobs = extract_jobs(response)
response.raise_for_status()

# GET job  by job_uid
# http://localhost:6010/api/v1/job/9978d901-96e6-4a80-bfec-3a7dd87d81ad
response = atlin.job_get_by_uid(jobs[0]['job_uid'])
response.raise_for_status()

print_jobs( extract_jobs(response))

job = Job(response.json())

# PUT - update the status of a job to running
response = atlin.job_set_status(job.job_uid, job_status.running)
job.from_json(response.json())
response.raise_for_status()

# GET - get quota
response = atlin.token_get(job.token_uid)
if response.status_code == 200:
    try:
        quota = response.json()['token_detail']['token_quota']
    except Exception as e:
        print(f"Could not fetch token quota. {e}")
response.raise_for_status()
        
# PUT - set quota 
response = atlin.token_set_quota(job.token_uid, job.social_platform, 300)
response.raise_for_status()

response = atlin.token_delete(job.token_uid)
if response:
    print(f"Deleted token with token id {token_yt.token_uid}")
response.raise_for_status()

# DEL - delete a job
response = atlin.job_delete(job.job_uid)
if response:
    print(f"Deleted job with job_uid '{job.job_uid}'")
response.raise_for_status()

pass