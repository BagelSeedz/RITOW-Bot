from aiohttp import web
import os
import discord
from .embeder import Embeder
import json

class WebhookHandler():
    bot: discord.Bot = None
    embeder: Embeder = None

    def __init__(self, bot, faceit):
        self.bot = bot
        self.embeder = Embeder(bot, faceit)


    async def handle_webhook(self, request):
        payload = await request.json()
        # with open("matchdemo.json", "r", encoding="utf-8") as f:
        #     payload = json.load(f)

        await self.embeder.handle_payload(payload)

        return web.Response(status=200)


    def create_web_app(self):
        app = web.Application()

        app.router.add_post(
            "/faceit/webhook",
            self.handle_webhook
        )

        return app

    async def start_web_server(self):

        app = self.create_web_app()

        runner = web.AppRunner(app)
        await runner.setup()

        port = int(os.environ.get("PORT", 8080))

        site = web.TCPSite(
            runner,
            "0.0.0.0",
            port
        )

        await site.start()

        print(f"Webhook server listening on port {port}")

        return runner