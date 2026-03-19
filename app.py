#!/usr/bin/env python3
"""
════════════════════════════════════════════
  MY TRADING ASSISTANT — Web App
  Run: python app.py
  Then open: http://localhost:5000
════════════════════════════════════════════
"""

import os
import json
import time
import threading
from datetime import datetime, timedelta, date

import numpy as np
from flask import Flask, render_template, redirect, request, session, url_for, jsonify
from kiteconnect import KiteConnect

from config import API_KEY, API_SECRET, CAPITAL, TRADING_STYLE

app = Flask(__name__)
app.secret_key = "trading-assistant-secret-2024"

# ─── Token Storage ─────────────────────────────────────────────
TOKEN_FILE = "access_token.json"

def load_saved_token():
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


# ─── Stock Universe ────────────────────────────────────────────
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

COMPANY_INFO = {
    "RELIANCE":   ("Reliance Industries",      "Makes fuel, runs Jio telecom and Reliance retail stores"),
    "TCS":        ("Tata Consultancy Services","Provides software and IT services to companies worldwide"),
    "HDFCBANK":   ("HDFC Bank",               "One of India's largest private banks"),
    "INFY":       ("Infosys",                 "Provides software and technology services globally"),
    "ICICIBANK":  ("ICICI Bank",              "Large private bank — loans, savings, and insurance"),
    "ITC":        ("ITC Limited",             "Makes cigarettes, Bingo, Aashirvaad, hotels, and paper"),
    "SBIN":       ("State Bank of India",     "India's largest government bank"),
    "BHARTIARTL": ("Bharti Airtel",           "Runs Airtel mobile and broadband services"),
    "KOTAKBANK":  ("Kotak Mahindra Bank",     "Private bank — banking, insurance, and investments"),
    "LT":         ("Larsen & Toubro",         "Builds large infrastructure — bridges, power plants"),
    "AXISBANK":   ("Axis Bank",               "Private bank — loans, credit cards, and savings"),
    "BAJFINANCE": ("Bajaj Finance",           "Provides loans for electronics, vehicles, and homes"),
    "MARUTI":     ("Maruti Suzuki",           "Makes the most popular cars in India — Alto, Swift, Brezza"),
    "TITAN":      ("Titan Company",           "Makes Titan watches, Tanishq gold jewellery"),
    "SUNPHARMA":  ("Sun Pharmaceutical",     "Makes medicines and drugs sold in India and worldwide"),
    "NTPC":       ("NTPC Limited",            "Government company that generates electricity"),
    "WIPRO":      ("Wipro",                   "Provides IT and software services globally"),
    "HCLTECH":    ("HCL Technologies",        "Provides IT services and software products globally"),
    "TECHM":      ("Tech Mahindra",           "Provides IT and telecom software services globally"),
    "TATAMOTORS": ("Tata Motors",             "Makes Nexon, Harrier, trucks, and Jaguar Land Rover"),
    "COALINDIA":  ("Coal India",              "Government company that mines and sells coal"),
    "TATASTEEL":  ("Tata Steel",              "Makes steel for construction, cars, and manufacturing"),
    "ADANIPORTS": ("Adani Ports",             "Owns and operates major ports across India"),
    "CIPLA":      ("Cipla",                   "Makes affordable medicines and generic drugs"),
    "DRREDDY":    ("Dr. Reddy's Laboratories","Makes medicines for India and international markets"),
    "BPCL":       ("Bharat Petroleum",        "Government oil company — petrol pumps and refineries"),
    "INDUSINDBK": ("IndusInd Bank",           "Private bank — retail and corporate banking"),
    "GRASIM":     ("Grasim Industries",       "Makes cement (UltraTech), textiles, and chemicals"),
    "TATACONSUM": ("Tata Consumer Products",  "Sells Tata Tea, Tata Salt, and Starbucks coffee"),
    "HINDALCO":   ("Hindalco Industries",     "Makes aluminium and copper products"),
    "HEROMOTOCO": ("Hero MotoCorp",           "India's largest two-wheeler maker — Hero bikes"),
    "BAJAJ-AUTO": ("Bajaj Auto",              "Makes Pulsar bikes and Bajaj three-wheelers"),
    "BANKBARODA": ("Bank of Baroda",          "Government bank — banking and loan services"),
    "CANBK":      ("Canara Bank",             "Large government bank across India"),
    "PNB":        ("Punjab National Bank",    "Government bank providing banking services"),
    "TATAPOWER":  ("Tata Power",              "Generates and distributes electricity across India"),
    "VEDL":       ("Vedanta Limited",         "Mines zinc, copper, aluminium, and oil"),
    "DLF":        ("DLF Limited",             "India's largest real estate company"),
    "GAIL":       ("GAIL India",              "Government company — transports natural gas"),
    "IOC":        ("Indian Oil Corporation",  "Government oil company — largest fuel seller in India"),
    "SAIL":       ("Steel Authority of India","Government company that makes steel products"),
    "IDFCFIRSTB": ("IDFC First Bank",         "Private bank — savings, loans, and credit cards"),
    "MUTHOOTFIN": ("Muthoot Finance",         "Provides gold loans — give gold, get cash"),
    "LUPIN":      ("Lupin Limited",           "Makes medicines and generic drugs"),
    "HAVELLS":    ("Havells India",           "Makes fans, lights, cables, and appliances"),
    "SIEMENS":    ("Siemens India",           "Makes industrial equipment and power systems"),
    "M&M":        ("Mahindra & Mahindra",     "Makes Scorpio, Thar, XUV cars and tractors"),
    "POWERGRID":  ("Power Grid Corporation",  "Government — runs India's electricity network"),
    "ULTRACEMCO": ("UltraTech Cement",        "India's largest cement maker"),
    "EICHERMOT":  ("Eicher Motors",           "Makes Royal Enfield bikes and commercial vehicles"),
    "APOLLOHOSP": ("Apollo Hospitals",        "Runs one of India's largest hospital chains"),
}


