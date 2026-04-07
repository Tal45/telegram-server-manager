# Bacon Network Status Bot

A modular Telegram bot designed for postmarketOS (Alpine-based) running on the OnePlus One (bacon) hardware. It provides secure, remote access to device network statistics via Telegram commands.

## Features

- **Security**: Access is restricted to a single authorized Telegram User ID.
- **Network Stats**: Retrieves hostname, active SSID, and local IPv4 address using `nmcli`.
- **Process Management**: Includes an OpenRC service script for persistent operation.
- **Extensible**: Modular handler and service architecture for adding future commands.

## Project Structure

- `bot/main.py`: Application entry point and handler registration.
- `bot/config.py`: Configuration management via environment variables.
- `bot/handlers/`: Individual command logic (start, ip, unknown).
- `bot/services/network.py`: System interaction layer for `nmcli` and `hostname`.
- `bot/security/auth.py`: Authorization decorator for user ID validation.

## Prerequisites

- Python 3.10+
- NetworkManager (`nmcli`)
- A Telegram Bot Token (via @BotFather)

## Installation

1. Clone the repository to the device:
   ```bash
   cd /root
   git clone <repository-url> bacon-bot
   cd bacon-bot
   ```

2. Create and activate a virtual environment:
   ```bash
   python3 -m venv venv
   ```

3. Install dependencies:
   ```bash
   ./venv/bin/pip install -r requirements.txt
   ```

4. Configure environment variables in `bot/.env`:
   ```env
   BOT_TOKEN=your_token_here
   AUTHORIZED_USER_ID=your_telegram_id_here
   ```

5. Secure the environment file:
   ```bash
   chmod 600 bot/.env
   ```


## Deployment (OpenRC)

1. Copy the service script:
   ```bash
   sudo cp bacon-bot.initd /etc/init.d/bacon-bot
   sudo chmod +x /etc/init.d/bacon-bot
   ```

2. Edit `/etc/init.d/bacon-bot` to set the correct `directory` and `command` paths for your environment.

3. Manage the service:
   ```bash
   sudo rc-service bacon-bot start
   sudo rc-update add bacon-bot default
   ```

## Usage

The bot responds to the following inputs from the authorized user:
- `/start`: Status check.
- `/ip`: Returns hostname, SSID, IP, and timestamp.
