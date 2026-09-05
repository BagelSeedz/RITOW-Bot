import discord
import asyncio
import os

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

async def run(ctx, mention,  when, User, Team, Sub, db, bot, SUB_ROLE_ENV):
    guild = bot.get_guild(ctx.guild.id)
    if not guild:
        await ctx.respond("No access :(")
        return

    member_id = id_from_mention(mention)
    member = guild.get_member(member_id)
    user = User.query.filter_by(discordID=member_id).first()
    if not member or not user:
        await ctx.respond("Error: Could not find user in mention.")
        return
    
    team = Team.query.filter_by(teamID=user.teamID).first()
    if not team:
        await ctx.respond("User is not part of a team!")
    
    sub_channel = bot.get_channel(int(os.getenv("SUB_CHANNEL_ID")))
    embed = discord.Embed(
        color=get_role_color(user.role),
        title="Substitution Requested❗",
        description=f"{ctx.author.mention} has requested a sub for <@{member_id}>",
        fields=[
            discord.EmbedField(name="When?", value=when, inline=True),
            discord.EmbedField(name="Team", value=team.name, inline=True),
            discord.EmbedField(name="Scrim-Level", value=str(team.scrim_level), inline=True),
            discord.EmbedField(name="Role", value=user.role, inline=True),
            discord.EmbedField(name="Sub-Role", value=user.sub_role, inline=True),
            discord.EmbedField(name="Heroes", value=user.heroes, inline=True)
        ]
    )
    view = discord.ui.View(
        discord.ui.Button(style=discord.ButtonStyle.green, label="SUB", custom_id="sub_button"),
        discord.ui.Button(style=discord.ButtonStyle.red, label="CANCEL", custom_id="cancel_button"),
        timeout=None
    )
    sub_message = await sub_channel.send(embed=embed, view=view)
    await sub_channel.send(f"<@&{os.getenv(SUB_ROLE_ENV)}>")
    await ctx.respond("Created sub request.", ephemeral=True)

    def __on_sub(interaction):
        return interaction.message == sub_message
    
    while True:
        interaction = await bot.wait_for("interaction", check=__on_sub)
        
        if interaction.custom_id == "sub_button":
            interaction_user = User.query.filter_by(discordID=interaction.user.id).first()
            if not interaction_user:
                await interaction.respond("You must be registered to sub.")
                continue
            
            await interaction.respond("Submission Logged.", ephemeral=True)
            accept_message = await sub_channel.send(f"{ctx.author.mention} | {interaction.user.mention} wants to sub for {user.name}\nReact to this message to acccept")
            def __react_check(reaction, reaction_user):
                return reaction.message == accept_message and reaction_user.id == ctx.author.id
            try:
                _, reaction_user = await bot.wait_for("reaction_add", check=__react_check, timeout=43200)
            except asyncio.TimeoutError:
                break
            
            sub = Sub(reaction_user.id, team.teamID, when)
            db.session.add(sub)
            db.session.commit()

            await sub_channel.send(f"{reaction_user.mention} You will be subbing for {user.name}.\nJoin a vc at ``{when}`` and ask to be dragged.")
            await sub_message.edit(content="Sub found.", embed=embed, view=None)
            break

        elif interaction.custom_id == "cancel_button" and interaction.user.id == ctx.author.id:
            await sub_message.edit(content="Cancelled", embed=embed, view=None)
            await interaction.respond("Sub request cancelled.")
            break