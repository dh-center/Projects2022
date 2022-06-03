
# Set up ssh key
```shell
cat <your machine>/id_rsa.pub >> ~/.ssh/authorized_keys
```

If you do not have the folder `~/.ssh/authorized_keys` , you can create this with the following commands:
```shell
mkdir -p ~/.ssh
touch ~/.ssh/authorized_keys
```

Overall setup:
```shell
#!/bin/bash


set -e

sudo apt update
sudo apt -y upgrade

sudo apt -y install openjdk-11-jdk
sudo apt -y install maven

sudo apt-get install -y python3.9-dev
sudo apt-get install -y python3.9-venv

sudo apt install -y build-essential libssl-dev libffi-dev python3-dev

# make venv
python3.9 -m venv venv
source venv/bin/activate

# install python libs
pip install -r  requirements.txt

# list them
pip list

# docker install
# https://docs.docker.com/engine/install/ubuntu/
# docker-compose setup
# https://docs.docker.com/compose/install/
sudo apt-get install -y curl
sudo curl -L "https://github.com/docker/compose/releases/download/1.29.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
sudo ln -s /usr/local/bin/docker-compose /usr/bin/docker-compose

sudo groupadd docker
sudo usermod -aG docker ${USER}
newgrp docker

# Reconnect to machine to have effect
```


Check traffic usage tool
```shell
https://github.com/raboof/nethogs
```