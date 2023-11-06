from pathlib import Path
import rcs
import sys

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()
sys.path.insert(0, BASE_DIR)

import Config as config
from Scheduler.utils import  WAIT_TIME
from job_scheduler import JobScheduler           

from Scheduler.ToolInterfaces.reddit_api_interface import reddit_interface
from ToolInterfaces.CrawlerInterface import CrawlerInterface
from ToolInterfaces.YouTubeInterface import YouTubeInterface

def main():
    """
    Setup and run the job scheduler
    """
    # Initialize logging
    rcs.utils.configure_logging(level=config.LOGGER_LEVEL,
                                output_directory=config.LOGGER_DIR_PATH,
                                output_filename_prefix=config.LOGGER_FILE_PREFIX,
                                n_log_files=config.N_LOG_FILES)

    js = JobScheduler(wait_time=WAIT_TIME)

    js.add_job_type('REDDIT', reddit_interface)
    js.add_job_type('YOUTUBE', YouTubeInterface)
    js.add_job_type('CRAWL', CrawlerInterface)

    js.run()

if __name__ == '__main__':
    main()

    