# Telegram Auto Reaction Bot

Channel-e notun post ashle bot auto random reaction dey.

## Setup
1. @BotFather -> /newbot -> token nao.
2. Bot-ke tomar channel-e **Admin** banao (post/message permission lagbe na, shudhu admin hote hobe).
3. Env variable set koro:
   - `BOT_TOKEN` (required)
   - `CHANNEL_IDS` (optional, e.g. `-1001234567890`)
   - `EMOJIS` (optional, e.g. `👍,❤,🔥`)

## Local run
```
pip install -r requirements.txt
BOT_TOKEN=xxxx python bot.py
```

## Free hosting
- **Koyeb / Render (Web Service, free)**: GitHub-e push -> deploy. Build: `pip install -r requirements.txt`, Start: `python bot.py`. `BOT_TOKEN` env dao. Render free sleep kore, tai UptimeRobot diye 5 min por por URL ping koro.
- **Oracle Cloud Always Free VM**: sobcheye stable. `nohup python bot.py &` ba systemd diye chalao.
- **Termux (phone)**: `pkg install python` -> run.

## Note
- Shudhu Telegram-er allowed emoji kaj kore (list bot.py-te).
- Channel ID paite: channel-er ekta post @getidsbot-e forward koro.
