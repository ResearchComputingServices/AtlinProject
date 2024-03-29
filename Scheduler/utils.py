import os
from pathlib import Path

WAIT_TIME = 5 # Amount of time to sleep before checking the data base for new jobs
BASE_DIR = BASE_DIR = Path(__file__).resolve().parent.parent
SCHEDULER_DIR = os.path.join(BASE_DIR, 'Scheduler')

REDDIT_JOB = 'REDDIT'
CRAWL_JOB = 'CRAWL'
YOUTUBE_JOB = 'YOUTUBE'
TWITTER_JOB = 'TWITTER'

JOB_TYPE_LIST = [REDDIT_JOB,
                 CRAWL_JOB,
                 YOUTUBE_JOB,
                 TWITTER_JOB]