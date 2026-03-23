# Ortegascy – Kalshi Prediction Markets API

A FastAPI service that exposes [Kalshi](https://kalshi.com) prediction-market data and trading through a clean REST API.

## Features

- 📊 **Browse markets & events** – list, filter and inspect prediction markets across news, sports, finance and more
- 📖 **Order book & trade history** – real-time depth and historical prices for any market
- 💼 **Account management** – view balances, open positions and fill history
- 🛒 **Order management** – place, amend and cancel limit/market orders
- 🔐 **RSA-PSS authentication** – Kalshi's signed-request auth model is handled automatically

## Quick start

### 1. Clone & install

```bash
pip install -r requirements.txt
```

### 2. Configure environment variables

Copy the example below to a `.env` file (never commit real secrets):

```dotenv
# Kalshi trading API base URL (switch to demo for testing)
KALSHI_API_BASE=https://trading-api.kalshi.com/trade-api/v2
# KALSHI_API_BASE=https://demo-api.kalshi.co/trade-api/v2   # demo

# Kalshi API credentials (required only for authenticated endpoints)
KALSHI_API_KEY_ID=your-key-id-here
KALSHI_PRIVATE_KEY_PATH=/path/to/your/private_key.pem
```

Public market-data endpoints work without credentials.

### 3. Run

```bash
uvicorn main:app --reload
```

Interactive API docs are available at <http://localhost:8000/docs>.

## API overview

| Method | Path | Auth | Description |
|--------|------|------|-------------|
| GET | `/` | – | Health check |
| GET | `/markets` | – | List markets (supports filtering) |
| GET | `/markets/{ticker}` | – | Single market details |
| GET | `/markets/{ticker}/orderbook` | – | Live order book |
| GET | `/markets/{ticker}/history` | – | Price history |
| GET | `/markets/{ticker}/trades` | – | Recent trades |
| GET | `/events` | – | List events |
| GET | `/events/{event_ticker}` | – | Single event details |
| GET | `/series` | – | List series |
| GET | `/series/{series_ticker}` | – | Single series details |
| GET | `/portfolio/balance` | ✅ | Account balance |
| GET | `/portfolio/positions` | ✅ | Open positions |
| GET | `/portfolio/fills` | ✅ | Trade fills |
| GET | `/portfolio/orders` | ✅ | List orders |
| POST | `/portfolio/orders` | ✅ | Place an order |
| GET | `/portfolio/orders/{id}` | ✅ | Order details |
| DELETE | `/portfolio/orders/{id}` | ✅ | Cancel an order |
| POST | `/portfolio/orders/{id}/amend` | ✅ | Amend an order |

## Deployment

The `Procfile` is configured for Heroku-style platforms:

```
web: uvicorn main:app --host 0.0.0.0 --port $PORT
```

## License

MIT
