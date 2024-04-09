#!/bin/bash
kill -9 $(ps aux | grep '[p]ython3 /home/ubuntu/gpt4/server.py' | awk '{print $2}')
kill -9 $(ps aux | grep '/home/pi/ubuntu/venv/bin/python3' | awk '{print $2}')
kill -9 $(ps aux | grep '/home/pi/ubuntu/venv/bin/python3' | awk '{print $2}')
