#!/usr/bin/env bash
rm -f ngrok.log
rm -f app.log
ngrok http 4000 --log=stdout > ngrok.log &
waitress-serve --host 127.0.0.1 --port 4000 app_test:app &
