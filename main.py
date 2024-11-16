import discord
from discord import option
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import asyncio

import commands.create_profile
import commands.create_team
import commands.join_team
import commands.search_player
import commands.sub

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
        team_name = "No team"
        if self.teamID:
            team_name = Team.query.filter_by(teamID=self.teamID).first().name
        output = f"ID: {self.discordID}\nName: {self.name}\nTeam: {team_name}\nRole: {self.role}\nSub-role: {self.sub_role}\n"
        hero_list = "Heroes: "
        for hero in eval(self.heroes):
            hero_list += hero.capitalize() + " "
        output += hero_list
        return output

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
        output = f"ID: {self.teamID}\nName: {self.name}\nCaptain: <@{self.captain}>\nScrim-Level: {str(self.scrim_level)}\n"
        member_list = "Members: "
        for member in eval(self.members):
            member_list += f"<@{str(member)}> "
        output += member_list
        return output

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

@bot.slash_command(description="View the stats of a player")
@option("bnet_tag_numbers", description="Enter Battle.net #numbers", required=False, default=None)
async def search_player(ctx, bnet_name, bnet_tag_numbers=None):
    await commands.search_player.cmd(ctx, bnet_name, bnet_tag_numbers)

@bot.slash_command(description="Create a profile in the database")
async def create_profile(ctx):
    user = User.query.filter_by(discordID=ctx.author.id).first()
    if not user:
        user = User(ctx.author.id, ctx.author.name)
        db.session.add(user)
        db.session.commit()
    
    await commands.create_profile.run(ctx, bot, user, db)
    

@bot.slash_command(description="Show a user's profile")
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

@bot.slash_command(description="Delete a user's profile")
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

@bot.slash_command(description="Ask for a sub")
@option("mention", description="@ a teammate who needs to be subbed.", required=True)
@option("when", description="When do you need a sub? (Day and time)", required=False)
async def sub(ctx, mention, when="Now!"):
    await commands.sub.run(ctx, mention, when, User, Team, bot, os.getenv("SUB_ROLE"))
    
@bot.slash_command(description="Create a team in the database")
@option("team_mention", description="@ a team to add to the database", required=True)
@option("scrim_level", description="ELO the team scrims (can be changed)", required=True)
async def create_team(ctx, team_mention, scrim_level):
    await commands.create_team.run(ctx, team_mention, scrim_level, Team, User, db, bot)

@bot.slash_command(description="Join a team in the database")
@option("team_mention", description="@ the team you want to join", required=True)
async def join_team(ctx, team_mention):
    await commands.join_team.run(ctx, team_mention, User, Team, bot)

@bot.slash_command(description="Leave a team")
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

@bot.slash_command(description="View team details")
@option("team_mention", description="@ the team you want to see", required=True)
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
    
    await ctx.respond(str(team))

@bot.slash_command(description="Update your team's scrim level")
@option("scrim_level", description="ELO the team scrims (can be changed)", required=True)
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

@bot.slash_command(description="Set the captain of a team")
@option("captain_mention", description="@ the member who should be promoted to captain", required=True)
async def set_team_captain(ctx, team_mention, captain_mention):
    if not is_manager(ctx.author):
        await ctx.respond("Only the manager can use this command.", ephemeral=True)
        return
    
    team_id = int(team_mention[3:].removesuffix(">"))
    team = Team.query.filter_by(teamID=team_id).first()
    if not team:
        await ctx.respond("Team not found.", ephemeral=True)
        return
    
    captain_id = id_from_mention(captain_mention)
    if team.members.find(str(captain_id)) == -1:
        await ctx.respond("Member must be part of the team mentioned to be considered for captain.", ephemeral=True)
        return

    team.set_captain(captain_id)
    await ctx.respond(f"Successfully made <@{captain_id}> the captain of <@&{team_id}>!")

@bot.slash_command(description="Delete a team in the database")
@option(name="team_mention", description="@ the team that should be deleted in the database", required=True)
async def delete_team(ctx, team_mention):
    if not is_manager(ctx.author):
        await ctx.respond("Only the manager can use this command.", ephemeral=True)
        return
    
    team_id = int(team_mention[3:].removesuffix(">"))
    team = Team.query.filter_by(teamID=team_id)
    if team.count() == 0:
        await ctx.respond("Team not found.", ephemeral=True)
        return
    
    team.delete()
    db.commit()
    await ctx.respond("Successfully deleted team.")

def main():
    with app.app_context():
        db.create_all()
        bot.run(os.getenv("TOKEN"))

main()