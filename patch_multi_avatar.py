#!/usr/bin/env python3
"""Patch: Multi-avatar result banner — 2 avatar vagy 2+ badge (v9.645 → v9.646)"""
import sys

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()
orig = src

def replace_once(old, new, label):
    global src
    if old not in src:
        print(f'MISSING: {label}'); sys.exit(1)
    if src.count(old) != 1:
        print(f'AMBIGUOUS ({src.count(old)}x): {label}'); sys.exit(1)
    src = src.replace(old, new, 1)
    print(f'OK: {label}')

# ── Közös: multiPlayers számítás a resultMinimized blokk előtt ────────────────
# Az rp meghatározása után a multiPlayers-t is kiszámítjuk
replace_once(
    """      {gameResult && (() => {
        const rp = gameResult.playerName ? players.find(p => p.name === gameResult.playerName) : null;
        const isCorrect = gameResult.correct;
        const bgGrad = isCorrect
          ? 'linear-gradient(160deg, #1a8a55f0 0%, #25b572f0 100%)'
          : 'linear-gradient(160deg, #c02828f0 0%, #e84040f0 100%)';
        const glow = isCorrect ? '#25b572' : '#e84040';""",
    """      {gameResult && (() => {
        const rp = gameResult.playerName ? players.find(p => p.name === gameResult.playerName) : null;
        const isCorrect = gameResult.correct;
        const bgGrad = isCorrect
          ? 'linear-gradient(160deg, #1a8a55f0 0%, #25b572f0 100%)'
          : 'linear-gradient(160deg, #c02828f0 0%, #e84040f0 100%)';
        const glow = isCorrect ? '#25b572' : '#e84040';
        // Több játékos ha subtitle-ban vannak (pl. "Sere: 1 rontás, Kecsi: 1 rontás")
        const subtitlePlayers = gameResult.subtitle
          ? gameResult.subtitle.split(', ')
              .map(s => { const name = s.split(':')[0].trim(); return players.find(p => p.name === name); })
              .filter(Boolean)
          : [];
        const multiPlayers = subtitlePlayers.length >= 2 ? subtitlePlayers : (rp ? [rp] : []);
        const shownAv = multiPlayers.slice(0, 2);
        const extraAv = Math.max(0, multiPlayers.length - 2);
        // Avatar pile helper — size px
        const AvatarPile = ({size, overlap, borderW}) => (
          <div style={{ display:'flex', alignItems:'center', flexShrink:0 }}>
            {shownAv.map((p, i) => (
              <div key={p.id||i} style={{ width:size, height:size, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', border:`${borderW}px solid rgba(255,255,255,0.6)`, marginLeft: i===0 ? 0 : -overlap, zIndex: shownAv.length - i, flexShrink:0 }}>
                {p.img ? <img src={p.img} style={{ width:size, height:size, objectFit:'cover' }} />
                  : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:Math.round(size*0.42), color:'#fff' }}>{(p.name||'?').charAt(0).toUpperCase()}</span>}
              </div>
            ))}
            {extraAv > 0 && (
              <div style={{ width:size*0.75, height:size*0.75, borderRadius:'50%', background:'rgba(255,255,255,0.28)', display:'grid', placeItems:'center', border:`${borderW}px solid rgba(255,255,255,0.5)`, marginLeft:-overlap, fontFamily:T.font, fontWeight:900, fontSize:Math.round(size*0.28), color:'#fff', flexShrink:0 }}>+{extraAv}</div>
            )}
            {multiPlayers.length === 0 && (
              <span style={{ fontSize:size*0.8, lineHeight:1 }}>{isCorrect ? '🌟' : '🍺'}</span>
            )}
          </div>
        );""",
    "multiPlayers számítás + AvatarPile helper"
)

# ── Shrinking overlay: egységes AvatarPile ────────────────────────────────────
replace_once(
    """                  }} onAnimationEnd={() => setResultMinimized(true)}>
                    {rp ? (
                      <div style={{ width:80, height:80, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 0 0 5px rgba(255,255,255,0.45)' }}>
                        {rp.img ? <img src={rp.img} style={{ width:80, height:80, objectFit:'cover' }} />
                          : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:34, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                      </div>
                    ) : <div style={{ fontSize:64 }}>{isCorrect ? '🌟' : '🍺'}</div>}""",
    """                  }} onAnimationEnd={() => setResultMinimized(true)}>
                    <AvatarPile size={72} overlap={20} borderW={3} />""",
    "Shrinking overlay: AvatarPile"
)

# ── Mini bar: AvatarPile (34px) ────────────────────────────────────────────────
replace_once(
    """                  {rp ? (
                    <div style={{ width:34, height:34, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0, boxShadow:'0 0 0 2.5px rgba(255,255,255,0.5)' }}>
                      {rp.img ? <img src={rp.img} style={{ width:34, height:34, objectFit:'cover' }} />
                        : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                    </div>
                  ) : <span style={{ fontSize:26, flexShrink:0 }}>{isCorrect ? '🌟' : '🍺'}</span>}""",
    """                  <AvatarPile size={34} overlap={10} borderW={2} />""",
    "Mini bar: AvatarPile"
)

# ── Full overlay: AvatarPile (72px) + shake animáció egynél ───────────────────
replace_once(
    """              {rp ? (
                <div style={{ width:80, height:80, borderRadius:'50%', background:rp.color, display:'grid', placeItems:'center', overflow:'hidden', boxShadow:'0 0 0 5px rgba(255,255,255,0.45)', animation: isCorrect ? undefined : 'shakeDrink .7s ease-in-out' }}>
                  {rp.img ? <img src={rp.img} style={{ width:80, height:80, objectFit:'cover' }} />
                    : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:34, color:'#fff' }}>{(rp.name||'?').charAt(0).toUpperCase()}</span>}
                </div>
              ) : (
                <div style={{ fontSize:64, lineHeight:1, animation: isCorrect ? 'starPop .45s' : 'shakeDrink .7s ease-in-out' }}>
                  {isCorrect ? '🌟' : '🍺'}
                </div>
              )}""",
    """              <div style={{ animation: !isCorrect && multiPlayers.length <= 1 ? 'shakeDrink .7s ease-in-out' : undefined }}>
                <AvatarPile size={72} overlap={22} borderW={3} />
              </div>""",
    "Full overlay: AvatarPile (72px)"
)

# playerName sor elrejtése ha többen vannak (a subtitle már tartalmazza)
replace_once(
    """              {gameResult.playerName && (
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'rgba(255,255,255,0.9)', textAlign:'center' }}>
                  {isCorrect ? `${gameResult.playerName} — +1 pont` : gameResult.playerName}
                </div>
              )}""",
    """              {gameResult.playerName && multiPlayers.length <= 1 && (
                <div style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'rgba(255,255,255,0.9)', textAlign:'center' }}>
                  {isCorrect ? `${gameResult.playerName} — +1 pont` : gameResult.playerName}
                </div>
              )}""",
    "playerName elrejtése ha multiPlayers"
)

# ── Version bump ──────────────────────────────────────────────────────────────
replace_once(
    "const APP_VERSION = 'v9.645';",
    "const APP_VERSION = 'v9.646';",
    "version bump 9.645 → 9.646"
)

assert src != orig
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)
print("\nAll patches applied.")
