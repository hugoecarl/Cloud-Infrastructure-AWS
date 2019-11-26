#!/bin/bash
sudo apt update
sudo apt install python3-pip -y
sudo apt install python3-flask -y
pip3 install flask
pip3 install flask_restful
pip3 install pymongo
sudo ufw allow 5000
cd /home/ubuntu/PF_Cloud
python3 MongoDBinit.py
export FLASK_APP=app.py
flask run --host=0.0.0.0
