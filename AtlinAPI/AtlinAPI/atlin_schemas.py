
_valid_social_platforms = ["YOUTUBE", "REDDIT"]
_valid_job_status = ["CREATED", "RUNNING", "PAUSED", "FAILED", "SUCCESS"]

def schema_token_put():
    return {
        "type" : "object",
        "properties": {
            "social_platform" : {"enum": _valid_social_platforms},
            "token_quota" : {"type": "number"},
        },
        "required": ["social_platform"],
    }

def schema_jobs_get(social_platform = None, job_status = None):
    job_details = schema_jobs_job_detail_get(social_platform=social_platform, job_status=job_status)
    token_detail = schema_jobs_token_details_get()
    schema =  {
        "type": "array",
        "items": {
            "type": "object",
            "properties": {
                "job_uid": {"type": "number"},
                "token_uid": {"type": "number"},
                "token_detail": token_detail,
                "job_status": {"enum": _valid_job_status},
                "social_platform": {"enum": _valid_social_platforms},
                "output_path": {"type": "string"},
                "job_detail": job_details,
            },
            "required": [
                "job_uid", 
                "token_uid", 
                "token_detail",
                "job_status",
                "social_platform",
                "output_path",
                "job_detail"],
        }
    }
    # schema ["job_detail"] = 
    return schema

def schema_jobs_job_detail_get(social_platform, job_status):
    schema = {"type": "object"}
    # if social_platform == "REDDIT":
        
    # elif social_platform == "YOUTUBE":
    return schema

def schema_jobs_token_details_get (social_platform):
    if social_platform == "YOUTUBE":
        schema = {
            "type": "object",
            "properties": {
                "api_token": "string",
                "token_quota": "number",
                "modified_date": "string",
            },
            "required": ["api_token", "token_quota", "modified_quota_timestamp"]
        }
    elif social_platform == "REDDIT":
        schema = {
            "type": "object",
            "properties": {
                "client_id": {"type": "string"},
                "secret_token": {"type": "string"},
                "username": {"type": "string"},
                "password": {"type": "string"},
                "token_quota": "number",
                "modified_quota_timestamp": "string",
            },
            "required": ["client_id", "secret_token","username", "password", "token_quota", "modified_quota_timestamp"]
        }
    else:
        raise ValueError("Invalid social platform")
    return schema


def schema_token_put():
    schema = {
        "type": "object",
        "properties" : {
            
        }
    }
if __name__ == "__main__":
    from jsonschema import validate
    import json
    
    validate(
        dict(social_platform="YOUTUBE"),
        schema_token_put()
    )
    
    validate(
        [{
            "job_uid": 10293,
            "token_uid": 12343,
            "token_detail": {},
            "job_status": "CREATED",
            "social_platform": "YOUTUBE",
            "output_path": "",
            "job_detail": {},
        }],
        schema_jobs_get()
    )
    
    