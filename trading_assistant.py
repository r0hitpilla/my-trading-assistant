#!/usr/bin/env python3
"""
════════════════════════════════════════════════
  MY PERSONAL INDIAN STOCK MARKET ASSISTANT
  Powered by Zerodha Kite Connect
  Run this every morning before 9:15 AM
════════════════════════════════════════════════
"""

import os
import sys
import json
import time
import threading
import webbrowser
from datetime import datetime, timedelta, date

import numpy as np
from flask import Flask, request as flask_request
from kiteconnect import KiteConnect

from config import API_KEY, API_SECRET, CAPITAL, TRADING_STYLE

# ─────────────────────────────────────────────────────────────
#  STOCKS WE WATCH EVERY DAY (Nifty 50 + top liquid stocks)
# ─────────────────────────────────────────────────────────────
WATCH_LIST = [
    "RELIANCE", "TCS", "HDFCBANK", "INFY", "ICICIBANK",
    "ITC", "SBIN", "BHARTIARTL", "KOTAKBANK", "LT",
    "AXISBANK", "BAJFINANCE", "MARUTI", "TITAN", "SUNPHARMA",
    "NTPC", "WIPRO", "HCLTECH", "TECHM", "TATAMOTORS",
    "COALINDIA", "TATASTEEL", "ADANIPORTS", "CIPLA", "DRREDDY",
    "BPCL", "INDUSINDBK", "GRASIM", "TATACONSUM", "HINDALCO",
    "HEROMOTOCO", "BAJAJ-AUTO", "BANKBARODA", "CANBK", "PNB",
    "TATAPOWER", "VEDL", "DLF", "GAIL", "IOC", "SAIL",
    "IDFCFIRSTB", "MUTHOOTFIN", "LUPIN", "HAVELLS", "SIEMENS",
    "M&M", "POWERGRID", "ULTRACEMCO", "EICHERMOT", "APOLLOHOSP",
]

