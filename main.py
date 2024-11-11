import discord
from discord import option
from dotenv import load_dotenv
import os

import commands.search_player

load_dotenv()

intents = discord.Intents.default()
intents.message_content = True

bot = discord.Bot(intents=intents)

@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command()
@option("bnet_tag_numbers", description="Enter Battle.net #numbers", required=False, default=None)
async def search_player(ctx, bnet_name, bnet_tag_numbers=None):
    await commands.search_player.cmd(ctx, bnet_name, bnet_tag_numbers)

def main():
    bot.run(os.getenv("TOKEN"))

main()