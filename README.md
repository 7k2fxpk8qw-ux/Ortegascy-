# ton_client.py - Versión FINAL y limpia
import os
import time
import logging
from typing import List, Dict
import requests
from dotenv import load_dotenv

load_dotenv()

TON_API_KEY = os.getenv("TON_API_KEY")
if not TON_API_KEY:
    raise ValueError("❌ Pon tu TON_API_KEY en el archivo .env")

BASE_URL = "https://tonapi.io/v2"
HEADERS = {"X-API-Key": TON_API_KEY}

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("Ortegascy_TON")

class TonClient:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(HEADERS)
        logger.info("✅ TonClient listo para Ortegascy 🎵")

    def get_balance(self, address: str) -> float:
        url = f"{BASE_URL}/accounts/{address}"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return int(r.json().get("balance", 0)) / 1_000_000_000

    def create_invoice(self, amount_ton: float, description: str = "Pago Ortegascy"):
        amount_nano = int(amount_ton * 1_000_000_000)
        logger.info(f"💰 Invoice creada: {amount_ton} TON - {description}")
        return f"ton://transfer/EQ...TU_WALLET_AQUI?amount={amount_nano}&text={description}"

    def check_payments(self, address: str) -> List[Dict]:
        url = f"{BASE_URL}/accounts/{address}/transactions?limit=20"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("transactions", [])

# Prueba rápida
if __name__ == "__main__":
    client = TonClient()
    direccion = "EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N"  # ejemplo
    print(f"Balance actual: {client.get_balance(direccion):.4f} TON")