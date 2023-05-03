#!/usr/bin/python3.10
#-*-coding: utf-8 -*-
##from __future__ import absolute_import
###
# ref: https://medium.com/linedevth/%E0%B8%AA%E0%B8%A3%E0%B9%89%E0%B8%B2%E0%B8%87-line-chatbot-%E0%B8%94%E0%B9%89%E0%B8%A7%E0%B8%A2%E0%B8%A0%E0%B8%B2%E0%B8%A9%E0%B8%B2-python-84750b353fba
# ref of socket communication: https://github.com/robocup-eic/robocup2022-cv-yolov5/blob/main/yolov5.py
################################

from flask import Flask, request, abort
import numpy as np

from linebot.models import *
from linebot.models.template import *
from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)

import os
from dotenv import load_dotenv

# custom socket for client connections
from custom_socket import CustomSocket
import socket

import time

import logging

logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.DEBUG)

load_dotenv()

lineaccesstoken = os.getenv('LINE_ACCESS_TOKEN')
channelsecret = os.getenv('CHANNEL_SECRET')

line_bot_api = LineBotApi(lineaccesstoken)
handler = WebhookHandler(channelsecret)

# host = socket.gethostname()
host = '127.0.0.1'
# host = ' http://freezer-engine.herokuapp.com'
port = 10000

c = CustomSocket(host,port, 'Socket client')

connected = False
while not connected:
    connected = c.clientConnect()
    time.sleep(1)

# start flask server
app = Flask(__name__)

@app.route('/')
def index():
    return "Hello World!"


@app.route('/webhook', methods=['POST'])
def callback():
    # get X-Line-Signature header value
    signature = request.headers['X-Line-Signature']

    # get request body as text
    body = request.get_data(as_text=True)
    app.logger.info("Request body: " + body)

    # handle webhook body
    try:
        logging.info('[Flask server] Received webhook')
        handler.handle(body, signature)
    except InvalidSignatureError:
        print("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):

    global c

    rtoken = event.reply_token
    msgType = event.message.type

    if msgType == "text":
        msg = str(event.message.text)

        # socket request
        try:
            res = c.req(msg)
            logging.info('[Flask server] Bot responds: {}'.format(res))
        except socket.error as e:
            logging.info('[Flask server] Error: {}'.format(e))
            # reconnect to the server
            host = '127.0.0.1'
            # host = ' http://freezer-engine.herokuapp.com'
            port = 10000

            c = CustomSocket(host, port, 'Socket client')

            connected = False
            while not connected:
                connected = c.clientConnect()
                time.sleep(2)


        # res_msg structure: {'type': , 'message': , 'aux_data'}
        # eg. "text", "hello", "
        # "quick_reply","select this", ["1","2","3"]
        # "image", "", "image url"

        if res['type'] == "text":
            replyObj = TextSendMessage(text=res['message'])
            line_bot_api.reply_message(rtoken, replyObj)
        elif res['type'] == "quick_reply":
            items = [QuickReplyButton(action=MessageAction(label=t, text=t)) for t in res['aux_data']]
            replyObj = TextSendMessage(text=res['message'],
                quick_reply=QuickReply(items=items))
            line_bot_api.reply_message(rtoken, replyObj)
        elif res['type'] == "image":
            camera_item = QuickReplyButton(action=CameraAction(label='camera'))
            text_item = QuickReplyButton(action=MessageAction(label='no', text='no'))
            replyObj = TextSendMessage(text=res['message'],
                quick_reply=QuickReply(items=[camera_item, text_item]))
            line_bot_api.reply_message(rtoken, replyObj)
    elif msgType == 'image':
        message_id = str(event.message.id)

        message_content = line_bot_api.get_message_content(message_id)

        res = c.req('save image')
        if res['type'] == 'image':
            # save image
            image_path = res['aux_data']
            with open(image_path, 'wb') as fd:
                for chunk in message_content.iter_content():
                    fd.write(chunk)

            replyObj = TextSendMessage(text=res['message'])
            line_bot_api.reply_message(rtoken, replyObj)
        elif res['type'] == "quick_reply":
            items = [QuickReplyButton(action=MessageAction(label=t, text=t)) for t in res['aux_data']]
            replyObj = TextSendMessage(text=res['message'],
                quick_reply=QuickReply(items=items))
            line_bot_api.reply_message(rtoken, replyObj)

    else:
        sk_id = np.random.randint(1,17)
        replyObj = StickerSendMessage(package_id=str(1),sticker_id=str(sk_id))
        line_bot_api.reply_message(rtoken, replyObj)


@app.route('/reminder', methods=['GET'])
def expire_reminder():
    global c

    logging.info("[Flask server] Checking expiring items...")

    # socket request
    res_msg = c.req('check')
    
    replyObj = TextSendMessage(text=res_msg['message'])
    # broadcast to all user
    line_bot_api.broadcast(replyObj)
    return res_msg


if __name__ == '__main__':

    app.run(debug=True, port = 80, use_reloader=False)
