# Discord Bot Invite Link Generator

## Required Permissions

Your bot needs these Discord permissions:
- **Send Messages** - To announce first bloods
- **Use Slash Commands** - For the /top10 command  
- **Read Message History** - To access channel data
- **View Channel** - To see channels
- **Embed Links** - For rich message formatting
- **Add Reactions** - For message reactions (optional)

## Permission Value

The calculated permission integer is: **2147518464**

## Generate Invite Link

1. Go to [Discord Developer Portal](https://discord.com/developers/applications)
2. Select your application/bot
3. Go to "General Information" and copy your **Application ID**
4. Use this URL template (replace `YOUR_BOT_ID` with your Application ID):

```
https://discord.com/api/oauth2/authorize?client_id=YOUR_BOT_ID&permissions=2147518464&scope=bot%20applications.commands
```

## Quick Setup

Run the included script to generate your specific invite link:

```bash
python generate_invite.py
```

You'll be prompted for your bot's Application ID, and it will generate the complete invite URL.
