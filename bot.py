import asyncio
import os
import requests
from telegram import Bot
from decimal import Decimal
from dotenv import load_dotenv

load_dotenv()

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
CHAT_ID = int(os.getenv("CHAT_ID", "0"))

NEXUS_TOKEN_ADDRESS = "4SLbbckLuMiUPFBT6FrqKtHd1j97ePmG3HDJUd24wBLV"
PREFERRED_CHAIN = "solana"

bot = Bot(token=TELEGRAM_TOKEN)

def _pick_best_pair(pairs, preferred_chain=None):
    if not pairs:
        return None
    if preferred_chain:
        filtered = [p for p in pairs if (p.get("chainId") == preferred_chain)]
        if filtered:
            pairs = filtered
    pairs = [p for p in pairs if p.get("priceUsd") is not None]
    if not pairs:
        return None

    def usd_liq(pair):
        liq = pair.get("liquidity") or {}
        return float(liq.get("usd") or 0)

    return max(pairs, key=usd_liq)

def _format_cap(market_cap, fdv):
    mc = market_cap if market_cap is not None else fdv
    if mc is None:
        return "N/A"
    try:
        mc_dec = Decimal(str(mc))
        s = format(mc_dec, 'f')
        int_part, dot, frac_part = s.partition('.')
        int_part_commas = f"{int(int_part):,}"
        if dot and frac_part.rstrip('0'):
            frac_clean = frac_part.rstrip('0')
            return f"${int_part_commas}.{frac_clean}"
        else:
            return f"${int_part_commas}"
    except Exception:
        return "N/A"

def get_nexus_price():
    headers = {"User-Agent": "Mozilla/5.0"}
    endpoints = [
        f"https://api.dexscreener.com/latest/dex/search?q={NEXUS_TOKEN_ADDRESS}",
        f"https://api.dexscreener.com/latest/dex/tokens/{NEXUS_TOKEN_ADDRESS}",
    ]

    last_reason = "Unknown error"
    for url in endpoints:
        try:
            resp = requests.get(url, headers=headers, timeout=15)
            resp.raise_for_status()
            data = resp.json()
            pairs = data.get("pairs", []) or []
            if not pairs:
                last_reason = f"No pairs found from {url}"
                continue
            best = _pick_best_pair(pairs, preferred_chain=PREFERRED_CHAIN)
            if not best:
                last_reason = "No pair with priceUsd and/or liquidity after filtering"
                continue
            price_str = best.get("priceUsd")
            price = float(price_str) if price_str is not None else None
            cap_str = _format_cap(best.get("marketCap"), best.get("fdv"))
            if price is None:
                last_reason = "priceUsd missing on best pair"
                continue
            return price, cap_str
        except requests.HTTPError as e:
            last_reason = f"HTTP {e.response.status_code} on {url}"
        except Exception as e:
            last_reason = f"{type(e).__name__}: {e}"

    print(f"Dexscreener lookup failed: {last_reason}")
    return None, None

async def send_price_loop():
    while True:
        price, market_cap = get_nexus_price()
        if price and market_cap:
            message = f"🚀 $NEXUS Update\n• Price: ${price:,.6f}\n• Market Cap: {market_cap}"
            await bot.send_message(chat_id=CHAT_ID, text=message)
        else:
            print("Could not fetch price.")
        await asyncio.sleep(60)

if __name__ == "__main__":
    asyncio.run(send_price_loop())
