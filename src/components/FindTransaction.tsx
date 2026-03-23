import React, { useState } from 'react';

const DEFAULT_BOC =
  'te6cckEBBQEA6wAB4YgB76ksIXpmobiUHDUtWosNdLgI+loKYwC+3DgXeRr2DJ4F4G+ja0rbyhi5yzD+xbfXI1owr5X3/uucREXZXZP4dqxPXukwqPGVrKzUL0g80tYaTgh95b0myTcmVFMS8cTIOU1NGLtDx7h4AAAQ8AAcAQJ7YgBFLU49uGmU3zOG8nNmcylqMjsoilVMAcYzYexnV5aM2BpiWgAAAAAAAAAAAAAAAAACMAAAAAEhlbGxvIYCBAEU/wD0pBP0vPLICwMASNMB0NMDAXGwkVvg+kAwcIAQyMsFWM8WIfoCy2oBzxbJgED7AAAAGE8sBQ==';

const NETWORKS = ['mainnet', 'testnet'] as const;
type Network = (typeof NETWORKS)[number];

function FindTransaction() {
  const [boc, setBoc] = useState(DEFAULT_BOC);
  const [network, setNetwork] = useState<Network>('mainnet');
  const [result, setResult] = useState<any>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'error' | 'info'>('info');
  const [loading, setLoading] = useState(false);

  const handleFind = async () => {
    try {
      setLoading(true);
      setStatus('Searching for transaction...');
      setStatusType('info');
      setResult(null);

      const apiBase =
        network === 'mainnet'
          ? 'https://tonapi.io/v2'
          : 'https://testnet.tonapi.io/v2';

      const res = await fetch(`${apiBase}/blockchain/transactions/by-message-body`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ boc }),
      });

      if (!res.ok) {
        const err = await res.json().catch(() => ({ error: res.statusText }));
        throw new Error(err.error || `HTTP ${res.status}`);
      }

      const data = await res.json();
      setResult(data);
      setStatus('Transaction found!');
      setStatusType('success');
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
      setStatusType('error');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="card">
      <div className="card-title">Find Transaction by External-in Message BOC</div>
      <div className="form-row">
        <textarea
          rows={5}
          value={boc}
          onChange={(e) => setBoc(e.target.value)}
          style={{ fontFamily: 'monospace', fontSize: '0.75rem', wordBreak: 'break-all' }}
        />
      </div>
      <div className="form-row">
        <label className="form-label">Network:</label>
        <div className="tag-group" style={{ marginTop: 4 }}>
          {NETWORKS.map((n) => (
            <span
              key={n}
              className={`tag ${network === n ? 'active' : ''}`}
              onClick={() => setNetwork(n)}
            >
              {n}
            </span>
          ))}
        </div>
      </div>
      <button className="btn" onClick={handleFind} disabled={loading || !boc.trim()}>
        {loading ? 'Searching...' : 'Find Transaction'}
      </button>
      {status && <div className={`status-msg ${statusType}`}>{status}</div>}
      {result && (
        <pre className="json-view" style={{ marginTop: 10 }}>
          {JSON.stringify(result, null, 2)}
        </pre>
      )}
    </div>
  );
}

export default FindTransaction;
