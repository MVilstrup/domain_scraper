#!/bin/sh
sudo apt-get upgrade -y
sudo apt-get update -y

sudo apt-get install python-dev python-numpy python-tk python-bs4 -y
sudo apt-get install python-pip python-scipy rabbitmq-server -y
sudo easy_install -U distribute
sudo apt-get install libfreetype6-dev libxft-dev -y
sudo apt-get install python-matplotlib -y
sudo pip install six scikit-learn  celery
sudo pip install -U matplotlib
