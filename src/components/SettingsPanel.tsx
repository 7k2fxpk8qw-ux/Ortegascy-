import React from 'react';

type Settings = {
  language: string;
  theme: string;
  borders: string;
  androidBackHandler: boolean;
  modals: string[];
  notifications: string[];
  returnStrategy: string;
  skipRedirect: 'ios' | 'never' | 'always';
};

type Props = {
  settings: Settings;
  onChange: (s: Settings) => void;
};

const LANGUAGES = ['en', 'ru', 'zh'];
const THEMES = ['dark', 'light', 'system'];
const BORDERS = ['none', 's', 'm', 'l', 'xl'];
const MODAL_EVENTS = ['before', 'success', 'error'];
const NOTIF_EVENTS = ['before', 'success', 'error'];
const RETURN_STRATEGIES = ['back', 'none'];
const SKIP_REDIRECTS = ['ios', 'never', 'always'] as const;
const ACCENT_COLORS = ['#e94560', '#2196f3', '#4caf50', '#ff9800', '#9c27b0', '#00bcd4'];

function SettingsPanel({ settings, onChange }: Props) {
  const set = (key: keyof Settings, value: any) => onChange({ ...settings, [key]: value });

  const toggleList = (key: 'modals' | 'notifications', val: string) => {
    const list = settings[key];
    const next = list.includes(val) ? list.filter((x) => x !== val) : [...list, val];
    set(key, next);
  };

  return (
    <div className="settings-panel">
      <div className="settings-grid">
        <div className="setting-item">
          <label>language</label>
          <div className="tag-group">
            {LANGUAGES.map((l) => (
              <span
                key={l}
                className={`tag ${settings.language === l ? 'active' : ''}`}
                onClick={() => set('language', l)}
              >
                {l}
              </span>
            ))}
          </div>
        </div>

        <div className="setting-item">
          <label>theme</label>
          <div className="tag-group">
            {THEMES.map((t) => (
              <span
                key={t}
                className={`tag ${settings.theme === t ? 'active' : ''}`}
                onClick={() => set('theme', t)}
              >
                {t}
              </span>
            ))}
          </div>
        </div>

        <div className="setting-item">
          <label>borders</label>
          <div className="tag-group">
            {BORDERS.map((b) => (
              <span
                key={b}
                className={`tag ${settings.borders === b ? 'active' : ''}`}
                onClick={() => set('borders', b)}
              >
                {b}
              </span>
            ))}
          </div>
        </div>

        <div className="setting-item">
          <label>enable android back handler</label>
          <div className="toggle-row">
            <span>{settings.androidBackHandler ? 'true' : 'false'}</span>
            <label className="toggle">
              <input
                type="checkbox"
                checked={settings.androidBackHandler}
                onChange={(e) => set('androidBackHandler', e.target.checked)}
              />
              <span className="toggle-slider" />
            </label>
          </div>
        </div>

        <div className="setting-item">
          <label>modals</label>
          <div className="tag-group">
            {MODAL_EVENTS.map((e) => (
              <span
                key={e}
                className={`tag ${settings.modals.includes(e) ? 'active' : ''}`}
                onClick={() => toggleList('modals', e)}
              >
                {e}
              </span>
            ))}
          </div>
        </div>

        <div className="setting-item">
          <label>notifications</label>
          <div className="tag-group">
            {NOTIF_EVENTS.map((e) => (
              <span
                key={e}
                className={`tag ${settings.notifications.includes(e) ? 'active' : ''}`}
                onClick={() => toggleList('notifications', e)}
              >
                {e}
              </span>
            ))}
          </div>
        </div>

        <div className="setting-item">
          <label>return strategy:</label>
          <div className="tag-group">
            {RETURN_STRATEGIES.map((s) => (
              <span
                key={s}
                className={`tag ${settings.returnStrategy === s ? 'active' : ''}`}
                onClick={() => set('returnStrategy', s)}
              >
                {s}
              </span>
            ))}
          </div>
        </div>

        <div className="setting-item">
          <label>skip redirect to wallet:</label>
          <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginBottom: 4 }}>
            {'(\'ios\', \'never\', \'always\')'}
          </div>
          <div className="tag-group">
            {SKIP_REDIRECTS.map((s) => (
              <span
                key={s}
                className={`tag ${settings.skipRedirect === s ? 'active' : ''}`}
                onClick={() => set('skipRedirect', s)}
              >
                {s}
              </span>
            ))}
          </div>
        </div>

        <div className="setting-item">
          <label>change colors</label>
          <div className="color-row">
            {ACCENT_COLORS.map((c) => (
              <div
                key={c}
                className="color-swatch"
                style={{ background: c }}
                onClick={() => {
                  document.documentElement.style.setProperty('--primary', c);
                }}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}

export default SettingsPanel;
