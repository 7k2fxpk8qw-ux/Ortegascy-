"""Tests for Ortegascy TON + Ethena on TON integration."""
from unittest.mock import MagicMock, patch

import pytest


def test_placeholder():
    assert True


# ---------------------------------------------------------------------------
# TonClient unit tests
# ---------------------------------------------------------------------------


class TestTonClient:
    def test_get_balance_converts_nanoton(self):
        """get_balance should convert nanoTON to TON correctly."""
        from ton_client import TonClient

        client = TonClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.json.return_value = {"balance": "5000000000"}
        mock_response.raise_for_status.return_value = None

        with patch.object(client.session, "get", return_value=mock_response):
            balance = client.get_balance("EQTEST")

        assert balance == pytest.approx(5.0)

    def test_create_invoice_format(self):
        """create_invoice should return a valid ton:// deeplink."""
        from ton_client import TonClient
        from urllib.parse import urlparse, parse_qs, unquote

        client = TonClient(api_key="test-key")
        link = client.create_invoice("EQMyWallet", 1.5, "Test payment")

        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        assert link.startswith("ton://transfer/EQMyWallet")
        assert params.get("amount", [""])[0] == "1500000000"
        assert unquote(params.get("text", [""])[0]) == "Test payment"

    def test_check_payments_returns_transactions(self):
        """check_payments should return the transactions list from the API."""
        from ton_client import TonClient

        client = TonClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.json.return_value = {"transactions": [{"hash": "abc123"}]}
        mock_response.raise_for_status.return_value = None

        with patch.object(client.session, "get", return_value=mock_response):
            txs = client.check_payments("EQTEST")

        assert len(txs) == 1
        assert txs[0]["hash"] == "abc123"

    def test_get_jetton_balance_uses_decimals(self):
        """get_jetton_balance should apply the jetton's decimal places."""
        from ton_client import TonClient

        client = TonClient(api_key="test-key")
        mock_response = MagicMock()
        mock_response.json.return_value = {
            "balance": "1000000000000000000",  # 1 token with 18 decimals
            "jetton": {"decimals": 18},
        }
        mock_response.raise_for_status.return_value = None

        with patch.object(client.session, "get", return_value=mock_response):
            balance = client.get_jetton_balance("EQOwner", "EQJetton")

        assert balance == pytest.approx(1.0)


# ---------------------------------------------------------------------------
# EthenaTonClient unit tests
# ---------------------------------------------------------------------------


class TestEthenaTonClient:
    def _make_client(self, wallet="EQPlatformWallet"):
        from ton_client import TonClient
        from ethena_ton import EthenaTonClient

        mock_ton = MagicMock(spec=TonClient)
        return EthenaTonClient(wallet=wallet, ton_client=mock_ton), mock_ton

    def test_get_usde_balance_delegates_to_ton_client(self):
        """get_usde_balance should call get_jetton_balance with the USDe master."""
        from ethena_ton import USDE_JETTON_MASTER

        client, mock_ton = self._make_client()
        mock_ton.get_jetton_balance.return_value = 42.0

        balance = client.get_usde_balance("EQSomeAddress")

        mock_ton.get_jetton_balance.assert_called_once_with("EQSomeAddress", USDE_JETTON_MASTER)
        assert balance == 42.0

    def test_get_usde_balance_defaults_to_wallet(self):
        """get_usde_balance with no address should use the platform wallet."""
        client, mock_ton = self._make_client(wallet="EQPlatformWallet")
        mock_ton.get_jetton_balance.return_value = 10.0

        client.get_usde_balance()

        args = mock_ton.get_jetton_balance.call_args[0]
        assert args[0] == "EQPlatformWallet"

    def test_create_usde_invoice_contains_amount(self):
        """create_usde_invoice deeplink should encode the raw USDe amount."""
        from ethena_ton import USDE_DECIMALS

        client, _ = self._make_client()
        link = client.create_usde_invoice(2.5, "Music subscription")

        expected_raw = int(2.5 * (10 ** USDE_DECIMALS))
        assert f"jetton_amount={expected_raw}" in link

    def test_check_usde_payments_filters_by_jetton(self):
        """check_usde_payments should only return USDe jetton transfers."""
        from ethena_ton import USDE_JETTON_MASTER, USDE_DECIMALS

        client, mock_ton = self._make_client()
        raw_amount = 5 * (10 ** USDE_DECIMALS)
        mock_ton.check_payments.return_value = [
            {
                "transaction_id": {"hash": "tx1"},
                "utime": 1700000000,
                "actions": [
                    {
                        "type": "JettonTransfer",
                        "JettonTransfer": {
                            "jetton": {"address": USDE_JETTON_MASTER},
                            "amount": str(raw_amount),
                            "sender": {"address": "EQSender"},
                            "comment": "test",
                        },
                    }
                ],
            },
            {
                "transaction_id": {"hash": "tx2"},
                "utime": 1700000001,
                "actions": [
                    {
                        "type": "JettonTransfer",
                        "JettonTransfer": {
                            "jetton": {"address": "EQOtherJetton"},
                            "amount": "1000",
                            "sender": {"address": "EQSender2"},
                            "comment": "",
                        },
                    }
                ],
            },
        ]

        payments = client.check_usde_payments()

        assert len(payments) == 1
        assert payments[0]["tx_hash"] == "tx1"
        assert payments[0]["amount_usde"] == pytest.approx(5.0)

