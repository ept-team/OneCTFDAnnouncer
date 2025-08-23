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

### Using Docker Compose (Recommended)

#### Local Development
- Copy `.env.example` to `.env` and configure
- Build and run: `docker compose up --build`

#### Production (using published image)
- Copy `.env.example` to `.env` and configure  
- Run with published image: `docker compose -f docker-compose.prod.yml up`

### Using Pre-built Images
The bot is automatically built and published to GitHub Container Registry:

```bash
# Pull the latest image
docker pull ghcr.io/[your-username]/onectfdannouncer:latest

# Run with environment file
docker run --env-file .env ghcr.io/[your-username]/onectfdannouncer:latest

# Or run with environment variables
docker run -e DISCORD_TOKEN=your_token \
           -e CTFD_URL=https://your.ctfd.com \
           -e CTFD_API_KEY=your_api_key \
           -e ANNOUNCE_CHANNEL_ID=your_channel_id \
           ghcr.io/[your-username]/onectfdannouncer:latest
```

### Available Tags
- `latest` - Latest stable release from main branch
- `v1.0.0` - Specific version tags
- `main` - Latest commit from main branch
- `develop` - Latest commit from develop branch

### Multi-Architecture Support
Images are built for multiple architectures:
- `linux/amd64` (x86_64)
- `linux/arm64` (ARM64/AArch64)

## Logging
The bot uses structured logging with timestamps and log levels. Set `LOG_LEVEL` environment variable to control verbosity:
- `DEBUG` - Detailed debug information
- `INFO` - General information (default)
- `WARNING` - Warning messages only
- `ERROR` - Error messages only
