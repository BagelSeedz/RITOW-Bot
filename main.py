import discord
from discord import option
import os
from dotenv import load_dotenv
from faceit.client import FaceitClient
from faceit.webhook import WebhookHandler
import asyncio

import commands.search_player

# env
load_dotenv()

# Setup Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# Faceit Client
faceit = FaceitClient(os.getenv("FACEIT_API_KEY"))

# Local Functions
def is_manager(member):
    return member.id == int(os.getenv("MANAGER_ID"))

def id_from_mention(mention: str):
    if not mention:
        return None
    return int(mention[2:].removesuffix(">"))

def get_role_color(role):
    if role == "Tank":
        return 10066431
    elif role == "Damage":
        return 16744576
    elif role == "Support":
        return 16777088
    return None

@bot.event
async def on_ready():
    results = await faceit.search_player("_Harlow_")
    for player in results["items"]:
        print(player["nickname"])
        print(player["player_id"])

    print(f'We have logged in as {bot.user}')

@bot.slash_command(description="View the stats of a player")
@option("bnet_tag_numbers", description="Enter Battle.net #numbers", required=False, default=None)
async def search_player(ctx, bnet_name, bnet_tag_numbers=None):
    await commands.search_player.cmd(ctx, bnet_name, bnet_tag_numbers)

async def main():
    await faceit.start()

    web_handler = WebhookHandler(bot)
    web_runner = await web_handler.start_web_server()
    try:
        await bot.start(
            os.getenv("DISCORD_TOKEN")
        )
    finally:
        await web_runner.cleanup()
        await faceit.close()

asyncio.run(main())