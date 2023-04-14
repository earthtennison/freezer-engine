#!/usr/bin/python3.10
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
# ref: https://medium.com/linedevth/%E0%B8%AA%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%87-line-chatbot-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2%E0%B8%A0%E0%B8%B2%E0%B8%A9%E0%B8%B2-python-84750b353fba
################################
from urllib.parse import uses_relative
from flask import Flask, jsonify, render_template, request
import json
import numpy as np
import pandas as pd

from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,TemplateSendMessage,ImageSendMessage, StickerSendMessage, AudioSendMessage
)
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)

import os
from dotenv import load_dotenv

from conversation import Conversation

# time library
import time
from datetime import datetime, timedelta
import schedule

# multiprocess for parallel processing
from multiprocessing import Process, Value


app = Flask(__name__)

load_dotenv()

lineaccesstoken = os.getenv('LINE_ACCESS_TOKEN')
line_bot_api = LineBotApi(lineaccesstoken)

# conversation module
con = Conversation("./database/data1.csv")


@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    json_line = request.get_json(force=False,cache=False)
    json_line = json.dumps(json_line)
    decoded = json.loads(json_line)
    no_event = len(decoded['events'])
    for i in range(no_event):
        event = decoded['events'][i]
        event_handle(event)
    return '',200


def event_handle(event):
    print(event)

    print("before event")
    print("conver_index",con.conver_index)
    print("conver_type",con.conver_type)
    try:
        userId = event['source']['userId']
    except:
        print('error cannot get userId')
        return ''

    try:
        rtoken = event['replyToken']
    except:
        print('error cannot get rtoken')
        return ''
    try:
        msgId = event["message"]["id"]
        msgType = event["message"]["type"]
    except:
        print('error cannot get msgID, and msgType')
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
        return ''

    if msgType == "text":
        msg = str(event["message"]["text"])

        con.push_msg(msg)
        res_msg = con.response()
        replyObj = TextSendMessage(text=res_msg)
        print("Bot:",res_msg)

        print("after event")
        print("conver_index",con.conver_index)
        print("conver_type",con.conver_type)
        line_bot_api.reply_message(rtoken, replyObj)

    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

def expire_reminder():
    print("Bot: I am checking expiring items.")
    msg = 'Expiring item! :'
    item_cnt = 0
    for idx, row in con.db.df.iterrows():
        date_diff =  datetime.strptime(row['expiry_date'], '%d.%m.%Y') - datetime.now().replace(hour=0, minute=0, second=0)
        if  date_diff.days + 1 < 2: # 2 days
            msg += '\n- ' + row['name'] + ' is expired in ' + str(date_diff.days + 1) + ' days'
            item_cnt += 1

    if item_cnt > 0:
        replyObj = TextSendMessage(text=msg)
        print("Bot:",msg)
        # broadcast to all user
        line_bot_api.broadcast(replyObj)
    else:
        msg = 'No item expiring today.'
        print("Bot:", msg)
        replyObj = TextSendMessage(text=msg)
        print("Bot:",msg)
        # broadcast to all user
        line_bot_api.broadcast(replyObj)


def expire_reminder_loop():

    # check every 10 am
    schedule.every().day.at("10:00").do(expire_reminder)
    # for debug
    schedule.every(5).minutes.do(expire_reminder)
    while True:
        schedule.run_pending()
        # print("running")
        time.sleep(1)

if __name__ == '__main__':
    
    p = Process(target=expire_reminder_loop)
    p.start()  
    app.run(debug=True, port = 80, use_reloader=False)
    p.join()
