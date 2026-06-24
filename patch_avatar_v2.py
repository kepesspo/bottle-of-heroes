#!/usr/bin/env python3
"""
v9.586b — Emoji avatar rendszer (biztonságos verzió)
Csak a PlayerEditSheet és PlayerCard érintett — NEM regex replace minden charAt-re.
playerAvatar() helper hozzáadva, de az existing charAt hívások érintetlenek maradnak.
Csak a releváns helyeken (PlayerCard avatar, PlayScreen pill, EditSheet circle) frissül.
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ── 1. Version bump ──────────────────────────────────────────────────────────
assert html.count('v9.585') >= 1
html = html.replace('v9.585', 'v9.586', 1)

# ── 2. AVATAR_EMOJIS + playerAvatar helper ───────────────────────────────────
OLD_INITIAL = "const INITIAL_PLAYERS = ["
NEW_INITIAL = """const AVATAR_EMOJIS = [
  { emoji:'🐻', color:'#C4956A' }, { emoji:'🦊', color:'#F97316' }, { emoji:'🐱', color:'#F59E0B' },
  { emoji:'🐶', color:'#92400E' }, { emoji:'🐸', color:'#84CC16' }, { emoji:'🐧', color:'#0EA5E9' },
  { emoji:'🦁', color:'#D97706' }, { emoji:'🐺', color:'#64748B' }, { emoji:'🦝', color:'#8B5CF6' },
  { emoji:'🐭', color:'#EC4899' }, { emoji:'🐰', color:'#E879F9' }, { emoji:'🦄', color:'#A855F7' },
  { emoji:'🐯', color:'#EF4444' }, { emoji:'🐮', color:'#14B8A6' }, { emoji:'🐷', color:'#FB7185' },
  { emoji:'🦈', color:'#2563EB' }, { emoji:'🐬', color:'#06B6D4' }, { emoji:'🦋', color:'#7C3AED' },
  { emoji:'🔥', color:'#EA580C' }, { emoji:'⚡', color:'#FBBF24' }, { emoji:'🌈', color:'#4FC2A0' },
  { emoji:'👑', color:'#D97706' }, { emoji:'💎', color:'#38BDF8' }, { emoji:'🎮', color:'#6366F1' },
  { emoji:'🍺', color:'#F59E0B' }, { emoji:'🎯', color:'#EF4444' }, { emoji:'🎸', color:'#8B5CF6' },
  { emoji:'🚀', color:'#3B82F6' }, { emoji:'🎲', color:'#10B981' }, { emoji:'🌙', color:'#6366F1' },
];
// Returns emoji if set, otherwise first letter of name
const playerAvatar = p => (p && p.emoji) ? p.emoji : ((p && p.name) ? p.name.charAt(0).toUpperCase() : '?');

