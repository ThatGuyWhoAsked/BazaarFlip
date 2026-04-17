# Hypixel Bazaar Flipper - Agent Instructions

This project provides a real-time web application and CLI tool for identifying profitable flips in the Hypixel SkyBlock Bazaar.

## 🏗️ Architecture & APIs

- **Web Application (`app.py`)**: Uses the **Coflnet API** (`sky.coflnet.com`).
  - **Bazaar Spread API**: `https://sky.coflnet.com/api/flip/bazaar/spread`
  - **Craft Profit API**: `https://sky.coflnet.com/api/craft/profit`
  - **Note**: Coflnet's naming convention in the JSON response is often "flipped" compared to standard terminology: `sellPrice` is usually the buy cost (entry), and `buyPrice` is the target sell price (exit).
- **CLI Tool (`main.py`)**: Uses the **Official Hypixel API** (`api.hypixel.net`).
  - Requires `HYPIXEL_API_KEY` environment variable.
  - Implements its own logic for calculating flips based on `quick_status`.

## 📈 Business Logic & Calculations

- **Tax Rate**: Always factor in a **1.25% bazaar tax** (`0.0125`) on the final sell price.
- **Profit Calculation**: `Net Profit = (Sell Price * (1 - TAX_RATE)) - Buy Price`.
- **Margin Calculation**: `Margin % = (Net Profit / Buy Price) * 100`.
- **Liquidity Filters**:
  - Minimum Margin: 1.0% (default)
  - Minimum Weekly Volume: 10,000 (default)
  - Minimum Sell Orders: 3 (default for CLI)

## 🛠️ Development Standards

- **Python/Flask**: Adhere to idiomatic Python. Use Flask for the web backend.
- **Coflnet Attribution (Mandatory)**: 
  - All webpages using Coflnet data MUST attribute `sky.coflnet.com` as the data source.
  - Provide a link to `https://sky.coflnet.com/data` or the relevant resource (e.g., `https://sky.coflnet.com/flips`).
  - Example: "Prices provided by SkyCofl" linking to the relevant item or flip page.
- **Concurrency & Caching**:
  - The web app implements a ~55-second cache to prevent API rate limiting.
  - Avoid frequent API calls outside this cache.
- **Frontend**: Located in `templates/index.html`. Uses Vanilla JS and CSS (glass morphism theme).
- **Verification**:
  - When modifying calculation logic, verify both `app.py` and `main.py` if they share that logic.
  - Always check if a change to the backend requires an update to the `api/flips` response format handled by the frontend.

## ⚠️ Safety & Constraints

- **No API Spams**: Do not bypass or significantly reduce cache times without considering rate limits (Hypixel and Coflnet).
- **Sensitive Data**: Never commit `HYPIXEL_API_KEY` to source control.
- **Logic Integrity**: Ensure the 1.25% tax is consistently applied; failing to account for it will mislead users about profitability.
