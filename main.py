"""
Ortegascy – Kalshi prediction-markets FastAPI service.

Exposes a REST API on top of Kalshi's trading API, letting clients:
  • Browse markets and events
  • Inspect order books and price history
  • Manage orders and view account positions (authenticated)
"""

import logging
from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import requests

from kalshi_client import KalshiClient

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("ortegascy")

app = FastAPI(
    title="Ortegascy – Kalshi Markets API",
    description=(
        "A FastAPI service that proxies Kalshi's prediction-markets REST API. "
        "Public endpoints (markets, events, order books) work without authentication. "
        "Trading endpoints (orders, balance, positions) require a valid Kalshi API key "
        "configured via environment variables."
    ),
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

client = KalshiClient()


# ---------------------------------------------------------------------------
# Exception handler helper
# ---------------------------------------------------------------------------

def _handle(exc: requests.HTTPError) -> HTTPException:
    try:
        detail = exc.response.json()
    except Exception:
        detail = exc.response.text
    return HTTPException(status_code=exc.response.status_code, detail=detail)


# ---------------------------------------------------------------------------
# Health check
# ---------------------------------------------------------------------------

@app.get("/", tags=["health"])
def root():
    """Health-check endpoint."""
    return {"status": "ok", "service": "Ortegascy Kalshi Markets API"}


# ---------------------------------------------------------------------------
# Markets
# ---------------------------------------------------------------------------

@app.get("/markets", tags=["markets"])
def list_markets(
    limit: int = Query(100, ge=1, le=1000, description="Maximum number of markets to return"),
    cursor: Optional[str] = Query(None, description="Pagination cursor from a previous response"),
    event_ticker: Optional[str] = Query(None, description="Filter by event ticker"),
    series_ticker: Optional[str] = Query(None, description="Filter by series ticker"),
    status: Optional[str] = Query(None, description="Filter by status: open, closed, settled"),
):
    """List available prediction markets."""
    try:
        return client.get_markets(
            limit=limit,
            cursor=cursor,
            event_ticker=event_ticker,
            series_ticker=series_ticker,
            status=status,
        )
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/markets/{ticker}", tags=["markets"])
def get_market(ticker: str):
    """Get details for a single market by its ticker symbol."""
    try:
        return client.get_market(ticker)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/markets/{ticker}/orderbook", tags=["markets"])
def get_market_orderbook(
    ticker: str,
    depth: int = Query(10, ge=1, le=200, description="Number of price levels to return per side"),
):
    """Get the live order book for a market."""
    try:
        return client.get_market_orderbook(ticker, depth=depth)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/markets/{ticker}/history", tags=["markets"])
def get_market_history(
    ticker: str,
    limit: int = Query(100, ge=1, le=1000),
):
    """Get price history for a market."""
    try:
        return client.get_market_history(ticker, limit=limit)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/markets/{ticker}/trades", tags=["markets"])
def get_market_trades(
    ticker: str,
    limit: int = Query(100, ge=1, le=1000),
):
    """Get recent trades for a market."""
    try:
        return client.get_market_trades(ticker, limit=limit)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


# ---------------------------------------------------------------------------
# Events
# ---------------------------------------------------------------------------

@app.get("/events", tags=["events"])
def list_events(
    limit: int = Query(100, ge=1, le=1000),
    cursor: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="Filter by status: open, closed, settled"),
    series_ticker: Optional[str] = Query(None),
):
    """List prediction market events."""
    try:
        return client.get_events(
            limit=limit,
            cursor=cursor,
            status=status,
            series_ticker=series_ticker,
        )
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/events/{event_ticker}", tags=["events"])
def get_event(event_ticker: str):
    """Get details for a single event."""
    try:
        return client.get_event(event_ticker)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


# ---------------------------------------------------------------------------
# Series
# ---------------------------------------------------------------------------

@app.get("/series", tags=["series"])
def list_series(
    limit: int = Query(100, ge=1, le=1000),
    cursor: Optional[str] = Query(None),
):
    """List all series."""
    try:
        return client.get_series_list(limit=limit, cursor=cursor)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/series/{series_ticker}", tags=["series"])
def get_series(series_ticker: str):
    """Get details for a series."""
    try:
        return client.get_series(series_ticker)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


