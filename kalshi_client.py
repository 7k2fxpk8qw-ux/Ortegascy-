import json
import os
import time
import base64
import logging
from typing import Optional, Dict, Any

import requests
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger("kalshi_client")

KALSHI_API_BASE = os.getenv("KALSHI_API_BASE", "https://trading-api.kalshi.com/trade-api/v2")
KALSHI_DEMO_API_BASE = "https://demo-api.kalshi.co/trade-api/v2"
KALSHI_API_KEY_ID = os.getenv("KALSHI_API_KEY_ID", "")
KALSHI_PRIVATE_KEY_PATH = os.getenv("KALSHI_PRIVATE_KEY_PATH", "")


def _load_private_key():
    path = KALSHI_PRIVATE_KEY_PATH
    if not path or not os.path.exists(path):
        return None
    with open(path, "rb") as f:
        return serialization.load_pem_private_key(f.read(), password=None)


def _sign_request(method: str, path: str, body: str = "") -> Dict[str, str]:
    """Generate RSA-PSS signed headers for Kalshi API authentication."""
    private_key = _load_private_key()
    if not private_key or not KALSHI_API_KEY_ID:
        return {}

    timestamp_ms = str(int(time.time() * 1000))
    msg_string = timestamp_ms + method.upper() + path + body
    message = msg_string.encode("utf-8")

    signature = private_key.sign(
        message,
        padding.PSS(
            mgf=padding.MGF1(hashes.SHA256()),
            salt_length=padding.PSS.DIGEST_LENGTH,
        ),
        hashes.SHA256(),
    )
    sig_b64 = base64.b64encode(signature).decode("utf-8")

    return {
        "KALSHI-ACCESS-KEY": KALSHI_API_KEY_ID,
        "KALSHI-ACCESS-TIMESTAMP": timestamp_ms,
        "KALSHI-ACCESS-SIGNATURE": sig_b64,
        "Content-Type": "application/json",
    }


