import logging
import discord
from discord import app_commands
from .ctfd_api import CTFdAPI
from .config import ANNOUNCE_CHANNEL_ID
from .utils import sanitize_team_name

logger = logging.getLogger(__name__)
ctfd = CTFdAPI()


def register_commands(bot):
    @bot.tree.command(
        name="top10", description="List the top 10 teams on the scoreboard."
    )
    async def top10(interaction: discord.Interaction):
        logger.info(f"Top10 command invoked by {interaction.user}")

        try:
            # Try to defer the response to give us more time
            await interaction.response.defer()
        except discord.NotFound:
            logger.error(
                "Interaction expired before we could defer - this might be a sync issue"
            )
            return
        except Exception as defer_error:
            logger.error(f"Failed to defer interaction: {defer_error}")

        try:
            teams = ctfd.get_top_teams()
            if not teams:
                if interaction.response.is_done():
                    await interaction.followup.send(
                        "❌ No teams found on the scoreboard."
                    )
                else:
                    await interaction.response.send_message(
                        "❌ No teams found on the scoreboard."
                    )
                return

            msg = "\n".join(
                [
                    f"{i+1}. {sanitize_team_name(team['name'])} ({team['score']})"
                    for i, team in enumerate(teams)
                ]
            )

            if interaction.response.is_done():
                await interaction.followup.send(f"**Top 10 Teams:**\n{msg}")
            else:
                await interaction.response.send_message(f"**Top 10 Teams:**\n{msg}")

            logger.info("Top10 command completed successfully")
        except Exception as e:
            logger.error(f"Error in top10 command: {e}")
            try:
                if interaction.response.is_done():
                    await interaction.followup.send("❌ Error fetching scoreboard data")
                else:
                    await interaction.response.send_message(
                        "❌ Error fetching scoreboard data", ephemeral=True
                    )
            except Exception as followup_error:
                logger.error(f"Failed to send error message: {followup_error}")

    @bot.tree.command(name="stats", description="Show CTF statistics and information.")
    async def stats(interaction: discord.Interaction):
        logger.info(f"Stats command invoked by {interaction.user}")

        try:
            await interaction.response.defer()
        except discord.NotFound:
            logger.error("Interaction expired before we could defer")
            return
        except Exception as defer_error:
            logger.error(f"Failed to defer interaction: {defer_error}")

        try:
            # Fetch all data in parallel for better performance
            import asyncio

            config_task = asyncio.create_task(asyncio.to_thread(ctfd.get_ctf_config))
            teams_task = asyncio.create_task(asyncio.to_thread(ctfd.get_all_teams))
            users_task = asyncio.create_task(asyncio.to_thread(ctfd.get_all_users))
            challenges_task = asyncio.create_task(
                asyncio.to_thread(ctfd.get_challenges)
            )
            # Use new comprehensive statistics method
            comprehensive_stats_task = asyncio.create_task(
                asyncio.to_thread(ctfd.get_comprehensive_statistics)
            )
            # Use new method to get only correct submissions
            correct_submissions_task = asyncio.create_task(
                asyncio.to_thread(ctfd.get_submissions_with_type, 'correct')
            )

            config = await config_task
            teams = await teams_task
            users = await users_task
            challenges = await challenges_task
            comprehensive_stats = await comprehensive_stats_task
            correct_submissions = await correct_submissions_task

            # Build stats message
            stats_lines = []

            # Convert config list to dict if needed
            config_dict = {}
            if isinstance(config, list):
                for item in config:
                    if isinstance(item, dict) and 'key' in item and 'value' in item:
                        config_dict[item['key']] = item['value']
            elif isinstance(config, dict):
                config_dict = config

            # CTF Name
            ctf_name = config_dict.get("ctf_name", config_dict.get("name", "CTF"))
            stats_lines.append(f"🏆 **{ctf_name}**")
            stats_lines.append("")

            # Basic counts
            stats_lines.append(f"👥 **Teams:** {len(teams)}")
            stats_lines.append(f"👤 **Players:** {len(users)}")
            stats_lines.append(f"🎯 **Challenges:** {len(challenges)}")
            stats_lines.append(f"✅ **Correct Solves:** {len(correct_submissions)}")
            
            # If we have comprehensive statistics, show additional info
            if comprehensive_stats:
                logger.debug(f"Comprehensive statistics available: {list(comprehensive_stats.keys())}")
                
                # Challenge solve statistics
                challenge_stats = comprehensive_stats.get('challenge_solves', {})
                if challenge_stats:
                    logger.debug(f"Challenge solve statistics: {challenge_stats}")
                    if isinstance(challenge_stats, dict):
                        total_solves = sum(challenge_stats.values()) if challenge_stats.values() else len(correct_submissions)
                        stats_lines.append(f"📊 **Total Solves (from stats):** {total_solves}")
                
                # Challenge percentages
                challenge_percentages = comprehensive_stats.get('challenge_percentages', {})
                if challenge_percentages:
                    logger.debug(f"Challenge percentages available")
                    stats_lines.append(f"📈 **Challenge percentage data available**")
                
                # Team statistics
                team_stats = comprehensive_stats.get('team_stats', {})
                if team_stats:
                    logger.debug(f"Team statistics available")
                    stats_lines.append(f"👥 **Team statistics available**")
                
                # Submission statistics  
                submission_stats = comprehensive_stats.get('submission_stats', {})
                if submission_stats:
                    logger.debug(f"Submission statistics available")
                    stats_lines.append(f"📝 **Submission statistics available**")
            
            # Show solve rate based on challenges vs teams
            if len(challenges) > 0 and len(teams) > 0:
                max_possible_solves = len(challenges) * len(teams)
                solve_rate = (len(correct_submissions) / max_possible_solves * 100) if max_possible_solves > 0 else 0
                stats_lines.append(f"� **Solve Rate:** {solve_rate:.1f}%")
            
            stats_lines.append("")

            # Timing information - CTFd typically uses 'start' and 'end' keys
            start_time = config_dict.get("start")
            end_time = config_dict.get("end")

            if start_time:
                from datetime import datetime

                try:
                    logger.debug(f"Start time value: {start_time} (type: {type(start_time)})")
                    if isinstance(start_time, str):
                        # Try to parse as timestamp first, then as ISO string
                        try:
                            start_dt = datetime.fromtimestamp(int(start_time))
                            stats_lines.append(
                                f"🚀 **Start:** {start_dt.strftime('%Y-%m-%d %H:%M UTC')}"
                            )
                        except ValueError:
                            # Not a timestamp, try ISO format
                            start_dt = datetime.fromisoformat(
                                start_time.replace("Z", "+00:00")
                            )
                            stats_lines.append(
                                f"🚀 **Start:** {start_dt.strftime('%Y-%m-%d %H:%M UTC')}"
                            )
                    elif isinstance(start_time, (int, float)):
                        start_dt = datetime.fromtimestamp(start_time)
                        stats_lines.append(
                            f"🚀 **Start:** {start_dt.strftime('%Y-%m-%d %H:%M UTC')}"
                        )
                    else:
                        stats_lines.append(f"🚀 **Start:** {start_time}")
                except Exception as time_error:
                    logger.debug(f"Error parsing start time: {time_error}")
                    stats_lines.append(f"🚀 **Start:** {start_time}")

            if end_time:
                try:
                    logger.debug(f"End time value: {end_time} (type: {type(end_time)})")
                    if isinstance(end_time, str):
                        # Try to parse as timestamp first, then as ISO string
                        try:
                            end_dt = datetime.fromtimestamp(int(end_time))
                            stats_lines.append(
                                f"🏁 **End:** {end_dt.strftime('%Y-%m-%d %H:%M UTC')}"
                            )
                        except ValueError:
                            # Not a timestamp, try ISO format
                            end_dt = datetime.fromisoformat(end_time.replace("Z", "+00:00"))
                            stats_lines.append(
                                f"🏁 **End:** {end_dt.strftime('%Y-%m-%d %H:%M UTC')}"
                            )
                    elif isinstance(end_time, (int, float)):
                        end_dt = datetime.fromtimestamp(end_time)
                        stats_lines.append(
                            f"🏁 **End:** {end_dt.strftime('%Y-%m-%d %H:%M UTC')}"
                        )
                    else:
                        stats_lines.append(f"🏁 **End:** {end_time}")
                except Exception as time_error:
                    logger.debug(f"Error parsing end time: {time_error}")
                    stats_lines.append(f"🏁 **End:** {end_time}")

            # CTF status
            if start_time and end_time:
                now = datetime.now()
                try:
                    if isinstance(start_time, str):
                        start_dt = datetime.fromisoformat(
                            start_time.replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                    elif isinstance(start_time, (int, float)):
                        start_dt = datetime.fromtimestamp(start_time)

                    if isinstance(end_time, str):
                        end_dt = datetime.fromisoformat(
                            end_time.replace("Z", "+00:00")
                        ).replace(tzinfo=None)
                    elif isinstance(end_time, (int, float)):
                        end_dt = datetime.fromtimestamp(end_time)

                    if now < start_dt:
                        stats_lines.append("⏳ **Status:** Not Started")
                    elif now > end_dt:
                        stats_lines.append("🔚 **Status:** Finished")
                    else:
                        stats_lines.append("🔥 **Status:** Running")
                except Exception as status_error:
                    logger.debug(f"Error determining CTF status: {status_error}")

            message = "\n".join(stats_lines)
            await interaction.followup.send(message)
            logger.info("Stats command completed successfully")

        except Exception as e:
            logger.error(f"Error in stats command: {e}")
            try:
                await interaction.followup.send("❌ Error fetching CTF statistics")
            except Exception as followup_error:
                logger.error(f"Failed to send error message: {followup_error}")

    @bot.tree.command(name="about", description="Show information about this bot")
    async def about(interaction: discord.Interaction):
        """Show information about the bot including source code and attribution"""
        logger.info(f"About command requested by {interaction.user}")

        embed = discord.Embed(
            title="🤖 OneCTFDAnnouncer Bot",
            description="A Discord bot for CTFd first blood announcements and team statistics",
            color=0x00ff00
        )

        embed.add_field(
            name="📋 Features",
            value="• First blood announcements\n• Top 10 teams leaderboard\n• CTF statistics\n• Real-time CTFd integration",
            inline=False
        )

        embed.add_field(
            name="🔗 Source Code",
            value="[GitHub Repository](https://github.com/ept-team/OneCTFDAnnouncer)",
            inline=False
        )

        embed.add_field(
            name="👨‍💻 Development",
            value="All code written by **Claude** (Anthropic's AI Assistant)\nCreated for the EPT",
            inline=False
        )

        embed.add_field(
            name="🐳 Docker Images",
            value="Available on [GitHub Container Registry](https://ghcr.io/ept-team/onectfdannouncer)",
            inline=False
        )

        embed.add_field(
            name="📜 License",
            value="Open source - check the repository for license details",
            inline=False
        )

        embed.set_footer(text="Made with ❤️ by Claude AI")
        embed.set_thumbnail(url="https://avatars.githubusercontent.com/u/66131880")  # You can replace with your team's avatar

        try:
            await interaction.response.send_message(embed=embed)
            logger.info("About command completed successfully")
        except Exception as e:
            logger.error(f"Error in about command: {e}")
            try:
                await interaction.response.send_message("❌ Error displaying bot information")
            except Exception as fallback_error:
                logger.error(f"Failed to send error message: {fallback_error}")

