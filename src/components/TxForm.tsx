import React, { useState } from 'react';
import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react';

const DEFAULT_TX = {
  validUntil: 1774268145,
  messages: [
    {
      address: 'EQCKWpx7cNMpvmcN5ObM5lLUZHZRFKqYA4xmw9jOry0ZsF9M',
      amount: '5000000',
      payload: 'te6cckEBAQEADAAAFAAAAABIZWxsbyGVgYQo',
      stateInit:
        'te6cckEBBAEAOgACATQCAQAAART/APSkE/S88sgLAwBI0wHQ0wMBcbCRW+D6QDBwgBDIywVYzxYh+gLLagHPFsmAQPsAlxCarA==',
    },
  ],
};

function TxForm() {
  const wallet = useTonWallet();
  const [tonConnectUI] = useTonConnectUI();
  const [status, setStatus] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'error' | 'info'>('info');
  const [txJson, setTxJson] = useState(JSON.stringify(DEFAULT_TX, null, 2));

  const handleSend = async () => {
    try {
      const tx = JSON.parse(txJson);
      setStatus('Sending transaction...');
      setStatusType('info');
      const result = await tonConnectUI.sendTransaction(tx);
      setStatus(`Transaction sent! BOC: ${result.boc.slice(0, 60)}...`);
      setStatusType('success');
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
      setStatusType('error');
    }
  };

  return (
    <div className="card">
      <div className="card-title">Configure and send transaction</div>
      <pre className="json-view">{JSON.stringify(DEFAULT_TX, null, 2)}</pre>
      <div className="form-row">
        <textarea
          rows={10}
          value={txJson}
          onChange={(e) => setTxJson(e.target.value)}
          style={{ fontFamily: 'monospace', fontSize: '0.78rem' }}
        />
      </div>
      {wallet ? (
        <>
          <button className="btn" onClick={handleSend}>
            Send transaction
          </button>
          {status && <div className={`status-msg ${statusType}`}>{status}</div>}
          <div className="status-msg info" style={{ marginTop: 8 }}>
            Wait for transaction confirmation
          </div>
        </>
      ) : (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Connect wallet to send the transaction
        </div>
      )}
    </div>
  );
}

export default TxForm;
