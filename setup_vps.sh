#!/bin/bash

# Install required packages
sudo apt update
sudo apt install -y python3.12-venv python3-pip

# Create directory
sudo mkdir -p /opt/discord-bot
sudo chown $USER:$USER /opt/discord-bot

# Clone repository (if not already done through deployment)
git clone https://github.com/apikdech/discord-selfbot.git /opt/discord-bot

# Create and activate virtual environment
cd /opt/discord-bot
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Copy systemd service file
sudo cp deployment/discord-bot.service /etc/systemd/system/

# Reload systemd and enable service
sudo systemctl daemon-reload
sudo systemctl enable discord-bot
sudo systemctl start discord-bot 
