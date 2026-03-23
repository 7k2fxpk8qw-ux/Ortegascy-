import React, { useState } from 'react';
import { TonConnectButton, useTonWallet } from '@tonconnect/ui-react';
import TxForm from './components/TxForm';
import BatchMessages from './components/BatchMessages';
import SignData from './components/SignData';
import UsdtExample from './components/UsdtExample';
import CreateJetton from './components/CreateJetton';
import FindTransaction from './components/FindTransaction';
import MerkleProof from './components/MerkleProof';
import SettingsPanel from './components/SettingsPanel';

function App() {
  const wallet = useTonWallet();
  const [settings, setSettings] = useState({
    language: 'en',
    theme: 'dark',
    borders: 'm',
    androidBackHandler: true,
    modals: ['before', 'success', 'error'] as string[],
    notifications: ['before', 'success', 'error'] as string[],
    returnStrategy: 'back',
    skipRedirect: 'ios' as 'ios' | 'never' | 'always',
  });

  const network = wallet?.account?.chain === '-239' ? 'mainnet' : wallet?.account?.chain === '-3' ? 'testnet' : 'Any Network';

  return (
    <div
      className="app"
      data-theme={settings.theme}
      data-borders={settings.borders}
    >
      <header className="app-header">
        <div>
          <div className="app-title">App with React UI</div>
          <div className="network-badge">{network}</div>
        </div>
        <TonConnectButton />
      </header>

      <TxForm />
      <BatchMessages />
      <SignData />
      <UsdtExample />
      <CreateJetton />
      <FindTransaction />
      <MerkleProof />
      <SettingsPanel settings={settings} onChange={setSettings} />
    </div>
  );
}

export default App;
