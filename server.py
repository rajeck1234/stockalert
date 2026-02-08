from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import yfinance as yf
import os
import json
import threading
import time

app = Flask(__name__, static_folder="public")
CORS(app)

PORT = int(os.environ.get("PORT", 3000))


# -----------------------------
# JSON Helpers
# -----------------------------
def load_json(file, default):
    try:
        with open(file) as f:
            return json.load(f)
    except:
        return default


def save_json(file, data):
    with open(file, "w") as f:
        json.dump(data, f, indent=2)


# -----------------------------
# Load Files
# -----------------------------
stocks = load_json("stocks.json", [])
portfolio = load_json("portfolio.json", [])
prices_cache = load_json("prices.json", {})


# -----------------------------
# ⭐ BEST PRICE FETCH FUNCTION
# -----------------------------
def fetch_price(symbol):

    try:
        ticker = yf.Ticker(symbol)

        # 1️⃣ Primary
        price = ticker.info.get("currentPrice")

        # 2️⃣ Fallback
        if price is None:
            price = ticker.fast_info.get("last_price")

        # 3️⃣ Last fallback
        if price is None:
            hist = ticker.history(period="1d")
            if not hist.empty:
                price = hist["Close"].iloc[-1]

        return price

    except Exception as e:
        print("Fetch error:", symbol, e)
        return None


# -----------------------------
# Update Prices From Yahoo
# -----------------------------
def update_prices():
    global prices_cache

    print("Updating prices...")

    for symbol in stocks:

        price = fetch_price(symbol)

        if price:
            prices_cache[symbol] = float(price)

    save_json("prices.json", prices_cache)


# -----------------------------
# Background Scheduler
# -----------------------------
def scheduler():
    while True:
        update_prices()
        time.sleep(5)


# -----------------------------
# Serve Frontend
# -----------------------------
@app.route("/")
def index():
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_files(path):
    return send_from_directory(app.static_folder, path)


# -----------------------------
# Get Stocks
# -----------------------------
@app.route("/stocks")
def get_stocks():

    result = []

    for symbol in stocks:
        result.append({
            "name": symbol,
            "price": prices_cache.get(symbol)
        })

    return jsonify(result)


# -----------------------------
# Add Stock
# -----------------------------
@app.route("/add-stock", methods=["POST"])
def add_stock():

    data = request.get_json()
    symbol = data["symbol"].upper()

    if not symbol.endswith(".NS"):
        symbol += ".NS"

    if symbol not in stocks:
        stocks.append(symbol)
        save_json("stocks.json", stocks)

    return jsonify(stocks)


# -----------------------------
# Portfolio
# -----------------------------
@app.route("/portfolio")
def get_portfolio():
    return jsonify(portfolio)


# -----------------------------
# Buy Stock
# -----------------------------
@app.route("/buy", methods=["POST"])
def buy_stock():

    data = request.get_json()
    buy_price = float(data["price"])

    stock = {
        "name": data["name"],
        "buy_price": buy_price,
        "target_price": buy_price * 1.03,
        "highest_price": buy_price,
        "alert_triggered": False
    }

    portfolio.append(stock)
    save_json("portfolio.json", portfolio)

    return jsonify(portfolio)


# -----------------------------
# Sell Stock
# -----------------------------
@app.route("/sell", methods=["POST"])
def sell_stock():

    name = request.get_json()["name"]

    global portfolio
    portfolio = [s for s in portfolio if s["name"] != name]

    save_json("portfolio.json", portfolio)

    return jsonify(portfolio)


# -----------------------------
# ALERT LOGIC
# -----------------------------
@app.route("/check-alerts")
def check_alerts():

    alerts = []

    for stock in portfolio:

        symbol = stock["name"]
        current_price = prices_cache.get(symbol)

        if not current_price:
            continue

        buy_price = stock["buy_price"]
        target_price = stock["target_price"]
        highest_price = stock["highest_price"]

        # Ignore before 3%
        if current_price < target_price:
            continue

        # Update highest
        if current_price > highest_price:
            stock["highest_price"] = current_price
            stock["alert_triggered"] = False
            continue

        # Trailing drop
        drop_percent = (highest_price - current_price) / highest_price

        if drop_percent >= 0.01 and not stock["alert_triggered"]:

            profit_percent = (current_price - buy_price) / buy_price

            if profit_percent >= 0.03:
                stock["alert_triggered"] = True
                alerts.append(symbol)

    save_json("portfolio.json", portfolio)

    return jsonify(alerts)


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":

    threading.Thread(target=scheduler, daemon=True).start()

    app.run(host="0.0.0.0", port=PORT)
