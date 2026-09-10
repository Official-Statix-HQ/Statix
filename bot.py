import os
import platform
import time
from datetime import datetime, timezone

import discord
from discord import app_commands
from discord.ext import commands
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("DISCORD_TOKEN")

if not TOKEN:
    raise RuntimeError(
        "DISCORD_TOKEN environment variable is not set. "
        "Add it to your .env file locally or to your Railway variables."
    )

intents = discord.Intents.default()
intents.message_content = True

bot = commands.Bot(command_prefix="!", intents=intents)
bot.start_time = time.time()


@bot.event
async def on_ready():
    print("=" * 50)
    print(f"Logged in as: {bot.user} (ID: {bot.user.id})")
    print(f"discord.py version: {discord.__version__}")
    print(f"Connected to {len(bot.guilds)} guild(s)")
    print("=" * 50)

    try:
        synced = await bot.tree.sync()
        print(f"Synced {len(synced)} slash command(s).")
    except Exception as e:
        print(f"Failed to sync commands: {e}")

    await bot.change_presence(
        status=discord.Status.online,
        activity=discord.Activity(
            type=discord.ActivityType.watching, name="/botinfo | 24/7 online"
        ),
    )


# ---------------------------------------------------------------------------
# /send — send a message through the bot into a chosen channel
# ---------------------------------------------------------------------------
@bot.tree.command(name="send", description="Send a message through the bot.")
@app_commands.describe(
    message="The message you want the bot to send.",
    channel="The channel to send the message to (defaults to this channel).",
)
@app_commands.checks.has_permissions(manage_messages=True)
async def send(
    interaction: discord.Interaction,
    message: str,
    channel: discord.TextChannel = None,
):
    target_channel = channel or interaction.channel

    bot_member = target_channel.guild.me
    perms = target_channel.permissions_for(bot_member)
    if not perms.send_messages:
        await interaction.response.send_message(
            f"I don't have permission to send messages in {target_channel.mention}.",
            ephemeral=True,
        )
        return

    try:
        await target_channel.send(message)
        await interaction.response.send_message(
            f"Message sent to {target_channel.mention}.", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "I don't have permission to send messages there.", ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"Failed to send message: {e}", ephemeral=True
        )


# ---------------------------------------------------------------------------
# /announce — send a formatted announcement through the bot
# ---------------------------------------------------------------------------
@bot.tree.command(name="announce", description="Send an announcement through the bot.")
@app_commands.describe(
    message="The announcement text.",
    channel="The channel to post the announcement in (defaults to this channel).",
    title="Optional title for the announcement embed.",
)
@app_commands.checks.has_permissions(manage_messages=True)
async def announce(
    interaction: discord.Interaction,
    message: str,
    channel: discord.TextChannel = None,
    title: str = "📢 Announcement",
):
    target_channel = channel or interaction.channel

    bot_member = target_channel.guild.me
    perms = target_channel.permissions_for(bot_member)
    if not perms.send_messages or not perms.embed_links:
        await interaction.response.send_message(
            f"I need Send Messages and Embed Links permissions in {target_channel.mention}.",
            ephemeral=True,
        )
        return

    embed = discord.Embed(
        title=title,
        description=message,
        color=discord.Color.blurple(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_footer(
        text=f"Announced by {interaction.user.display_name}",
        icon_url=interaction.user.display_avatar.url,
    )

    try:
        await target_channel.send(embed=embed)
        await interaction.response.send_message(
            f"Announcement posted in {target_channel.mention}.", ephemeral=True
        )
    except discord.Forbidden:
        await interaction.response.send_message(
            "I don't have permission to post there.", ephemeral=True
        )
    except discord.HTTPException as e:
        await interaction.response.send_message(
            f"Failed to post announcement: {e}", ephemeral=True
        )


# ---------------------------------------------------------------------------
# /ping — check if the bot is online
# ---------------------------------------------------------------------------
@bot.tree.command(name="ping", description="Check if the bot is online.")
async def ping(interaction: discord.Interaction):
    latency_ms = round(bot.latency * 1000)
    await interaction.response.send_message(f"🏓 Pong! Latency: {latency_ms}ms")


# ---------------------------------------------------------------------------
# /botinfo — show bot information and status
# ---------------------------------------------------------------------------
@bot.tree.command(name="botinfo", description="Show bot information and status.")
async def botinfo(interaction: discord.Interaction):
    uptime_seconds = int(time.time() - bot.start_time)
    days, remainder = divmod(uptime_seconds, 86400)
    hours, remainder = divmod(remainder, 3600)
    minutes, seconds = divmod(remainder, 60)
    uptime_str = f"{days}d {hours}h {minutes}m {seconds}s"

    embed = discord.Embed(
        title=f"{bot.user.name} — Bot Info",
        color=discord.Color.green(),
        timestamp=datetime.now(timezone.utc),
    )
    embed.set_thumbnail(url=bot.user.display_avatar.url)
    embed.add_field(name="Status", value="🟢 Online", inline=True)
    embed.add_field(name="Latency", value=f"{round(bot.latency * 1000)}ms", inline=True)
    embed.add_field(name="Uptime", value=uptime_str, inline=True)
    embed.add_field(name="Servers", value=str(len(bot.guilds)), inline=True)
    embed.add_field(
        name="Users",
        value=str(sum(g.member_count for g in bot.guilds)),
        inline=True,
    )
    embed.add_field(name="discord.py", value=discord.__version__, inline=True)
    embed.add_field(name="Python", value=platform.python_version(), inline=True)
    embed.set_footer(text=f"Bot ID: {bot.user.id}")

    await interaction.response.send_message(embed=embed)


# ---------------------------------------------------------------------------
# Error handling for permission checks
# ---------------------------------------------------------------------------
@send.error
@announce.error
async def permission_error_handler(interaction: discord.Interaction, error: app_commands.AppCommandError):
    if isinstance(error, app_commands.MissingPermissions):
        await interaction.response.send_message(
            "You need the **Manage Messages** permission to use this command.",
            ephemeral=True,
        )
    else:
        if interaction.response.is_done():
            await interaction.followup.send(f"An error occurred: {error}", ephemeral=True)
        else:
            await interaction.response.send_message(
                f"An error occurred: {error}", ephemeral=True
            )


if __name__ == "__main__":
    bot.run(TOKEN)
