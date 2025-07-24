import asyncio
import requests
from telegram import Bot
from decimal import Decimal

# ✅ Telegram bot credentials
TELEGRAM_TOKEN = "8427501495:AAGeFvcNR00yYJ2fapNPnW9zp63csMzeuMg"
CHAT_ID = -1002744054235  # <- Replace with your chat ID or group ID if needed
COINGECKO_ID = "ben-pasternak"  # CoinGecko's ID for $LAUNCHCOIN

# ✅ Initialize the Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

# ✅ Function to fetch price + market cap from CoinGecko
def get_launchcoin_price():
    url = f"https://api.coingecko.com/api/v3/coins/{COINGECKO_ID}?localization=false&tickers=false&market_data=true"
    try:
        response = requests.get(url)
        response.raise_for_status()
        data = response.json()

        market_data = data.get("market_data", {})
        price = market_data.get("current_price", {}).get("usd")
        market_cap = market_data.get("market_cap", {}).get("usd")

        if price is None or market_cap is None:
            return None, None

        # ✅ Format market cap to M (millions)
        cap_formatted = f"${Decimal(market_cap) / 1_000_000:.2f}M"
        return price, cap_formatted

    except Exception as e:
        print("❌ Error fetching price:", e)
        return None, None

# ✅ Auto-send message loop
async def send_price_loop():
    while True:
        price, market_cap = get_launchcoin_price()
        if price and market_cap:
            message = f"🚀 $LAUNCHCOIN Update\n• Price: ${price:,.6f}\n• Market Cap: {market_cap}"
            await bot.send_message(chat_id=CHAT_ID, text=message)
        else:
            print("⚠️ Could not fetch price.")
        await asyncio.sleep(60)  # Wait 1 minute before next update

# ✅ Entry point
if __name__ == "__main__":
    asyncio.run(send_price_loop())
