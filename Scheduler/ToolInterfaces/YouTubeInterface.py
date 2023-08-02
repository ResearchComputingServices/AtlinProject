import sqlite3
from Tools.YouTubeAPI.youtube.youtube import *
import traceback
import Tools.YouTubeAPI.youtube.utils as utils
from Tools.YouTubeAPI.youtube.setup_logger import logger
from atlin_api.atlin_api import YoutubeJobDetails
import Tools.YouTubeAPI.youtube.config as config
import atlin_api.atlin_api.atlin as atlinAPI
import atlin_api.atlin_api.job as atlinJob
import atlin_api.atlin_api.token as atlinToken
from pathlib import Path
import os

BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUT_DIR="OUTPUT_DATA"
class AtlinYouTubeJob(atlinAPI.Atlin):
    def __init__(self, domain: str):
        super().__init__(domain)
        self.token = atlinToken.YoutubeToken()
        self.job = atlinJob.Job()

####################################################################################################
def validate_output_dir(output_dir):

    if output_dir==None or len(output_dir)==0:
        output_dir= os.path.join(BASE_DIR, OUTPUT_DIR)

    #Check if the output directory exists, it if doesn't create it.
    if not os.path.isdir(output_dir):
        os.mkdir(output_dir)

    #Update database with output folder
    atlin_yt_job.job.output_path = output_dir
    response = atlin_yt_job.job_update(job_uid=atlin_yt_job.job.job_uid, data=atlin_yt_job.job.to_dict())

    return output_dir

####################################################################################################
def load_job_state(state):
    try:
        state.quota_exceeded = atlin_yt_job.job.job_detail.job_resume.quota_exceeded
        state.api_key_valid = atlin_yt_job.job.job_detail.job_resume.api_key_valid
        state.videos_ids = atlin_yt_job.job.job_detail.job_resume.videos_ids
        state.comments_count = atlin_yt_job.job.job_detail.job_resume.comments_count
        state.actions = atlin_yt_job.job.job_detail.job_resume.actions
        state.all_videos_retrieved = atlin_yt_job.job.job_detail.job_resume.all_videos_retrieved
        state.all_comments_retrieved = atlin_yt_job.job.job_detail.job_resume.all_comments_retrieved
        state.error = atlin_yt_job.job.job_detail.job_resume.error
        state.error_description = atlin_yt_job.job.job_detail.job_resume.error_description = state.error_description
    except:
        logger.debug("An error occurred when loading the state")
        ex = traceback.format_exc()
        logger.debug(ex)
        #TODO: Log the exception
    return state


####################################################################################################
def save_job_state(state):

    job_status_completed = atlinAPI.JobStatus()
    job_status_completed = job_status.success
    try:
        youtube_job_details = YoutubeJobDetails()
        youtube_job_details.job_submit = atlin_yt_job.job.job_detail.job_submit
        youtube_job_details.job_resume.current_quota = state.current_quota
        youtube_job_details.job_resume.quota_exceeded = state.quota_exceeded
        youtube_job_details.job_resume.api_key_valid = state.api_key_valid
        youtube_job_details.job_resume.videos_ids = state.videos_ids
        youtube_job_details.job_resume.comments_count = state.comments_count
        youtube_job_details.job_resume.actions = state.actions
        youtube_job_details.job_resume.all_videos_retrieved = state.all_videos_retrieved
        youtube_job_details.job_resume.all_comments_retrieved = state.all_comments_retrieved
        youtube_job_details.job_resume.error = state.error
        youtube_job_details.job_resume.error_description = state.error_description

        atlin_yt_job.job.job_detail = youtube_job_details.to_dict()

        response = atlin_yt_job.job_update(job_uid=atlin_yt_job.job.job_uid, data=atlin_yt_job.job.to_dict())
        if response.status_code != 200:
            job_status_completed = job_status.failed
    except:
        ex = traceback.format_exc()
        logger.debug("An error occurred when saving the state")
        logger.debug(ex)
        #TODO: Log the exception

    return job_status_completed



####################################################################################################
def change_job_status(new_job_status):
    response = atlin_yt_job.job_set_status(job_uid=atlin_yt_job.job.job_uid, job_status=new_job_status)
    atlin_yt_job.job.job_status = new_job_status
    if response.status_code != 200:
        #ToDo: Handle this scenario
        return response.status_code

