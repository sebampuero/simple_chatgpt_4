#!/bin/bash
kill -9 $(ps aux | grep '[p]ython3 /home/pi/gpt-4chat/server.py' | awk '{print $2}')
kill -9 $(ps aux | grep '/home/pi/gpt-4chat/venv/bin/python3' | awk '{print $2}')
kill -9 $(ps aux | grep '/home/pi/gpt-4chat/venv/bin/python3' | awk '{print $2}')