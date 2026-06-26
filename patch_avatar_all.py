#!/usr/bin/env python3
"""Patch: Add avatar images to all remaining letter-circle components (v9.638 → v9.639)"""

import sys

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

orig = src

def replace_once(old, new, label):
    global src
    if old not in src:
        print(f'MISSING: {label}')
        sys.exit(1)
    count = src.count(old)
    if count != 1:
        print(f'AMBIGUOUS ({count}x): {label}')
        sys.exit(1)
    src = src.replace(old, new, 1)
    print(f'OK: {label}')

def replace_n(old, new, label, n):
    global src
    count = src.count(old)
    if count != n:
        print(f'EXPECTED {n}x got {count}x: {label}')
        sys.exit(1)
    src = src.replace(old, new)
    print(f'OK ({n}x): {label}')

# ── 1. Beer Pong bracket: 56px winner button ─────────────────────────────────
replace_once(
    """<div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:24, color:'#fff', boxShadow:'0 4px 12px ' + p.color + '55' }}>
                      {p.name.charAt(0).toUpperCase()}
                    </div>""",
    """<div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:24, color:'#fff', boxShadow:'0 4px 12px ' + p.color + '55', overflow:'hidden' }}>
                      {p.img ? <img src={p.img} style={{ width:56, height:56, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:24, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}
                    </div>""",
    "Beer Pong bracket 56px"
)

# ── 2. Mindennap játék current player 120px ───────────────────────────────────
replace_once(
    """<div style={{ width:120, height:120, borderRadius:'50%', background:current.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:52, color:'#fff', boxShadow:`0 8px 32px ${current.color}66` }}>
            {current.name.charAt(0).toUpperCase()}
          </div>""",
    """<div style={{ width:120, height:120, borderRadius:'50%', background:current.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:52, color:'#fff', boxShadow:`0 8px 32px ${current.color}66`, overflow:'hidden' }}>
            {current.img ? <img src={current.img} style={{ width:120, height:120, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:52, color:'#fff' }}>{current.name.charAt(0).toUpperCase()}</span>}
          </div>""",
    "Current player 120px"
)

# ── 3. Player queue row (Mindennap): 44px ─────────────────────────────────────
replace_once(
    """                  width:44, height:44, borderRadius:'50%',
                  background: active ? p.color : `${p.color}55`,
                  display:'grid', placeItems:'center',
                  fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff',
                  border: active ? `3px solid ${p.color}` : '3px solid transparent',
                  outline: active ? `3px solid ${p.color}44` : 'none',
                  transition:'all .2s',
                }}>
                  {p.name.charAt(0).toUpperCase()}""",
    """                  width:44, height:44, borderRadius:'50%',
                  background: active ? p.color : `${p.color}55`,
                  display:'grid', placeItems:'center',
                  fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff',
                  border: active ? `3px solid ${p.color}` : '3px solid transparent',
                  outline: active ? `3px solid ${p.color}44` : 'none',
                  transition:'all .2s', overflow:'hidden',
                }}>
                  {p.img ? <img src={p.img} style={{ width:44, height:44, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}""",
    "Player queue 44px"
)

# ── 4. Fingerit distribute drinkers list: 28px ───────────────────────────────
replace_once(
    """<div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', flexShrink:0 }}>
                {p.name.charAt(0).toUpperCase()}
              </div>""",
    """<div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                {p.img ? <img src={p.img} style={{ width:28, height:28, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}
              </div>""",
    "Fingerit drinkers 28px"
)

# ── 5. Spinner dynamic size: player ──────────────────────────────────────────
replace_once(
    """<div style={{ width:isCenter?44:32, height:isCenter?44:32, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:isCenter?18:13, color:'#fff', flexShrink:0, transition:'all .1s' }}>
                {player.name.charAt(0).toUpperCase()}
              </div>""",
    """<div style={{ width:isCenter?44:32, height:isCenter?44:32, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:isCenter?18:13, color:'#fff', flexShrink:0, transition:'all .1s', overflow:'hidden' }}>
                {player.img ? <img src={player.img} style={{ width:isCenter?44:32, height:isCenter?44:32, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:isCenter?18:13, color:'#fff' }}>{player.name.charAt(0).toUpperCase()}</span>}
              </div>""",
    "Spinner dynamic 44/32px"
)

# ── 6. DrinkDistributor 30px ──────────────────────────────────────────────────
replace_once(
    """<div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0 }}>
              {p.name.charAt(0).toUpperCase()}
            </div>""",
    """<div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0, overflow:'hidden' }}>
              {p.img ? <img src={p.img} style={{ width:30, height:30, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}
            </div>""",
    "DrinkDistributor 30px"
)

# ── 7. Imposztor reveal step: pl 36px ─────────────────────────────────────────
replace_once(
    """<div style={{ width:36, height:36, borderRadius:'50%', background:pl.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
            {pl.name.charAt(0).toUpperCase()}
          </div>""",
    """<div style={{ width:36, height:36, borderRadius:'50%', background:pl.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0, overflow:'hidden' }}>
            {pl.img ? <img src={pl.img} style={{ width:36, height:36, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff' }}>{pl.name.charAt(0).toUpperCase()}</span>}
          </div>""",
    "Imposztor reveal pl 36px"
)