####################################################################################################
#
####################################################################################################
def handle_state(yt):
    logger.debug("Handle state")
    job_status_completed = atlinAPI.JobStatus()
    #SUCCESS
    if len(yt.state.actions)==0:
        change_job_status(job_status.success)
        job_status_completed = job_status.success
    else:
        if yt.state.quota_exceeded:
            change_job_status(job_status.paused)
            job_status_completed = job_status.paused
            save_job_state(yt.state)
            #ToDo: Update Job Message in DB
        else:
            #change_job_status(job_status.failed)
            job_status_completed = job_status.failed
            #job_status_completed = save_job_state(yt.state)
            #ToDo JobMessage = yt.state.error_description

    #Save the quota
    updated_quota = yt.state.current_quota
    response = atlin_yt_job.token_set_quota(atlin_yt_job.token.token_uid, job_platform.youtube, updated_quota)
    if response.status_code!=200:
        print ("Report error to scheduler")

    return job_status_completed


####################################################################################################
#
####################################################################################################
#def handle_new_job(jobDict, api_token, quota, output_dir, uuid):
def handle_new_job():

    response_list = []

    try:
        yt = Youtube(atlin_yt_job.token.token_detail['api_token'], atlin_yt_job.token.token_detail['token_quota'])
        if not yt.service:
            logger.error("The YouTube service was not created. Verify if the API key is valid or if the quota usage has been exceeded")
            print(yt.state.error_description)
            job_status_completed = handle_state(yt)
            return job_status_completed

        option = atlin_yt_job.job.job_detail.job_submit.option_type
        actions = atlin_yt_job.job.job_detail.job_submit.actions
        input = atlin_yt_job.job.job_detail.job_submit.option_value
        extension = "xlsx"

        #Validate path
        #atlin_yt_job.job.output_path = "/Users/jazminromero/development/AtlinProject/Output/YouTube"
        atlin_yt_job.job.output_path = validate_output_dir(atlin_yt_job.job.output_path)

        if option == "VIDEO":
            for action in actions:
                filename = atlin_yt_job.job.job_uid + "_" + action
                filename = utils.get_filename(filename, extension)


                if action == "METADATA":
                    response = yt.get_video_metadata_for_url(input)
                    utils.save_file(response, atlin_yt_job.job.output_path, filename)
                else:
                    response = yt.get_video_comments_for_url(input)
                    utils.save_file(response, atlin_yt_job.job.output_path, filename)

                response_list.append(response)
                # An error occurred while doing the above action or the quota exceeded we cannot continue executing actions
                if yt.state.error or yt.state.quota_exceeded:
                    break

        if option == "PLAYLIST":
            for action in actions:
                filename = atlin_yt_job.job.job_uid + "_" + action
                filename = utils.get_filename(filename, extension)
                if action == "METADATA":
                    response = yt.get_videos_metadata_from_playlist(input)
                    utils.save_file(response, atlin_yt_job.job.output_path, filename)
                else:
                    response = yt.get_videos_comments_from_playlist(input)
                    utils.save_file(response, atlin_yt_job.job.output_path, filename)

                # An error occurred while doing the above action or the quota exceeded we cannot continue executing actions
                if yt.state.error or yt.state.quota_exceeded:
                    break

                response_list.append(response)


        if option == "FILE":
            for action in actions:
                if action == "METADATA":
                    filename = atlin_yt_job.job.job_uid + "_" + action
                    filename = utils.get_filename(filename, extension)

                    response = yt.get_videos_metadata_from_file(input)
                    utils.save_file(response, atlin_yt_job.job.output_path, filename)
                else:
                    response = yt.get_videos_comments_from_file(input)
                    utils.save_file(response, atlin_yt_job.job.output_path, filename)

                # An error occurred while doing the above action or the quota exceeded we cannot continue executing actions
                if yt.state.error or yt.state.quota_exceeded:
                    break

                response_list.append(response)

        if option == "QUERY":

            videos = atlin_yt_job.job.job_detail.job_submit.video_count
            for action in actions:
                filename = atlin_yt_job.job.job_uid + "_" + action
                filename = utils.get_filename(filename, extension)

                if action == "METADATA":
                    response = yt.get_videos_metadata_from_query(input, videos)
                    utils.save_file(response, atlin_yt_job.job.output_path, filename)
                else:
                    response = yt.get_videos_comments_from_query(input, videos)
                    utils.save_file(response, atlin_yt_job.job.output_path, filename)

                # An error occurred while doing the above action or the quota exceeded we cannot continue executing actions
                if yt.state.error or yt.state.quota_exceeded:
                    break
            response_list.append(response)
    except:
        ex = traceback.format_exc()
        st = utils.log_format("handle_new_job", ex)
        logger.error(st)
        yt.state.set_error_description(True, st)

    job_status_completed = handle_state(yt)

    return job_status_completed




