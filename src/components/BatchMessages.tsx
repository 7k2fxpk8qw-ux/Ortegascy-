import React, { useState } from 'react';
import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react';

function BatchMessages() {
  const wallet = useTonWallet();
  const [tonConnectUI] = useTonConnectUI();
  const [count, setCount] = useState(4);
  const [status, setStatus] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'error' | 'info'>('info');

  const handleSend = async () => {
    try {
      const messages = Array.from({ length: count }, (_, i) => ({
        address: 'EQCKWpx7cNMpvmcN5ObM5lLUZHZRFKqYA4xmw9jOry0ZsF9M',
        amount: String(1000000 * (i + 1)),
      }));
      setStatus(`Sending ${count} messages...`);
      setStatusType('info');
      await tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 300,
        messages,
      });
      setStatus(`Successfully sent ${count} messages!`);
      setStatusType('success');
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
      setStatusType('error');
    }
  };

  return (
    <div className="card">
      <div className="card-title">Batch Message Limits Test</div>
      <div className="card-desc">
        Send multiple messages to the wallet to test message batching capabilities
      </div>
      {wallet ? (
        <>
          <div className="form-row">
            <label className="form-label">Number of messages</label>
            <input
              type="number"
              min={1}
              max={255}
              value={count}
              onChange={(e) => setCount(Number(e.target.value))}
              style={{ width: 100 }}
            />
          </div>
          <button className="btn" onClick={handleSend}>
            Send {count} messages
          </button>
          {status && <div className={`status-msg ${statusType}`}>{status}</div>}
        </>
      ) : (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Connect wallet to test batch limits
        </div>
      )}
    </div>
  );
}

export default BatchMessages;