# ── 8. Imposztor vote step: voter 36px ────────────────────────────────────────
replace_once(
    """<div style={{ width:36, height:36, borderRadius:'50%', background:voter.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
            {voter.name.charAt(0).toUpperCase()}
          </div>""",
    """<div style={{ width:36, height:36, borderRadius:'50%', background:voter.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0, overflow:'hidden' }}>
            {voter.img ? <img src={voter.img} style={{ width:36, height:36, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff' }}>{voter.name.charAt(0).toUpperCase()}</span>}
          </div>""",
    "Imposztor vote voter 36px"
)

# ── 9. Kisebb (Number Guess) current player 36px ─────────────────────────────
replace_once(
    """<div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.coral, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
            {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
          </div>""",
    """<div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.coral, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0, overflow:'hidden' }}>
            {currentPlayer?.img ? <img src={currentPlayer.img} style={{ width:36, height:36, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff' }}>{(currentPlayer?.name||'?').charAt(0).toUpperCase()}</span>}
          </div>""",
    "Kisebb currentPlayer 36px"
)

# ── 10. Rulett wheel avatar: dynamic AVATAR_D ────────────────────────────────
replace_once(
    """                display:'grid', placeItems:'center',
                fontFamily:T.font, fontWeight:800, fontSize:22, color:'#fff',
                transition:'box-shadow .3s, border .3s',
                flexShrink:0,
              }}>
                {(p.name||'?').charAt(0).toUpperCase()}
              </div>""",
    """                display:'grid', placeItems:'center',
                fontFamily:T.font, fontWeight:800, fontSize:22, color:'#fff',
                transition:'box-shadow .3s, border .3s',
                flexShrink:0, overflow:'hidden',
              }}>
                {p.img ? <img src={p.img} style={{ width:AVATAR_D, height:AVATAR_D, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:800, fontSize:22, color:'#fff' }}>{(p.name||'?').charAt(0).toUpperCase()}</span>}
              </div>""",
    "Rulett wheel avatar AVATAR_D"
)

# ── 11. Loverseny loser pick 44px ─────────────────────────────────────────────
replace_once(
    """<div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>
                {p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:selected?T.coral:T.ink }}>""",
    """<div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff', overflow:'hidden' }}>
                {p.img ? <img src={p.img} style={{ width:44, height:44, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}
              </div>
              <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:selected?T.coral:T.ink }}>""",
    "Loverseny loser pick 44px"
)

# ── 12. Erem pick phase: challenger 30px ─────────────────────────────────────
replace_once(
    """<div style={{ width:30, height:30, borderRadius:'50%', background:challenger.color,
                display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>
                {challenger.name.charAt(0).toUpperCase()}
              </div>""",
    """<div style={{ width:30, height:30, borderRadius:'50%', background:challenger.color,
                display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', overflow:'hidden' }}>
                {challenger.img ? <img src={challenger.img} style={{ width:30, height:30, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{challenger.name.charAt(0).toUpperCase()}</span>}
              </div>""",
    "Erem pick challenger 30px"
)

# ── 13. Erem flipping phase: challenger 26px ─────────────────────────────────
replace_once(
    """<div style={{ width:26, height:26, borderRadius:'50%', background:challenger.color,
                display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>
                {challenger.name.charAt(0).toUpperCase()}
              </div>""",
    """<div style={{ width:26, height:26, borderRadius:'50%', background:challenger.color,
                display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff', overflow:'hidden' }}>
                {challenger.img ? <img src={challenger.img} style={{ width:26, height:26, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:11, color:'#fff' }}>{challenger.name.charAt(0).toUpperCase()}</span>}
              </div>""",
    "Erem flipping challenger 26px"
)

# ── 14. Kopapir (Ring of Fire) current player 34px ───────────────────────────
replace_once(
    """<div style={{ width:34, height:34, borderRadius:'50%', background:currentPlayer.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', flexShrink:0 }}>
            {currentPlayer.name.charAt(0).toUpperCase()}
          </div>""",
    """<div style={{ width:34, height:34, borderRadius:'50%', background:currentPlayer.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', flexShrink:0, overflow:'hidden' }}>
            {currentPlayer.img ? <img src={currentPlayer.img} style={{ width:34, height:34, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>{currentPlayer.name.charAt(0).toUpperCase()}</span>}
          </div>""",
    "Kopapir currentPlayer 34px"
)

# ── 15. Ticktak current player 36px ──────────────────────────────────────────
replace_once(
    """<div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.mint, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
              {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
            </div>""",
    """<div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.mint, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0, overflow:'hidden' }}>
              {currentPlayer?.img ? <img src={currentPlayer.img} style={{ width:36, height:36, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff' }}>{(currentPlayer?.name||'?').charAt(0).toUpperCase()}</span>}
            </div>""",
    "Ticktak currentPlayer 36px"
)

