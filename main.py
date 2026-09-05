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

def main():
    with app.app_context():
        db.create_all()
        bot.run(os.getenv("TOKEN"))

main()