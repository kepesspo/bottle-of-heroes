#!/usr/bin/env python3
"""
v9.587 — Illusztrált karakter avatarok:
- 5 PNG beágyazva base64-ként
- CHAR_AVATARS konstans (id, img, color)
- PlayerEditSheet: avatar képválasztó
- PlayerCard + footer pillek: img megjelenítés
- addPlayer: auto avatar kiosztás
"""
import base64, re

UPLOAD = '/root/.claude/uploads/ac37e0ea-6dd5-542a-9365-8ab2fbe09fab'

avatars = [
    ('char_girl',    f'{UPLOAD}/507804b8-avatar.png',   '#F4C57E'),  # sárga háttér
    ('char_old',     f'{UPLOAD}/1d846591-man_2.png',    '#4FC2A0'),  # zöld
    ('char_glasses', f'{UPLOAD}/1b3921b4-people.png',   '#3DA888'),  # zöld2
    ('char_asian',   f'{UPLOAD}/fe670fbd-avatar_3.png', '#5BA0DB'),  # kék
    ('char_curly',   f'{UPLOAD}/c7aaa68e-black.png',    '#F97316'),  # narancs
]

# Base64 encode each image
encoded = {}
for aid, path, color in avatars:
    with open(path, 'rb') as f:
        data = base64.b64encode(f.read()).decode('ascii')
    encoded[aid] = f'data:image/png;base64,{data}'
    print(f"{aid}: {len(data)} b64 chars")

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ── 1. Version bump ──────────────────────────────────────────────────────────
assert html.count('v9.586') >= 1
html = html.replace('v9.586', 'v9.587', 1)

# ── 2. Embed avatar images + CHAR_AVATARS const ──────────────────────────────
# Insert right before INITIAL_PLAYERS
OLD_INITIAL = "const INITIAL_PLAYERS = ["

char_avatars_js = "const CHAR_AVATARS = [\n"
for aid, path, color in avatars:
    b64 = encoded[aid]
    char_avatars_js += f"  {{ id:'{aid}', color:'{color}', img:'{b64}' }},\n"
char_avatars_js += "];\n\n"
char_avatars_js += "const INITIAL_PLAYERS = ["

assert html.count(OLD_INITIAL) == 1
html = html.replace(OLD_INITIAL, char_avatars_js, 1)

# ── 3. addPlayer: auto avatar ────────────────────────────────────────────────
OLD_ADD = """  const addPlayer = () => {
    const usedEmojis = new Set(players.map(p => p.emoji).filter(Boolean));
    const availEmoji = AVATAR_EMOJIS.find(a => !usedEmojis.has(a.emoji));
    const color = availEmoji ? availEmoji.color : (PLAYER_COLORS.find(c => !new Set(players.map(p=>p.color)).has(c)) || PLAYER_COLORS[0]);
    const emoji = availEmoji ? availEmoji.emoji : null;
    const np = { id:'p'+Date.now(), name:`Játékos ${players.length + 1}`, color, drinks:0, points:0, img:null, emoji };
    setPlayers([...players, np]);
    setEditing(np.id);
  };"""
NEW_ADD = """  const addPlayer = () => {
    const usedImgs = new Set(players.map(p => p.avatarId).filter(Boolean));
    const availChar = CHAR_AVATARS.find(a => !usedImgs.has(a.id));
    const color = availChar ? availChar.color : (PLAYER_COLORS.find(c => !new Set(players.map(p=>p.color)).has(c)) || PLAYER_COLORS[0]);
    const avatarId = availChar ? availChar.id : null;
    const img = availChar ? availChar.img : null;
    const np = { id:'p'+Date.now(), name:`Játékos ${players.length + 1}`, color, drinks:0, points:0, img, avatarId };
    setPlayers([...players, np]);
    setEditing(np.id);
  };"""
assert html.count(OLD_ADD) == 1
html = html.replace(OLD_ADD, NEW_ADD, 1)

# ── 4. PlayerCard: img already handled, fix circle overflow ─────────────────
# Existing code: {p.img ? <img ...> : p.emoji ? ... : Icon.user}
# Now avatarId sets p.img directly, so display is automatic.
# Just ensure the img has borderRadius 50% (already does).

# ── 5. PlayerEditSheet: replace emoji picker with char avatar picker ──────────
OLD_EMOJI_PICKER = """          {/* Emoji avatar picker */}
          <div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.10em', marginBottom:8 }}>Avatar</div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(6,1fr)', gap:6 }}>
              {AVATAR_EMOJIS.map(function(av) {
                const active = player.emoji === av.emoji;
                return (
                  <button key={av.emoji} onClick={() => onChange({ emoji:av.emoji, color:av.color })} style={{
                    aspectRatio:'1/1', borderRadius:12, border:'none', cursor:'pointer',
                    background: active ? av.color+'28' : T.surfaceMuted,
                    outline: active ? ('2.5px solid '+av.color) : '2px solid transparent',
                    fontSize:20, display:'grid', placeItems:'center',
                    transition:'all .12s', transform: active ? 'scale(1.14)' : 'scale(1)',
                    padding:0,
                  }}>{av.emoji}</button>
                );
              })}
              <button onClick={() => onChange({ emoji:null })} style={{
                aspectRatio:'1/1', borderRadius:12, border:'none', cursor:'pointer',
                background: !player.emoji ? T.inkMute+'22' : T.surfaceMuted,
                outline: !player.emoji ? ('2.5px solid '+T.inkMute) : '2px solid transparent',
                fontSize:14, color:T.inkMute, display:'grid', placeItems:'center',
                transition:'all .12s', fontFamily:T.font, fontWeight:800, padding:0,
              }}>A</button>
            </div>
          </div>"""
