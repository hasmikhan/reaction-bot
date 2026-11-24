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

BOT_TOKEN = os.environ["BOT_TOKEN"]

# Telegram-er allowed free reaction emoji
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


def main() -> None:
    start_health_server()
    asyncio.set_event_loop(asyncio.new_event_loop())
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.UpdateType.CHANNEL_POSTS, react))
    log.info("Bot started")
    app.run_polling(allowed_updates=["channel_post"], drop_pending_updates=True)


if __name__ == "__main__":
    main()
