import asyncio
import requests
from telegram import Bot

TELEGRAM_TOKEN = '8427501495:AAGeFvcNR00yYJ2fapNPnW9zp63csMzeuMg'
CHAT_ID = 1459051152
COIN_ID = 'ben-pasternak'  # This is the CoinGecko ID for $LAUNCHCOIN

bot = Bot(token=TELEGRAM_TOKEN)

async def get_price():
    url = f'https://api.coingecko.com/api/v3/simple/price?ids={COIN_ID}&vs_currencies=usd'
    try:
        response = requests.get(url)
        data = response.json()
        price = data[COIN_ID]['usd']
        return price
    except Exception as e:
        print("Error getting price:", e)
        return None

async def send_price_loop():
    while True:
        price = await get_price()
        if price:
            message = f"$LAUNCHCOIN is currently: ${price:.6f} USD"
            await bot.send_message(chat_id=CHAT_ID, text=message)
        await asyncio.sleep(60)  # Wait 60 seconds before sending next update

asyncio.run(send_price_loop())
