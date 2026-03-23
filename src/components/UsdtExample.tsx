import React, { useState } from 'react';
import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react';
import { beginCell, Address, toNano } from '@ton/ton';

function buildJettonTransferPayload(
  queryId: bigint,
  jettonAmount: bigint,
  toAddress: string,
  responseAddress: string
): string {
  const cell = beginCell()
    .storeUint(0x0f8a7ea5, 32) // jetton transfer op
    .storeUint(queryId, 64)
    .storeCoins(jettonAmount)
    .storeAddress(Address.parse(toAddress))
    .storeAddress(Address.parse(responseAddress))
    .storeBit(false) // no custom payload
    .storeCoins(toNano('0.000000001')) // forward amount
    .storeBit(false) // no forward payload
    .endCell();
  return cell.toBoc().toString('base64');
}

function UsdtExample() {
  const wallet = useTonWallet();
  const [tonConnectUI] = useTonConnectUI();
  const [amount, setAmount] = useState('0.01');
  const [destination, setDestination] = useState('');
  const [jettonWallet, setJettonWallet] = useState('');
  const [usdtBalance, setUsdtBalance] = useState<string>('');
  const [tonBalance, setTonBalance] = useState<string>('');
  const [status, setStatus] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'error' | 'info'>('info');

  const handleSend = async () => {
    if (!wallet || !destination || !jettonWallet) {
      setStatus('Please fill in destination and jetton wallet addresses');
      setStatusType('error');
      return;
    }
    try {
      const jettonAmount = BigInt(Math.round(parseFloat(amount) * 1_000_000));
      setStatus('Sending USDT...');
      setStatusType('info');

      const payload = buildJettonTransferPayload(
        0n,
        jettonAmount,
        destination,
        wallet.account.address
      );

      await tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 300,
        messages: [
          {
            address: jettonWallet,
            amount: '50000000', // 0.05 TON for gas
            payload,
          },
        ],
      });
      setStatus('USDT transfer sent!');
      setStatusType('success');
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
      setStatusType('error');
    }
  };

  return (
    <div className="card">
      <div className="card-title">USDT Sending example</div>
      <div style={{ fontSize: '0.85rem', marginBottom: 12 }}>
        <div>
          USDT Balance:{' '}
          <strong>{usdtBalance || <span style={{ color: 'var(--text-muted)' }}>&nbsp;</span>}</strong>
        </div>
        <div>
          TON Balance:{' '}
          <strong>{tonBalance || <span style={{ color: 'var(--text-muted)' }}>&nbsp;</span>}</strong>
        </div>
      </div>
      {wallet ? (
        <>
          <div className="form-row">
            <label className="form-label">USDT Amount</label>
            <input
              type="number"
              min="0.01"
              step="0.01"
              value={amount}
              onChange={(e) => setAmount(e.target.value)}
            />
          </div>
          <div className="form-row">
            <label className="form-label">Destination</label>
            <input
              value={destination}
              onChange={(e) => setDestination(e.target.value)}
              placeholder="EQ..."
            />
          </div>
          <div className="form-row">
            <label className="form-label">Sender Jetton Wallet</label>
            <input
              value={jettonWallet}
              onChange={(e) => setJettonWallet(e.target.value)}
              placeholder="Your USDT jetton wallet address"
            />
          </div>
          <button className="btn" onClick={handleSend}>
            Send USDT
          </button>
          {status && <div className={`status-msg ${statusType}`}>{status}</div>}
        </>
      ) : (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Connect wallet to send USDT
        </div>
      )}
    </div>
  );
}

export default UsdtExample;

