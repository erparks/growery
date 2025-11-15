#!/bin/bash

cd /hub
python3 -m venv hub_env

cp /hub/system/hub.service /etc/systemd/system/hub.service
sudo systemctl daemon-reload
sudo systemctl enable hub.service