# ─────────────────────────────────────────────────────────────
#  WHAT EACH COMPANY DOES (in simple English)
# ─────────────────────────────────────────────────────────────
COMPANY_INFO = {
    "RELIANCE":   ("Reliance Industries",         "Makes fuel, runs Jio telecom and Reliance retail stores across India"),
    "TCS":        ("Tata Consultancy Services",    "Provides software and IT services to companies around the world"),
    "HDFCBANK":   ("HDFC Bank",                   "One of India's largest private banks — loans, savings, and credit cards"),
    "INFY":       ("Infosys",                     "Provides software and technology services to global companies"),
    "ICICIBANK":  ("ICICI Bank",                  "Large private bank offering loans, savings accounts, and insurance"),
    "ITC":        ("ITC Limited",                 "Makes cigarettes, foods (Bingo, Aashirvaad), hotels, and paper products"),
    "SBIN":       ("State Bank of India",         "India's largest government bank with branches across the country"),
    "BHARTIARTL": ("Bharti Airtel",               "Telecom company — runs Airtel mobile and broadband services"),
    "KOTAKBANK":  ("Kotak Mahindra Bank",         "Private bank offering banking, insurance, and investment products"),
    "LT":         ("Larsen & Toubro",             "Builds large infrastructure projects — bridges, buildings, power plants"),
    "AXISBANK":   ("Axis Bank",                   "Private bank providing loans, credit cards, and savings accounts"),
    "BAJFINANCE": ("Bajaj Finance",               "Provides loans for buying electronics, vehicles, and homes"),
    "MARUTI":     ("Maruti Suzuki",               "Makes and sells the most popular cars in India — Alto, Swift, Brezza"),
    "TITAN":      ("Titan Company",               "Makes Titan watches, Tanishq gold jewellery, and Fastrack accessories"),
    "SUNPHARMA":  ("Sun Pharmaceutical",          "Makes medicines and drugs sold in India and worldwide"),
    "NTPC":       ("NTPC Limited",                "Government company that generates electricity for India"),
    "WIPRO":      ("Wipro",                       "Provides IT and software services to companies globally"),
    "HCLTECH":    ("HCL Technologies",            "Provides IT services and software products globally"),
    "TECHM":      ("Tech Mahindra",               "Provides IT and telecom software services globally"),
    "TATAMOTORS": ("Tata Motors",                 "Makes cars (Nexon, Harrier), trucks, and Jaguar Land Rover vehicles"),
    "COALINDIA":  ("Coal India",                  "Government company that mines and sells coal across India"),
    "TATASTEEL":  ("Tata Steel",                  "Makes steel used in construction, cars, and manufacturing"),
    "ADANIPORTS": ("Adani Ports",                 "Owns and operates major ports and logistics across India"),
    "CIPLA":      ("Cipla",                       "Makes affordable medicines and generic drugs sold in India and globally"),
    "DRREDDY":    ("Dr. Reddy's Laboratories",    "Makes medicines and drugs for India and international markets"),
    "BPCL":       ("Bharat Petroleum",            "Government oil company — runs petrol pumps and refineries"),
    "INDUSINDBK": ("IndusInd Bank",               "Private bank offering retail and corporate banking services"),
    "GRASIM":     ("Grasim Industries",           "Makes cement (UltraTech), textiles, and chemicals"),
    "TATACONSUM": ("Tata Consumer Products",      "Sells Tata Tea, Tata Salt, Starbucks coffee, and other food brands"),
    "HINDALCO":   ("Hindalco Industries",         "Makes aluminium and copper products for construction and manufacturing"),
    "HEROMOTOCO": ("Hero MotoCorp",               "India's largest two-wheeler maker — sells Hero bikes and scooters"),
    "BAJAJ-AUTO": ("Bajaj Auto",                  "Makes Pulsar bikes, Platina, and Bajaj three-wheelers (auto-rickshaws)"),
    "BANKBARODA": ("Bank of Baroda",              "Government bank offering banking and loan services"),
    "CANBK":      ("Canara Bank",                 "Large government bank with branches across India"),
    "PNB":        ("Punjab National Bank",        "Government bank providing banking services across India"),
    "TATAPOWER":  ("Tata Power",                  "Generates and distributes electricity across India"),
    "VEDL":       ("Vedanta Limited",             "Mines and produces zinc, copper, aluminium, and oil"),
    "DLF":        ("DLF Limited",                 "India's largest real estate company — builds homes, offices, and malls"),
    "GAIL":       ("GAIL India",                  "Government company that transports and sells natural gas"),
    "IOC":        ("Indian Oil Corporation",      "Government oil company — largest fuel seller in India"),
    "SAIL":       ("Steel Authority of India",    "Government company that makes steel products"),
    "IDFCFIRSTB": ("IDFC First Bank",             "Private bank offering savings, loans, and credit cards"),
    "MUTHOOTFIN": ("Muthoot Finance",             "Provides gold loans — give your gold, get cash instantly"),
    "LUPIN":      ("Lupin Limited",               "Makes medicines and generic drugs for India and worldwide"),
    "HAVELLS":    ("Havells India",               "Makes fans, lights, cables, and kitchen appliances"),
    "SIEMENS":    ("Siemens India",               "Makes industrial equipment, power systems, and smart infrastructure"),
    "M&M":        ("Mahindra & Mahindra",         "Makes Scorpio, Thar, XUV cars, tractors, and farm equipment"),
    "POWERGRID":  ("Power Grid Corporation",      "Government company that runs India's electricity transmission network"),
    "ULTRACEMCO": ("UltraTech Cement",            "India's largest cement maker — used in buildings and construction"),
    "EICHERMOT":  ("Eicher Motors",               "Makes Royal Enfield bikes and commercial vehicles"),
    "APOLLOHOSP": ("Apollo Hospitals",            "Runs one of India's largest private hospital chains"),
}


# ══════════════════════════════════════════════
#  AUTHENTICATION — LOGIN TO ZERODHA
# ══════════════════════════════════════════════

TOKEN_FILE = "access_token.json"


def load_saved_token():
    """Check if we already logged in today and reuse the token."""
    if not os.path.exists(TOKEN_FILE):
        return None
    with open(TOKEN_FILE, "r") as f:
        data = json.load(f)
    if data.get("date") == str(date.today()):
        return data.get("access_token")
    return None


def save_token(access_token):
    with open(TOKEN_FILE, "w") as f:
        json.dump({"date": str(date.today()), "access_token": access_token}, f)