# ─── Analysis Logic ────────────────────────────────────────────

def calculate_rsi(closes, period=14):
    if len(closes) < period + 2:
        return None
    deltas = np.diff(closes)
    gains  = np.where(deltas > 0, deltas, 0.0)
    losses = np.where(deltas < 0, -deltas, 0.0)
    avg_gain = np.mean(gains[:period])
    avg_loss = np.mean(losses[:period])
    for i in range(period, len(gains)):
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    if avg_loss == 0:
        return 100.0
    return round(100 - (100 / (1 + avg_gain / avg_loss)), 1)


def analyze_stock(kite, symbol, token, quote):
    try:
        to_date   = datetime.now()
        from_date = to_date - timedelta(days=75)
        hist = kite.historical_data(token, from_date, to_date, "day")
        if len(hist) < 52:
            return None
        closes  = [d["close"]  for d in hist]
        volumes = [d["volume"] for d in hist]
        price   = quote.get("last_price", 0)
        if price <= 0:
            return None
        ma50         = round(float(np.mean(closes[-50:])), 2)
        avg_vol      = float(np.mean(volumes[-20:]))
        today_vol    = quote.get("volume", 0)
        volume_ratio = round(today_vol / avg_vol, 2) if avg_vol > 0 else 0
        rsi          = calculate_rsi(closes)
        above_ma50   = price > ma50
        rsi_ok       = rsi is not None and 45 <= rsi <= 65
        volume_ok    = volume_ratio >= 1.5
        return {
            "symbol":       symbol,
            "name":         COMPANY_INFO.get(symbol, (symbol, ""))[0],
            "description":  COMPANY_INFO.get(symbol, ("", "NSE Listed Company"))[1],
            "price":        price,
            "ma50":         ma50,
            "above_ma50":   above_ma50,
            "rsi":          rsi,
            "rsi_ok":       rsi_ok,
            "volume_ratio": volume_ratio,
            "volume_ok":    volume_ok,
            "score":        sum([above_ma50, rsi_ok, volume_ok]),
            "change_pct":   round(quote.get("net_change", 0), 2),
        }
    except Exception:
        return None


