#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# AdminBingo teljes csere: a tipp-szerkesztő mostantól csapatok + mérkőzések +
# bónuszok (végső győztes, gólkirály-csapat). A bingó-szerkesztő változatlan.
import io

PATH = 'app.src.html'
src = io.open(PATH, encoding='utf-8').read()

AB_START = 'function AdminBingo() {'
AB_END = '\nfunction AdminWildcards() {'
j1 = src.index(AB_START); j2 = src.index(AB_END, j1)

NEW_AB = r'''function AdminBingo() {
  const [enabled, setEnabled] = React.useState(true);
  const [mode, setMode] = React.useState('bingo');
  const [title, setTitle] = React.useState('VB Bingó');
  const [items, setItems] = React.useState(null);
  const [tippTitle, setTippTitle] = React.useState('Tippbajnokság');
  const [tippRequireCode, setTippRequireCode] = React.useState(false);
  const [tippMailUrl, setTippMailUrl] = React.useState('');
  const [teamsText, setTeamsText] = React.useState('');
  const [matches, setMatches] = React.useState([]);
  const [bWinner, setBWinner] = React.useState({ enabled: false, deadline: '', correct: '' });
  const [bScorer, setBScorer] = React.useState({ enabled: false, deadline: '', correct: '' });
  const [saving, setSaving] = React.useState(false);
  const [saved, setSaved] = React.useState(false);
  const [dirty, setDirty] = React.useState(false);
  const [confirmReset, setConfirmReset] = React.useState(false);
  React.useEffect(() => {
    (window.getBingoConfig ? window.getBingoConfig() : Promise.resolve(null)).then(c => {
      setEnabled(c ? c.enabled !== false : true);
      setMode((c && c.mode === 'tipp') ? 'tipp' : 'bingo');
      setTitle((c && c.title) || 'VB Bingó');
      setTippTitle((c && c.tippTitle) || 'Tippbajnokság');
      setTippRequireCode(!!(c && c.tippRequireCode));
      setTippMailUrl((c && c.tippMailUrl) || '');
      setTeamsText((c && Array.isArray(c.teams)) ? c.teams.join('\n') : '');
      setMatches((c && Array.isArray(c.matches)) ? c.matches.map(m => ({ id: m.id || ('m_' + Math.random().toString(36).slice(2,8)), home: m.home || '', away: m.away || '', kickoff: m.kickoff || '', knockout: !!m.knockout, hs: (m.hs == null ? '' : String(m.hs)), as: (m.as == null ? '' : String(m.as)) })) : []);
      setBWinner(Object.assign({ enabled: false, deadline: '', correct: '' }, (c && c.bonusWinner) || {}));
      setBScorer(Object.assign({ enabled: false, deadline: '', correct: '' }, (c && c.bonusScorer) || {}));
      setItems((c && Array.isArray(c.items) && c.items.length) ? c.items.map(it => ({ e: it.e || '', t: it.t || '' })) : BINGO_ITEMS.map(it => ({ e: it.e, t: it.t })));
    }).catch(() => { setItems(BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }))); });
  }, []);
  const markDirty = () => { setDirty(true); setSaved(false); };

  const updItem = (i, f, v) => { setItems(l => l.map((w, j) => j === i ? { ...w, [f]: v } : w)); markDirty(); };
  const delItem = (i) => { setItems(l => l.filter((_, j) => j !== i)); markDirty(); };
  const addItem = () => { setItems(l => [...l, { e: '⚽', t: '' }]); markDirty(); };
  const addMatch = () => { setMatches(l => [...l, { id: 'm_' + Date.now().toString(36) + Math.random().toString(36).slice(2,5), home: '', away: '', kickoff: '', knockout: false, hs: '', as: '' }]); markDirty(); };
  const updM = (i, f, v) => { setMatches(l => l.map((m, j) => j === i ? { ...m, [f]: v } : m)); markDirty(); };
  const delM = (i) => { setMatches(l => l.filter((_, j) => j !== i)); markDirty(); };

  const teamsArr = teamsText.split('\n').map(s => s.trim()).filter(Boolean);

  const persist = (payload) => {
    setSaving(true);
    (window.setBingoConfig ? window.setBingoConfig(payload) : Promise.resolve())
      .then(() => { setSaving(false); setDirty(false); setSaved(true); setConfirmReset(false); })
      .catch(() => setSaving(false));
  };
  const buildPayload = (over) => {
    const cleanItems = (items || []).map(w => ({ e: (w.e || '').trim() || '⚽', t: (w.t || '').trim() })).filter(w => w.t);
    const cleanM = (matches || []).map(m => ({
      id: m.id, home: (m.home || '').trim(), away: (m.away || '').trim(), kickoff: m.kickoff || '', knockout: !!m.knockout,
      hs: (m.hs === '' || m.hs == null) ? null : Math.max(0, parseInt(m.hs) || 0),
      as: (m.as === '' || m.as == null) ? null : Math.max(0, parseInt(m.as) || 0),
    })).filter(m => m.home && m.away && m.kickoff);
    const bw = { enabled: !!bWinner.enabled, deadline: bWinner.deadline || '', correct: (bWinner.correct || '').trim(), teams: teamsArr };
    const bs = { enabled: !!bScorer.enabled, deadline: bScorer.deadline || '', correct: (bScorer.correct || '').trim(), teams: teamsArr };
    return Object.assign({ enabled, mode, title: (title || '').trim() || 'VB Bingó', items: cleanItems, tippTitle: (tippTitle || '').trim() || 'Tippbajnokság', tippRequireCode, tippMailUrl: (tippMailUrl || '').trim(), teams: teamsArr, matches: cleanM, bonusWinner: bw, bonusScorer: bs, questions: [] }, over || {});
  };
  const save = () => persist(buildPayload());
  const reset = () => {
    const d = BINGO_ITEMS.map(it => ({ e: it.e, t: it.t }));
    setEnabled(true); setMode('bingo'); setTitle('VB Bingó'); setItems(d); setTippTitle('Tippbajnokság'); setTippRequireCode(false); setMatches([]); setTeamsText(''); setBWinner({ enabled:false, deadline:'', correct:'' }); setBScorer({ enabled:false, deadline:'', correct:'' });
    persist({ enabled: true, mode: 'bingo', title: 'VB Bingó', items: d, tippTitle: 'Tippbajnokság', tippRequireCode: false, tippMailUrl: (tippMailUrl || '').trim(), teams: [], matches: [], bonusWinner: { enabled:false }, bonusScorer: { enabled:false }, questions: [] });
  };

  if (items === null) return <div style={{ textAlign:'center', padding:30, fontFamily:T.font, color:T.sub }}>Betöltés…</div>;
  const validCount = items.filter(w => (w.t || '').trim()).length;
  const tooFew = validCount < 24;
  const validM = matches.filter(m => (m.home||'').trim() && (m.away||'').trim() && m.kickoff).length;
  const inpS = { boxSizing:'border-box', padding:'9px 11px', borderRadius:10, border:`1.5px solid ${T.border}`, background:T.bg, fontFamily:T.font, fontSize:13.5, color:T.ink, outline:'none' };
  const dtS = { ...inpS, WebkitAppearance:'none', appearance:'none' };
  const lbl = txt => <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:7 }}>{txt}</div>;
  const BonusCard = ({ title:bt, emoji, bn, setBn }) => (
    <div style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:10 }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:10 }}>
        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>{emoji} {bt} <span style={{ fontWeight:700, fontSize:11, color:T.inkMute }}>(+25)</span></div>
        <Toggle on={bn.enabled} onChange={() => { setBn({ ...bn, enabled: !bn.enabled }); markDirty(); }} />
      </div>
      {bn.enabled && (
        <div style={{ marginTop:10 }}>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, fontWeight:700, marginBottom:4 }}>Határidő (torna kezdete)</div>
          <input type="datetime-local" value={bn.deadline || ''} onChange={e => { setBn({ ...bn, deadline: e.target.value }); markDirty(); }} style={{ ...dtS, width:'100%', height:42 }} />
          <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, fontWeight:700, margin:'9px 0 4px' }}>Helyes válasz (a torna után)</div>
          <select value={bn.correct || ''} onChange={e => { setBn({ ...bn, correct: e.target.value }); markDirty(); }} style={{ ...inpS, width:'100%', height:40 }}>
            <option value="">— még nincs —</option>
            {teamsArr.map(tm => <option key={tm} value={tm}>{tm}</option>)}
          </select>
          {teamsArr.length === 0 && <div style={{ fontFamily:T.font, fontSize:10.5, color:T.coral, marginTop:5 }}>Előbb adj meg csapatokat a Csapatok mezőben.</div>}
        </div>
      )}
    </div>
  );
  return (
    <div style={{ padding:16 }}>
      <div style={{ display:'flex', alignItems:'center', gap:8, marginBottom:10 }}>
        <span style={{ fontSize:20, lineHeight:1 }}>{mode === 'tipp' ? '🎯' : '⚽'}</span>
        <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>Bingó / Tipp bajnokság</span>
      </div>
      <div style={{ display:'flex', gap:8, marginBottom:12 }}>
        {[['bingo','⚽ Bingó'],['tipp','🎯 Tipp bajnokság']].map(([k,l]) => (
          <button key={k} onClick={() => { setMode(k); markDirty(); }} style={{ flex:1, padding:'11px 0', borderRadius:13, border:'none', cursor:'pointer', fontFamily:T.font, fontWeight:900, fontSize:13.5, background: mode === k ? T.mint : T.surface, color: mode === k ? '#fff' : T.inkSoft, boxShadow: mode === k ? `0 4px 12px ${T.mint}55` : T.shadow }}>{l}</button>
        ))}
      </div>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
        <div>
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>Megjelenítés a főképernyőn</div>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{enabled ? 'Látszik a gomb' : 'El van rejtve'}</div>
        </div>
        <Toggle on={enabled} onChange={() => { setEnabled(v => !v); markDirty(); }} />
      </div>

      {mode === 'bingo' ? (
        <React.Fragment>
          <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>A kártya 24 mezőt sorsol ki (középen fix DÖNTŐ), ezért legalább 24 mező kell — kevesebbnél a beépített lista marad érvényben. <span style={{ fontWeight:800, color: tooFew ? T.coral : T.mint }}>{validCount} mező</span></div>
          <div style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            {lbl('Cím / tematika')}
            <input value={title} onChange={e => { setTitle(e.target.value); markDirty(); }} placeholder="VB Bingó" style={{ ...inpS, width:'100%' }} />
          </div>
          {tooFew && <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.coral, background:T.coralSoft, borderRadius:10, padding:'8px 12px', marginBottom:10 }}>Legalább 24 mező kell — jelenleg {validCount}.</div>}
          <div style={{ display:'flex', flexDirection:'column', gap:7, marginBottom:12 }}>
            {items.map((w, i) => (
              <div key={i} style={{ display:'flex', gap:7, alignItems:'center', background:T.surface, borderRadius:12, padding:'7px 9px', boxShadow:T.shadow }}>
                <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkMute, width:20, textAlign:'center', flexShrink:0 }}>{i+1}</span>
                <input value={w.e} onChange={e => updItem(i, 'e', e.target.value)} placeholder="⚽" style={{ ...inpS, width:46, textAlign:'center', fontSize:17, padding:'8px 4px', flexShrink:0 }} />
                <input value={w.t} onChange={e => updItem(i, 't', e.target.value)} placeholder="Esemény szövege…" style={{ ...inpS, flex:1, minWidth:0, border:`1.5px solid ${(w.t||'').trim() ? T.border : T.coral}` }} />
                <button onClick={() => delItem(i)} style={{ padding:'8px 9px', borderRadius:9, border:'none', background:T.coralSoft, color:T.coral, cursor:'pointer', flexShrink:0, display:'flex', alignItems:'center' }}><BohIcon name="trash" size={13} /></button>
              </div>
            ))}
          </div>
          <button onClick={addItem} style={{ width:'100%', padding:'12px', borderRadius:14, border:`2px dashed ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer', marginBottom:14 }}>+ Új mező</button>
        </React.Fragment>
      ) : (
        <React.Fragment>
          <div style={{ fontFamily:T.font, fontSize:12.5, color:T.sub, marginBottom:12 }}>Mérkőzés-eredmény tippelés. Vegyél fel mérkőzéseket kezdési idővel; a döntő/meccs után írd be a <b>végeredményt</b> — a pontok (5/3/2/1) automatikusan kiszámolódnak. <span style={{ fontWeight:800, color: validM ? T.mint : T.coral }}>{validM} mérkőzés</span></div>
          <div style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            {lbl('Bajnokság neve')}
            <input value={tippTitle} onChange={e => { setTippTitle(e.target.value); markDirty(); }} placeholder="Tippbajnokság" style={{ ...inpS, width:'100%' }} />
          </div>
          <div style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            {lbl('Csapatok (soronként egy) — a bónuszokhoz')}
            <textarea value={teamsText} onChange={e => { setTeamsText(e.target.value); markDirty(); }} rows={3} placeholder={'Argentína\nFranciaország\nSpanyolország'} style={{ ...inpS, width:'100%', resize:'vertical', lineHeight:1.5 }} />
          </div>
          {/* Kódos védelem */}
          <div style={{ background:T.surface, borderRadius:14, padding:'12px 14px', boxShadow:T.shadow, marginBottom:12 }}>
            <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', gap:10 }}>
              <div>
                <div style={{ fontFamily:T.font, fontWeight:800, fontSize:14, color:T.ink }}>E-mailes kódvédelem</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{tippRequireCode ? 'A tippeléshez kód kell (e-mailben)' : 'Bárki tippelhet kód nélkül'}</div>
              </div>
              <Toggle on={tippRequireCode} onChange={() => { setTippRequireCode(v => !v); markDirty(); }} />
            </div>
            {tippRequireCode && (
              <div style={{ marginTop:11 }}>
                {lbl('E-mail küldő URL (Google Apps Script)')}
                <input value={tippMailUrl} onChange={e => { setTippMailUrl(e.target.value); markDirty(); }} placeholder="https://script.google.com/macros/s/…/exec" style={{ ...inpS, width:'100%' }} />
              </div>
            )}
          </div>
          {/* Mérkőzések */}
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:8 }}>Mérkőzések</div>
          <div style={{ display:'flex', flexDirection:'column', gap:10, marginBottom:12 }}>
            {matches.map((m, mi) => (
              <div key={m.id} style={{ background:T.surface, borderRadius:14, padding:'12px', boxShadow:T.shadow }}>
                <div style={{ display:'flex', gap:6, alignItems:'center', marginBottom:8 }}>
                  <input value={m.home} onChange={e => updM(mi, 'home', e.target.value)} placeholder="Hazai" list="tipp-teams" style={{ ...inpS, flex:1, minWidth:0 }} />
                  <span style={{ fontFamily:T.font, fontWeight:900, color:T.inkMute }}>–</span>
                  <input value={m.away} onChange={e => updM(mi, 'away', e.target.value)} placeholder="Vendég" list="tipp-teams" style={{ ...inpS, flex:1, minWidth:0 }} />
                  <button onClick={() => delM(mi)} style={{ padding:'8px 9px', borderRadius:9, border:'none', background:T.coralSoft, color:T.coral, cursor:'pointer', flexShrink:0, display:'flex', alignItems:'center' }}><BohIcon name="trash" size={13} /></button>
                </div>
                <div style={{ display:'flex', gap:8, alignItems:'center', marginBottom:8 }}>
                  <input type="datetime-local" value={m.kickoff || ''} onChange={e => updM(mi, 'kickoff', e.target.value)} style={{ ...dtS, flex:1, minWidth:0, height:40 }} />
                  <label style={{ display:'flex', alignItems:'center', gap:5, fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, cursor:'pointer', flexShrink:0 }}>
                    <input type="checkbox" checked={!!m.knockout} onChange={e => updM(mi, 'knockout', e.target.checked)} /> kieséses
                  </label>
                </div>
                <div style={{ display:'flex', gap:6, alignItems:'center' }}>
                  <span style={{ fontFamily:T.font, fontWeight:800, fontSize:11.5, color:T.inkSoft, flexShrink:0 }}>Végeredmény:</span>
                  <input value={m.hs} onChange={e => updM(mi, 'hs', e.target.value.replace(/[^0-9]/g,''))} inputMode="numeric" placeholder="–" style={{ ...inpS, width:48, textAlign:'center', fontWeight:900, fontSize:15 }} />
                  <span style={{ fontFamily:T.font, fontWeight:900, color:T.inkMute }}>:</span>
                  <input value={m.as} onChange={e => updM(mi, 'as', e.target.value.replace(/[^0-9]/g,''))} inputMode="numeric" placeholder="–" style={{ ...inpS, width:48, textAlign:'center', fontWeight:900, fontSize:15 }} />
                  <div style={{ flex:1 }} />
                  <span style={{ fontFamily:T.font, fontSize:10, color:T.inkMute }}>meccs után</span>
                </div>
              </div>
            ))}
          </div>
          <datalist id="tipp-teams">{teamsArr.map(tm => <option key={tm} value={tm} />)}</datalist>
          <button onClick={addMatch} style={{ width:'100%', padding:'12px', borderRadius:14, border:`2px dashed ${T.border}`, background:'transparent', fontFamily:T.font, fontWeight:800, fontSize:14, color:T.inkSoft, cursor:'pointer', marginBottom:14 }}>+ Új mérkőzés</button>
          {/* Bónuszok */}
          <div style={{ fontFamily:T.font, fontWeight:800, fontSize:11, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.06em', marginBottom:8 }}>Plusz pontok</div>
          <BonusCard title="Végső győztes" emoji="🏆" bn={bWinner} setBn={setBWinner} />
          <BonusCard title="Gólkirályt adó csapat" emoji="⚽" bn={bScorer} setBn={setBScorer} />
        </React.Fragment>
      )}

      <div style={{ display:'flex', gap:8, alignItems:'center', marginTop:2 }}>
        <button onClick={() => { if (confirmReset) reset(); else setConfirmReset(true); }} disabled={saving} style={{ padding:'11px 14px', borderRadius:12, border:'none', background: confirmReset ? T.coral : T.surfaceMuted, color: confirmReset ? '#fff' : T.inkSoft, fontFamily:T.font, fontWeight:800, fontSize:13, cursor:'pointer' }}>{confirmReset ? 'Biztos? Alaphelyzet!' : 'Alaphelyzet'}</button>
        <div style={{ flex:1 }} />
        {saved && !dirty && <span style={{ fontFamily:T.font, fontWeight:800, fontSize:12, color:T.mint }}>Mentve ✓</span>}
        <button onClick={save} disabled={saving || !dirty} style={{ padding:'12px 20px', borderRadius:12, border:'none', background: dirty ? T.mint : T.mintSoft, color:'#fff', fontFamily:T.font, fontWeight:900, fontSize:14, cursor: dirty ? 'pointer' : 'default', opacity: saving ? 0.6 : 1 }}>Mentés</button>
      </div>
    </div>
  );
}
'''

src = src[:j1] + NEW_AB + src[j2+1:]

# Verziobump
assert src.count("const APP_VERSION = 'v9.994';") == 1
src = src.replace("const APP_VERSION = 'v9.994';", "const APP_VERSION = 'v9.995';")

io.open(PATH, 'w', encoding='utf-8').write(src)
print('OK — AdminBingo match editor applied')
