async def run(ctx, team_mention, User, Team, bot):
    guild = bot.get_guild(ctx.guild.id)
    if not guild:
        await ctx.respond("No access :(", ephemeral=True)
        return
    
    role = guild.get_role(int(team_mention[3:].removesuffix(">")))
    if not role:
        await ctx.respond("No team role found.", ephemeral=True)
        return
    
    if role not in ctx.author.roles:
        await ctx.respond("You must have the team's role to use this command.", ephemeral=True)
        return
    
    user = User.query.filter_by(discordID=ctx.author.id).first()
    if not user:
        await ctx.respond("You must be registered to join a team. Use ``/create_profile`` to register.")
        return
    
    team = Team.query.filter_by(teamID=role.id).first()
    if not team:
        await ctx.respond("Team is not registered. Ask the captain to use ``/create_team``")
        return

    user.set_team_id(team.teamID)
    team.add_member(user.discordID)
    await ctx.respond(f"Successfully added you to the ``{team.name}`` team.")