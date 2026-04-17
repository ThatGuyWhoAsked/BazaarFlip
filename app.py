#!/usr/bin/env python3
from flask import Flask, jsonify, render_template, request
import requests
from datetime import datetime, timedelta
import os
import re

app = Flask(__name__)

# API Configuration
COFLNET_BZ_SPREAD_URL = "https://sky.coflnet.com/api/flip/bazaar/spread"
COFLNET_CRAFT_URL = "https://sky.coflnet.com/api/craft/profit"
TAX_RATE = 0.0125

# Cache configuration
cache = {}

def clean_minecraft_text(text):
    """Remove Minecraft color codes from text."""
    if not text: return ""
    return re.sub(r'§[0-9a-fk-or]', '', text)

def fetch_coflnet_bazaar_flips():
    """Fetch bazaar spread flips from Coflnet."""
    try:
        response = requests.get(COFLNET_BZ_SPREAD_URL, timeout=15)
        response.raise_for_status()
        data = response.json()
        
        normalized_flips = []
        for item in data:
            f = item.get("flip", {})
            # Coflnet naming is flipped: buyPrice is target sell, sellPrice is buy cost
            buy_at = f.get("sellPrice", 0)
            sell_at = f.get("buyPrice", 0)
            
            if buy_at <= 0 or sell_at <= 0: continue
            
            revenue = sell_at * (1 - TAX_RATE)
            profit_per = revenue - buy_at
            margin_pct = (profit_per / buy_at * 100) if buy_at > 0 else 0
            
            normalized_flips.append({
                "productId": f.get("itemTag"),
                "name": clean_minecraft_text(item.get("itemName", f.get("itemTag", "Unknown"))),
                "buyAt": round(buy_at, 2),
                "sellAt": round(sell_at, 2),
                "marginPct": round(margin_pct, 1),
                "profitPotential": round(profit_per * f.get("volume", 0), 0),
                "profitPerHour": round(f.get("profitPerHour", 0), 2),
                "weeklyVolume": int(f.get("volume", 0)),
                "isManipulated": item.get("isManipulated", False),
                "manipulationReason": "Potential Manipulation" if item.get("isManipulated") else None
            })
        
        return normalized_flips
    except Exception as e:
        print(f"⚠️ Coflnet Bazaar API Error: {e}")
        return []

def fetch_coflnet_craft_flips(player=None, profile=None):
    """Fetch craft flipping data from Coflnet with personalization."""
    params = {}
    if player: params["player"] = player
    if profile: params["profile"] = profile
    try:
        response = requests.get(COFLNET_CRAFT_URL, params=params, timeout=15)
        response.raise_for_status()
        data = response.json()
        normalized_flips = []
        for item in data:
            sell_price = item.get("sellPrice", 0)
            craft_cost = item.get("craftCost", 0)
            profit = sell_price - craft_cost
            margin_pct = (profit / craft_cost * 100) if craft_cost > 0 else 0
            normalized_flips.append({
                "productId": item.get("itemId"),
                "name": clean_minecraft_text(item.get("itemName", item.get("itemId", "Unknown"))),
                "sellPrice": round(sell_price, 2),
                "craftCost": round(craft_cost, 2),
                "profit": round(profit, 2),
                "marginPct": round(margin_pct, 1),
                "volume": int(item.get("volume", 0)),
                "ingredients": [
                    {
                        "name": clean_minecraft_text(ing.get("itemId", "Unknown").replace("_", " ").title()),
                        "count": ing.get("count", 0)
                    } for ing in item.get("ingredients", [])
                ]
            })
        normalized_flips.sort(key=lambda x: x["profit"], reverse=True)
        return normalized_flips
    except Exception as e:
        print(f"⚠️ Coflnet Craft API Error: {e}")
        return []

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/flips")
def api_flips():
    player = request.args.get("player", "")
    profile = request.args.get("profile", "")
    cache_key = f"{player}:{profile}"
    now = datetime.now()
    
    if (cache_key not in cache or now - cache[cache_key]["updated"] > timedelta(seconds=55)):
        try:
            bazaar_flips = fetch_coflnet_bazaar_flips()
            craft_flips = fetch_coflnet_craft_flips(player, profile)
            cache[cache_key] = {
                "flips": bazaar_flips,
                "craftFlips": craft_flips,
                "updated": now
            }
        except Exception as e:
            return jsonify({"success": False, "error": str(e)}), 200
            
    entry = cache[cache_key]
    return jsonify({
        "success": True,
        "updated": entry["updated"].isoformat(),
        "totalProducts": len(entry["flips"]),
        "flips": entry["flips"],
        "craftFlips": entry["craftFlips"]
    })

@app.route("/api/health")
def api_health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

if __name__ == "__main__":
    print("🚀 Starting Bazaar Flipper (Pure Coflnet Edition)...")
    port = int(os.environ.get("PORT", 5002))
    app.run(host="0.0.0.0", port=port, debug=False)