def login(kite):
    """Open Zerodha login in browser and capture the access token automatically."""
    print("\n" + "="*50)
    print("  STEP 1: LOGIN TO ZERODHA")
    print("="*50)
    print("\nYour browser will open the Zerodha login page.")
    print("Login with your Zerodha ID and password.")
    print("After login, come back here — the script will continue automatically.\n")

    app = Flask(__name__)
    token_store = {}
    done_event = threading.Event()

    @app.route("/")
    def callback():
        req_token = flask_request.args.get("request_token")
        if req_token:
            token_store["request_token"] = req_token
            done_event.set()
        return """
        <html><body style='font-family:sans-serif; text-align:center; padding:50px'>
        <h2>✅ Login Successful!</h2>
        <p>You can close this browser tab and go back to your terminal.</p>
        </body></html>
        """

    server = threading.Thread(
        target=lambda: app.run(port=5000, debug=False, use_reloader=False)
    )
    server.daemon = True
    server.start()
    time.sleep(1)  # Give Flask a moment to start

    login_url = kite.login_url()
    webbrowser.open(login_url)
    print("Waiting for you to complete login in the browser...")
    print("(You have 2 minutes)\n")

    done_event.wait(timeout=120)

    if "request_token" not in token_store:
        print("\n❌ Login timed out. Please run the script again.")
        sys.exit(1)

    print("Generating secure session...")
    data = kite.generate_session(token_store["request_token"], api_secret=API_SECRET)
    access_token = data["access_token"]
    save_token(access_token)
    print("✅ Logged in successfully!\n")
    return access_token


# ══════════════════════════════════════════════
#  CALCULATIONS — RSI AND MOVING AVERAGE
# ══════════════════════════════════════════════

def calculate_rsi(closes, period=14):
    """
    RSI = Relative Strength Index
    It tells us if a stock is being bought too much (overbought) or too little (oversold).
    Safe zone: 45 to 65
    """
    if len(closes) < period + 2:
        return None
    deltas = np.diff(closes)
    gains = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)

    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])

    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period

    if avg_loss == 0:
        return 100.0
    rs = avg_gain / avg_loss
    return round(100 - (100 / (1 + rs)), 1)


def describe_rsi(rsi):
    if rsi is None:
        return "Unknown"
    if rsi < 30:
        return f"{rsi} — OVERSOLD (stock has been sold too much, may bounce up)"
    elif rsi < 45:
        return f"{rsi} — SLIGHTLY WEAK (not in the ideal buying zone yet)"
    elif rsi <= 65:
        return f"{rsi} — SAFE ZONE ✅ (good balance — not too hot, not too cold)"
    elif rsi <= 75:
        return f"{rsi} — SLIGHTLY HIGH (many people already bought — it may slow down)"
    else:
        return f"{rsi} — OVERBOUGHT ⚠️ (too many buyers already — risky to enter)"


# ══════════════════════════════════════════════
#  MONEY MANAGEMENT
# ══════════════════════════════════════════════

def get_position_sizes(capital, vix):
    """
    Calculate exactly how much money to put in each trade.
    If VIX is above 20 (market is scared), we cut amounts in half.
    """
    max_per_stock = capital * 0.20   # 20% per stock
    cash_reserve  = capital * 0.30   # 30% kept as cash
    max_risk      = capital * 0.01   # 1% max loss per intraday trade

    vix_warning = ""
    if vix > 20:
        max_per_stock = max_per_stock / 2
        max_risk      = max_risk / 2
        vix_warning   = " ← HALVED because VIX is above 20 (market is very scared)"

    return max_per_stock, cash_reserve, max_risk, vix_warning


# ══════════════════════════════════════════════
#  MARKET HEALTH
# ══════════════════════════════════════════════

def describe_vix(vix):
    if vix < 15:
        return "CALM 🟢 — Good day to trade normally"
    elif vix < 20:
        return "SLIGHTLY NERVOUS 🟡 — Trade carefully with smaller amounts"
    else:
        return "VERY NERVOUS 🔴 — Market is scared. High chance of sudden drops"


def get_market_verdict(nifty_change_pct, vix):
    if vix > 22 or nifty_change_pct < -1.5:
        return (
            "🔴 RED — Avoid trading today",
            "Market is falling sharply and fear is very high. "
            "Chances of losing money are much higher than usual today."
        )
    elif vix > 18 or nifty_change_pct < -0.5:
        return (
            "🟡 YELLOW — Be careful today",
            "Market is nervous. Only trade the strongest setups and use smaller amounts."
        )
    else:
        return (
            "🟢 GREEN — Good day to trade",
            "Market looks healthy and calm. Good conditions for today's trades."
        )


# ══════════════════════════════════════════════
#  STOCK ANALYSIS
# ══════════════════════════════════════════════

