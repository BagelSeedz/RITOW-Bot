import discord
from .client import FaceitClient
import os
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

FACEIT_OUTPUT_CHANNEL_ID = os.getenv("FACEIT_OUTPUT_CHANNEL_ID")

def create_announcement_embed(payload, team1, team2, team1Score, team2Score):
    team1Name = f"| {team1['team_stats']['Team']} |"
    team2Name = f"| {team2['team_stats']['Team']} |"
    score_str =  f"**{team1Score}** - {team2Score}" if team1Score > team2Score else f"{team1Score} - **{team2Score}**"
    return discord.Embed(
        author=discord.EmbedAuthor(payload["payload"]["entity"]["name"]),
        title=f"{team1Name} {score_str} {team2Name}",
        color=0xff6600,
        footer=discord.EmbedFooter(datetime.today().isoformat())
    )

def get_roster(team):
    tank = None
    dps1 = None
    dps2 = None
    sup1 = None
    sup2 = None
    for plr in team["players"]:
        role = plr['player_stats']['Role']
        if role == "Tank":
            tank = f"🛡️ *{plr['nickname']}*"
        elif role == "Damage":
            if dps1 == None:
                dps1 = f"⚔️ *{plr['nickname']}*"
            else:
                dps2 = f"⚔️ *{plr['nickname']}*"
        elif role == "Support":
            if sup1 == None:
                sup1 = f"⛑️ *{plr['nickname']}*"
            else:
                sup2 = f"⛑️ *{plr['nickname']}*"
    roster = [tank, dps1, dps2, sup1, sup2]
    return roster

def create_round_embed(round, round_dict, round_code):
    team1 = round_dict["teams"][0]
    team2 = round_dict["teams"][1]
    team1Name = f"| {team1['team_stats']['Team']} |"
    team2Name = f"| {team2['team_stats']['Team']} |"
    team1Roster = get_roster(team1)
    team2Roster = get_roster(team2)
    team1Elims = [str(plr["player_stats"]["Eliminations"]) for plr in team1["players"]]
    team2Elims = [str(plr["player_stats"]["Eliminations"]) for plr in team2["players"]]
    team1Deaths = [str(plr["player_stats"]["Deaths"]) for plr in team1["players"]]
    team2Deaths = [str(plr["player_stats"]["Deaths"]) for plr in team2["players"]]
    scoreSummary = round_dict['round_stats']['Score Summary']
    team1Score = scoreSummary[0]
    team2Score = scoreSummary[len(scoreSummary)-1]
    winnerName = team1Name if team1Score > team2Score else team2Name    

    embed = discord.Embed(
        title=f"| Round {round} |",
        description=f"**Winner :trophy::** {winnerName}\n" \
                    f"**Mode:** {round_dict['round_stats']['OW2 Mode']}\n" \
                    f"**Score:** {round_dict['round_stats']['Score Summary']}\n" \
                    f"**VOD:** {round_code}",
        color=0xff6600,
        fields=[
            discord.EmbedField(name=team1Name, value="\n\n".join(team1Roster), inline=True),
            discord.EmbedField(name="| Elims |", value="\n\n".join(team1Elims), inline=True),
            discord.EmbedField(name="| Deaths |", value="\n\n".join(team1Deaths), inline=True),
            discord.EmbedField(name=team2Name, value="\n\n".join(team2Roster), inline=True),
            discord.EmbedField(name="| Elims |", value="\n\n".join(team2Elims), inline=True),
            discord.EmbedField(name="| Deaths |", value="\n\n".join(team2Deaths), inline=True)
        ]
    )

    return embed

class RoundViewer(discord.ui.View):
    def __init__(self, rounds, codes):
        super().__init__(timeout=None)
        self.rounds = rounds
        self.codes = codes
        self.index = 0

    def get_embed(self):
        round_data = self.rounds[self.index]
        round_code = self.codes[self.index]
        return create_round_embed(self.index + 1, round_data, round_code)

    @discord.ui.button(label="Previous", style=discord.ButtonStyle.secondary)
    async def previous(self, button, interaction):
        if self.index > 0:
            self.index -= 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

    @discord.ui.button(label="Next", style=discord.ButtonStyle.primary)
    async def next(self, button, interaction):
        if self.index < len(self.rounds) - 1:
            self.index += 1
        await interaction.response.edit_message(embed=self.get_embed(), view=self)

class OpenViewer(discord.ui.View):
    def __init__(self, rounds, codes):
        super().__init__(timeout=None)
        self.rounds = rounds
        self.codes = codes

    @discord.ui.button(label="View Rounds", style=discord.ButtonStyle.primary)
    async def open(self, button, interaction):
        view = RoundViewer(self.rounds, self.codes)
        await interaction.response.send_message(
            embed=view.get_embed(),
            view=view,
            ephemeral=True
        )

class Embeder:
    bot: discord.Bot = None
    faceit: FaceitClient = None

    def __init__(self, bot, faceit):
        self.bot = bot
        self.faceit = faceit

    async def handle_payload(self, payload: dict):
        if not "event" in payload.keys() or payload["event"] != "match_demo_ready":
            return

        match_id = payload["payload"]["match_instance_id"][:-4]
        match_stats: dict = await self.faceit.get_match_stats(match_id)

        if not "rounds" in match_stats:
            print("no 'rounds' in match stats.")
            return

        rounds: list = match_stats["rounds"]
        if len(rounds) == 0:
            print("rounds empty.")
            return

        last_round = rounds[len(rounds)-1]
        best_of = int(last_round["best_of"])
        num_played = int(last_round["played"])
        min_num_played = (best_of // 2) + 1
        if num_played < min_num_played:
            return # Not done yet

        team1 = last_round["teams"][0]
        team2 = last_round["teams"][1]
        team1Id = team1["team_id"]
        team2Id = team2["team_id"]
        team1Score = 0
        team2Score = 0
        for round in rounds:
            if round["round_stats"]["Winner"] == team1Id:
                team1Score+=1
            elif round["round_stats"]["Winner"] == team2Id:
                team2Score+=1
        min_score = min_num_played # Same formula
        if team1Score < min_score and team2Score < min_score:
            return # Not done yet
        
        codes = [x['demos'][0] for x in payload['payload']['instances']]
        
        channel = self.bot.get_channel(int(FACEIT_OUTPUT_CHANNEL_ID))
        announcement = create_announcement_embed(payload, team1, team2, team1Score, team2Score)
        await channel.send(embed=announcement, view=OpenViewer(rounds, codes))