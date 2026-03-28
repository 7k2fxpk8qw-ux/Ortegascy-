# ethena_ton.py - Ethena USDe integration on TON blockchain
"""
Ethena on TON
-------------
This module enables Ethena's USDe stablecoin payments and sUSDe staking
on the TON blockchain via the jetton (TON token standard) interface.

USDe is Ethena's synthetic dollar stablecoin.  On TON it is deployed as a
jetton with its own master contract address.  Users can:
  - Check their USDe balance on TON.
  - Generate a USDe payment deeplink (ton://transfer with jetton payload).
  - Check incoming USDe jetton transfers.
"""

import logging
import os
from typing import List, Dict, Optional
from urllib.parse import quote

from ton_client import TonClient

logger = logging.getLogger("Ortegascy_Ethena")

# Ethena USDe jetton master address on TON mainnet.
USDE_JETTON_MASTER = os.getenv(
    "USDE_JETTON_MASTER",
    "EQAvlWFDxGF2Ba2ySNgcJwF0M0jjPYVWJ8XQcj9OzgJJMhRk",  # USDe on TON mainnet
)
SUSDE_JETTON_MASTER = os.getenv(
    "SUSDE_JETTON_MASTER",
    "EQBzAm1SiJfnFf7sDSIx1L7pFBk9bDi-dC1kYlLx-OFGSKpq",  # sUSDe on TON mainnet
)

# USDe uses 18 decimals matching the EVM version.
USDE_DECIMALS = 18


class EthenaTonClient:
    """High-level client for Ethena USDe/sUSDe operations on TON."""

    def __init__(self, wallet: str, ton_client: Optional[TonClient] = None):
        """
        Parameters
        ----------
        wallet:
            The TON wallet address that receives payments.
        ton_client:
            An optional pre-configured :class:`TonClient`.  A new one is
            created if not provided.
        """
        self.wallet = wallet
        self.ton = ton_client or TonClient()

    # ------------------------------------------------------------------
    # Balance helpers
    # ------------------------------------------------------------------

    def get_usde_balance(self, address: Optional[str] = None) -> float:
        """Return the USDe balance (in USDe units) for *address*.

        Defaults to :attr:`wallet` when *address* is ``None``.
        """
        addr = address or self.wallet
        return self.ton.get_jetton_balance(addr, USDE_JETTON_MASTER)

    def get_susde_balance(self, address: Optional[str] = None) -> float:
        """Return the sUSDe balance (in sUSDe units) for *address*."""
        addr = address or self.wallet
        return self.ton.get_jetton_balance(addr, SUSDE_JETTON_MASTER)

    # ------------------------------------------------------------------
    # Payment helpers
    # ------------------------------------------------------------------

    def create_usde_invoice(
        self,
        amount_usde: float,
        description: str = "Pago Ortegascy USDe",
    ) -> str:
        """Return a ``ton://transfer`` deeplink for a USDe jetton payment.

        The deeplink encodes the jetton transfer so that a compatible TON
        wallet (e.g. Tonkeeper) will forward the correct amount of USDe to
        :attr:`wallet`.
        """
        amount_raw = int(amount_usde * (10 ** USDE_DECIMALS))
        comment_encoded = quote(description)
        logger.info(f"💵 USDe invoice creada: {amount_usde} USDe - {description}")
        # ton://transfer/<jetton_wallet>?amount=<nano_ton_for_gas>&bin=<payload>
        # Simplified deeplink – real wallets also accept the comment field.
        return (
            f"ton://transfer/{USDE_JETTON_MASTER}"
            f"?amount=50000000"  # 0.05 TON for gas
            f"&jetton_amount={amount_raw}"
            f"&jetton_destination={self.wallet}"
            f"&text={comment_encoded}"
        )

    # ------------------------------------------------------------------
    # Transaction helpers
    # ------------------------------------------------------------------

    def check_usde_payments(self, limit: int = 20) -> List[Dict]:
        """Return recent USDe jetton transfers received by :attr:`wallet`."""
        transactions = self.ton.check_payments(self.wallet, limit=limit)
        usde_payments: List[Dict] = []
        for tx in transactions:
            actions = tx.get("actions", [])
            for action in actions:
                if action.get("type") == "JettonTransfer":
                    jt = action.get("JettonTransfer", {})
                    jetton_info = jt.get("jetton", {})
                    master = jetton_info.get("address", "")
                    if master == USDE_JETTON_MASTER:
                        amount_raw = int(jt.get("amount", 0))
                        usde_payments.append(
                            {
                                "tx_hash": tx.get("transaction_id", {}).get("hash", ""),
                                "sender": jt.get("sender", {}).get("address", ""),
                                "amount_usde": amount_raw / (10 ** USDE_DECIMALS),
                                "comment": jt.get("comment", ""),
                                "timestamp": tx.get("utime", 0),
                            }
                        )
        return usde_payments
