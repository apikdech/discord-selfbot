#!/bin/bash

# Create directory
sudo mkdir -p /opt/discord-bot
sudo chown $USER:$USER /opt/discord-bot

# Clone repository (if not already done through deployment)
git clone <your-repo-url> /opt/discord-bot

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