class KalshiClient:
    """Client for the Kalshi prediction markets REST API."""

    def __init__(self, base_url: Optional[str] = None):
        self.base_url = (base_url or KALSHI_API_BASE).rstrip("/")
        self.session = requests.Session()
        self.session.headers.update({"Content-Type": "application/json"})
        logger.info("KalshiClient initialised with base_url=%s", self.base_url)

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def _headers(self, method: str, path: str, body: str = "") -> Dict[str, str]:
        return _sign_request(method, path, body)

    def _get(self, path: str, params: Optional[Dict] = None) -> Any:
        headers = self._headers("GET", path)
        resp = self.session.get(self._url(path), params=params, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _post(self, path: str, payload: Dict) -> Any:
        body = json.dumps(payload)
        headers = self._headers("POST", path, body)
        resp = self.session.post(self._url(path), data=body, headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    def _delete(self, path: str) -> Any:
        headers = self._headers("DELETE", path)
        resp = self.session.delete(self._url(path), headers=headers, timeout=10)
        resp.raise_for_status()
        return resp.json()

    # ------------------------------------------------------------------
    # Markets
    # ------------------------------------------------------------------

    def get_markets(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        event_ticker: Optional[str] = None,
        series_ticker: Optional[str] = None,
        status: Optional[str] = None,
    ) -> Dict:
        """List markets with optional filters."""
        params: Dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if event_ticker:
            params["event_ticker"] = event_ticker
        if series_ticker:
            params["series_ticker"] = series_ticker
        if status:
            params["status"] = status
        return self._get("/markets", params=params)

    def get_market(self, ticker: str) -> Dict:
        """Get details for a single market by ticker."""
        return self._get(f"/markets/{ticker}")

    def get_market_orderbook(self, ticker: str, depth: int = 10) -> Dict:
        """Get the order book for a market."""
        return self._get(f"/markets/{ticker}/orderbook", params={"depth": depth})

    def get_market_history(self, ticker: str, limit: int = 100) -> Dict:
        """Get price history for a market."""
        return self._get(f"/markets/{ticker}/history", params={"limit": limit})

    def get_market_trades(self, ticker: str, limit: int = 100) -> Dict:
        """Get recent trades for a market."""
        return self._get(f"/markets/{ticker}/trades", params={"limit": limit})

    # ------------------------------------------------------------------
    # Events
    # ------------------------------------------------------------------

    def get_events(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        status: Optional[str] = None,
        series_ticker: Optional[str] = None,
    ) -> Dict:
        """List events with optional filters."""
        params: Dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if status:
            params["status"] = status
        if series_ticker:
            params["series_ticker"] = series_ticker
        return self._get("/events", params=params)

    def get_event(self, event_ticker: str) -> Dict:
        """Get details for a single event by ticker."""
        return self._get(f"/events/{event_ticker}")

    # ------------------------------------------------------------------
    # Account (authenticated)
    # ------------------------------------------------------------------

    def get_balance(self) -> Dict:
        """Get account balance."""
        return self._get("/portfolio/balance")

    def get_positions(
        self,
        limit: int = 100,
        cursor: Optional[str] = None,
        settlement_status: Optional[str] = None,
        ticker: Optional[str] = None,
        event_ticker: Optional[str] = None,
    ) -> Dict:
        """Get open positions."""
        params: Dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        if settlement_status:
            params["settlement_status"] = settlement_status
        if ticker:
            params["ticker"] = ticker
        if event_ticker:
            params["event_ticker"] = event_ticker
        return self._get("/portfolio/positions", params=params)

    def get_fills(self, ticker: Optional[str] = None, limit: int = 100) -> Dict:
        """Get trade fills."""
        params: Dict[str, Any] = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        return self._get("/portfolio/fills", params=params)

    # ------------------------------------------------------------------
    # Orders (authenticated)
    # ------------------------------------------------------------------

    def get_orders(
        self,
        ticker: Optional[str] = None,
        event_ticker: Optional[str] = None,
        status: Optional[str] = None,
        limit: int = 100,
    ) -> Dict:
        """Get open/historical orders."""
        params: Dict[str, Any] = {"limit": limit}
        if ticker:
            params["ticker"] = ticker
        if event_ticker:
            params["event_ticker"] = event_ticker
        if status:
            params["status"] = status
        return self._get("/portfolio/orders", params=params)

    def create_order(
        self,
        ticker: str,
        action: str,
        side: str,
        order_type: str,
        count: int,
        yes_price: Optional[int] = None,
        no_price: Optional[int] = None,
        expiration_ts: Optional[int] = None,
        sell_position_floor: Optional[int] = None,
        buy_max_cost: Optional[int] = None,
    ) -> Dict:
        """
        Place an order.

        :param ticker: Market ticker (e.g. ``INXD-23DEC31-T4000``)
        :param action: ``"buy"`` or ``"sell"``
        :param side: ``"yes"`` or ``"no"``
        :param order_type: ``"market"`` or ``"limit"``
        :param count: Number of contracts
        :param yes_price: Limit price in cents for YES side (1-99)
        :param no_price: Limit price in cents for NO side (1-99)
        :param expiration_ts: Unix timestamp (seconds) for GTC expiry
        :param sell_position_floor: Minimum remaining position after sell
        :param buy_max_cost: Maximum total cost in cents
        """
        payload: Dict[str, Any] = {
            "ticker": ticker,
            "action": action,
            "side": side,
            "type": order_type,
            "count": count,
        }
        if yes_price is not None:
            payload["yes_price"] = yes_price
        if no_price is not None:
            payload["no_price"] = no_price
        if expiration_ts is not None:
            payload["expiration_ts"] = expiration_ts
        if sell_position_floor is not None:
            payload["sell_position_floor"] = sell_position_floor
        if buy_max_cost is not None:
            payload["buy_max_cost"] = buy_max_cost
        return self._post("/portfolio/orders", payload)

    def get_order(self, order_id: str) -> Dict:
        """Get details of a specific order."""
        return self._get(f"/portfolio/orders/{order_id}")

    def cancel_order(self, order_id: str) -> Dict:
        """Cancel an open order."""
        return self._delete(f"/portfolio/orders/{order_id}")

    def amend_order(self, order_id: str, count: int, yes_price: Optional[int] = None, no_price: Optional[int] = None) -> Dict:
        """Amend the count and/or price of an open order."""
        payload: Dict[str, Any] = {"count": count}
        if yes_price is not None:
            payload["yes_price"] = yes_price
        if no_price is not None:
            payload["no_price"] = no_price
        return self._post(f"/portfolio/orders/{order_id}/amend", payload)

    # ------------------------------------------------------------------
    # Series
    # ------------------------------------------------------------------

    def get_series(self, series_ticker: str) -> Dict:
        """Get details for a series."""
        return self._get(f"/series/{series_ticker}")

    def get_series_list(self, limit: int = 100, cursor: Optional[str] = None) -> Dict:
        """List all series."""
        params: Dict[str, Any] = {"limit": limit}
        if cursor:
            params["cursor"] = cursor
        return self._get("/series", params=params)
