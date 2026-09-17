from aiohttp import web
import os

async def handle_webhook(request):
    payload = await request.json()

    print("FACEIT WEBHOOK:")
    print(payload)

    return web.Response(status=200)


def create_web_app():
    app = web.Application()

    app.router.add_post(
        "/faceit/webhook",
        handle_webhook
    )

    return app

async def start_web_server():

    app = create_web_app()

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