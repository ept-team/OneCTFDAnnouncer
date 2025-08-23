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

#### Local Development with Bind Mounts
- Copy `.env.example` to `.env` and configure
- Build and run: `docker compose -f docker-compose.dev.yml up --build`
- Database will be stored in `./data/state.db` (accessible from host)

#### Local Development with Docker Volumes
- Copy `.env.example` to `.env` and configure
- Build and run: `docker compose up --build`
- Database will be stored in a Docker volume `bot_data`

#### Production (using published image)
- Copy `.env.example` to `.env` and configure  
- Run with published image: `docker compose -f docker-compose.prod.yml up`
- Database will be stored in a Docker volume `bot_data`

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

## Database and Data Persistence

The bot uses SQLite to track announced first bloods. Data persistence is handled differently depending on your setup:

### Docker Volumes (Recommended for Production)
- Data is stored in a Docker volume named `bot_data`
- Persists across container restarts and updates
- Managed by Docker

```bash
# View volume information
docker volume inspect onectfdannouncer_bot_data

# Backup the database
docker run --rm -v onectfdannouncer_bot_data:/data -v $(pwd):/backup alpine cp /data/state.db /backup/

# Restore the database
docker run --rm -v onectfdannouncer_bot_data:/data -v $(pwd):/backup alpine cp /backup/state.db /data/
```

### Bind Mounts (Recommended for Development)
- Data is stored in `./data/state.db` on the host
- Directly accessible and editable from the host system
- Easy to backup and restore

## Logging
The bot uses structured logging with timestamps and log levels. Set `LOG_LEVEL` environment variable to control verbosity:
- `DEBUG` - Detailed debug information
- `INFO` - General information (default)
- `WARNING` - Warning messages only
- `ERROR` - Error messages only
