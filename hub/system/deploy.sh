#!/bin/bash

pip freeze > requirements.txt

rsync -av --exclude='hub_env' ../ ethan@hub.local:/hub --rsync-path="sudo rsync"

ssh ethan@hub.local << EOF
    cd /hub
    source hub_env/bin/activate
    cd system
    pip install -r requirements.txt
EOF
