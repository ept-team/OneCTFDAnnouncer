#!/usr/bin/env python3
"""
Generate Discord bot invite link with correct permissions.
"""

import discord
from onectfdannouncer.config import DISCORD_TOKEN


def generate_invite_link():
    """Generate invite link with required permissions."""

    # Required permissions for the bot
    permissions = discord.Permissions(
        send_messages=True,  # Send first blood announcements
        use_application_commands=True,  # For /top10 slash command
        read_message_history=True,  # To access channels
        view_channel=True,  # To see channels
        embed_links=True,  # For rich message formatting (optional)
        add_reactions=True,  # For message reactions (optional)
    )

    # Get application ID from token (you'll need to replace this)
    print("To generate invite link, you need your bot's Application/Client ID")
    print(
        "You can find this in Discord Developer Portal > Your Application > General Information"
    )
    print()

    app_id = input("Enter your bot's Application/Client ID: ").strip()

    if not app_id:
        print("Error: Application ID is required")
        return

    try:
        # Generate invite URL
        invite_url = discord.utils.oauth_url(
            client_id=app_id,
            permissions=permissions,
            scopes=["bot", "applications.commands"],
        )

        print("\n" + "=" * 60)
        print("DISCORD BOT INVITE LINK")
        print("=" * 60)
        print(f"\n{invite_url}\n")
        print("Required permissions included:")
        print("- Send Messages (for announcements)")
        print("- Use Application Commands (for /top10)")
        print("- Read Message History")
        print("- View Channel")
        print("- Embed Links")
        print("- Add Reactions")
        print("\nCopy this link and paste it in your browser to invite the bot!")
        print("=" * 60)

    except Exception as e:
        print(f"Error generating invite link: {e}")


if __name__ == "__main__":
    generate_invite_link()
