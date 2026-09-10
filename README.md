# Discord Bot (discord.py, Railway-ready)

A simple, production-ready Discord bot with slash commands, built for 24/7
uptime on Railway.

## Features

- `/send` — Send a message through the bot into any channel
- `/announce` — Post a formatted announcement embed
- `/ping` — Check bot latency/online status
- `/botinfo` — Show bot stats (uptime, servers, latency, versions)

## Requirements

- Python 3.10+
- A Discord bot token (see QUICKSTART.md for how to get one)

## Local setup

1. Clone/download this project.
2. Create a virtual environment (optional but recommended):
```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
```
3. Install dependencies:
```bash
   pip install -r requirements.txt
```
4. Copy `.env.example` to `.env` and paste your real token:
```bash
   cp .env.example .env
```
5. Run the bot:
```bash
   python bot.py
```

## Deploying to Railway

See `QUICKSTART.md` for the full step-by-step walkthrough, including creating
the Discord application, inviting the bot, and deploying on Railway.

## Permissions

`/send` and `/announce` require the user to have the **Manage Messages**
permission in the server. This prevents random members from spamming
channels through the bot. You can change or remove this restriction in
`bot.py` by editing the `@app_commands.checks.has_permissions(...)` lines.

## Notes

- The bot token is read from the `DISCORD_TOKEN` environment variable. It is
  never hardcoded in the source code.
- Slash commands are synced automatically every time the bot starts up.
- `message_content` intent is enabled — make sure it's also enabled in the
  Discord Developer Portal under **Bot > Privileged Gateway Intents**.
