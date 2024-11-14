import discord
from discord import option
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

import commands.create_profile
import commands.search_player

# env
load_dotenv()

# Setup Discord Bot
intents = discord.Intents.default()
intents.message_content = True
bot = discord.Bot(intents=intents)

# Flask app setup
app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///users.sqlite3'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database
db = SQLAlchemy(app)

class User(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    discordID = db.Column("discordID", db.Integer)
    name = db.Column("name", db.String(100))
    role = db.Column("role", db.String(10))
    sub_role = db.Column("sub-role", db.String(10))
    heroes = db.Column("heroes", db.String(5000))
    teamID = db.Column("teamID", db.Integer)

    def __init__(self, discordID, name):
        self.discordID = discordID
        self.name = name
        self.role = None
        self.sub_role = None
        self.heroes = None
        self.teamID = None
    
    def set_role(self, role):
        self.role = role
    
    def set_sub_role(self, sub_role):
        self.sub_role = sub_role
    
    def set_heroes(self, heroes):
        self.heroes = heroes
    
    def set_team_id(self, teamID):
        self.teamID = teamID

    def __str__(self):
        return f"ID: {self.discordID}\nName: {self.name}\nTeam: {self.teamID}\nRole: {self.role}\nSub-role: {self.sub_role}\nHeroes: {self.heroes}"

class Team(db.Model):
    _id = db.Column("id", db.Integer, primary_key=True)
    teamID = db.Column("teamID", db.Integer)
    name = db.Column("name", db.String(40))
    captain = db.Column("captain", db.Integer)
    members = db.Column("members", db.String(5000))
    scrim_level = db.Column("scrim_level", db.Numeric(10, 1))

    def __init__(self, teamID, name, captain, scrim_level):
        self.teamID = teamID
        self.name = name
        self.captain = captain
        self.scrim_level = scrim_level
        self.members = "set()"

    def set_captain(self, captain):
        self.captain = captain
        db.session.commit()

    def set_scrim_level(self, scrim_level):
        self.scrim_level = scrim_level
        db.session.commit()

    def add_member(self, member_id): # This is used
        member_set = eval(self.members)
        member_set.add(member_id)
        self.members = str(member_set)
        db.session.commit()
    
    def remove_member(self, member_id):
        member_set = eval(self.members)
        try:
            member_set.remove(member_id)
        except KeyError:
            return False
        self.members = str(member_set)
        db.session.commit()
        return True
    
    def __str__(self):
        return f"ID: {self.teamID}\nName: {self.name}\n"

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
    print(f'We have logged in as {bot.user}')

@bot.slash_command()
@option("bnet_tag_numbers", description="Enter Battle.net #numbers", required=False, default=None)
async def search_player(ctx, bnet_name, bnet_tag_numbers=None):
    await commands.search_player.cmd(ctx, bnet_name, bnet_tag_numbers)

@bot.slash_command()
async def create_profile(ctx):
    user = User.query.filter_by(discordID=ctx.author.id).first()
    if not user:
        user = User(ctx.author.id, ctx.author.name)
        db.session.add(user)
        db.session.commit()
    
    await commands.create_profile.run(ctx, bot, user, db)
    

@bot.slash_command()
@option("mention", description="@ a member whose profile you want to see", required=False, default=None)
async def show_profile(ctx, mention=None):
    member_id = ctx.author.id
    if mention != None:
        member_id = id_from_mention(mention)

    user = User.query.filter_by(discordID=member_id).first()
    if not user:
        await ctx.respond("Profile does not exist.", ephemeral=True)
        return

    await ctx.respond(str(user))

@bot.slash_command()
@option("mention", description="@ a member whose profile should get deleted.", required=True)
async def delete_profile(ctx, mention):
    mention_id = id_from_mention(mention)
    if mention_id != ctx.author.id and not is_manager(ctx.author):
        await ctx.respond("This command can only be used by the manager.", ephemeral=True)
        return
    
    user = User.query.filter_by(discordID=mention_id)
    if user.count():
        user.delete()
        db.session.commit()
        await ctx.respond(f"Successfully deleted profile for <@{mention_id}>.")
    else:
        await ctx.respond(f"Could not find profile for <@{mention_id}>.", ephemeral=True)

@bot.slash_command()
async def sub(ctx, mention):
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
        description=f"{ctx.author.mention} has requested a sub for <@&{team.teamID}>",
        fields=[
            discord.EmbedField(name="Team", value=team.name),
            discord.EmbedField(name="Scrim-Level", value=str(team.scrim_level), inline=True),
            discord.EmbedField(name="Role", value=user.role),
            discord.EmbedField(name="Sub-Role", value=user.sub_role, inline=True),
            discord.EmbedField(name="Heroes", value=user.heroes)
        ]
    )
    await sub_channel.send(embed=embed)

    await ctx.respond("Created sub request.", ephemeral=True)
    
@bot.slash_command()
async def create_team(ctx, team_mention, scrim_level):
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
    
    team = Team(role.id, role.name, ctx.author.id, scrim_level)
    db.session.add(team)
    db.session.commit()

    for member in role.members:
        user = User.query.filter_by(discordID=member.id).first()
        if user != None: # only add users that have registered their profile
            user.set_team_id(team.teamID)
            team.add_member(member.id)
    
    await ctx.respond("Succesfully created team: " + team.name)

@bot.slash_command()
async def join_team(ctx, team_mention):
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

@bot.slash_command()
@option("mention", description="@ a member who should be removed from their team", required=True)
async def leave_team(ctx, mention):
    mention_id = id_from_mention(mention)
    if mention_id != ctx.author.id and not is_manager(ctx.author):
        await ctx.respond("This command can only be used by the manager.", ephemeral=True)
        return

    user = User.query.filter_by(discordID=mention_id).first()
    if not user:
        await ctx.respond("The member mentioned is not registered.", ephemeral=True)
        return
    if user.teamID == None:
        await ctx.respond("The member mentioned is not part of a team.", ephemeral=True)
        return
    
    team = Team.query.filter_by(teamID=user.teamID).first()
    team.remove_member(user.discordID)
    user.set_team_id(None)
    await ctx.respond("Successfully removed the member from the team.")

@bot.slash_command()
async def show_team(ctx, team_mention):
    guild = bot.get_guild(ctx.guild.id)
    if not guild:
        await ctx.respond("No access :(", ephemeral=True)
        return
    
    team_id = int(team_mention[3:].removesuffix(">"))
    team = Team.query.filter_by(teamID=team_id).first()
    if not team:
        await ctx.respond("Team not found.", ephemeral=True)
        return
    
    await ctx.respond(team.name + ": " + team.members)

@bot.slash_command()
async def update_scrim_level(ctx, scrim_level):
    try:
        scrim_level = float(scrim_level)
    except ValueError:
        await ctx.respond("Please us a valid scrim_level (number)")
        return
    
    user = User.query.filter_by(discordID=ctx.author.id).first()
    if not user:
        await ctx.respond("You must be registered to use this command.", ephemeral=True)
        return
    if user.teamID == None:
        await ctx.respond("You must be on a team to use this command.", ephemeral=True)
        return
    
    team = Team.query.filter_by(teamID=user.teamID).first()
    if team.captain != user.discordID:
        await ctx.respond("You must be the captain of your team to use this command.", ephemeral=True)
        return
    
    team.set_scrim_level(scrim_level)
    await ctx.respond("Successfully set scrim level to " + str(scrim_level))

def main():
    with app.app_context():
        db.create_all()
        bot.run(os.getenv("TOKEN"))

main()