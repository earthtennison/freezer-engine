import logging
import time
logging.basicConfig(filename='example.log', encoding='utf-8', level=logging.DEBUG)
logging.debug('This message should go to the log file')
logging.info('So should this')
logging.warning('And this, too')
logging.error('And non-ASCII stuff, too, like Øresund and Malmö')

count = 0
while True:
    count += 1
    logging.info('Loop %s', count)
    time.sleep(1)
