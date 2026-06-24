#!/usr/bin/env python3
"""
v9.597 — Avatar fix #2:
1. Profil fejléc ikon: avatar kép megjelenítés kiválasztott profilnál
2. Avatar picker border: outline -> box-shadow (nem vágódik le)
3. Session restore: avatarId/img visszatöltés PRESET_PLAYERS-ből
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.596') >= 1
html = html.replace('v9.596', 'v9.597', 1)

# ── 1. Profil fejléc: avatar kép ha ki van választva ────────────────────────
OLD_HEADER_ICON = """                  <div style={{ width:32, height:32, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', flexShrink:0 }}>
                    <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>
                  </div>"""
NEW_HEADER_ICON = """                  <div style={{ width:32, height:32, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', flexShrink:0, overflow:'hidden' }}>
                    {player.img ? <img src={player.img} style={{ width:32, height:32, objectFit:'cover' }} /> : <svg width="17" height="17" viewBox="0 0 24 24" fill="none"><circle cx="12" cy="8" r="4" fill="#fff"/><path d="M4 20c1.5-4 4-6 8-6s6.5 2 8 6" stroke="#fff" strokeWidth="2.5" strokeLinecap="round"/></svg>}
                  </div>"""
assert html.count(OLD_HEADER_ICON) == 1, f"header icon: {html.count(OLD_HEADER_ICON)}"
html = html.replace(OLD_HEADER_ICON, NEW_HEADER_ICON, 1)

# ── 2. Avatar picker: outline -> box-shadow (nem vágódik le) ─────────────────
OLD_AVATAR_BTN = """                      outline: active ? '3px solid '+T.ink : '3px solid transparent',
                      outlineOffset:'2px',
                      transform: active ? 'scale(1.1)' : 'scale(1)',
                      transition:'all .15s',
                      boxShadow: active ? ('0 4px 12px '+av.color+'99') : T.shadow,"""
NEW_AVATAR_BTN = """                      boxShadow: active ? ('0 0 0 2px '+T.ink+', 0 4px 12px '+av.color+'99') : T.shadow,
                      transform: active ? 'scale(1.08)' : 'scale(1)',
                      transition:'all .15s',"""
assert html.count(OLD_AVATAR_BTN) == 1, f"avatar btn: {html.count(OLD_AVATAR_BTN)}"
html = html.replace(OLD_AVATAR_BTN, NEW_AVATAR_BTN, 1)

# "A" gomb (nincs avatar) ugyanígy
OLD_A_BTN = """                  outline: !player.avatarId ? '3px solid '+T.inkMute : '3px solid transparent',
                  outlineOffset:'2px',
                  transform: !player.avatarId ? 'scale(1.1)' : 'scale(1)',
                  transition:'all .15s',"""
NEW_A_BTN = """                  boxShadow: !player.avatarId ? '0 0 0 2px '+T.inkMute : 'none',
                  transform: !player.avatarId ? 'scale(1.08)' : 'scale(1)',
                  transition:'all .15s',"""
assert html.count(OLD_A_BTN) == 1, f"a btn: {html.count(OLD_A_BTN)}"
html = html.replace(OLD_A_BTN, NEW_A_BTN, 1)

# ── 3. Session restore: avatar visszatöltés PRESET_PLAYERS-ből ───────────────
OLD_RESUME = """<button onClick={() => { const d = resumeOffer; setResumeOffer(null); setPlayers(d.players); setTurn(d.turn); setGameIdx(d.gameIdx); setRound(d.round); }}"""
NEW_RESUME = """<button onClick={() => { const d = resumeOffer; setResumeOffer(null); const restoredPlayers = (d.players||[]).map(p => { if (p.img) return p; const preset = PRESET_PLAYERS.find(x => x.id === p.profileId); const avatarId = p.avatarId || preset?.avatarId || null; const charAv = avatarId ? CHAR_AVATARS.find(a => a.id === avatarId) : null; return { ...p, avatarId, img: charAv ? charAv.img : null }; }); setPlayers(restoredPlayers); setTurn(d.turn); setGameIdx(d.gameIdx); setRound(d.round); }}"""
assert html.count(OLD_RESUME) == 1, f"resume: {html.count(OLD_RESUME)}"
html = html.replace(OLD_RESUME, NEW_RESUME, 1)

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