def analyze_stock(kite, symbol, token, quote):
    """
    Check if a stock passes our 3 main tests:
    1. Price is above its 50-day average (healthy uptrend)
    2. RSI is between 45 and 65 (safe zone)
    3. Volume today is 1.5x the normal (unusual activity)
    """
    try:
        to_date   = datetime.now()
        from_date = to_date - timedelta(days=75)
        hist = kite.historical_data(token, from_date, to_date, "day")

        if len(hist) < 52:
            return None

        closes  = [d["close"]  for d in hist]
        volumes = [d["volume"] for d in hist]

        current_price = quote.get("last_price", 0)
        if current_price <= 0:
            return None

        ma50         = round(float(np.mean(closes[-50:])), 2)
        avg_volume   = float(np.mean(volumes[-20:]))
        today_volume = quote.get("volume", 0)
        volume_ratio = round(today_volume / avg_volume, 2) if avg_volume > 0 else 0
        rsi          = calculate_rsi(closes)

        above_ma50 = current_price > ma50
        rsi_ok     = rsi is not None and 45 <= rsi <= 65
        volume_ok  = volume_ratio >= 1.5

        score = sum([above_ma50, rsi_ok, volume_ok])

        return {
            "symbol":       symbol,
            "price":        current_price,
            "ma50":         ma50,
            "above_ma50":   above_ma50,
            "rsi":          rsi,
            "rsi_ok":       rsi_ok,
            "volume_ratio": volume_ratio,
            "volume_ok":    volume_ok,
            "score":        score,
            "change_pct":   quote.get("net_change", 0),
        }
    except Exception:
        return None


# ══════════════════════════════════════════════
#  PRINT ONE STOCK SUGGESTION
# ══════════════════════════════════════════════

