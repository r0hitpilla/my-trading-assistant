# 📈 NSE Trader — Personal Indian Stock Market Assistant

A professional, AI-powered trading dashboard built for the Indian stock market (NSE). Designed for beginner traders — every suggestion is explained in plain English.

🔗 **Live App:** https://web-production-8b6a.up.railway.app/dashboard

---

## What This Does

- Scans 50 NSE stocks every morning using real-time Zerodha data
- Gives you the **top 3 stock suggestions** with exact buy price, targets, and stop loss
- Explains every technical term in simple language (no jargon)
- Lets you **place orders directly on Zerodha** from the dashboard
- Tracks your live portfolio and today's P&L
- Works on mobile and desktop

---

## Features

| Feature | Details |
|---|---|
| Live Market Data | Nifty 50, Bank Nifty, India VIX — refreshes every 30 seconds |
| AI Suggestions | Screens 50 stocks for RSI, volume, moving average, and trend |
| Order Placement | One-click BUY redirects to Zerodha Kite with stock pre-filled |
| Portfolio Tracker | Live positions and order status from your Zerodha account |
| Watchlist | 8 stocks with signal, RSI bar, candlestick pattern, and analysis |
| Beginner Mode | Every technical term has a plain English explanation on hover |
| Mobile Friendly | Fully responsive — works on any phone browser |

---

## Tech Stack

- **Backend:** Python, Flask, Gunicorn
- **Data:** Zerodha Kite Connect API
- **Frontend:** Vanilla HTML/CSS/JS (single file dashboard)
- **Hosting:** Railway
- **Fonts:** DM Sans + DM Mono (Google Fonts)

---

## Setup (Run Locally)

### 1. Clone the repo
```bash
git clone https://github.com/r0hitpilla/my-trading-assistant.git
cd my-trading-assistant
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Add your Zerodha API credentials
Edit `config.py`:
```python
API_KEY    = "your_kite_api_key"
API_SECRET = "your_kite_api_secret"
CAPITAL    = 2000   # Your trading capital in rupees
```

### 4. Set the Redirect URL in Zerodha Kite Connect
Go to [kite.trade](https://kite.trade) → your app → set Redirect URL to:
```
http://127.0.0.1:5000/callback
```

### 5. Run
```bash
python app.py
```
Open `http://localhost:5000/dashboard` in your browser.

---

## Deploy to Railway

1. Push this repo to GitHub
2. Go to [railway.app](https://railway.app) → New Project → Deploy from GitHub
3. Add these environment variables in Railway:

| Variable | Value |
|---|---|
| `KITE_API_KEY` | Your Zerodha API key |
| `KITE_API_SECRET` | Your Zerodha API secret |
| `CAPITAL` | Your trading capital (e.g. `2000`) |
| `TRADING_STYLE` | `intraday` or `swing` |

4. Update the Redirect URL in Zerodha Kite Connect to your Railway URL + `/callback`

---

## How to Use Every Morning

1. Open the dashboard on your phone or computer
2. Login with Zerodha (once per day)
3. Dashboard auto-scans 50 stocks — takes 1–2 minutes
4. Review the top 3 suggestions
5. Click **BUY** → review order details → confirm on Zerodha Kite
6. Set a stop loss immediately after buying
7. Sell before 3:15 PM (intraday) or at your target price

---

## Important Disclaimer

> ⚠️ This tool is for **research and educational purposes only**.
> It is not financial advice. Stock markets involve risk.
> Always verify prices on Zerodha before placing any order.
> The final decision is always yours.

---

## Project Structure

```
my-trading-assistant/
├── app.py                  # Flask backend + Zerodha API integration
├── config.py               # Your credentials and trading profile
├── dashboard.html          # Professional trading dashboard (single file)
├── trading_assistant.py    # Terminal version (alternative to web UI)
├── templates/
│   ├── index.html          # Login / analysis trigger page
│   └── results.html        # Analysis results page
├── static/
│   └── style.css           # Dark theme styles
├── requirements.txt
└── Procfile                # Railway deployment config
```

---

Built with ❤️ for Indian retail investors.
