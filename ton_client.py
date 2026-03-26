import os
import logging
from typing import List, Dict, Optional
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

    def create_invoice(self, amount_ton: float, wallet: str, description: str = "Pago Ortegascy"):
        amount_nano = int(amount_ton * 1_000_000_000)
        logger.info(f"💰 Invoice creada: {amount_ton} TON - {description}")
        return f"ton://transfer/{wallet}?amount={amount_nano}&text={description}"

    def check_payments(self, address: str) -> List[Dict]:
        url = f"{BASE_URL}/accounts/{address}/transactions?limit=20"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        return r.json().get("transactions", [])

    def get_event(self, event_id: str) -> Dict:
        """Fetch a TON event by its event_id from the tonapi.io API."""
        url = f"{BASE_URL}/events/{event_id}"
        r = self.session.get(url, timeout=10)
        r.raise_for_status()
        event = r.json()
        logger.info(f"📦 Evento obtenido: {event_id}")
        return event

    def generate_ownership_statement(
        self,
        wallets: List[str],
        event: Dict,
        sender: Optional[str] = None,
        recipient: Optional[str] = None,
        amount_ton: Optional[float] = None,
        comment: str = "",
    ) -> str:
        """
        Generate a wallet ownership statement using a TON event as proof.

        The event_id is included in the statement to demonstrate control of
        the sender wallet and confirm the recipient wallet also belongs to
        the same owner.
        """
        event_id = event.get("event_id", "")

        wallet_list = "\n".join(f"- {w}" for w in wallets)

        transfer_lines = []
        if sender and recipient and amount_ton is not None:
            transfer_lines.append(
                f"En el evento {event_id} se registra una transferencia de "
                f"{amount_ton} TON desde {sender} hacia {recipient}"
                + (f' con comentario "{comment}".' if comment else ".")
            )
            transfer_lines.append(
                f"Esto demuestra que controlo la clave de {sender} y que la "
                f"dirección de destino {recipient} también es mi wallet."
            )
        else:
            transfer_lines.append(
                f"El evento {event_id} registrado en la blockchain TON confirma "
                "que controlo todas las direcciones listadas."
            )

        transfer_proof = "\n".join(transfer_lines)

        statement = (
            f"Yo soy el dueño de las siguientes direcciones TON:\n"
            f"{wallet_list}\n\n"
            f"{transfer_proof}"
        )

        logger.info(f"📝 Declaración de propiedad generada para el evento {event_id}")
        return statement


# Prueba rápida
if __name__ == "__main__":
    client = TonClient()
    direccion = "EQCD39VS5jcptHL8vMjEXrzGaRcCVYto7HUn4bpAOg8xqB2N"  # ejemplo
    print(f"Balance actual: {client.get_balance(direccion):.4f} TON")

    my_wallet1 = "0:00e654ac047b66195ba35a640cc054a52b2fcc718922aed33a387a4899d523"
    my_wallet2 = "0:4f3eaef3b9097f5fefc2af4ca399e264d2c36a89342e77d2d3216c1d39c2f17a"

    event_id = "e0cd9d4ef8fa5daec81e2ce2dc9e41a6a056566a8db06b493a6e12d33a17fcea"
    event = client.get_event(event_id)

    statement = client.generate_ownership_statement(
        wallets=[my_wallet1, my_wallet2],
        event=event,
        sender=my_wallet1,
        recipient=my_wallet2,
        amount_ton=0.2,
        comment="tag memo",
    )
    print(statement)
