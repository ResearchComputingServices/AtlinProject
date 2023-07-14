import sqlite3
import sys
import time
import random
import logging

sys.path.insert(0, '/home/nickshiell/Documents/Work/SocialMediaAPIInterface/SocialMediaAPIInterface/')

from Utils import *

####################################################################################################
#
####################################################################################################

def PerformCrawl(sqliteCursor,jobDict):
    
    listOfResponsesJSON = []

    time.sleep(random.randint(1,5))
    
    return listOfResponsesJSON

####################################################################################################
#
####################################################################################################
def CrawlerInterface(dataBaseFilename,
                    jobDict):
   
    logging.info('PERFORMING JOBS:',flush=True)
    logging.info(jobDict,flush=True)
   
    return  
              