####################################################################################################
#
####################################################################################################
def resume_job():
    response_list = []
    try:
        yt = Youtube(atlin_yt_job.token.token_detail['api_token'], atlin_yt_job.token.token_detail['token_quota'])
        if not yt.service:
            logger.error("The YouTube service was not created. Verify if the API key is valid or if the quota usage has been exceeded")
            print(yt.state.error_description)
            handle_state(yt)
            return response_list

        yt.state = load_job_state(yt.state)
        yt.state.error = False
        yt.state.error_description = ""
        yt.state.quota_exceeded = False
        extension = "xlsx"

        #Validate path
        #atlin_yt_job.job.output_path = "/Users/jazminromero/development/AtlinProject/Output/YouTube"
        atlin_yt_job.job.output_path = validate_output_dir(atlin_yt_job.job.output_path)


        #Resume retrieving videos
        if len(yt.state.actions)>0 and (config.ACTION_RETRIEVE_VIDEOS in yt.state.actions):
            videos_ids = yt.state.videos_ids
            if videos_ids:
                # Get data from YouTube API
                response = yt.videos.get_videos_and_videocreators(videos_ids)
                filename = atlin_yt_job.job.job_uid + "_" + "METADATA"
                filename = utils.get_filename(filename, extension)
                utils.save_file(response, atlin_yt_job.job.output_path, filename)

        # Resume retrieving comments
        if len(yt.state.actions) > 0 and (config.ACTION_RETRIEVE_COMMENTS in yt.state.actions) and (not yt.state.error) and (not yt.state.quota_exceeded):
            videos_ids = yt.state.videos_ids
            if videos_ids:
                # Get data from YouTube API
                response = yt.comments.get_comments_and_commenters(videos_ids)
                filename = atlin_yt_job.job.job_uid + "_" + "COMMENTS"
                filename = utils.get_filename(filename, extension)
                utils.save_file(response, atlin_yt_job.job.output_path, filename)
    except:
        ex = traceback.format_exc()
        st = utils.log_format("handle_new_job", ex)
        logger.error(st)
        yt.state.set_error_description(True, st)

    job_status_completed = handle_state(yt)

    return job_status_completed


#======================================================================================================
#======================================================================================================
def extract_jobs(response):
    jobs = []
    if response.status_code == 200:
        jobs = response.json()
    return jobs

####################################################################################################
#
####################################################################################################
def YouTubeInterface(job):
    try:
        logger.info('Creating API class')
        print ("Starting job...")

        #Create a class for the AtlinYoutube
        #ToDo: Ask question: Is this the best place to put these statements?

        global atlin_yt_job
        atlin_yt_job= AtlinYouTubeJob("http://localhost:6010")    #ToDo: ####---> Question: From where do I get this address?

        global job_status
        job_status = atlinAPI.JobStatus()

        global job_platform
        job_platform = atlinAPI.JobPlatform()


        #For testing only +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
        #response = atlin_yt_job.job_get(job_status=[job_status.created])
        #if response.status_code == 200:
        #    jobs = response.json()
        #job = jobs[0]
        #++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++

        atlin_yt_job.job = atlinJob.Job(job)

        logger.info('Performing YouTube job:')
        logger.info(job)

        #Get token information (api token and quota)
        #response = atlin_job.token_get(atlin_job.token_uid)
        response = atlin_yt_job.token_get(token_uid=atlin_yt_job.job.token_uid)

        if response.status_code == 200:
            try:
                atlin_yt_job.token.from_json(response.json())
            except Exception as e:
                print(f"Could not fetch token quota. {e}")
                #exit()
                #ToDo: Handle this scenario

        if response.status_code != 200:
            print("Report error to scheduler")

        #ToDo: Verify that there isn't another job already running  with the same token_uid

        if atlin_yt_job.job.job_status == "CREATED":
            job_status_completed = handle_new_job()
        elif atlin_yt_job.job.job_status == "PAUSED":
            job_status_completed = resume_job()

        return job_status_completed
    except:
        ex = traceback.format_exc()
        print (ex)
        
################################################
#jobDict = {"status": "NewJob", "option": "video", "actions": ["metadata", "comments"], "input" : "https://www.youtube.com/watch?v=-DkpWjlJQIY", "videos": 0}
#jobDict = {"status": "NewJob", "option": "playlist", "actions": ["metadata", "comments"], "input" : "https://www.youtube.com/playlist?list=PLADighMnAG4DczAOY7i6-nJhB9sQDhIoR", "videos": 0}
#jobDict = {"status": "NewJob", "option": "query", "actions": ["metadata", "comments"], "input" : "pao de queijo minero", "videos": 50}
#jobDict = {"status": "NewJob", "option": "query", "actions": ["comments"], "input" : "pao de queijo liquidificador", "videos": 50}
#YouTubeInterface(jobDict)
