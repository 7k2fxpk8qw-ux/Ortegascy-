import React, { useState } from 'react';
import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react';

function MerkleProof() {
  const wallet = useTonWallet();
  const [tonConnectUI] = useTonConnectUI();
  const [status, setStatus] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'error' | 'info'>('info');

  const handleSend = async () => {
    try {
      setStatus('Sending Merkle proof/update transaction...');
      setStatusType('info');
      await tonConnectUI.sendTransaction({
        validUntil: Math.floor(Date.now() / 1000) + 300,
        messages: [
          {
            address: 'EQCKWpx7cNMpvmcN5ObM5lLUZHZRFKqYA4xmw9jOry0ZsF9M',
            amount: '5000000',
            payload: 'te6cckEBAQEADAAAFAAAAABIZWxsbyGVgYQo',
          },
        ],
      });
      setStatus('Merkle proof/update transaction sent!');
      setStatusType('success');
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
      setStatusType('error');
    }
  };

  return (
    <div className="card">
      <div className="card-title">Merkle proof/update</div>
      {wallet ? (
        <>
          <button className="btn" onClick={handleSend}>
            Send transaction
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

export default MerkleProof;
