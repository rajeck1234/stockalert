from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
import yfinance as yf
import os

# -----------------------------
# Flask Setup
# -----------------------------
app = Flask(__name__, static_folder="public")
CORS(app)

# PORT = 3000
# const PORT = process.env.PORT || 3000;


PORT = int(os.environ.get("PORT", 3000))

# -----------------------------
# Demo Portfolio (Memory Only)
# -----------------------------
portfolio = []

# -----------------------------
# Stock List
# -----------------------------
stocks = [
    "RELIANCE.NS",
    "TCS.NS",
    "INFY.NS",
    "HDFCBANK.NS",
    "ICICIBANK.NS",
    "ITC.NS"
]

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
            # print(price)
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

        stock = {
            "name": data["name"],
            "price": data["price"]
        }

        portfolio.append(stock)

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

        return jsonify({
            "message": "Stock Sold Successfully",
            "portfolio": portfolio
        })

    except Exception as e:
        return jsonify({"error": str(e)}), 400


# -----------------------------
# Run Server
# -----------------------------
if __name__ == "__main__":
    
    app.run(host="0.0.0.0", port=PORT)

    # app.run(port=PORT, debug=True)

