#!/usr/bin/env python3
"""v9.402 — Szólánc: 2 szóról indul, done screen egyszerűsítve, scrollable;
             Kártyacsata: scrollable; Kvíz: scrollable;
             Mindhárom játék: onSetHideFooter eltávolítva (game controller látható)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Szólánc: fresh(1,0) → fresh(2,0) ─────────────────────────────────────
html = html.replace(
    "  const [S, setS] = React.useState(() => fresh(1, 0));\n  const [done, setDone] = React.useState(null); // { failName, failColor, failPid }\n\n  React.useEffect(() => { setS(fresh(1, 0)); setDone(null); }, [gameIdx]);\n  React.useEffect(() => {\n    if (onSetHideFooter) onSetHideFooter(true);\n    return () => { if (onSetHideFooter) onSetHideFooter(false); };\n  }, []);",
    "  const [S, setS] = React.useState(() => fresh(2, 0));\n  const [done, setDone] = React.useState(null);\n\n  React.useEffect(() => { setS(fresh(2, 0)); setDone(null); }, [gameIdx]);",
    1
)

# ── 2. Szólánc: done screen egyszerűsítés (iszik/pontok szekció eltávolítva) ─
old_done = """      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,padding:'24px 0',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:52}}>{winMsg ? '🏆' : '😵'}</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:winMsg?T.mint:T.coral}}>
          {winMsg ? 'Bravo! Elfogytak a szavak!' : `${done.failName} elrontotta!`}
        </div>
        {!winMsg && (
          <div style={{display:'flex',flexDirection:'column',gap:8,width:'100%'}}>
            <div style={{padding:'12px 16px',borderRadius:14,background:T.coral+'18',border:'1.5px solid '+T.coral+'44',fontFamily:T.font,fontWeight:700,fontSize:15,color:T.coral}}>
              🍺 {done.failName} iszik egyet
            </div>
            <div style={{padding:'12px 16px',borderRadius:14,background:T.mint+'18',border:'1.5px solid '+T.mint+'44',fontFamily:T.font,fontWeight:700,fontSize:15,color:T.mint}}>
              ⭐ A többiek pontot kapnak
            </div>
          </div>
        )}
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:4}}>
          Elért szint: {S.chain.length} szó · {cat}
        </div>
      </div>"""
new_done = """      <div style={{display:'flex',flexDirection:'column',alignItems:'center',gap:16,padding:'24px 0',textAlign:'center',animation:'popIn .4s cubic-bezier(.2,.9,.3,1.2)'}}>
        <div style={{fontSize:52}}>{winMsg ? '🏆' : '😵'}</div>
        <div style={{fontFamily:T.font,fontWeight:900,fontSize:22,color:winMsg?T.mint:T.coral}}>
          {winMsg ? 'Bravo! Elfogytak a szavak!' : `${done.failName} elrontotta!`}
        </div>
        <div style={{fontFamily:T.font,fontSize:13,color:T.inkSoft,marginTop:4}}>
          Elért szint: {S.chain.length} szó · {cat}
        </div>
      </div>"""
assert old_done in html, "FAIL: szolánc done screen"
html = html.replace(old_done, new_done, 1)

# ── 3. Szólánc: show fázis div scrollable ────────────────────────────────────
old_show_div = "      <div style={{display:'flex',flexDirection:'column',gap:14}}>\n        {/* Fejléc */}\n        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'4px 0'}}>\n          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 14px',background:curPlayer?.color+'22'||T.mint+'22',borderRadius:999}}>\n            <div style={{width:8,height:8,borderRadius:'50%',background:curPlayer?.color||T.mint}} />\n            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{curPlayer?.name}</span>\n          </div>\n          <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>{cat}</div>\n        </div>\n\n        {/* Szó megjelenítő */}"
new_show_div = "      <div style={{display:'flex',flexDirection:'column',gap:14,overflowY:'auto'}}>\n        {/* Fejléc */}\n        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'4px 0'}}>\n          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 14px',background:curPlayer?.color+'22'||T.mint+'22',borderRadius:999}}>\n            <div style={{width:8,height:8,borderRadius:'50%',background:curPlayer?.color||T.mint}} />\n            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{curPlayer?.name}</span>\n          </div>\n          <div style={{fontFamily:T.font,fontSize:12,color:T.inkSoft}}>{cat}</div>\n        </div>\n\n        {/* Szó megjelenítő */}"
assert old_show_div in html, "FAIL: szolánc show div"
html = html.replace(old_show_div, new_show_div, 1)

# ── 4. Szólánc: recall fázis div scrollable ──────────────────────────────────
old_recall_div = "      <div style={{display:'flex',flexDirection:'column',gap:14}}>\n        {/* Fejléc */}\n        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'4px 0'}}>\n          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 14px',background:curPlayer?.color+'22'||T.mint+'22',borderRadius:999}}>\n            <div style={{width:8,height:8,borderRadius:'50%',background:curPlayer?.color||T.mint}} />\n            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{curPlayer?.name} — sorrendben!</span>"
new_recall_div = "      <div style={{display:'flex',flexDirection:'column',gap:14,overflowY:'auto'}}>\n        {/* Fejléc */}\n        <div style={{display:'flex',alignItems:'center',justifyContent:'space-between',padding:'4px 0'}}>\n          <div style={{display:'inline-flex',alignItems:'center',gap:8,padding:'5px 14px',background:curPlayer?.color+'22'||T.mint+'22',borderRadius:999}}>\n            <div style={{width:8,height:8,borderRadius:'50%',background:curPlayer?.color||T.mint}} />\n            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{curPlayer?.name} — sorrendben!</span>"
assert old_recall_div in html, "FAIL: szolánc recall div"
html = html.replace(old_recall_div, new_recall_div, 1)

# ── 5. Kártyacsata: onSetHideFooter eltávolítva + scrollable ────────────────
old_cb_effect = """  const [S, setS] = React.useState(fresh);
  React.useEffect(() => { setS(fresh()); }, [gameIdx]);
  React.useEffect(() => {
    if (onSetHideFooter) onSetHideFooter(true);
    return () => { if (onSetHideFooter) onSetHideFooter(false); };
  }, []);"""
new_cb_effect = """  const [S, setS] = React.useState(fresh);
  React.useEffect(() => { setS(fresh()); }, [gameIdx]);"""
assert old_cb_effect in html, "FAIL: cardbattle effect"
html = html.replace(old_cb_effect, new_cb_effect, 1)

# Kártyacsata tervezés div scrollable
old_cb_div = "      <div style={{display:'flex',flexDirection:'column',gap:10}}>\n        <div style={{textAlign:'center',padding:'4px 0 6px'}}>"
new_cb_div = "      <div style={{display:'flex',flexDirection:'column',gap:10,overflowY:'auto'}}>\n        <div style={{textAlign:'center',padding:'4px 0 6px'}}>"
assert old_cb_div in html, "FAIL: cardbattle plan div"
html = html.replace(old_cb_div, new_cb_div, 1)

# Kártyacsata reveal div scrollable
old_cb_rev = "      <div style={{display:'flex',flexDirection:'column',gap:12}}>\n        <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:28,padding:'4px 0 8px'}}>"
new_cb_rev = "      <div style={{display:'flex',flexDirection:'column',gap:12,overflowY:'auto'}}>\n        <div style={{display:'flex',alignItems:'center',justifyContent:'center',gap:28,padding:'4px 0 8px'}}>"
assert old_cb_rev in html, "FAIL: cardbattle reveal div"
html = html.replace(old_cb_rev, new_cb_rev, 1)

# ── 6. Kvíz: onSetHideFooter eltávolítva ────────────────────────────────────
old_quiz_effect = """  React.useEffect(() => {
    if (onSetHideFooter) onSetHideFooter(true);
    return () => { if (onSetHideFooter) onSetHideFooter(false); };
  }, []);

  const cats = (gameMeta?.quizConfig?.cats)"""
new_quiz_effect = """  const cats = (gameMeta?.quizConfig?.cats)"""
assert old_quiz_effect in html, "FAIL: quiz effect"
html = html.replace(old_quiz_effect, new_quiz_effect, 1)

html = html.replace("const APP_VERSION = 'v9.401';", "const APP_VERSION = 'v9.402';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.402 — Szólánc 2 szóról, scrollable tartalom, game controller látható mindhárom játéknál")
