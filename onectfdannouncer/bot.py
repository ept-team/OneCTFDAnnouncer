import logging
import discord
from discord.ext import tasks
from discord import app_commands
from .config import DISCORD_TOKEN, ANNOUNCE_CHANNEL_ID, POLL_INTERVAL, LOG_LEVEL
from .commands import register_commands
from .tasks import register_tasks

# Configure logging with environment variable
log_level = getattr(logging, LOG_LEVEL, logging.INFO)
logging.basicConfig(
    level=log_level, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

intents = discord.Intents.default()


class AnnouncerBot(discord.Client):
    def __init__(self):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        logger.info("Setting up bot...")
        register_commands(self)
        logger.info(f"Registered {len(self.tree.get_commands())} commands")
        register_tasks(self)
        logger.info("Syncing command tree...")
        try:
            synced = await self.tree.sync()
            logger.info(
                f"Command tree synced successfully - {len(synced)} commands synced"
            )
            for cmd in synced:
                logger.info(f"Synced command: {cmd.name}")
        except Exception as sync_error:
            logger.error(f"Failed to sync command tree: {sync_error}")
        # Don't start polling task here - wait for on_ready


bot = AnnouncerBot()


@bot.event
async def on_ready():
    logger.info(f"Logged in as {bot.user} (ID: {bot.user.id})")
    logger.info(f"Bot is ready and connected to {len(bot.guilds)} guild(s)")

    # Start polling task only after bot is fully ready
    if hasattr(bot, "poll_first_bloods"):
        bot.poll_first_bloods.start()
        logger.info("Started first blood polling task")
    else:
        logger.warning("poll_first_bloods task not found")


if __name__ == "__main__":
    logger.info("Starting bot...")
    try:
        bot.run(DISCORD_TOKEN)
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise
