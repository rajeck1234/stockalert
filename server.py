from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import yfinance as yf
import os

# -----------------------------
# Flask Setup
# -----------------------------
app = Flask(__name__, static_folder="public")
CORS(app)

live_prices = {}
# PORT = 3000
# const PORT = process.env.PORT || 3000;


PORT = int(os.environ.get("PORT", 3000))

# -----------------------------
# Demo Portfolio (Memory Only)
# -----------------------------
# portfolio = []



# -----------------------------
# Stock List
# -----------------------------
import json

with open("stocks.json") as f:
    stocks = json.load(f)
    
with open("portfolio.json") as f:
    portfolio = json.load(f)    
# stocks = [
#     "RELIANCE.NS",
#     "TCS.NS",
#     "INFY.NS",
#     "HDFCBANK.NS",
#     "ICICIBANK.NS",
#     "MAZDOCK.NS",
#     "ITC.NS"
# ]

# -----------------------------
# Serve Frontend
# -----------------------------
@app.route("/")
def serve_frontend():
    return send_from_directory(app.static_folder, "index.html")

@app.route("/<path:path>")
def serve_static_files(path):
    return send_from_directory(app.static_folder, path)


# -----------------------------
# Get Live Stock Prices
# -----------------------------
@app.route("/stocks", methods=["GET"])
def get_stocks():

    try:
        result = []

        for symbol in stocks:
            ticker = yf.Ticker(symbol)

            # Try getting current price
            price = ticker.info.get("currentPrice")

            # Fallback if currentPrice missing
            live_prices[symbol] = price
            print(price)
            if price is None:
                price = ticker.fast_info.get("last_price")

            result.append({
                "name": symbol,
                "price": price,
                
            })

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500


# -----------------------------
# Get Portfolio
# -----------------------------

@app.route("/add-stock", methods=["POST"])
def add_stock():
    try:
        data = request.get_json()
        symbol = data["symbol"].upper()

        if not symbol.endswith(".NS"):
            symbol += ".NS"

        if symbol not in stocks:
            stocks.append(symbol)

            # ⭐ Save to file permanently
            with open("stocks.json", "w") as f:
                json.dump(stocks, f)

        return jsonify({"message": "Stock Added", "stocks": stocks})

    except Exception as e:
        return jsonify({"error": str(e)}), 400


@app.route("/portfolio", methods=["GET"])
def get_portfolio():
    
    print(portfolio)
    return jsonify(portfolio)


# -----------------------------
# Buy Stock
# -----------------------------
@app.route("/buy", methods=["POST"])
def buy_stock():
    try:
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

        # ⭐ Save to JSON
        with open("portfolio.json", "w") as f:
            json.dump(portfolio, f)

        return jsonify({
            "message": "Stock Bought Successfully",
            "portfolio": portfolio
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Sell Stock
# -----------------------------
@app.route("/sell", methods=["POST"])
def sell_stock():
    try:
        data = request.get_json()
        stock_name = data["name"]

        global portfolio
        portfolio = [s for s in portfolio if s["name"] != stock_name]

        # ⭐ Save updated list
        with open("portfolio.json", "w") as f:
            json.dump(portfolio, f)

        return jsonify({
            "message": "Stock Sold Successfully",
            "portfolio": portfolio
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Run Server
# -----------------------------
@app.route("/check-alerts", methods=["GET"])
def check_alerts():
    alerts = []
    print("hii")
    for stock in portfolio:
        # ticker = yf.Ticker(stock["name"])
        # current_price = ticker.fast_info.get("currentPrice")
        current_price = live_prices.get(stock["name"])
        print(current_price)
        print(stock)
        # print("uuu")
        if current_price is None:
            continue
         
        if current_price >= stock["target_price"]:
            # print("ooo")
            # stock["alert_triggered"] = True
            # alerts.append(stock["name"])

            if current_price > stock["highest_price"]:
                stock["highest_price"] = current_price
                stock["alert_triggered"] = False

            elif current_price < stock["highest_price"]:
                stock["alert_triggered"] = True
                alerts.append(stock["name"])
    # alerts.append(stock["name"])
    return jsonify(alerts)


if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=PORT)

    # app.run(port=PORT, debug=True)

