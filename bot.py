import asyncio
import requests
from telegram import Bot
from decimal import Decimal

# ✅ Telegram bot credentials
TELEGRAM_TOKEN = "8427501495:AAGeFvcNR00yYJ2fapNPnW9zp63csMzeuMg"
CHAT_ID = -1002744054235  # <- Replace with your chat ID or group ID if needed

# ✅ $NEXUS token address (Solana mint)
NEXUS_TOKEN_ADDRESS = "4SLbbckLuMiUPFBT6FrqKtHd1j97ePmG3HDJUd24wBLV"  # ← paste the full mint from Dexscreener
PREFERRED_CHAIN = "solana"  # keep if NEXUS is on Solana

# ✅ Initialize the Telegram bot
bot = Bot(token=TELEGRAM_TOKEN)

def _pick_best_pair(pairs, preferred_chain=None):
    """
    From a list of Dexscreener pairs, pick the one with the highest USD liquidity.
    Optionally prefer a specific chain.
    """
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

# ↓↓↓ NEW: your requested market-cap formatter ↓↓↓
def _format_cap(market_cap, fdv):
    """
    Prefer marketCap; fall back to FDV.
    Show the exact amount with commas, no 'M' suffix and no rounding.
    Examples:
      400000      -> "$400,000"
      1234567.89  -> "$1,234,567.89"
    """
    mc = market_cap if market_cap is not None else fdv
    if mc is None:
        return "N/A"
    try:
        mc_dec = Decimal(str(mc))  # preserve exact value from API

        # Build a string without scientific notation
        s = format(mc_dec, 'f')  # fixed-point
        int_part, dot, frac_part = s.partition('.')

        # Add commas to the integer part
        int_part_commas = f"{int(int_part):,}"

        # Keep fractional part if it's non-zero (no rounding; just trim trailing zeros)
        if dot and frac_part.rstrip('0'):
            frac_clean = frac_part.rstrip('0')
            return f"${int_part_commas}.{frac_clean}"
        else:
            return f"${int_part_commas}"
    except Exception:
        return "N/A"
# ↑↑↑ NEW formatter ends here ↑↑↑

# ✅ Function to fetch price + market cap from Dexscreener (by token address)
def get_nexus_price():
    """
    Queries Dexscreener for all DEX pairs of the given token address.
    Selects the pair with the highest USD liquidity, then returns priceUsd
    and a formatted market cap string using _format_cap.
    """
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

            # ← uses your new formatter
            cap_str = _format_cap(best.get("marketCap"), best.get("fdv"))

            if price is None:
                last_reason = "priceUsd missing on best pair"
                continue

            return price, cap_str

        except requests.HTTPError as e:
            last_reason = f"HTTP {e.response.status_code} on {url}"
        except Exception as e:
            last_reason = f"{type(e).__name__}: {e}"

    print(f"🔎 Dexscreener lookup failed: {last_reason}")
    return None, None

# ✅ Auto-send message loop
async def send_price_loop():
    while True:
        price, market_cap = get_nexus_price()
        if price and market_cap:
            message = f"🚀 $NEXUS Update\n• Price: ${price:,.6f}\n• Market Cap: {market_cap}"
            await bot.send_message(chat_id=CHAT_ID, text=message)
        else:
            print("⚠️ Could not fetch price.")
        await asyncio.sleep(60)  # Wait 1 minute before next update

# ✅ Entry point
if __name__ == "__main__":
    asyncio.run(send_price_loop())
