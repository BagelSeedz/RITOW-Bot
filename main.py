import requests
import datetime
import discord
from discord import option
from dotenv import load_dotenv
import os

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
    await ctx.defer()

    # Get player_id
    if bnet_tag_numbers != None:
        player_id = bnet_name + "-" + str(bnet_tag_numbers)
    else:
        url = f"https://overfast-api.tekrop.fr/players?name={bnet_name}"
        try:
            response = requests.get(url, timeout=10)
        except:
            await ctx.respond("Error.")
            return
        json = response.json()
        if json['total'] == 0:
            await ctx.respond("Error: Player not found")
            return
        player_id = json['results'][0]['player_id']
    
    # Get Player Data
    url = f"https://overfast-api.tekrop.fr/players/{player_id}/summary"
    try:
        response = requests.get(url, timeout=10)
    except:
        await ctx.respond("Error.")
        return
    json = response.json()
    if json.get('error', None) != None:
        await ctx.respond("Error: " + json['error'])
        return

    print(str(json))

    # Create Embeds based on Player data
    embeds = []
    user_embed = discord.Embed(
        color=16750899, 
        title=bnet_name, 
        description=json['title'], 
        thumbnail=json['avatar'],
        fields= [
            discord.EmbedField(
                name="Endorsement Level: ",
                value=json['endorsement']['level']
            )
        ],
        footer=discord.EmbedFooter(f"Last updated: {datetime.datetime.fromtimestamp(json['last_updated_at']).isoformat(sep=" ")}")
    )
    embeds.append(user_embed)

    if json['competitive'] != None and json['competitive']['pc'] != None:
        if json['competitive']['pc']['tank'] != None:
            tank_embed = discord.Embed(
                color=225, 
                title="Tank 🛡️", 
                thumbnail=json['competitive']['pc']['tank']['rank_icon'],
                fields=[
                    discord.EmbedField(
                        name="__Rank__",
                        value= json['competitive']['pc']['tank']['division'].upper() + " " + str(json['competitive']['pc']['tank']['tier']),
                    )
                ]
            )
            embeds.append(tank_embed)
        
        if json['competitive']['pc']['damage'] != None:
            damage_embed = discord.Embed(
                color=16711680, 
                title="Damage 🗡️", 
                thumbnail=json['competitive']['pc']['damage']['rank_icon'],
                fields=[
                    discord.EmbedField(
                        name="__Rank__",
                        value= json['competitive']['pc']['damage']['division'].upper() + " " + str(json['competitive']['pc']['damage']['tier']),
                    )
                ]
            )
            embeds.append(damage_embed)
        
        if json['competitive']['pc']['support'] != None:
            support_embed = discord.Embed(
                color=16750899, 
                title="Support 💉", 
                thumbnail=json['competitive']['pc']['support']['rank_icon'],
                fields=[
                    discord.EmbedField(
                        name="__Rank__",
                        value= json['competitive']['pc']['support']['division'].upper() + " " + str(json['competitive']['pc']['support']['tier']),
                    )
                ]
            )
            embeds.append(support_embed)

    await ctx.send_followup(embeds=embeds, ephemeral=False)


bot.run(os.getenv("TOKEN"))
