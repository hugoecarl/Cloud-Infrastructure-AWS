#!/bin/bash
sudo apt update
sudo apt install python3-pip -y
sudo apt install python3-flask -y
pip3 install flask
pip3 install flask_restful
sudo ufw allow 5000
crontab -l | { cat; echo "@reboot cd /home/ubuntu/PF_Cloud;export FLASK_APP=pass_on.py;flask run --host=0.0.0.0"; } | crontab -
cd /home/ubuntu/PF_Cloud
export FLASK_APP=pass_on.py
flask run --host=0.0.0.0


