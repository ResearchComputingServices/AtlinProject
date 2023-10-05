import logging
import Config as config
import os

#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('youtube')

# youtube_log_file_path = os.path.join(config.LOGGER_DIR_PATH,'Log_Youtube.txt') 

# logging.basicConfig(filename=youtube_log_file_path,
#                     filemode='a',
#                     format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
#                     datefmt='%H:%M:%S',
#                     level=logging.DEBUG)

#Level   Numeric value
#CRITICAL  50
#ERROR     40
#WARNING   30
#INFO      20
#DEBUG     10
#NOTSET     0