#!/usr/bin/env bash
ngrok http 4000 --log=stdout > ngrok.log &
python3 conversation.py >> app.log 2>&1 &
waitress-serve --host 127.0.0.1 --port 4000 app:app >> app.log 2>&1 &
python3 scheduler.py &