# ---------------------------------------------------------------------------
# Account / Portfolio  (authenticated)
# ---------------------------------------------------------------------------

@app.get("/portfolio/balance", tags=["portfolio"])
def get_balance():
    """Get account balance (requires authentication)."""
    try:
        return client.get_balance()
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/portfolio/positions", tags=["portfolio"])
def get_positions(
    limit: int = Query(100, ge=1, le=1000),
    cursor: Optional[str] = Query(None),
    settlement_status: Optional[str] = Query(None),
    ticker: Optional[str] = Query(None),
    event_ticker: Optional[str] = Query(None),
):
    """Get open positions (requires authentication)."""
    try:
        return client.get_positions(
            limit=limit,
            cursor=cursor,
            settlement_status=settlement_status,
            ticker=ticker,
            event_ticker=event_ticker,
        )
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/portfolio/fills", tags=["portfolio"])
def get_fills(
    ticker: Optional[str] = Query(None),
    limit: int = Query(100, ge=1, le=1000),
):
    """Get trade fills (requires authentication)."""
    try:
        return client.get_fills(ticker=ticker, limit=limit)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


# ---------------------------------------------------------------------------
# Orders  (authenticated)
# ---------------------------------------------------------------------------

@app.get("/portfolio/orders", tags=["orders"])
def list_orders(
    ticker: Optional[str] = Query(None),
    event_ticker: Optional[str] = Query(None),
    status: Optional[str] = Query(None, description="Filter by order status: resting, canceled, executed"),
    limit: int = Query(100, ge=1, le=1000),
):
    """List orders (requires authentication)."""
    try:
        return client.get_orders(
            ticker=ticker,
            event_ticker=event_ticker,
            status=status,
            limit=limit,
        )
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


class OrderRequest(BaseModel):
    ticker: str = Field(..., description="Market ticker symbol")
    action: str = Field(..., description="'buy' or 'sell'")
    side: str = Field(..., description="'yes' or 'no'")
    type: str = Field(..., description="'market' or 'limit'")
    count: int = Field(..., ge=1, description="Number of contracts")
    yes_price: Optional[int] = Field(None, ge=1, le=99, description="Limit price for YES side in cents (1-99)")
    no_price: Optional[int] = Field(None, ge=1, le=99, description="Limit price for NO side in cents (1-99)")
    expiration_ts: Optional[int] = Field(None, description="Unix timestamp (seconds) for order expiry")
    sell_position_floor: Optional[int] = Field(None, description="Minimum remaining position after sell")
    buy_max_cost: Optional[int] = Field(None, description="Maximum total cost in cents")


@app.post("/portfolio/orders", tags=["orders"], status_code=201)
def create_order(order: OrderRequest):
    """Place a new order (requires authentication)."""
    try:
        return client.create_order(
            ticker=order.ticker,
            action=order.action,
            side=order.side,
            order_type=order.type,
            count=order.count,
            yes_price=order.yes_price,
            no_price=order.no_price,
            expiration_ts=order.expiration_ts,
            sell_position_floor=order.sell_position_floor,
            buy_max_cost=order.buy_max_cost,
        )
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.get("/portfolio/orders/{order_id}", tags=["orders"])
def get_order(order_id: str):
    """Get details of a specific order (requires authentication)."""
    try:
        return client.get_order(order_id)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


@app.delete("/portfolio/orders/{order_id}", tags=["orders"])
def cancel_order(order_id: str):
    """Cancel an open order (requires authentication)."""
    try:
        return client.cancel_order(order_id)
    except requests.HTTPError as exc:
        raise _handle(exc) from exc


class AmendOrderRequest(BaseModel):
    count: int = Field(..., ge=1, description="New contract count")
    yes_price: Optional[int] = Field(None, ge=1, le=99, description="New limit price for YES side in cents")
    no_price: Optional[int] = Field(None, ge=1, le=99, description="New limit price for NO side in cents")


@app.post("/portfolio/orders/{order_id}/amend", tags=["orders"])
def amend_order(order_id: str, amend: AmendOrderRequest):
    """Amend the count and/or price of an open order (requires authentication)."""
    try:
        return client.amend_order(
            order_id=order_id,
            count=amend.count,
            yes_price=amend.yes_price,
            no_price=amend.no_price,
        )
    except requests.HTTPError as exc:
        raise _handle(exc) from exc
