# onectfdannouncer

A Discord bot for CTFd first blood announcements and top 10 teams.

## Features
- Announces first bloods in a specified channel
- Command to list top 10 teams

## Setup
- Copy `.env.example` to `.env` and fill in your config
- Install dependencies with `uv pip install .`
- Run the bot: `python -m onectfdannouncer.bot`

## Docker Setup
- Copy `.env.example` to `.env` and configure
- Build and run: `docker compose up --build`

## Logging
The bot uses structured logging with timestamps and log levels. Set `LOG_LEVEL` environment variable to control verbosity:
- `DEBUG` - Detailed debug information
- `INFO` - General information (default)
- `WARNING` - Warning messages only
- `ERROR` - Error messages only
