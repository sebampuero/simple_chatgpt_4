#!/bin/bash
kill -9 $(ps aux | grep '[p]ython3 /home/pi/gpt-4chat/server.py' | awk '{print $2}')