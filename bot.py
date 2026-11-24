import os
import random
import logging
import asyncio
import threading
from http.server import BaseHTTPRequestHandler, HTTPServer

from telegram import ReactionTypeEmoji, Update
from telegram.error import RetryAfter, TelegramError
from telegram.ext import Application, ContextTypes, MessageHandler, filters

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s", level=logging.INFO
)
log = logging.getLogger("reaction-bot")

BOT_TOKENS = [
    t.strip()
    for t in os.environ.get("BOT_TOKENS", os.environ.get("BOT_TOKEN", "")).split(",")
    if t.strip()
]
if not BOT_TOKENS:
    raise RuntimeError("BOT_TOKENS is not set")

# Free reaction emoji allowed by Telegram
EMOJIS = ["👍", "❤", "🔥", "🥰", "👏", "🎉", "🤩", "💯", "😍", "⚡", "🏆", "🙏", "😎", "🤝", "👌"]

if os.getenv("EMOJIS"):
    EMOJIS = [e.strip() for e in os.environ["EMOJIS"].split(",") if e.strip()]

ALLOWED = {int(x) for x in os.getenv("CHANNEL_IDS", "").split(",") if x.strip()}


async def react(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    msg = update.channel_post
    if not msg:
        return
    if ALLOWED and msg.chat_id not in ALLOWED:
        return

    emoji = random.choice(EMOJIS)

    for _ in range(3):
        try:
            await context.bot.set_message_reaction(
                chat_id=msg.chat_id,
                message_id=msg.message_id,
                reaction=[ReactionTypeEmoji(emoji)],
            )
            log.info("Reacted %s to %s/%s", emoji, msg.chat_id, msg.message_id)
            return
        except RetryAfter as e:
            await asyncio.sleep(e.retry_after + 1)
        except TelegramError as e:
            log.warning("Reaction failed: %s", e)
            return


class Health(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b"ok")

    def log_message(self, *args):
        pass


def start_health_server():
    port = os.getenv("PORT")
    if not port:
        return
    server = HTTPServer(("0.0.0.0", int(port)), Health)
    threading.Thread(target=server.serve_forever, daemon=True).start()
    log.info("Health server on port %s", port)


async def run_all() -> None:
    apps = []
    for token in BOT_TOKENS:
        app = Application.builder().token(token).build()
        app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS, react))
        await app.initialize()
        await app.start()
        await app.updater.start_polling(
            allowed_updates=["channel_post"], drop_pending_updates=True
        )
        apps.append(app)
    log.info("Started %d bots", len(apps))
    try:
        await asyncio.Event().wait()
    finally:
        for app in apps:
            await app.updater.stop()
            await app.stop()
            await app.shutdown()


def main() -> None:
    start_health_server()
    asyncio.run(run_all())


if __name__ == "__main__":
    main()
