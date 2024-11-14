import discord

def create_view_for_role(role):
    if role == "Tank":
        return discord.ui.View(
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="D.VA", custom_id="dva"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Doomfist", custom_id="doomfist"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Junker Queen", custom_id="junker-queen"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Mauga", custom_id="mauga"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Orisa", custom_id="orisa"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Ramattra", custom_id="ramattra"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Reinhardt", custom_id="reinhardt"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Roadhog", custom_id="roadhog"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Sigma", custom_id="sigma"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Winston", custom_id="winston"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Wrecking Ball", custom_id="wrecking-ball"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Zarya", custom_id="zarya"),
            discord.ui.Button(style=discord.ButtonStyle.red, label="DONE", custom_id="done_button"),
            timeout=None
        )
    elif role == "Damage":
        return discord.ui.View(
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Ashe", custom_id="ashe"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Bastion", custom_id="bastion"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Cassidy", custom_id="cassidy"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Echo", custom_id="echo"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Genji", custom_id="genji"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Hanzo", custom_id="hanzo"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Junkrat", custom_id="junkrat"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Mei", custom_id="mei"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Pharah", custom_id="pharah"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Reaper", custom_id="reaper"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Sojourn", custom_id="sojourn"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Soldier: 76", custom_id="solider-76"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Sombra", custom_id="sombra"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Symmetra", custom_id="symmetra"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Torbjorn", custom_id="torbjorn"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Tracer", custom_id="tracer"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Venture", custom_id="venture"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Widowmaker", custom_id="widowmaker"),
            discord.ui.Button(style=discord.ButtonStyle.red, label="DONE", custom_id="done_button"),
            timeout=None
        )
    elif role == "Support":
        return discord.ui.View(
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Ana", custom_id="ana"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Baptiste", custom_id="baptiste"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Brigitte", custom_id="brigitte"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Illari", custom_id="illari"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Juno", custom_id="juno"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Kiriko", custom_id="kiriko"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Lifeweaver", custom_id="lifeweaver"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Lucio", custom_id="lucio"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Mercy", custom_id="mercy"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Moira", custom_id="moira"),
            discord.ui.Button(style=discord.ButtonStyle.blurple, label="Zenyatta", custom_id="zenyatta"),
            discord.ui.Button(style=discord.ButtonStyle.red, label="DONE", custom_id="done_button"),
            timeout=None
        )
    
async def run(ctx, bot, user, db):
    await ctx.defer()

    def interaction_check(interaction):
        return interaction.channel == ctx.channel

    role_menu = discord.ui.Select(options=[
        discord.SelectOption(label="Tank"),
        discord.SelectOption(label="Damage"),
        discord.SelectOption(label="Support")
    ])
    view = discord.ui.View(role_menu, timeout=None)
    followup = await ctx.send_followup("Select a role:", view=view, ephemeral=True)
    await bot.wait_for("interaction", check=interaction_check)
    await followup.delete()
    role = role_menu.values[0]

    sub_role_menu = discord.ui.Select(options=[
        discord.SelectOption(label="Main"),
        discord.SelectOption(label="Flex")
    ])
    view = discord.ui.View(sub_role_menu, timeout=None)
    followup = await ctx.send_followup("Select a sub-role:", view=view, ephemeral=True)
    await bot.wait_for("interaction", check=interaction_check)
    await followup.delete()
    sub_role = sub_role_menu.values[0]

    heroes = set()
    view = create_view_for_role(role)
    done = False
    lastfollowup = await ctx.send_followup(f"Click all the heroes that you play for this role.\nHeroes: {str(heroes)}", view=view)
    while not done:
        interaction = await bot.wait_for("interaction", check=interaction_check)
        if interaction.custom_id == "done_button":
            done = True
            await lastfollowup.delete()
        else:
            heroes.add(interaction.custom_id)
            await lastfollowup.delete()
            lastfollowup = await ctx.send_followup(f"**Click all the heroes that you play for this role.**\nHeroes: {str(heroes)}", view=view)

    user.set_role(role)
    user.set_sub_role(sub_role)
    user.set_heroes(str(heroes))
    db.session.commit()

    await ctx.send_followup("__Profile successfully created__\n" + str(user))