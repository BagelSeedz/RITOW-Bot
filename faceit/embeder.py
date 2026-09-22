import discord
from .client import FaceitClient

class Embeder:
    bot: discord.Bot = None
    faceit: FaceitClient = None

    def __init__(self, bot, faceit):
        self.bot = bot
        self.faceit = faceit

    def handle_payload(self, payload: dict):
        if not "event" in payload.keys() or payload["event"] != "match_demo_ready":
            return

        match_id = payload["payload"]["match_instance_id"][:-4]
        match_stats: dict = self.faceit.get_match_stats(match_id)

        if not "rounds" in match_stats.keys():
            print("no 'rounds' in match stats.")
            return

        rounds: list = match_stats["rounds"]
        if len(rounds) == 0:
            print("rounds empty.")
            return

        last_round = rounds[len(rounds)-1]
        best_of = last_round["best_of"]
        num_played = last_round["played"]
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

        team1Name = team1["team_stats"]["Team"]
        team2Name = team2["team_stats"]["Team"]
        team1Roster = [f"**{plr["nickname"]}**" for plr in team1["players"]]
        team2Roster = [f"**{plr["nickname"]}**" for plr in team2["players"]]
        team1Elims = [str(plr["player_stats"]["Eliminations"]) for plr in team1["players"]]
        team2Elims = [str(plr["player_stats"]["Eliminations"]) for plr in team2["players"]]
        team1Deaths = [str(plr["player_stats"]["Deaths"]) for plr in team1["players"]]
        team2Deaths = [str(plr["player_stats"]["Deaths"]) for plr in team2["players"]]
        score_str =  f"**{team1Score}** - {team2Score}" if team1Score > team2Score else f"{team1Score} - **{team2Score}**"
        winnerName = team1Name if team1Score > team2Score else team2Name

        embed = discord.Embed(
            author=discord.EmbedAuthor(payload["payload"]["entity"]["name"]),
            title=f"{team1Name} | {score_str} | {team2Name}",
            color=0xff6600,
            fields=[
                discord.EmbedField(
                    name="Round 1",
                    value=f"Winner: {winnerName}\n" \
                            f"Mode: {round["round_stats"]["OW2 Mode"]}\n" \
                            f"Score: {round["round_stats"]["Score Summary"]}",
                    inline=True
                ),
                discord.EmbedField(
                    name=team1Name,
                    value="\n\n".join(team1Roster),
                    inline=True
                ),
                discord.EmbedField(
                    name="Elims",
                    value="\n\n".join(team1Elims),
                    inline=True
                ),
                discord.EmbedField(
                    name="Deaths",
                    value="\n\n".join(team1Deaths),
                    inline=True
                ),
                discord.EmbedField(
                    name=team2Name,
                    value="\n\n".join(team2Roster),
                    inline=True
                ),
                discord.EmbedField(
                    name="Elims",
                    value="\n\n".join(team2Elims),
                    inline=True
                ),
                discord.EmbedField(
                    name="Deaths",
                    value="\n\n".join(team2Deaths),
                    inline=True
                )
            ]
        )