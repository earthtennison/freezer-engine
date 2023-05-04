"""
Demo line api from https://github.com/line/line-bot-sdk-python
"""

from flask import Flask, request, abort

from linebot import (
    LineBotApi, WebhookHandler
)
from linebot.exceptions import (
    InvalidSignatureError
)
from linebot.models import (
    MessageEvent, TextMessage, TextSendMessage,
)

import os
from dotenv import load_dotenv

import logging

logging.basicConfig(filename='app.log', encoding='utf-8', level=logging.DEBUG, format='%(asctime)-15s:%(levelname)s:%(name)s:%(message)s')

load_dotenv()

lineaccesstoken = os.getenv('LINE_ACCESS_TOKEN')
channelsecret = os.getenv('CHANNEL_SECRET')

app = Flask(__name__)

line_bot_api = LineBotApi(lineaccesstoken)
handler = WebhookHandler(channelsecret)


@app.route("/webhook", methods=['POST'])
def callback():
    try:
        logging.info('Received webhook')
        # get X-Line-Signature header value
        signature = request.headers['X-Line-Signature']

        # get request body as text
        body = request.get_data(as_text=True)
        logging.info("Request body: " + body)

    except Exception as e:
        logging.error('Error'+e)
        abort(400)
    # handle webhook body
    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        logging.error("Invalid signature. Please check your channel access token/channel secret.")
        abort(400)
    return 'OK'


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text))


if __name__ == "__main__":
    app.run(debug=True, port = 80)
