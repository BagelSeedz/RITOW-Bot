import discord
from discord import option
import os
from dotenv import load_dotenv
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

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
    heroes = db.Column("heroes", db.String(1000))

    def __init__(self, discordID, name):
        self.discordID = discordID
        self.name = name
        self.role = None
        self.sub_role = None
        self.heroes = None
    
    def set_role(self, role):
        self.role = role
    
    def set_sub_role(self, sub_role):
        self.sub_role = sub_role
    
    def set_heroes(self, heroes):
        self.heroes = heroes
    
    def __str__(self):
        return f"ID: {self.discordID}\nName: {self.name}\nRole: {self.role}\nSub-role: {self.sub_role}\nHeroes: {self.heroes}"

# Local Functions
def is_manager(member):
    return member.id == int(os.getenv("MANAGER_ID"))

def id_from_mention(mention: str):
    if not mention:
        return None
    return int(mention[2:].removesuffix(">"))

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


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')

@bot.slash_command()
@option("bnet_tag_numbers", description="Enter Battle.net #numbers", required=False, default=None)
async def search_player(ctx, bnet_name, bnet_tag_numbers=None):
    await commands.search_player.cmd(ctx, bnet_name, bnet_tag_numbers)

@bot.slash_command()
async def create_profile(ctx):
    await ctx.defer()

    user = User.query.filter_by(discordID=ctx.author.id).first()
    if not user:
        user = User(ctx.author.id, ctx.author.name)
        db.session.add(user)
        db.session.commit()
    
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
            lastfollowup = await ctx.send_followup(f"**Click all the heroes that you play for this role.**\nDisregard the 'interaction failed'\nHeroes: {str(heroes)}", view=view)

    user.set_role(role)
    user.set_sub_role(sub_role)
    user.set_heroes(str(heroes))

    await ctx.send_followup("__Profile successfully created__\n" + str(user))

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

def main():
    with app.app_context():
        db.create_all()
        bot.run(os.getenv("TOKEN"))

main()