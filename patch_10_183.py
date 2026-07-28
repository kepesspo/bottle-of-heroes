#!/usr/bin/env python3
# v10.183 — Ország-Város: saját rajzú értékelés, és a nagyító a szó bal oldalára
#
# Ket baj volt a szavazo sorral:
#
# 1) A nagyito BE VOLT SZORULVA a ket ertekelo gomb koze. Aki keresni akart,
#    konnyen szavazott helyette — es a szavazat azonnal el is ment.
# 2) A ket ertekelo gomb rendszer-emoji volt (👍/👎), ami keszulekenkent maskepp
#    nez ki, es kilogott a jatek sajat, vonalas ikonnyelvebol (OVFJ_ICONS).
#
# A pipa/X ráadásul pontosabb is: itt nem tetszesrol van szo, hanem arrol, hogy
# ervenyes-e a valasz.
import sys

P = 'app.src.html'
src = open(P, encoding='utf-8').read()

# ─── 1) Az uj ikonok — ugyanazon a nyelven, mint a kategoria-ikonok ───
ANCHOR = "const OVFJ_CATS = ["
assert src.count(ANCHOR) == 1, 'OVFJ_CATS: %d' % src.count(ANCHOR)
ICONS = """// A szavazó sor ikonjai. Szándékosan ugyanaz a nyelv, mint az OVFJ_ICONS-é
// (24-es viewBox, vonalas rajz, kerek végződés) — a rendszer-emoji készülékenként
// máshogy néz ki, és kilóg a játék többi ikonja közül.
// A pipa/X vastagabb vonala tudatos: ezek gombok, nem díszek.
const OVFJ_UI = {
  check:  (c,s=20)=><svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round"><path d="M5 12.6l4.7 4.7L19 7"/></svg>,
  cross:  (c,s=20)=><svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2.8" strokeLinecap="round" strokeLinejoin="round"><path d="M6.8 6.8l10.4 10.4M17.2 6.8L6.8 17.2"/></svg>,
  search: (c,s=20)=><svg width={s} height={s} viewBox="0 0 24 24" fill="none" stroke={c} strokeWidth="2.1" strokeLinecap="round" strokeLinejoin="round"><circle cx="10.4" cy="10.4" r="6.2"/><path d="M15 15l5 5"/></svg>,
};
const OVFJ_CATS = ["""
src = src.replace(ANCHOR, ICONS, 1)

# ─── 2) A fejlec ───
# Ha a cimben marad a 👍👎, miközben a gombokon mar pipa/X van, az aktivan
# felrevezet — ezert az uj jelekre cserelodik.
OLD_HDR = """      <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:16,color:T.ink,textAlign:'center',letterSpacing:T.letterDisplay}}>„{letter}" — Szavazás 👍👎</div>"""
assert src.count(OLD_HDR) == 1, 'fejlec: %d' % src.count(OLD_HDR)
NEW_HDR = """      <div style={{fontFamily:T.font,fontWeight:T.weightDisplay,fontSize:16,color:T.ink,textAlign:'center',letterSpacing:T.letterDisplay,display:'flex',alignItems:'center',justifyContent:'center',gap:7}}>
        <span>„{letter}" — Szavazás</span>
        <span style={{display:'flex',alignItems:'center',gap:3}}>{OVFJ_UI.check(T.mint,15)}{OVFJ_UI.cross(T.coral,15)}</span>
      </div>"""
src = src.replace(OLD_HDR, NEW_HDR, 1)

# ─── 3) A sor ujrarendezese ───
OLD_ROW = """              <div key={p.id} style={{display:'flex',alignItems:'center',gap:8}}>
                <OVFJAvatar p={p} size={22} />
                <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:12,color:T.inkSoft,width:78,flexShrink:0,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{p.name}{isMe?' (Te)':''}</span>
                <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,flex:1,minWidth:0,color:!vi.val?T.inkMute:vi.valid?T.ink:T.coral,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',textDecoration:vi.val&&!vi.valid?'line-through':'none',opacity:vi.val&&!vi.valid?0.7:1}}>{vi.val||'—'}</span>
                {vi.valid && !isMe ? (
                  <div style={{display:'flex',gap:4,flexShrink:0,alignItems:'center'}}>
                    {tl && <span style={{fontFamily:T.font,fontSize:10,color:T.inkSoft}}>👍{tl.yes}</span>}
                    <a href={`https://www.google.com/search?q=${encodeURIComponent(vi.val)}`} target="_blank" rel="noreferrer" style={{fontSize:13,textDecoration:'none',opacity:0.5,lineHeight:1}}>🔍</a>
                    <button onClick={()=>onVote(p.id,cat.key,true)} style={{width:32,height:30,borderRadius:8,border:`1.5px solid ${mv===true?T.mint:T.surfaceMuted}`,background:mv===true?T.mintSoft:'transparent',cursor:'pointer',fontSize:14,display:'grid',placeItems:'center'}}>👍</button>
                    <button onClick={()=>onVote(p.id,cat.key,false)} style={{width:32,height:30,borderRadius:8,border:`1.5px solid ${mv===false?T.coral:T.surfaceMuted}`,background:mv===false?T.coralSoft:'transparent',cursor:'pointer',fontSize:14,display:'grid',placeItems:'center'}}>👎</button>
                  </div>
                ) : vi.valid && isMe ? ("""
