async def run(ctx, team_mention, scrim_level, Team, User, db, bot):
    try:
        scrim_level = float(scrim_level)
    except ValueError:
        await ctx.respond("Please us a valid scrim_level (number)")
        return

    guild = bot.get_guild(ctx.guild.id)
    if not guild:
        await ctx.respond("No access :(", ephemeral=True)
        return
    
    role = guild.get_role(int(team_mention[3:].removesuffix(">")))
    if not role:
        await ctx.respond("No team role found.", ephemeral=True)
        return
    
    team_found = Team.query.filter_by(teamID=role.id).first()
    if team_found != None:
        await ctx.respond("This team already exists.", ephemeral=True)
        return
    
    team = Team(role.id, role.name, ctx.author.id, scrim_level)
    db.session.add(team)
    db.session.commit()

    for member in role.members:
        user = User.query.filter_by(discordID=member.id).first()
        if user != None: # only add users that have registered their profile
            user.set_team_id(team.teamID)
            team.add_member(member.id)
    
    await ctx.respond("Succesfully created team: " + team.name)