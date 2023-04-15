
# time library
import time
from datetime import datetime, timedelta
import schedule

import requests

def get_reminder():
	requests.get('http://127.0.0.1:80/reminder')

def expire_reminder_loop():

    # check every 10 am
    schedule.every().day.at("10:00").do(get_reminder)
    # for debug
    schedule.every(1).minutes.do(get_reminder)
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    expire_reminder_loop()
    # get_reminder()