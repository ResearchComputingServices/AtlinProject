from AtlinAPI import JobStatus, AtlinYoutube

job_status = JobStatus()
job_uid = 123456789
token_uid = 24681379
atlin = AtlinYoutube("http://localhost:5000")

# GET all the jobs in the database
response = atlin.jobs_get()
if response.status_code == 200:
    jobs = response.json()
    
# GET only jobs with job_status = "CREATED" or "PAUSED"
response = atlin.jobs_get(job_status = dict(status=[job_status.created, job_status.paused] ))

# GET - get fields of a job (social_platform and job_details)
atlin.job_get_fields(job_uid, dict(social_platform="", job_details=""))

# PUT - update the status of a job to running
atlin.job_set_status(job_uid, job_status.running)

# DEL - delete a job
atlin.job_delete(job_uid)

# GET - get quota 
response = atlin.token_get_quota(token_uid)
if response.status_code == 200:
    quota = response.json()['token_quota']

# PUT - set quota
response = atlin.token_set_quota(token_uid, 300)

#TODO Field for token: in_use?

