from Tools.YouTubeAPI.youtube.youtube import *
from Tools.YouTubeAPI.youtube.utils import save_file
import sys
import json

#*****************************************************************************************************
#Gets the API key from the config file
#*****************************************************************************************************
def get_api_key():
    try:
        with open('api_key.json') as client_secrets_file:
            client_secrets = json.load(client_secrets_file)
        if client_secrets:
            return client_secrets["key"]
        else:
            return None
    except:
        print("File api_key.json couldn't be loaded. Please verify this file.")
    return None




##########################################################################################################
api_key = get_api_key()
quota = 0
yt = Youtube(api_key, quota)

#state = yt.state.load_state_from_file("output","state.pkl")
#yt.state.from_dict_to_state(state)

if not yt.service:
    print ("The YouTube service was not created. Verify the API key or the quota usage has been exceeded")
    print (yt.state.error_description)
    sys.exit()




option="network"   #["playlist" "query" "file" "network"]
action ="comments" #["metadata" "comments"]
output_file = "test.xlsx"


#Video url
if option == "video":
    url = "https://www.youtube.com/watch?v=ZU_wbPigVRI"
    if action == "metadata":
        r =yt.get_video_metadata_for_url(url)
        save_file(yt.videos.video_records, "output", output_file)
    else:
        r= yt.get_video_comments_for_url(url)
        #save_file(yt.comments.comments_records,"output", output_file)
    print ("# of records: {}".format(len(r)))

if option == "playlist":
    url = "https://www.youtube.com/playlist?list=PLADighMnAG4DczAOY7i6-nJhB9sQDhIoR"
    #url = "https://www.youtube.com/playlist?list=PLADighola"


    if action == "metadata":
        r= yt.get_videos_metadata_from_playlist(url)
        #save_file(yt.videos.video_records, "output", output_file)
    else:
        r= yt.get_videos_comments_from_playlist(url)
        #save_file(yt.comments.comments_records,"output", output_file)

    print("# of records: {}".format(len(r)))

if option == "file":
    file_location = "output/ottawa_search_ids.xlsx"
    if action == "metadata":
        r = yt.get_videos_metadata_from_file(file_location)
        #save_file(yt.videos.video_records, "output", output_file)
    else:
        r = yt.get_videos_comments_from_file(file_location)
        #save_file(yt.comments.comments_records,"output", output_file)

    print("# of records: {}".format(len(r)))

if option == "query":
    query = "ottawa smoke"
    videos = 50
    if action == "metadata":
        r = yt.get_videos_metadata_from_query(query,videos)
        #save_file(yt.videos.video_records, "output", output_file)
    else:
        r = yt.get_videos_comments_from_query(query, videos)
        #save_file(yt.comments.comments_records,"output", output_file)

    print("# of records: {}".format(len(r)))

#yt.state.save_state_to_file("output", "state.pkl")


print ("Your current quota usage is: ")
print (yt.state.current_quota)

