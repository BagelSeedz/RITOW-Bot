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
        last_best_of = last_round["best_of"]
        num_played = last_round["played"]
        if num_played < (last_best_of // 2) + 1:
            return # Not done yet

        team1score = 0
        team2score = 0

        
