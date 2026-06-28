# launchcoin-bot

A Telegram bot that posts live price and market cap updates for a Solana token every minute, pulling data from Dexscreener.

## What it does

- Queries Dexscreener for the token pair with the highest USD liquidity
- Sends a formatted price + market cap update to a Telegram group every 60 seconds
- Falls back between multiple Dexscreener endpoints for reliability

## Setup

**1. Create a bot via [@BotFather](https://t.me/botfather) and get your token**

**2. Clone and install dependencies**

```bash
git clone https://github.com/Skirozik/launchcoin-bot.git
cd launchcoin-bot
pip install -r requirements.txt
```

**3. Configure environment variables**

```bash
cp .env.example .env
```

Edit `.env`:

```
TELEGRAM_TOKEN=your_bot_token_from_botfather
CHAT_ID=your_telegram_group_chat_id
```

To get your group's `CHAT_ID`, add `@userinfobot` to the group and it will print the ID.

**4. Set the token address**

In `bot.py`, update `NEXUS_TOKEN_ADDRESS` to the Solana mint address of whichever token you want to track (paste from Dexscreener).

**5. Run**

```bash
python bot.py
```

## Dependencies

- `python-telegram-bot`
- `requests`
- `python-dotenv`