# ── 16. Ticktak loser select 34px ─────────────────────────────────────────────
replace_once(
    """<div style={{ width:34, height:34, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', flexShrink:0 }}>
                {p.name.charAt(0).toUpperCase()}
              </div>""",
    """<div style={{ width:34, height:34, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                {p.img ? <img src={p.img} style={{ width:34, height:34, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}
              </div>""",
    "Ticktak loser select 34px"
)

# ── 17. Kategoria current player (inkSoft bg) 36px ───────────────────────────
replace_once(
    """<div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.ink, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0 }}>
          {(currentPlayer?.name||'?').charAt(0).toUpperCase()}
        </div>""",
    """<div style={{ width:36, height:36, borderRadius:'50%', background:currentPlayer?.color||T.ink, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff', flexShrink:0, overflow:'hidden' }}>
          {currentPlayer?.img ? <img src={currentPlayer.img} style={{ width:36, height:36, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:700, fontSize:15, color:'#fff' }}>{(currentPlayer?.name||'?').charAt(0).toUpperCase()}</span>}
        </div>""",
    "Kategoria currentPlayer 36px"
)

# ── 18. Anagramma player list (cnt=mistakes, 30px) ───────────────────────────
# Two similar patterns in different game functions - handle both
# First one (Anagramma): border and background references 'mistakes' differently
# Use context: "removeMistake(p.id)} disabled={cnt===0}"
replace_once(
    """<div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0 }}>
                {p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:13, color: selected ? T.coral : T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
              <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
                <button onClick={() => removeMistake(p.id)} disabled={cnt===0}""",
    """<div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                {p.img ? <img src={p.img} style={{ width:30, height:30, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}
              </div>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:13, color: selected ? T.coral : T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
              <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
                <button onClick={() => removeMistake(p.id)} disabled={cnt===0}""",
    "Anagramma player 30px (cnt===0)"
)

# Second one (Hajime): same pattern but spaces differ in disabled
replace_once(
    """<div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0 }}>
                {p.name.charAt(0).toUpperCase()}
              </div>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:13, color: selected ? T.coral : T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
              <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
                <button onClick={() => removeMistake(p.id)} disabled={cnt === 0}""",
    """<div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0, overflow:'hidden' }}>
                {p.img ? <img src={p.img} style={{ width:30, height:30, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}
              </div>
              <div style={{ flex:1, fontFamily:T.font, fontWeight:700, fontSize:13, color: selected ? T.coral : T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{p.name}</div>
              <div style={{ display:'flex', alignItems:'center', gap:5, flexShrink:0 }}>
                <button onClick={() => removeMistake(p.id)} disabled={cnt === 0}""",
    "Hajime player 30px (cnt === 0)"
)

# ── 19. Szerencse (gift game) player list 36px ────────────────────────────────
replace_once(
    """<div style={{width:36,height:36,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0}}>
                  {(p.name||'?').charAt(0).toUpperCase()}
                </div>""",
    """<div style={{width:36,height:36,borderRadius:'50%',background:p.color,display:'grid',placeItems:'center',fontFamily:T.font,fontWeight:900,fontSize:15,color:'#fff',flexShrink:0,overflow:'hidden'}}>
                  {p.img ? <img src={p.img} style={{ width:36, height:36, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff' }}>{(p.name||'?').charAt(0).toUpperCase()}</span>}
                </div>""",
    "Szerencse player 36px"
)

# ── 20. Loverseny csapat losers 44px ─────────────────────────────────────────
replace_once(
    """<div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>
                    {p.name.charAt(0).toUpperCase()}
                  </div>
                  <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:sel?T.coral:T.ink }}>""",
    """<div style={{ width:44, height:44, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff', overflow:'hidden' }}>
                    {p.img ? <img src={p.img} style={{ width:44, height:44, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:'#fff' }}>{p.name.charAt(0).toUpperCase()}</span>}
                  </div>
                  <div style={{ fontFamily:T.font, fontWeight:600, fontSize:12, color:sel?T.coral:T.ink }}>""",
    "Loverseny csapat losers 44px"
)

# ── 21. Soha sem (IgazHamis?) result display 38px ────────────────────────────
replace_once(
    """<div style={{ width:38, height:38, borderRadius:'50%', background: p?.color||T.mint,
                  display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>
                  {(p?.name||'?').charAt(0).toUpperCase()}
                </div>""",
    """<div style={{ width:38, height:38, borderRadius:'50%', background: p?.color||T.mint,
                  display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff', overflow:'hidden' }}>
                  {p?.img ? <img src={p.img} style={{ width:38, height:38, objectFit:'cover' }} /> : <span style={{ fontFamily:T.font, fontWeight:900, fontSize:16, color:'#fff' }}>{(p?.name||'?').charAt(0).toUpperCase()}</span>}
                </div>""",
    "Result display 38px"
)

# ── Version bump ──────────────────────────────────────────────────────────────
old_ver = "const APP_VERSION = 'v9.638';"
new_ver = "const APP_VERSION = 'v9.639';"
if old_ver not in src:
    print(f'MISSING version string: {old_ver}')
    sys.exit(1)
src = src.replace(old_ver, new_ver, 1)
print("OK: version bump 9.638 → 9.639")

assert src != orig, "No changes made!"

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print("\nAll patches applied successfully.")