# ─── Global Analysis State ─────────────────────────────────────
analysis = {
    "status":   "idle",   # idle | running | done | error
    "result":   None,
    "progress": 0,
    "message":  "",
    "error":    None,
}


def run_analysis_thread():
    global analysis
    analysis["status"]   = "running"
    analysis["progress"] = 0
    analysis["error"]    = None

    try:
        kite = KiteConnect(api_key=API_KEY)
        token = load_saved_token()
        if not token:
            analysis["status"] = "error"
            analysis["error"]  = "Not logged in. Please login first."
            return
        kite.set_access_token(token)

        analysis["message"] = "Fetching market data..."
        analysis["progress"] = 5

        # ── Nifty + VIX ──────────────────────────────────────
        try:
            indices    = kite.quote(["NSE:NIFTY 50", "NSE:INDIA VIX"])
            nifty_data = indices.get("NSE:NIFTY 50", {})
            vix_data   = indices.get("NSE:INDIA VIX", {})
            nifty_price  = nifty_data.get("last_price", 0)
            nifty_prev   = nifty_data.get("ohlc", {}).get("close", nifty_price)
            nifty_pct    = round(((nifty_price - nifty_prev) / nifty_prev) * 100, 2) if nifty_prev else 0
            vix          = vix_data.get("last_price", 0)
        except Exception:
            nifty_price, nifty_pct, vix = 0, 0, 0

        # ── Money management ─────────────────────────────────
        max_per_stock = CAPITAL * 0.20
        cash_reserve  = CAPITAL * 0.30
        max_risk      = CAPITAL * 0.01
        vix_halved    = False
        if vix > 20:
            max_per_stock = max_per_stock / 2
            max_risk      = max_risk / 2
            vix_halved    = True

        # ── Verdict ───────────────────────────────────────────
        if vix > 22 or nifty_pct < -1.5:
            verdict = "RED"
            verdict_text = "Avoid trading today — market is falling and fear is very high"
        elif vix > 18 or nifty_pct < -0.5:
            verdict = "YELLOW"
            verdict_text = "Be careful today — market is nervous, trade smaller amounts"
        else:
            verdict = "GREEN"
            verdict_text = "Good day to trade — market looks calm and healthy"

        analysis["progress"] = 15
        analysis["message"]  = "Loading instruments..."

        # ── Instruments ───────────────────────────────────────
        instruments = kite.instruments("NSE")
        token_map   = {i["tradingsymbol"]: i["instrument_token"] for i in instruments}

        analysis["progress"] = 25
        analysis["message"]  = "Fetching stock prices..."

        # ── Quotes ────────────────────────────────────────────
        ex_syms    = [f"NSE:{s}" for s in WATCH_LIST]
        all_quotes = kite.quote(ex_syms)

        analysis["progress"] = 35
        analysis["message"]  = "Analyzing each stock..."

        candidates = []
        total = len(WATCH_LIST)
        for idx, symbol in enumerate(WATCH_LIST):
            key   = f"NSE:{symbol}"
            quote = all_quotes.get(key)
            tok   = token_map.get(symbol)
            if not quote or not tok:
                continue
            result = analyze_stock(kite, symbol, tok, quote)
            if result:
                candidates.append(result)
            pct = 35 + int((idx / total) * 55)
            analysis["progress"] = pct
            analysis["message"]  = f"Analyzing {symbol}... ({idx+1}/{total})"
            time.sleep(0.4)

        candidates.sort(key=lambda x: (x["score"], x["volume_ratio"]), reverse=True)
        top3   = [c for c in candidates if c["score"] >= 2][:3] or candidates[:3]
        avoid  = []
        for c in candidates:
            if c["rsi"] and c["rsi"] > 70:
                avoid.append({**c, "avoid_reason": f"RSI is {c['rsi']} — too many buyers already. May fall soon."})
            elif not c["above_ma50"]:
                avoid.append({**c, "avoid_reason": f"Price is below its 50-day average (₹{c['ma50']}). Stock is in a downtrend."})
            if len(avoid) == 2:
                break

        # ── Build suggestions ─────────────────────────────────
        suggestions = []
        for s in top3:
            price     = s["price"]
            shares    = int(max_per_stock // price) if price <= max_per_stock else 0
            target1   = round(price * 1.02, 2)
            target2   = round(price * 1.04, 2)
            stop_loss = round(price * 0.985, 2)
            reasons   = []
            if s["volume_ok"]:
                reasons.append(f"Volume is {s['volume_ratio']}x normal — unusual activity happening")
            if s["above_ma50"]:
                diff = round(((price - s["ma50"]) / s["ma50"]) * 100, 1)
                reasons.append(f"Price is {diff}% above its 50-day average — steady uptrend")
            if s["rsi_ok"]:
                reasons.append(f"RSI {s['rsi']} — in safe zone (45–65), not overbought")
            suggestions.append({
                **s,
                "shares":    shares,
                "target1":   target1,
                "target2":   target2,
                "stop_loss": stop_loss,
                "buy_low":   round(price * 0.998, 2),
                "buy_high":  round(price * 1.002, 2),
                "max_invest":round(max_per_stock, 0),
                "max_loss":  round(shares * (price - stop_loss), 2),
                "profit_t1": round(shares * (target1 - price), 2),
                "profit_t2": round(shares * (target2 - price), 2),
                "confidence":min(60 + s["score"] * 12, 85),
                "reasons":   reasons,
                "affordable": price <= max_per_stock,
            })

        analysis["result"] = {
            "date":          datetime.now().strftime("%d %B %Y, %A"),
            "time":          datetime.now().strftime("%I:%M %p"),
            "nifty_price":   nifty_price,
            "nifty_pct":     nifty_pct,
            "nifty_dir":     "UP" if nifty_pct >= 0 else "DOWN",
            "vix":           vix,
            "vix_halved":    vix_halved,
            "verdict":       verdict,
            "verdict_text":  verdict_text,
            "capital":       CAPITAL,
            "max_per_stock": round(max_per_stock, 0),
            "cash_reserve":  round(cash_reserve, 0),
            "max_risk":      round(max_risk, 0),
            "suggestions":   suggestions,
            "avoid":         avoid,
        }
        analysis["status"]   = "done"
        analysis["progress"] = 100
        analysis["message"]  = "Done!"

    except Exception as e:
        analysis["status"] = "error"
        analysis["error"]  = str(e)


# ══════════════════════════════════════════
#  ROUTES
# ══════════════════════════════════════════

@app.route("/")
def index():
    token = load_saved_token()
    logged_in = token is not None
    return render_template("index.html",
                           logged_in=logged_in,
                           analysis=analysis,
                           capital=CAPITAL)


@app.route("/login")
def login():
    kite = KiteConnect(api_key=API_KEY)
    return redirect(kite.login_url())


@app.route("/callback")
def callback():
    req_token = request.args.get("request_token")
    if not req_token:
        return render_template("error.html", msg="Login failed — no token received. Please try again.")
    try:
        kite = KiteConnect(api_key=API_KEY)
        data = kite.generate_session(req_token, api_secret=API_SECRET)
        save_token(data["access_token"])
    except Exception as e:
        return render_template("error.html", msg=f"Login error: {e}")
    return redirect(url_for("index"))


@app.route("/analyze", methods=["POST"])
def start_analysis():
    if analysis["status"] == "running":
        return jsonify({"status": "already_running"})
    thread = threading.Thread(target=run_analysis_thread, daemon=True)
    thread.start()
    return jsonify({"status": "started"})


@app.route("/status")
def get_status():
    return jsonify({
        "status":   analysis["status"],
        "progress": analysis["progress"],
        "message":  analysis["message"],
        "error":    analysis["error"],
    })


@app.route("/results")
def results():
    if analysis["status"] != "done" or not analysis["result"]:
        return redirect(url_for("index"))
    return render_template("results.html", data=analysis["result"])


@app.route("/reset")
def reset():
    global analysis
    analysis = {"status": "idle", "result": None, "progress": 0, "message": "", "error": None}
    return redirect(url_for("index"))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
