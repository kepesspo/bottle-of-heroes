#!/usr/bin/env python3
"""v9.395 — Zene szűrő gombok: téma-tudatos színek (sötét módban is jó)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old_btns = """    const btnBase = { border:'1.5px solid rgba(26,42,74,0.12)', borderRadius:14, cursor:'pointer', fontFamily:T.font, fontWeight:600, fontSize:15, padding:'13px 10px', textAlign:'center', transition:'background .12s,color .12s,border .12s' };
    return (
      <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
        {/* "Minden X" — full width, clears selection */}
        <button onClick={() => setConfig(c=>({...c,[configKey]:[]}))} style={{
          ...btnBase, width:'100%',
          background: allActive ? T.mintSoft : '#fff',
          color:       allActive ? T.mintDeep : T.ink,
          border:      allActive ? `1.5px solid ${T.mint}` : '1.5px solid rgba(26,42,74,0.12)',
          fontWeight:  allActive ? 700 : 600,
        }}>{configKey==='eras' ? 'Minden korszak' : 'Minden stílus'}</button>
        {/* Options — 2 column grid, multi-select */}
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
          {options.map(o => {
            const active = selected.includes(o.v);
            return (
              <button key={o.v} onClick={() => setConfig(c=>({...c,[configKey]:toggle(c[configKey]||[],o.v)}))} style={{
                ...btnBase,
                background: active ? T.mintSoft : '#fff',
                color:       active ? T.mintDeep : T.ink,
                border:      active ? `1.5px solid ${T.mint}` : '1.5px solid rgba(26,42,74,0.12)',
                fontWeight:  active ? 700 : 600,
              }}>{o.label}</button>
            );
          })}
        </div>
      </div>
    );"""

new_btns = """    const btnBase = { border:'1.5px solid '+T.inkMute+'30', borderRadius:14, cursor:'pointer', fontFamily:T.font, fontWeight:600, fontSize:15, padding:'13px 10px', textAlign:'center', transition:'background .12s,color .12s,border .12s' };
    return (
      <div style={{ display:'flex', flexDirection:'column', gap:10 }}>
        {/* "Minden X" — full width, clears selection */}
        <button onClick={() => setConfig(c=>({...c,[configKey]:[]}))} style={{
          ...btnBase, width:'100%',
          background: allActive ? T.mintSoft : T.surface,
          color:       allActive ? T.mintDeep : T.ink,
          border:      allActive ? `1.5px solid ${T.mint}` : '1.5px solid '+T.inkMute+'30',
          fontWeight:  allActive ? 700 : 600,
        }}>{configKey==='eras' ? 'Minden korszak' : 'Minden stílus'}</button>
        {/* Options — 2 column grid, multi-select */}
        <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
          {options.map(o => {
            const active = selected.includes(o.v);
            return (
              <button key={o.v} onClick={() => setConfig(c=>({...c,[configKey]:toggle(c[configKey]||[],o.v)}))} style={{
                ...btnBase,
                background: active ? T.mintSoft : T.surface,
                color:       active ? T.mintDeep : T.ink,
                border:      active ? `1.5px solid ${T.mint}` : '1.5px solid '+T.inkMute+'30',
                fontWeight:  active ? 700 : 600,
              }}>{o.label}</button>
            );
          })}
        </div>
      </div>
    );"""

assert old_btns in html, "FAIL: zene filter btns"
html = html.replace(old_btns, new_btns, 1)

html = html.replace("const APP_VERSION = 'v9.394';", "const APP_VERSION = 'v9.395';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.395 — Zene szűrő gombok téma-tudatos színek")