def print_suggestion(rank, stock, capital, max_per_stock, max_risk, trading_style):
    symbol        = stock["symbol"]
    name, desc    = COMPANY_INFO.get(symbol, (symbol, "Listed on NSE India"))
    price         = stock["price"]
    fetch_time    = datetime.now().strftime("%I:%M %p")

    # ── Targets and stop loss (aggressive intraday settings)
    buy_low   = round(price * 0.998, 2)
    buy_high  = round(price * 1.002, 2)
    target1   = round(price * 1.02, 2)   # +2%
    target2   = round(price * 1.04, 2)   # +4%
    stop_loss = round(price * 0.985, 2)  # -1.5%

    # ── Share count
    shares    = int(max_per_stock // price) if price <= max_per_stock else 0
    max_loss  = round(shares * (price - stop_loss), 2)
    profit_t1 = round(shares * (target1 - price), 2)
    profit_t2 = round(shares * (target2 - price), 2)

    # ── Confidence
    confidence = min(60 + stock["score"] * 12, 85)

    # ── Reasons in plain English
    reasons = []
    if stock["volume_ok"]:
        reasons.append(
            f"More people than usual are trading this stock today "
            f"({stock['volume_ratio']}x normal) — something is happening"
        )
    if stock["above_ma50"]:
        diff = round(((price - stock["ma50"]) / stock["ma50"]) * 100, 1)
        reasons.append(
            f"Price (₹{price}) is {diff}% above its 50-day average (₹{stock['ma50']}) "
            f"— the stock has been going up steadily"
        )
    if stock["rsi_ok"]:
        reasons.append(
            f"RSI is {stock['rsi']} — this is in the safe zone (45–65), "
            f"meaning the stock is not overbought or ignored"
        )

    hold_time = (
        "Today only — sell before 3:15 PM IST (15 min before market close)"
        if trading_style == "intraday"
        else "2 to 5 days"
    )

    affordability_note = ""
    if shares == 0:
        affordability_note = (
            f"\n  ⚠️  ₹{price} is above your max of ₹{max_per_stock:.0f}. "
            f"You cannot buy even 1 share. SKIP this stock today."
        )

    sep = "━" * 46

    print(f"""
{sep}
STOCK SUGGESTION [{rank}/3]

Company name  : {name} ({symbol})
What they do  : {desc}
Current price : ₹{price} — fetched from Zerodha Kite at {fetch_time}

WHY I AM SUGGESTING THIS TODAY:""")

    for i, r in enumerate(reasons, 1):
        print(f"  {i}. {r}")

    print(f"""
TECHNICAL INDICATORS:
  RSI (safe zone = 45 to 65)   : {describe_rsi(stock['rsi'])}
  50-Day Moving Average        : ₹{stock['ma50']}
     → Price is {'ABOVE ✅ — healthy uptrend' if stock['above_ma50'] else 'BELOW ⚠️ — be cautious'}
  Volume today vs normal       : {stock['volume_ratio']}x {'✅ Unusually high' if stock['volume_ok'] else '— Normal'}

WHAT TO DO:
  Buy between    : ₹{buy_low} and ₹{buy_high}
  Target 1       : ₹{target1}  (+2%) — sell HALF your shares here and take some profit
  Target 2       : ₹{target2}  (+4%) — sell the REST of your shares here
  Stop Loss ⛔   : ₹{stop_loss} (-1.5%) — if price drops HERE, SELL EVERYTHING immediately
                   Do not wait. Do not hope. Sell and protect your money.

IF YOU HAVE ₹{capital} TO INVEST:
  Max to put in this stock : ₹{max_per_stock:.0f}
  Buy approximately        : {shares} shares{affordability_note}
  If stop loss hits        : Maximum loss = ₹{max_loss}
  If Target 1 hits         : Profit = ₹{profit_t1}
  If Target 2 hits         : Profit = ₹{profit_t2}

RISK LEVEL     : HIGH (Aggressive intraday)
CONFIDENCE     : {confidence}% — {stock['score']} out of 3 key signals are positive
HOW LONG       : {hold_time}

DATA SOURCE    : Zerodha Kite Connect API (live)

⚠️  This is research to help you decide — NOT a guarantee.
    Verify the price on Zerodha before clicking Buy.
    The final decision is always yours.
{sep}""")


# ══════════════════════════════════════════════
#  MAIN — RUNS EVERYTHING
# ══════════════════════════════════════════════

def main():
    today = datetime.now().strftime("%d %B %Y, %A")
    print(f"\n{'═'*50}")
    print(f"  MY TRADING ASSISTANT — {today}")
    print(f"{'═'*50}")

    # ── AUTH ──────────────────────────────────────────────────
    kite          = KiteConnect(api_key=API_KEY)
    access_token  = load_saved_token()
    if not access_token:
        access_token = login(kite)
    kite.set_access_token(access_token)

    # ── MARKET HEALTH CHECK ───────────────────────────────────
    print("\nFetching live market data from Zerodha... please wait...\n")

    try:
        indices    = kite.quote(["NSE:NIFTY 50", "NSE:INDIA VIX"])
        nifty_data = indices.get("NSE:NIFTY 50", {})
        vix_data   = indices.get("NSE:INDIA VIX", {})

        nifty_price    = nifty_data.get("last_price", 0)
        nifty_prev     = nifty_data.get("ohlc", {}).get("close", nifty_price)
        nifty_change   = round(nifty_price - nifty_prev, 2)
        nifty_pct      = round((nifty_change / nifty_prev) * 100, 2) if nifty_prev else 0
        nifty_dir      = "UP ▲" if nifty_pct >= 0 else "DOWN ▼"
        vix            = vix_data.get("last_price", 0)

    except Exception as e:
        print(f"⚠️  Could not auto-fetch index data ({e})")
        print("Please type these values manually:\n")
        nifty_price  = float(input("  Nifty 50 current value (e.g. 23192): "))
        nifty_pct    = float(input("  Nifty change % (e.g. -0.5 or 1.2): "))
        nifty_change = round(nifty_price * nifty_pct / 100, 2)
        nifty_dir    = "UP ▲" if nifty_pct >= 0 else "DOWN ▼"
        vix          = float(input("  India VIX value (e.g. 21.88): "))
        print()

    max_per_stock, cash_reserve, max_risk, vix_warn = get_position_sizes(CAPITAL, vix)
    verdict, verdict_reason = get_market_verdict(nifty_pct, vix)

    print(f"""{'─'*50}
MARKET HEALTH CHECK — {today}

Overall market (Nifty 50) : {nifty_dir} {abs(nifty_pct)}% at ₹{nifty_price:,.2f}
  In simple words : {'Market is rising today — generally good for buying' if nifty_pct >= 0 else 'Market is falling today — be extra careful with every trade'}

Fear meter (India VIX)    : {vix} — {describe_vix(vix)}

YOUR MONEY LIMITS FOR TODAY:
  Your total capital       : ₹{CAPITAL:,}
  Max per stock            : ₹{max_per_stock:.0f}{vix_warn}
  Keep as cash (do not invest) : ₹{cash_reserve:.0f}
  Max you can lose per trade   : ₹{max_risk:.0f}

VERDICT : {verdict}
Reason  : {verdict_reason}
{'─'*50}""")

    if "RED" in verdict:
        print("\n🔴 Today is a RED day. I strongly suggest NOT trading today.")
        print("   Sitting in cash is also a strategy. Your money is safe if you do nothing.\n")
        ans = input("   Do you still want to see stock suggestions? (yes / no): ").strip().lower()
        if ans != "yes":
            print("\n   Smart choice. Come back tomorrow morning. Good luck!\n")
            return

    # ── FETCH ALL QUOTES ──────────────────────────────────────
    print(f"\n{'─'*50}")
    print("STEP 2: Screening stocks... (this takes 1–2 minutes)")
    print(f"{'─'*50}\n")

    exchange_symbols = [f"NSE:{s}" for s in WATCH_LIST]
    try:
        all_quotes = kite.quote(exchange_symbols)
    except Exception as e:
        print(f"❌ Could not fetch stock data: {e}")
        return

    # ── GET INSTRUMENT TOKENS (needed for historical data) ────
    print("Loading instrument list from NSE...")
    try:
        instruments = kite.instruments("NSE")
        token_map   = {inst["tradingsymbol"]: inst["instrument_token"] for inst in instruments}
        print(f"Loaded {len(instruments):,} instruments.\n")
    except Exception as e:
        print(f"❌ Could not load instruments: {e}")
        return

    # ── ANALYZE EACH STOCK ────────────────────────────────────
    candidates = []
    total = len(WATCH_LIST)

    for i, symbol in enumerate(WATCH_LIST, 1):
        key   = f"NSE:{symbol}"
        quote = all_quotes.get(key)
        token = token_map.get(symbol)

        if not quote or not token:
            continue

        print(f"  Analyzing {symbol}... ({i}/{total})", end="\r")
        result = analyze_stock(kite, symbol, token, quote)

        if result:
            candidates.append(result)

        time.sleep(0.4)  # Stay within Kite's 3 requests/second limit

    print(f"  Done screening {total} stocks.          \n")

    # ── SORT: highest score first, then highest volume ratio ──
    candidates.sort(key=lambda x: (x["score"], x["volume_ratio"]), reverse=True)

    # ── TOP 3 SUGGESTIONS ─────────────────────────────────────
    top3 = [c for c in candidates if c["score"] >= 2][:3]
    if not top3:
        top3 = candidates[:3]  # Fallback: show best available even if not perfect

    print(f"\n{'═'*50}")
    print("  TOP STOCK SUGGESTIONS FOR TODAY")
    print(f"{'═'*50}")

    if not top3:
        print("\n❌ Could not find suitable stocks today.")
        print("   Market conditions may not be ideal. Consider not trading today.\n")
    else:
        for rank, stock in enumerate(top3, 1):
            print_suggestion(rank, stock, CAPITAL, max_per_stock, max_risk, TRADING_STYLE)

    # ── STOCKS TO AVOID ───────────────────────────────────────
    avoid = []
    for c in candidates:
        if c["rsi"] and c["rsi"] > 70:
            avoid.append((c, f"RSI is {c['rsi']} — too many people have already bought this stock. "
                             f"It may fall soon. Wait for it to calm down below RSI 65 before buying."))
        elif not c["above_ma50"]:
            avoid.append((c, f"The stock is trading BELOW its 50-day average price (₹{c['ma50']}). "
                             f"This means it has been falling. Not a safe time to buy."))
        if len(avoid) == 2:
            break

    if avoid:
        print(f"\n{'═'*50}")
        print("  STOCKS TO AVOID TODAY")
        print(f"{'═'*50}")
        for stock, reason in avoid:
            name, _ = COMPANY_INFO.get(stock["symbol"], (stock["symbol"], ""))
            print(f"\n  AVOID: {name} ({stock['symbol']})")
            print(f"  Reason: {reason}")

    # ── FINAL REMINDERS ───────────────────────────────────────
    print(f"""
{'═'*50}
  IMPORTANT REMINDERS FOR TODAY
{'═'*50}

  1. Market opens at 9:15 AM IST. Best time to buy: 9:15–9:45 AM.
  2. Set your STOP LOSS on Zerodha immediately after buying.
     (In Zerodha Kite: place a Stop Loss Market order right after your buy)
  3. Sell ALL your positions by 3:15 PM — 15 minutes before market close.
  4. Never put more than ₹{max_per_stock:.0f} in a single stock today.
  5. Keep ₹{cash_reserve:.0f} as cash — never invest everything.
  6. If a stock hits stop loss — sell immediately. Do not hope for recovery.

  Good luck today! Protect your capital first. Profits will follow.
{'═'*50}
""")


if __name__ == "__main__":
    main()
