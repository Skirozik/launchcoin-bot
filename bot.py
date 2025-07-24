import asyncio
import requests
from telegram import Bot

# === Config ===
TELEGRAM_TOKEN = '8427501495:AAGeFvcNR00yYJ2fapNPnW9zp63csMzeuMg'
CHAT_ID = -1002744054235
COIN_ID = 'ben-pasternak'  # CoinGecko ID for $LAUNCHCOIN

bot = Bot(token=TELEGRAM_TOKEN)

# === Helper: Format Market Cap like $72.5M or $1.2B ===
def format_market_cap(cap):
    if cap >= 1_000_000_000:
        return f"${cap / 1_000_000_000:.2f}B"
    elif cap >= 1_000_000:
        return f"${cap / 1_000_000:.2f}M"
    elif cap >= 1_000:
        return f"${cap / 1_000:.2f}K"
    else:
        return f"${cap:.2f}"

# === Get price & market cap from CoinGecko ===
async def get_price():
    url = f'https://api.coingecko.com/api/v3/coins/{COIN_ID}?localization=false&tickers=false&market_data=true&community_data=false&developer_data=false&sparkline=false'
    try:
        response = requests.get(url)
        data = response.json()
        price = data['market_data']['current_price']['usd']
        market_cap = data['market_data']['market_cap']['usd']
        return price, market_cap
    except Exception as e:
        print("Error getting data:", e)
        return None, None

# === Telegram loop ===
async def send_price_loop():
    while True:
        price, market_cap = await get_price()
        if price and market_cap:
            cap_formatted = format_market_cap(market_cap)
            message = (
                f"🚀 $LAUNCHCOIN Update\n"
                f"• Price: ${price:,.6f}\n"
                f"• Market Cap: {cap_formatted}"
            )
            await bot.send_message(chat_id=CHAT_ID, text=message)
        await asyncio.sleep(60)

asyncio.run(send_price_loop())
