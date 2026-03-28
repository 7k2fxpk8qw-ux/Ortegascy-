# main.py - Ortegascy FastAPI application with TON and Ethena USDe payments
import os
import logging
from typing import Optional

from fastapi import FastAPI, HTTPException
from dotenv import load_dotenv

from ton_client import TonClient
from ethena_ton import EthenaTonClient

load_dotenv()

logging.basicConfig(level=logging.INFO, format="%(asctime)s | %(levelname)s | %(message)s")
logger = logging.getLogger("Ortegascy")

app = FastAPI(
    title="Ortegascy TON + Ethena API",
    description="Receive TON and USDe (Ethena on TON) payments for Ortegascy 🎵",
    version="1.0.0",
)

PLATFORM_WALLET = os.getenv("PLATFORM_WALLET", "")

ton_client = TonClient()


def _get_ethena_client() -> EthenaTonClient:
    if not PLATFORM_WALLET:
        raise HTTPException(status_code=500, detail="PLATFORM_WALLET not configured")
    return EthenaTonClient(wallet=PLATFORM_WALLET, ton_client=ton_client)


# ---------------------------------------------------------------------------
# Health
# ---------------------------------------------------------------------------


@app.get("/")
def root():
    return {"status": "ok", "service": "Ortegascy TON + Ethena on TON 🎵"}


# ---------------------------------------------------------------------------
# TON endpoints
# ---------------------------------------------------------------------------


@app.get("/balance/{address}")
def get_balance(address: str):
    """Return the native TON balance for *address*."""
    try:
        balance = ton_client.get_balance(address)
        return {"address": address, "balance_ton": balance}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/invoice/ton")
def create_ton_invoice(amount: float, description: Optional[str] = "Pago Ortegascy"):
    """Generate a TON payment deeplink."""
    if not PLATFORM_WALLET:
        raise HTTPException(status_code=500, detail="PLATFORM_WALLET not configured")
    link = ton_client.create_invoice(PLATFORM_WALLET, amount, description)
    return {"deeplink": link, "amount_ton": amount, "description": description}


@app.get("/payments/ton")
def check_ton_payments():
    """Return recent TON transactions for the platform wallet."""
    if not PLATFORM_WALLET:
        raise HTTPException(status_code=500, detail="PLATFORM_WALLET not configured")
    try:
        txs = ton_client.check_payments(PLATFORM_WALLET)
        return {"transactions": txs}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


# ---------------------------------------------------------------------------
# Ethena USDe endpoints
# ---------------------------------------------------------------------------


@app.get("/balance/usde/{address}")
def get_usde_balance(address: str):
    """Return the USDe (Ethena on TON) balance for *address*."""
    client = _get_ethena_client()
    try:
        balance = client.get_usde_balance(address)
        return {"address": address, "balance_usde": balance}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/balance/susde/{address}")
def get_susde_balance(address: str):
    """Return the sUSDe (staked Ethena) balance for *address*."""
    client = _get_ethena_client()
    try:
        balance = client.get_susde_balance(address)
        return {"address": address, "balance_susde": balance}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))


@app.get("/invoice/usde")
def create_usde_invoice(amount: float, description: Optional[str] = "Pago Ortegascy USDe"):
    """Generate a USDe payment deeplink (Ethena on TON)."""
    client = _get_ethena_client()
    link = client.create_usde_invoice(amount, description)
    return {"deeplink": link, "amount_usde": amount, "description": description}


@app.get("/payments/usde")
def check_usde_payments():
    """Return recent USDe jetton transfers received by the platform wallet."""
    client = _get_ethena_client()
    try:
        payments = client.check_usde_payments()
        return {"payments": payments}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc))
