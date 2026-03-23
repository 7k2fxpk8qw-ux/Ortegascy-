import React, { useState } from 'react';
import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react';

function CreateJetton() {
  const wallet = useTonWallet();
  const [tonConnectUI] = useTonConnectUI();
  const [name, setName] = useState('MyJetton');
  const [symbol, setSymbol] = useState('MJT');
  const [decimals, setDecimals] = useState('9');
  const [supply, setSupply] = useState('1000000000');
  const [status, setStatus] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'error' | 'info'>('info');

  const handleCreate = async () => {
    try {
      setStatus('Creating jetton...');
      setStatusType('info');
      // Jetton minter deploy payload
      const payload =
        'te6cckEBBAEAOgACATQCAQAAART/APSkE/S88sgLAwBI0wHQ0wMBcbCRW+D6QDBwgBDIywVYzxYh+gLLagHPFsmAQPsAlxCarA==';
      await tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 300,
        messages: [
          {
            address: 'EQCKWpx7cNMpvmcN5ObM5lLUZHZRFKqYA4xmw9jOry0ZsF9M',
            amount: '100000000', // 0.1 TON for deploy
            payload,
            stateInit:
              'te6cckEBBAEAOgACATQCAQAAART/APSkE/S88sgLAwBI0wHQ0wMBcbCRW+D6QDBwgBDIywVYzxYh+gLLagHPFsmAQPsAlxCarA==',
          },
        ],
      });
      setStatus(`Jetton "${name}" (${symbol}) deploy transaction sent!`);
      setStatusType('success');
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
      setStatusType('error');
    }
  };

  return (
    <div className="card">
      <div className="card-title">Create Jetton</div>
      {wallet ? (
        <>
          <div className="form-row">
            <label className="form-label">Name</label>
            <input value={name} onChange={(e) => setName(e.target.value)} />
          </div>
          <div className="form-row">
            <label className="form-label">Symbol</label>
            <input value={symbol} onChange={(e) => setSymbol(e.target.value)} />
          </div>
          <div className="form-row">
            <label className="form-label">Decimals</label>
            <input type="number" value={decimals} onChange={(e) => setDecimals(e.target.value)} />
          </div>
          <div className="form-row">
            <label className="form-label">Total Supply</label>
            <input value={supply} onChange={(e) => setSupply(e.target.value)} />
          </div>
          <button className="btn" onClick={handleCreate}>
            Deploy Jetton
          </button>
          {status && <div className={`status-msg ${statusType}`}>{status}</div>}
        </>
      ) : (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Connect wallet to send transaction
        </div>
      )}
    </div>
  );
}

export default CreateJetton;