const INITIAL_PLAYERS = ["""

assert html.count(OLD_INITIAL) == 1, f"INITIAL_PLAYERS count: {html.count(OLD_INITIAL)}"
html = html.replace(OLD_INITIAL, NEW_INITIAL, 1)

# ── 3. addPlayer: auto emoji assign ─────────────────────────────────────────
OLD_ADD = """  const addPlayer = () => {
    const used = new Set(players.map(p => p.color));
    const color = PLAYER_COLORS.find(c => !used.has(c)) || PLAYER_COLORS[0];
    const np = { id:'p'+Date.now(), name:`Játékos ${players.length + 1}`, color, drinks:0, points:0, img:null };
    setPlayers([...players, np]);
    setEditing(np.id);
  };"""
NEW_ADD = """  const addPlayer = () => {
    const usedEmojis = new Set(players.map(p => p.emoji).filter(Boolean));
    const availEmoji = AVATAR_EMOJIS.find(a => !usedEmojis.has(a.emoji));
    const color = availEmoji ? availEmoji.color : (PLAYER_COLORS.find(c => !new Set(players.map(p=>p.color)).has(c)) || PLAYER_COLORS[0]);
    const emoji = availEmoji ? availEmoji.emoji : null;
    const np = { id:'p'+Date.now(), name:`Játékos ${players.length + 1}`, color, drinks:0, points:0, img:null, emoji };
    setPlayers([...players, np]);
    setEditing(np.id);
  };"""
assert html.count(OLD_ADD) == 1
html = html.replace(OLD_ADD, NEW_ADD, 1)

# ── 4. PlayerCard: show emoji in avatar circle ───────────────────────────────
OLD_CARD_AVA = "      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>\n        {p.img ? <img src={p.img} style={{ width:56, height:56, objectFit:'cover', borderRadius:'50%' }} /> : Icon.user('#fff')}\n      </div>"
NEW_CARD_AVA = "      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>\n        {p.img ? <img src={p.img} style={{ width:56, height:56, objectFit:'cover', borderRadius:'50%' }} />\n          : p.emoji ? <span style={{ fontSize:28, lineHeight:1, userSelect:'none' }}>{p.emoji}</span>\n          : Icon.user('#fff')}\n      </div>"
assert html.count(OLD_CARD_AVA) == 1
html = html.replace(OLD_CARD_AVA, NEW_CARD_AVA, 1)

# ── 5. PlayerEditSheet: name circle shows emoji ──────────────────────────────
OLD_EDIT_CIRC = """            <div style={{ width:48, height:48, borderRadius:'50%', background:player.color, flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
              {player.img ? <img src={player.img} style={{ width:48, height:48, objectFit:'cover', borderRadius:'50%' }} /> : (
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                  <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </div>"""
NEW_EDIT_CIRC = """            <div style={{ width:48, height:48, borderRadius:'50%', background:player.color, flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
              {player.img ? <img src={player.img} style={{ width:48, height:48, objectFit:'cover', borderRadius:'50%' }} />
                : player.emoji ? <span style={{ fontSize:26, lineHeight:1 }}>{player.emoji}</span>
                : (
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                  <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </div>"""
assert html.count(OLD_EDIT_CIRC) == 1
html = html.replace(OLD_EDIT_CIRC, NEW_EDIT_CIRC, 1)

# ── 6. PlayerEditSheet: emoji picker section ─────────────────────────────────
OLD_NAME_ROW = "          {/* Név input */}\n          <div style={{ display:'flex', alignItems:'center', gap:12 }}>"
NEW_NAME_ROW = """          {/* Emoji avatar picker */}
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
          </div>

          {/* Név input */}
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>"""
assert html.count(OLD_NAME_ROW) == 1
html = html.replace(OLD_NAME_ROW, NEW_NAME_ROW, 1)

# ── 7. PlayScreen single-player pill: show emoji ─────────────────────────────
# Line ~49690: the single player circle in footer pill
OLD_PILL_SINGLE = "display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:15, color:'#fff', boxShadow: scorePulse ? `0 0 0 4px ${currentPlayer.color}44` : `0 0 0 2px ${currentPlayer.color}30`, transition:'box-shadow .3s', flexShrink:0 }}>{currentPlayer.name.charAt(0).toUpperCase()||'?'}</div>"
NEW_PILL_SINGLE = "display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:T.weightDisplay, fontSize: currentPlayer.emoji ? 18 : 15, color:'#fff', boxShadow: scorePulse ? `0 0 0 4px ${currentPlayer.color}44` : `0 0 0 2px ${currentPlayer.color}30`, transition:'box-shadow .3s', flexShrink:0 }}>{playerAvatar(currentPlayer)}</div>"
assert html.count(OLD_PILL_SINGLE) == 1, f"pill single: {html.count(OLD_PILL_SINGLE)}"
html = html.replace(OLD_PILL_SINGLE, NEW_PILL_SINGLE, 1)

assert len(html) > original_len
print(f"Done. {len(html) - original_len:+d} chars")

# Verify no broken patterns
assert html.count('const AVATAR_EMOJIS') == 1
assert html.count('const playerAvatar') == 1
print("Assertions passed.")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written.")
