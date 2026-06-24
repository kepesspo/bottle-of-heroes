#!/usr/bin/env python3
"""
v9.589 — Illusztrált karakter avatarok (clean, v9.585 alapon)
- CHAR_AVATARS konstans (10 db)
- addPlayer: auto avatar
- PlayerCard: img megjelenítés
- PlayerEditSheet: karakter picker
- Footer pill: img megjelenítés
- SW cache bust: query param
"""
import base64

UPLOAD = '/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab'

all_avatars = [
    ('char_girl',    f'{UPLOAD}/507804b8-avatar.png',   '#F4C57E'),
    ('char_old',     f'{UPLOAD}/1d846591-man_2.png',    '#4FC2A0'),
    ('char_glasses', f'{UPLOAD}/1b3921b4-people.png',   '#3DA888'),
    ('char_asian',   f'{UPLOAD}/fe670fbd-avatar_3.png', '#5BA0DB'),
    ('char_curly',   f'{UPLOAD}/c7aaa68e-black.png',    '#F97316'),
    ('char_hijab',   f'{UPLOAD}/561bbb5f-avatar_4.png', '#FBBF24'),
    ('char_ginger',  f'{UPLOAD}/89fa9324-man_3.png',    '#38BDF8'),
    ('char_bun',     f'{UPLOAD}/05afdd50-avatar_2.png', '#FB923C'),
    ('char_beard',   f'{UPLOAD}/249212ef-person.png',   '#E985B8'),
    ('char_biz',     f'{UPLOAD}/172393a1-man.png',      '#14B8A6'),
]

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.585') >= 1
html = html.replace('v9.585', 'v9.589', 1)

# ── 1. Build CHAR_AVATARS JS ─────────────────────────────────────────────────
char_js = "const CHAR_AVATARS = [\n"
for aid, path, color in all_avatars:
    with open(path, 'rb') as f:
        b64 = base64.b64encode(f.read()).decode('ascii')
    char_js += f"  {{ id:'{aid}', color:'{color}', img:'data:image/png;base64,{b64}' }},\n"
    print(f"  {aid}: {len(b64)} b64 chars")
char_js += "];\n\n"

# Insert before INITIAL_PLAYERS
OLD = "const INITIAL_PLAYERS = ["
assert html.count(OLD) == 1
html = html.replace(OLD, char_js + OLD, 1)

# ── 2. addPlayer: auto avatar ────────────────────────────────────────────────
OLD_ADD = """  const addPlayer = () => {
    const used = new Set(players.map(p => p.color));
    const color = PLAYER_COLORS.find(c => !used.has(c)) || PLAYER_COLORS[0];
    const np = { id:'p'+Date.now(), name:`Játékos ${players.length + 1}`, color, drinks:0, points:0, img:null };
    setPlayers([...players, np]);
    setEditing(np.id);
  };"""
NEW_ADD = """  const addPlayer = () => {
    const usedIds = new Set(players.map(p => p.avatarId).filter(Boolean));
    const availChar = CHAR_AVATARS.find(a => !usedIds.has(a.id));
    const color = availChar ? availChar.color : (PLAYER_COLORS.find(c => !new Set(players.map(p=>p.color)).has(c)) || PLAYER_COLORS[0]);
    const np = { id:'p'+Date.now(), name:`Játékos ${players.length + 1}`, color, drinks:0, points:0,
                 img: availChar ? availChar.img : null, avatarId: availChar ? availChar.id : null };
    setPlayers([...players, np]);
    setEditing(np.id);
  };"""
assert html.count(OLD_ADD) == 1
html = html.replace(OLD_ADD, NEW_ADD, 1)

# ── 3. PlayerCard: show img ──────────────────────────────────────────────────
OLD_CARD = "      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>\n        {p.img ? <img src={p.img} style={{ width:56, height:56, objectFit:'cover', borderRadius:'50%' }} /> : Icon.user('#fff')}\n      </div>"
# Already handles img — no change needed (img is set by addPlayer/selectProfile)

