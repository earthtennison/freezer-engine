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

# multiprocess for parallel processing
from multiprocessing import Process

# custom socket for client connections
from custom_socket import CustomSocket
import socket

import time


app = Flask(__name__)

load_dotenv()

lineaccesstoken = os.getenv('LINE_ACCESS_TOKEN')
line_bot_api = LineBotApi(lineaccesstoken)

host = socket.gethostname()
# host = ' http://freezer-engine.herokuapp.com'
port = 10000

# delay
time.sleep(5)

c = CustomSocket(host,port)
# c.clientConnect()

connected = False
while not connected:
    connected = c.clientConnect()


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
    global c
    print(event)

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

        # socket request
        res_msg = c.req(msg)

        replyObj = TextSendMessage(text=res_msg)
        print("Bot:",res_msg)

        line_bot_api.reply_message(rtoken, replyObj)

    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)
    return ''

@app.route('/reminder', methods=['GET'])
def expire_reminder():
    global c

    print("Bot: I'm checking expiring items")

    # socket request
    res_msg = c.req('check')
    
    replyObj = TextSendMessage(text=res_msg)
    # broadcast to all user
    line_bot_api.broadcast(replyObj)
    return res_msg


if __name__ == '__main__':

    app.run(debug=True, port = 80, use_reloader=False)

    # p = Process(target=expire_reminder)
    # p.start()  
    # app.run(debug=True, port = 80, use_reloader=False)
    # p.join()
