import os
import json
import signal
import sys
import discord
from discord.ext import commands

def cleanup_and_exit(signum, frame):
    try:
        if not bot.is_closed():
            bot.loop.create_task(bot.close())
    except Exception:
        pass
    sys.exit(0)

signal.signal(signal.SIGINT, cleanup_and_exit)
signal.signal(signal.SIGTERM, cleanup_and_exit)
if hasattr(signal, 'SIGBREAK'):
    signal.signal(signal.SIGBREAK, cleanup_and_exit)

WEBHOOKS = {}
webhook_path = os.path.join(os.path.dirname(__file__), "..", "webhook.json")
if os.path.exists(webhook_path):
    with open(webhook_path, "r", encoding="utf-8") as f:
        WEBHOOKS = json.load(f)

BOT_TOKEN = WEBHOOKS.get("bot_token")

intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix="!", intents=intents)


@bot.command(name="clear")
@commands.has_permissions(manage_messages=True)
async def clear(ctx, amount: int = 10):
    if amount > 100:
        amount = 100
    deleted = await ctx.channel.purge(limit=amount + 1)
    await ctx.send(f"{len(deleted)} messages deleted.", delete_after=3)

if __name__ == "__main__":
    if not BOT_TOKEN:
        print("Erreur: token missing in webhook.json")
    else:
        bot.run(BOT_TOKEN)