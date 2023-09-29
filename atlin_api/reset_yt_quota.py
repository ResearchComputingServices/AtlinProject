import atlin_api.atlin as atlinAPI
import Config as config

atlin = atlinAPI.Atlin(config.ATLIN_API_ADDRESS)

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