# ── 4. PlayerEditSheet: add avatar picker ────────────────────────────────────
OLD_NAME_ROW = "          {/* Név input */}\n          <div style={{ display:'flex', alignItems:'center', gap:12 }}>"
NEW_NAME_ROW = """          {/* Karakter választó */}
          <div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.10em', marginBottom:8 }}>Avatar</div>
            <div style={{ display:'flex', gap:8, flexWrap:'wrap' }}>
              {CHAR_AVATARS.map(function(av) {
                const active = player.avatarId === av.id;
                return (
                  <button key={av.id}
                    onClick={() => onChange({ avatarId:av.id, img:av.img, color:av.color })}
                    style={{
                      width:50, height:50, borderRadius:'50%', border:'none',
                      cursor:'pointer', padding:0, overflow:'hidden', flexShrink:0,
                      outline: active ? '3px solid '+T.ink : '3px solid transparent',
                      outlineOffset:'2px',
                      transform: active ? 'scale(1.1)' : 'scale(1)',
                      transition:'all .15s',
                      boxShadow: active ? ('0 4px 12px '+av.color+'99') : T.shadow,
                    }}>
                    <img src={av.img} style={{ width:50, height:50, objectFit:'cover', display:'block' }} />
                  </button>
                );
              })}
              <button
                onClick={() => onChange({ avatarId:null, img:null })}
                style={{
                  width:50, height:50, borderRadius:'50%', border:'none',
                  cursor:'pointer', flexShrink:0, display:'grid', placeItems:'center',
                  background: !player.avatarId ? T.inkMute+'28' : T.surfaceMuted,
                  outline: !player.avatarId ? '3px solid '+T.inkMute : '3px solid transparent',
                  outlineOffset:'2px',
                  transform: !player.avatarId ? 'scale(1.1)' : 'scale(1)',
                  transition:'all .15s',
                  fontFamily:T.font, fontWeight:900, fontSize:18, color:T.inkMute,
                }}>A</button>
            </div>
          </div>

          {/* Név input */}
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>"""
assert html.count(OLD_NAME_ROW) == 1
html = html.replace(OLD_NAME_ROW, NEW_NAME_ROW, 1)

# ── 5. Footer solo pill: show img ────────────────────────────────────────────
OLD_SOLO = "display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', boxShadow: scorePulse ? `0 0 0 4px ${currentPlayer.color}44` : `0 0 0 2px ${currentPlayer.color}30`, transition:'box-shadow .3s', flexShrink:0 }}>{currentPlayer.name.charAt(0).toUpperCase()||'?'}</div>"
NEW_SOLO = "display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:14, color:'#fff', boxShadow: scorePulse ? `0 0 0 4px ${currentPlayer.color}44` : `0 0 0 2px ${currentPlayer.color}30`, transition:'box-shadow .3s', flexShrink:0, overflow:'hidden' }}>{currentPlayer.img ? <img src={currentPlayer.img} style={{width:32,height:32,objectFit:'cover'}} /> : currentPlayer.name.charAt(0).toUpperCase()}</div>"
assert html.count(OLD_SOLO) == 1, f"solo: {html.count(OLD_SOLO)}"
html = html.replace(OLD_SOLO, NEW_SOLO, 1)

# ── 6. Footer pair pill: show img ────────────────────────────────────────────
OLD_PAIR = "display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:13, color:'#fff', border:`2px solid ${T.surface}`, zIndex:2 }}>{currentPlayer.name.charAt(0).toUpperCase()}</div>"
NEW_PAIR = "display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:13, color:'#fff', border:`2px solid ${T.surface}`, zIndex:2, overflow:'hidden' }}>{currentPlayer.img ? <img src={currentPlayer.img} style={{width:32,height:32,objectFit:'cover'}} /> : currentPlayer.name.charAt(0).toUpperCase()}</div>"
assert html.count(OLD_PAIR) == 1, f"pair: {html.count(OLD_PAIR)}"
html = html.replace(OLD_PAIR, NEW_PAIR, 1)

# ── 7. SW cache bust: update sw.js version comment in HTML ──────────────────
# Force service worker to update by bumping cache name in sw.js if exists
import os
if os.path.exists('sw.js'):
    with open('sw.js', 'r') as f:
        sw = f.read()
    import re
    sw = re.sub(r"'boh-v[\d.]+'", "'boh-v9.589'", sw)
    sw = re.sub(r'"boh-v[\d.]+"', '"boh-v9.589"', sw)
    with open('sw.js', 'w') as f:
        f.write(sw)
    print("sw.js cache version bumped")

print(f"\nFinal size: {len(html):,} chars")
assert html.count('const CHAR_AVATARS') == 1
assert html.count('avatarId') >= 3

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
