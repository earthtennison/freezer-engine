#!/usr/bin/env bash
ngrok http 4000 --log=stdout > ngrok.log &
python3 conversation.py &
python3 app.py &
python3 scheduler.py &
