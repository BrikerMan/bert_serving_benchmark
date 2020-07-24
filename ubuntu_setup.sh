#!/bin/sh

curl -fsSL https://get.docker.com -o get-docker.sh
sh get-docker.sh
sudo apt-get install -y docker-compose
sudo apt-get install -y apache2-utils
sudo systemctl enable --now docker
sudo usermod -aG docker ${USER}
pip3 install -r requirements.txt
