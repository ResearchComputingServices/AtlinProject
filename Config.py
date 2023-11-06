"""
configuration parameters required by the Atlin Project
"""
from pathlib import Path
import os

ATLIN_API_ADDRESS ="http://localhost:6010"

BASE_DIR = Path(__file__).resolve().parent.parent.as_posix()

SOCIAL_MEDIA_API_BASE_DIR = os.path.join(BASE_DIR, "SocialMediaAPIInterface")

LOGGER_DIR_PATH = os.path.join(SOCIAL_MEDIA_API_BASE_DIR,"Logs")
LOGGER_FILE_PREFIX = 'Atlin_Log_'
LOGGER_LEVEL = 'debug'
N_LOG_FILES = 5

MAIN_OUTPUT_DIR = os.path.join(SOCIAL_MEDIA_API_BASE_DIR,"Output")

DATA_FILE_KEEP_N_DAYS = 60
