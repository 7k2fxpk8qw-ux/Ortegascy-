
def get_balance(address):
    url = f"{BASE_URL}/accounts/{address}"
    response = requests.get(url, headers=HEADERS)
    data = response.json()
    balance = data.get('balance', 0) / 1e9  # NanoTON a TON
    return balance

def create_invoice(amount_ton, description="Pago por app musical"):
    # Simula invoice; usa TonConnect para frontend real
    print(f"Invoice generada: {amount_ton} TON - {description}")
    return f"pay://pay/EQ...wallet?amount={int(amount_ton * 1e9)}"

def check_payments(address, last_known_tx=None):
    url = f"{BASE_URL}/accounts/{address}/transactions?limit=10"
    response = requests.get(url, headers=HEADERS)
    txs = response.json().get('transactions', [])
    for tx in txs:
        if tx['utime'] > time.time() - 3600:  # Última hora
            print(f"Nueva TX: {tx['hash']} - Valor: {tx.get('in_msg', {}).get('value', 0)/1e9} TON")
    return txs
