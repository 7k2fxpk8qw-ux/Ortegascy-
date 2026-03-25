# ton_client.py - TON blockchain client for Ortegascy
import os
import logging
from typing import List, Dict, Optional
from urllib.parse import quote
import requests
from dotenv import load_dotenv

load_dotenv()

TON_API_KEY = os.getenv("TON_API_KEY", "")
BASE_URL = "https://tonapi.io/v2"

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("Ortegascy_TON")


class TonClient:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or TON_API_KEY
        self.session = requests.Session()
        if self.api_key:
            self.session.headers.update({"X-API-Key": self.api_key})
        logger.info("✅ TonClient listo para Ortegascy 🎵")

    def get_balance(self, address: str) -> float:
        """Return TON balance for the given address in TON units."""
        url = f"{BASE_URL}/accounts/{address}"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return int(r.json().get("balance", 0)) / 1_000_000_000

    def create_invoice(self, wallet: str, amount_ton: float, description: str = "Pago Ortegascy") -> str:
        """Create a TON transfer deeplink for the given wallet and amount."""
        amount_nano = int(amount_ton * 1_000_000_000)
        logger.info(f"💰 Invoice creada: {amount_ton} TON - {description}")
        return f"ton://transfer/{wallet}?amount={amount_nano}&text={quote(description)}"

    def check_payments(self, address: str, limit: int = 20) -> List[Dict]:
        """Return the last `limit` transactions for the given address."""
        url = f"{BASE_URL}/accounts/{address}/transactions?limit={limit}"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("transactions", [])

    def get_jetton_balance(self, owner_address: str, jetton_master: str) -> float:
        """Return the jetton balance (in human-readable units) for owner_address."""
        url = f"{BASE_URL}/accounts/{owner_address}/jettons/{jetton_master}"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        data = r.json()
        balance_raw = int(data.get("balance", 0))
        decimals = int(data.get("jetton", {}).get("decimals", 9))
        return balance_raw / (10 ** decimals)


# Quick test
if __name__ == "__main__":
    try:
        client = TonClient()
        address = "EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N"
        print(f"Balance actual: {client.get_balance(address):.4f} TON")
    except Exception as e:
        print(f"Error al conectar con TON API: {e}")