NEW_CHAR_PICKER = """          {/* Karakter avatar picker */}
          <div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.10em', marginBottom:8 }}>Avatar</div>
            <div style={{ display:'flex', gap:8 }}>
              {CHAR_AVATARS.map(function(av) {
                const active = player.avatarId === av.id;
                return (
                  <button key={av.id} onClick={() => onChange({ avatarId:av.id, img:av.img, color:av.color })} style={{
                    width:52, height:52, borderRadius:'50%', border:'none', cursor:'pointer', padding:0,
                    outline: active ? ('3px solid '+T.ink) : '3px solid transparent',
                    outlineOffset: '2px',
                    transform: active ? 'scale(1.1)' : 'scale(1)',
                    transition:'all .15s', flexShrink:0, overflow:'hidden',
                    boxShadow: active ? ('0 4px 14px '+av.color+'88') : T.shadow,
                  }}>
                    <img src={av.img} style={{ width:52, height:52, objectFit:'cover', borderRadius:'50%', display:'block' }} />
                  </button>
                );
              })}
              {/* "Nincs" gomb */}
              <button onClick={() => onChange({ avatarId:null, img:null })} style={{
                width:52, height:52, borderRadius:'50%', border:'none', cursor:'pointer', padding:0,
                background: !player.avatarId ? T.inkMute+'22' : T.surfaceMuted,
                outline: !player.avatarId ? ('3px solid '+T.inkMute) : '3px solid transparent',
                outlineOffset: '2px',
                transform: !player.avatarId ? 'scale(1.1)' : 'scale(1)',
                transition:'all .15s', flexShrink:0, display:'grid', placeItems:'center',
                fontFamily:T.font, fontWeight:900, fontSize:16, color:T.inkSoft,
              }}>A</button>
            </div>
          </div>"""
assert html.count(OLD_EMOJI_PICKER) == 1, f"emoji picker: {html.count(OLD_EMOJI_PICKER)}"
html = html.replace(OLD_EMOJI_PICKER, NEW_CHAR_PICKER, 1)

# ── 6. PlayerEditSheet: circle preview shows img ─────────────────────────────
# Already handled by existing: player.img ? <img...> : ...
# Just fix the emoji fallback to show avatar letter cleanly
OLD_EDIT_EMOJI = """              {player.img ? <img src={player.img} style={{ width:48, height:48, objectFit:'cover', borderRadius:'50%' }} />
                : player.emoji ? <span style={{ fontSize:26, lineHeight:1 }}>{player.emoji}</span>
                : (
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                  <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}"""
NEW_EDIT_IMG = """              {player.img
                ? <img src={player.img} style={{ width:48, height:48, objectFit:'cover', borderRadius:'50%' }} />
                : <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                    <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                    <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                  </svg>}"""
assert html.count(OLD_EDIT_EMOJI) == 1
html = html.replace(OLD_EDIT_EMOJI, NEW_EDIT_IMG, 1)

# ── 7. Footer pills: show img if set ─────────────────────────────────────────
# Pair pill (line ~49728): 32px circle with first letter
OLD_PAIR_PILL = '<div style={{ position:\'absolute\', left:0, top:0, width:32, height:32, borderRadius:\'50%\', background:currentPlayer.color, display:\'grid\', placeItems:\'center\', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:13, color:\'#fff\', border:`2px solid ${T.surface}`, zIndex:2 }}>{currentPlayer.name.charAt(0).toUpperCase()}</div>'
NEW_PAIR_PILL = '<div style={{ position:\'absolute\', left:0, top:0, width:32, height:32, borderRadius:\'50%\', background:currentPlayer.color, display:\'grid\', placeItems:\'center\', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:13, color:\'#fff\', border:`2px solid ${T.surface}`, zIndex:2, overflow:\'hidden\' }}>{currentPlayer.img ? <img src={currentPlayer.img} style={{width:32,height:32,objectFit:\'cover\'}} /> : currentPlayer.name.charAt(0).toUpperCase()}</div>'
assert html.count(OLD_PAIR_PILL) == 1, f"pair pill: {html.count(OLD_PAIR_PILL)}"
html = html.replace(OLD_PAIR_PILL, NEW_PAIR_PILL, 1)

# Single player pill (line ~49738): 32px circle
OLD_SOLO_PILL = "display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize: currentPlayer.emoji ? 18 : 15, color:'#fff', boxShadow: scorePulse ? `0 0 0 4px ${currentPlayer.color}44` : `0 0 0 2px ${currentPlayer.color}30`, transition:'box-shadow .3s', flexShrink:0 }}>{playerAvatar(currentPlayer)}</div>"
NEW_SOLO_PILL = "display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:14, color:'#fff', boxShadow: scorePulse ? `0 0 0 4px ${currentPlayer.color}44` : `0 0 0 2px ${currentPlayer.color}30`, transition:'box-shadow .3s', flexShrink:0, overflow:'hidden' }}>{currentPlayer.img ? <img src={currentPlayer.img} style={{width:32,height:32,objectFit:'cover',borderRadius:'50%'}} /> : currentPlayer.name.charAt(0).toUpperCase()}</div>"
assert html.count(OLD_SOLO_PILL) == 1, f"solo pill: {html.count(OLD_SOLO_PILL)}"
html = html.replace(OLD_SOLO_PILL, NEW_SOLO_PILL, 1)

assert len(html) > original_len
assert html.count('const CHAR_AVATARS') == 1
print(f"\nTotal: {len(html) - original_len:+d} chars")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
