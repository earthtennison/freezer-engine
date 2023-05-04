#!/usr/bin/env bash
rm -f ngrok.log
rm -f app.log
ngrok http --region jp 4000 --log=stdout > ngrok.log &
python3 conversation.py &
waitress-serve --host 127.0.0.1 --port 4000 app:app &
python3 scheduler.py &
