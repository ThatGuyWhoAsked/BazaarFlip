# 🏪 Bazaar Flipper

A modern, real-time web application for identifying profitable arbitrage opportunities in Hypixel SkyBlock's Bazaar.

![Bazaar Flipper Screenshot](https://via.placeholder.com/800x400/0a0a0c/10b981?text=Bazaar+Flipper+Dashboard)

## ✨ Features

- **Real-time Data**: Fetches live bazaar and craft data from the [Coflnet API](https://sky.coflnet.com/data) every 60 seconds.
- **Prices provided by [SkyCofl](https://sky.coflnet.com/data)**.
- **Smart Filtering**: Automatically identifies profitable flips based on:
  - Minimum margin percentage (default: 1%)
  - Minimum weekly volume (default: 10,000 coins)
  - Minimum sell orders (default: 3) for liquidity
- **Tax Calculation**: Accounts for Hypixel's 1.25% bazaar tax
- **Modern UI**: Beautiful, responsive dark theme with glass morphism design
- **Custom Filters**: Adjust margin, volume, and result limits on the fly
- **Profit Ranking**: Sorts opportunities by estimated total profit
- **Auto-refresh**: Updates data automatically without page reload

## 🚀 Quick Start

### Prerequisites

- Python 3.7 or higher
- pip (Python package manager)
- Internet connection

### Installation

1. **Clone or download** the project:
   ```bash
   cd hypixel-bazaar-flipper
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python app.py
   ```

4. **Open your browser** and navigate to:
   ```
   http://localhost:5001
   ```

That's it! The dashboard will automatically start fetching and displaying bazaar flip opportunities.

## 📖 Usage

### Dashboard Interface

1. **Stats Cards** (Top of page):
   - **Items Tracked**: Total number of bazaar items being monitored
   - **Best Margin**: Highest profit margin percentage found
   - **Opportunities**: Number of viable flip opportunities
   - **Top Profit**: Estimated profit from the best opportunity

2. **Filter Controls**:
   - **Min Margin**: Minimum profit margin percentage (e.g., 1.0 = 1%)
   - **Min Volume**: Minimum weekly trading volume in coins
   - **Show**: Number of results to display (10, 15, 25, 50, 100)

3. **Results Table**:
   - **Item**: Name of the bazaar item
   - **Buy At**: Recommended buy price (instant buy)
   - **Sell At**: Recommended sell price (instant sell)
   - **Margin**: Profit margin percentage
   - **Volume/wk**: Weekly trading volume
   - **Est. Profit**: Estimated total profit potential

### How Flips Are Calculated

The algorithm identifies arbitrage opportunities by:

1. **Fetching** current buy and sell prices from the Hypixel API
2. **Calculating** the price difference (buy price - sell price)
3. **Applying** the 1.25% bazaar tax to the transaction
4. **Filtering** based on:
   - Minimum profit margin (default 1%)
   - Minimum weekly volume (default 10,000)
   - Minimum sell orders for liquidity (default 3)
5. **Ranking** by total profit potential (profit per item × weekly volume)

### Example Flip

If an item has:
- **Instant Buy Price**: 100 coins
- **Instant Sell Price**: 105 coins
- **Weekly Volume**: 50,000 items

The calculation:
- **Gross Margin**: 105 - 100 = 5 coins
- **Tax (1.25%)**: 105 × 0.0125 = 1.31 coins
- **Net Profit**: 5 - 1.31 = 3.69 coins per item
- **Total Potential**: 3.69 × 50,000 = 184,500 coins/week

## 🔧 Configuration

### Environment Variables

Optional environment variables:

- `HYPIXEL_API_KEY`: Your Hypixel API key (not required, but recommended for higher rate limits)

To set it:
```bash
export HYPIXEL_API_KEY="your-api-key-here"
python app.py
```

### Modifying Default Filters

Edit the constants in `app.py`:

```python
DEFAULT_MIN_MARGIN_PCT = 1.0      # Minimum margin percentage
DEFAULT_MIN_WEEKLY_VOLUME = 10000 # Minimum weekly volume
DEFAULT_MIN_SELL_ORDERS = 3       # Minimum sell orders
```

### Changing Refresh Rate

The dashboard refreshes every 60 seconds by default. To change this, modify the JavaScript in `templates/index.html`:

```javascript
// Change 60000 (60 seconds) to your desired interval
refreshInterval = setInterval(fetchFlips, 60000);
```

## 🌐 API Endpoints

The application provides several API endpoints for programmatic access:

### GET `/api/flips`
Returns current flip opportunities.

**Response:**
```json
{
  "success": true,
  "updated": "2024-01-15T14:30:00",
  "totalProducts": 234,
  "flips": [
    {
      "name": "Enchanted Diamond",
      "buyAt": 1250.1,
      "sellAt": 1275.9,
      "marginPct": 2.1,
      "profitPotential": 125000,
      "weeklyVolume": 50000
    }
  ]
}
```

### GET `/api/health`
Health check endpoint.

**Response:**
```json
{
  "status": "healthy",
  "cacheValid": true,
  "lastUpdate": "2024-01-15T14:30:00",
  "timestamp": "2024-01-15T14:30:45"
}
```

### GET `/api/product/<product_id>`
Get details for a specific product.

**Response:**
```json
{
  "productId": "ENCHANTED_DIAMOND",
  "data": { /* full product data */ },
  "flipOpportunity": { /* flip calculation if viable */ }
}
```

## 🛠️ Development

### Running in Development Mode

```bash
# Install development dependencies
pip install -r requirements.txt

# Run with debug mode enabled
python -c "from app import app; app.run(debug=True, port=5001)"
```

### Project Structure

```
hypixel-bazaar-flipper/
├── app.py                 # Flask backend server
├── main.py                # CLI version (standalone)
├── requirements.txt       # Python dependencies
├── templates/
│   └── index.html        # Frontend dashboard
└── README.md             # This file
```

### Dependencies

- **Flask**: Web framework
- **Requests**: HTTP library for API calls
- **Rich**: Terminal UI library (for CLI version)

## ⚠️ Important Notes

1. **Not Financial Advice**: This tool is for educational purposes. Always do your own research.

2. **Market Volatility**: Bazaar prices change rapidly. Opportunities may disappear quickly.

3. **API Rate Limits**: Hypixel API has rate limits. The app caches data for 55 seconds to respect these limits.

4. **Tax Consideration**: The 1.25% bazaar tax is already factored into all profit calculations.

5. **Liquidity Risk**: High-volume items are prioritized to ensure you can actually execute the trades.

## 🤝 Contributing

Contributions are welcome! Feel free to:

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## 📄 License

This project is provided as-is for educational purposes.

## 🙏 Acknowledgments

- **Hypixel**: For providing the public bazaar API
- **Hypixel SkyBlock Community**: For inspiration and testing

## 💬 Support

If you encounter issues:

1. Check that Python and dependencies are properly installed
2. Ensure you have an internet connection
3. Verify that Hypixel API is accessible
4. Check the console for error messages

## 🔄 Changelog

### v2.0 (Current)
- ✨ Complete web interface redesign
- 🎨 Modern dark theme with glass morphism
- 🔧 Custom filter controls
- 📊 Enhanced statistics dashboard
- 🚀 Improved performance and caching
- 📱 Fully responsive design

### v1.0
- Initial CLI-based implementation
- Basic flip detection algorithm

---

**Happy flipping! 🚀**

*Remember: The bazaar market is competitive. Act fast on good opportunities, but always trade responsibly.*