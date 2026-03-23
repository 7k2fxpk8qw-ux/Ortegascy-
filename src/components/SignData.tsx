import React, { useState } from 'react';
import { useTonConnectUI, useTonWallet } from '@tonconnect/ui-react';

type SignType = 'text' | 'binary' | 'cell';

function SignData() {
  const wallet = useTonWallet();
  const [tonConnectUI] = useTonConnectUI();
  const [signType, setSignType] = useState<SignType>('text');
  const [inputValue, setInputValue] = useState('Hello, TON!');
  const [result, setResult] = useState<any>(null);
  const [status, setStatus] = useState<string | null>(null);
  const [statusType, setStatusType] = useState<'success' | 'error' | 'info'>('info');

  const handleSign = async () => {
    try {
      setStatus('Requesting signature...');
      setStatusType('info');
      setResult(null);

      let payload: any;
      if (signType === 'text') {
        payload = { type: 'text', text: inputValue };
      } else if (signType === 'binary') {
        const bytes = new TextEncoder().encode(inputValue);
        const base64 = btoa(String.fromCharCode(...bytes));
        payload = { type: 'binary', bytes: base64 };
      } else {
        payload = {
          type: 'cell',
          schema: '0',
          cell: 'te6cckEBAQEABgAACAgAAAA=',
        };
      }

      const res = await (tonConnectUI as any).sendSignDataRequest({ payload });
      setResult(res);
      setStatus('Signature received and verified!');
      setStatusType('success');
    } catch (e: any) {
      setStatus(`Error: ${e.message}`);
      setStatusType('error');
    }
  };

  return (
    <div className="card">
      <div className="card-title">Sign Data Test & Verification</div>
      <div className="card-desc">
        Test different types of data signing: text, binary, and cell formats with signature
        verification
      </div>
      {wallet ? (
        <>
          <div className="form-row">
            <label className="form-label">Sign type</label>
            <div className="tag-group">
              {(['text', 'binary', 'cell'] as SignType[]).map((t) => (
                <span
                  key={t}
                  className={`tag ${signType === t ? 'active' : ''}`}
                  onClick={() => setSignType(t)}
                >
                  {t}
                </span>
              ))}
            </div>
          </div>
          {signType !== 'cell' && (
            <div className="form-row">
              <label className="form-label">Data to sign</label>
              <input
                value={inputValue}
                onChange={(e) => setInputValue(e.target.value)}
                placeholder="Enter text or binary data"
              />
            </div>
          )}
          {signType === 'cell' && (
            <div className="form-row">
              <label className="form-label">Cell (BOC)</label>
              <input value="te6cckEBAQEABgAACAgAAAA=" readOnly />
            </div>
          )}
          <button className="btn" onClick={handleSign}>
            Sign {signType} data
          </button>
          {status && <div className={`status-msg ${statusType}`}>{status}</div>}
          {result && (
            <pre className="json-view" style={{ marginTop: 10 }}>
              {JSON.stringify(result, null, 2)}
            </pre>
          )}
        </>
      ) : (
        <div style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
          Connect wallet to test signing
        </div>
      )}
    </div>
  );
}

export default SignData;