assert src.count(OLD_ROW) == 1, 'sor: %d' % src.count(OLD_ROW)

NEW_ROW = """              // A kereso a szo BAL oldalan all, hogy ne a ket ertekelo gomb koze
              // szoruljon. A helye akkor is megmarad, ha nincs mit keresni —
              // kulonben a szavak nem egy oszlopban allnanak, pedig fentrol
              // lefele olvasva hasonlitja ossze oket az ember.
              const canSearch = !!(vi.val && vi.valid);
              const voteBtn = (yes) => (
                <button onClick={()=>onVote(p.id,cat.key,yes)}
                  aria-label={yes?'Elfogadom':'Nem fogadom el'}
                  style={{width:32,height:30,borderRadius:9,flexShrink:0,cursor:'pointer',display:'grid',placeItems:'center',
                          border:`1.5px solid ${mv===yes?(yes?T.mint:T.coral):T.surfaceMuted}`,
                          background: mv===yes ? (yes?T.mint:T.coral) : 'transparent',
                          WebkitTapHighlightColor:'transparent',padding:0}}>
                  {(yes?OVFJ_UI.check:OVFJ_UI.cross)(mv===yes ? '#fff' : T.inkMute, 17)}
                </button>
              );
              return (
              <div key={p.id} style={{display:'flex',alignItems:'center',gap:8}}>
                <OVFJAvatar p={p} size={22} />
                <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:12,color:T.inkSoft,width:78,flexShrink:0,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap'}}>{p.name}{isMe?' (Te)':''}</span>
                <div style={{width:20,flexShrink:0,display:'grid',placeItems:'center',marginRight:-2}}>
                  {canSearch && (
                    <a href={`https://www.google.com/search?q=${encodeURIComponent(vi.val)}`} target="_blank" rel="noreferrer"
                       aria-label="Rákeresek" style={{display:'grid',placeItems:'center',opacity:0.55,lineHeight:0}}>
                      {OVFJ_UI.search(T.inkSoft,17)}
                    </a>
                  )}
                </div>
                <span style={{fontFamily:T.font,fontWeight:T.weightTitle,fontSize:14,flex:1,minWidth:0,color:!vi.val?T.inkMute:vi.valid?T.ink:T.coral,overflow:'hidden',textOverflow:'ellipsis',whiteSpace:'nowrap',textDecoration:vi.val&&!vi.valid?'line-through':'none',opacity:vi.val&&!vi.valid?0.7:1}}>{vi.val||'—'}</span>
                {vi.valid && !isMe ? (
                  <div style={{display:'flex',gap:4,flexShrink:0,alignItems:'center'}}>
                    {tl && <span style={{fontFamily:T.font,fontSize:10,fontWeight:T.weightTitle,color:T.inkSoft,display:'flex',alignItems:'center',gap:1}}>{OVFJ_UI.check(T.inkSoft,11)}{tl.yes}</span>}
                    {voteBtn(true)}
                    {voteBtn(false)}
                  </div>
                ) : vi.valid && isMe ? ("""
src = src.replace(OLD_ROW, NEW_ROW, 1)

# A regi `return (` sor kikerul: az uj blokk mar tartalmazza.
OLD_RET = """            const tl = tallies ? (tallies[vk] || {yes:0,no:0}) : null;
            return (
              // A kereso a szo BAL oldalan all"""
assert src.count(OLD_RET) == 1, 'return-sor: %d' % src.count(OLD_RET)
src = src.replace(OLD_RET, """            const tl = tallies ? (tallies[vk] || {yes:0,no:0}) : null;
              // A kereso a szo BAL oldalan all""", 1)

# ─── verziobump ───
assert src.count("const APP_VERSION = 'v10.182';") == 1
src = src.replace("const APP_VERSION = 'v10.182';", "const APP_VERSION = 'v10.183';", 1)

open(P, 'w', encoding='utf-8').write(src)
print('OK — pipa/X gombok, sajat rajzu nagyito, a kereso a szo bal oldalan')
