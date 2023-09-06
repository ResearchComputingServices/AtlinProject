import atlin_api.atlin as atlinAPI


# valid values from test database
user_uid = "b1d93700-aee5-4eca-939d-cf8b866f2be4"
# job_uid = "9ef8b11b-0d51-4303-ada0-111ed9f6fbaa"
atlin = atlinAPI.Atlin("http://localhost:6010")

#Let's get all tokens in the DB


def reset_Youtube_quota():
        social_platform = "YOUTUBE"
        response = atlin.token_get(social_platform=social_platform)
        if response:
            print(f"got {len(response.json())} tokens for social_platform 'YOUTUBE'")
        response.raise_for_status()
        tokens = response.json()

        quota = 0
        for token in tokens:
            try:
                response = atlin.token_set_quota(token["token_uid"], "YOUTUBE", quota)
            except Exception as e:
                print(f"Could not update token quota. {e}")




reset_Youtube_quota()
