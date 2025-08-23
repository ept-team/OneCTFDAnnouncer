import logging
from discord.ext import tasks
from .config import ANNOUNCE_CHANNEL_ID, POLL_INTERVAL
from .ctfd_api import CTFdAPI
from .state_db import StateDB
from .utils import sanitize_team_name, sanitize_challenge_name

logger = logging.getLogger(__name__)


def register_tasks(bot):
    ctfd = CTFdAPI()
    db = StateDB()

    @tasks.loop(seconds=POLL_INTERVAL)
    async def poll_first_bloods():
        try:
            channel = bot.get_channel(ANNOUNCE_CHANNEL_ID)
            if not channel:
                logger.warning(
                    f"Channel {ANNOUNCE_CHANNEL_ID} not found - checking permissions and accessibility"
                )
                # Try to get channel from all guilds
                for guild in bot.guilds:
                    channel = guild.get_channel(ANNOUNCE_CHANNEL_ID)
                    if channel:
                        logger.info(
                            f"Found channel {ANNOUNCE_CHANNEL_ID} in guild {guild.name}, but bot.get_channel() failed"
                        )
                        break
                else:
                    logger.error(
                        f"Channel {ANNOUNCE_CHANNEL_ID} not found in any guild. Bot is in {len(bot.guilds)} guilds."
                    )
                return

            logger.debug(
                f"Successfully accessed channel #{channel.name} ({channel.id})"
            )

            challenges = ctfd.get_challenges()
            logger.debug(f"Checking {len(challenges)} challenges for first bloods")

            # Filter out challenges that already have announced first bloods
            unannnounced_challenges = []
            for chal in challenges:
                if not db.is_announced(chal["id"]):
                    unannnounced_challenges.append(chal)
                else:
                    logger.debug(
                        f"Skipping challenge '{chal['name']}' - first blood already announced"
                    )

            logger.debug(
                f"Found {len(unannnounced_challenges)} challenges without announced first bloods"
            )

            for chal in unannnounced_challenges:
                logger.debug(
                    f"Checking solves for challenge '{chal['name']}' ({chal['id']})"
                )
                solves = ctfd.get_solves(chal["id"])
                if solves:
                    first = solves[0]
                    logger.info(
                        f"Found first solve for challenge {chal['id']}: {first}"
                    )

                    # Handle different possible structures for team name and user name
                    team_name = sanitize_team_name(first["name"])
                    challenge_name = sanitize_challenge_name(chal["name"])

                    announcement = f":drop_of_blood: First blood on **{challenge_name}** by {team_name}!"

                    await channel.send(announcement)
                    db.mark_announced(chal["id"])
                    logger.info(
                        f"Announced first blood for challenge '{chal['name']}' by team '{first['name']}'"
                    )
        except Exception as e:
            logger.error(f"Error in poll_first_bloods task: {e}")

    bot.poll_first_bloods = poll_first_bloods
