import logging
#logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger('youtube')

logging.basicConfig(filename="/Users/jazminromero/development/AtlinProject/Scheduler/log.txt",
                    filemode='a',
                    format='%(asctime)s,%(msecs)d %(name)s %(levelname)s %(message)s',
                    datefmt='%H:%M:%S',
                    level=logging.DEBUG)

#Level   Numeric value
#CRITICAL  50
#ERROR     40
#WARNING   30
#INFO      20
#DEBUG     10
#NOTSET     0