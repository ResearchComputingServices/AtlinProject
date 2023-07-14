from AtlinAPI import JobStatus, JobPlatform, AtlinYoutube
import json

job_status = JobStatus()
job_platform = JobPlatform()

# valid values from test database
user_uid = "b1d93700-aee5-4eca-939d-cf8b866f2be4"
job_uid = "9978d901-96e6-4a80-bfec-3a7dd87d81ad"
token_uid = "dc3b1d6d-cbb9-41e5-8713-c7620bbbc21f"


atlin = AtlinYoutube("http://localhost:6010")

def extract_jobs(response):
    jobs = []
    if response.status_code == 200:
        jobs = response.json()
    return jobs 

def print_jobs(jobs):
    for job in jobs:
        print(json.dumps(job, indent=2))


# response = atlin.job_create(
#     user_uid,
#     token_uid,
#     job_status.created,
#     job_platform.youtube,
#     )

# GET all the jobs in the database #TODO not yet implemented in the backend.
response = atlin.job_get()
print_jobs( extract_jobs(response))
    
# GET only jobs with job_status = "CREATED"
response = atlin.job_get(job_status =[job_status.created])

# GET only jobs with job_status = "CREATED" or "PAUSED" TODO not implemented in backend.
response = atlin.job_get(job_status =[job_status.created, job_status.paused])
print_jobs( extract_jobs(response))

# GET job  by job_uid
# http://localhost:6010/api/v1/job/9978d901-96e6-4a80-bfec-3a7dd87d81ad
response = atlin.job_get_by_uid(job_uid)

# PUT - update the status of a job to running
response = atlin.job_set_status(job_uid, job_status.running)

# DEL - delete a job #TODO not working
response = atlin.job_delete(job_uid)

# GET - get quota #TODO not working - returning ''
response = atlin.token_get(token_uid)
if response.status_code == 200:
    try:
        quota = response.json()['token_quota']
    except Exception as e:
        print(f"Could not fetch token quota. {e}")
        
# PUT - set quota #TODO not returning the value not working
response = atlin.token_set_quota(token_uid, job_platform.youtube, 300)

print("Done")
#TODO Field for token: in_use?

