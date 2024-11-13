import requests
import discord
import datetime

async def cmd(ctx, bnet_name, bnet_tag_numbers=None):
    await ctx.defer()

    # Get player_id
    if bnet_tag_numbers != None:
        player_id = bnet_name + "-" + str(bnet_tag_numbers)
    else:
        url = f"https://overfast-api.tekrop.fr/players?name={bnet_name}"
        try:
            response = requests.get(url, timeout=10)
        except:
            await ctx.send_followup("Error.", ephemeral=True)
            return
        json = response.json()
        if json['total'] == 0:
            await ctx.send_followup("Error: Player not found", ephemeral=True)
            return
        player_id = json['results'][0]['player_id']
    
    # Get Player Data
    url = f"https://overfast-api.tekrop.fr/players/{player_id}/summary"
    try:
        response = requests.get(url, timeout=10)
    except:
        await ctx.send_followup("Error. Make sure player's profile is set to ``public``", ephemeral=True)
        return
    json = response.json()
    if json.get('error', None) != None:
        await ctx.send_followup("Error: " + json['error'], ephemeral=True)
        return

    # print(str(json))

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
        footer=discord.EmbedFooter(f"Last updated: {datetime.datetime.fromtimestamp(json['last_updated_at']).isoformat(sep=' ')}")
    )
    embeds.append(user_embed)

    if json['competitive'] != None and json['competitive']['pc'] != None:
        if json['competitive']['pc']['tank'] != None:
            tank_embed = discord.Embed(
                color=10066431, 
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
                color=16744576, 
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
                color=16777088, 
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

    await ctx.send_followup(embeds=embeds, ephemeral=False, delete_after=30)