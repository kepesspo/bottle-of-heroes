#!/usr/bin/env python3
"""
v9.586 — Emoji avatar rendszer:
- AVATAR_EMOJIS konstans (30 emoji + auto-szín)
- playerAvatar(p) helper → emoji ha van, egyébként betű
- addPlayer: véletlenszerű emoji
- PlayerEditSheet: emoji picker szekció
- PlayerCard: emoji megjelenítés
- Összes charAt(0) csere playerAvatar()-ra (regex)
"""
import re

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

original_len = len(html)

# ── 1. Version bump ──────────────────────────────────────────────────────────
assert html.count('v9.585') >= 1
html = html.replace('v9.585', 'v9.586', 1)

# ── 2. AVATAR_EMOJIS + playerAvatar helper — after PLAYER_COLORS ─────────────
OLD_COLORS_END = """const INITIAL_PLAYERS = ["""
AVATAR_INSERT = """const AVATAR_EMOJIS = [
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

// Returns emoji (if set) or first letter — used everywhere a player circle shows text
const playerAvatar = p => p && p.emoji ? p.emoji : ((p && p.name) ? p.name.charAt(0).toUpperCase() : '?');

const INITIAL_PLAYERS = ["""
assert html.count(OLD_COLORS_END) == 1
html = html.replace(OLD_COLORS_END, AVATAR_INSERT, 1)

# ── 3. addPlayer: assign random emoji ────────────────────────────────────────
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
OLD_CARD_AVATAR = """      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
        {p.img ? <img src={p.img} style={{ width:56, height:56, objectFit:'cover', borderRadius:'50%' }} /> : Icon.user('#fff')}
      </div>"""
NEW_CARD_AVATAR = """      <div style={{ width:56, height:56, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', overflow:'hidden', flexShrink:0 }}>
        {p.img ? <img src={p.img} style={{ width:56, height:56, objectFit:'cover', borderRadius:'50%' }} />
          : p.emoji ? <span style={{ fontSize:28, lineHeight:1, userSelect:'none' }}>{p.emoji}</span>
          : Icon.user('#fff')}
      </div>"""
assert html.count(OLD_CARD_AVATAR) == 1
html = html.replace(OLD_CARD_AVATAR, NEW_CARD_AVATAR, 1)

# ── 5. PlayerEditSheet: show emoji in name row circle ────────────────────────
OLD_EDIT_CIRCLE = """            <div style={{ width:48, height:48, borderRadius:'50%', background:player.color, flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
              {player.img ? <img src={player.img} style={{ width:48, height:48, objectFit:'cover', borderRadius:'50%' }} /> : (
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                  <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </div>"""
NEW_EDIT_CIRCLE = """            <div style={{ width:48, height:48, borderRadius:'50%', background:player.color, flexShrink:0, display:'grid', placeItems:'center', overflow:'hidden' }}>
              {player.img ? <img src={player.img} style={{ width:48, height:48, objectFit:'cover', borderRadius:'50%' }} />
                : player.emoji ? <span style={{ fontSize:26, lineHeight:1 }}>{player.emoji}</span>
                : (
                <svg width="26" height="26" viewBox="0 0 24 24" fill="none">
                  <circle cx="12" cy="8" r="3.5" stroke="#fff" strokeWidth="2"/>
                  <path d="M5 20c1.5-3.5 4-5 7-5s5.5 1.5 7 5" stroke="#fff" strokeWidth="2" strokeLinecap="round"/>
                </svg>
              )}
            </div>"""
assert html.count(OLD_EDIT_CIRCLE) == 1
html = html.replace(OLD_EDIT_CIRCLE, NEW_EDIT_CIRCLE, 1)

# ── 6. PlayerEditSheet: add emoji picker above name input ────────────────────
OLD_NAME_ROW = """          {/* Név input */}
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>"""
NEW_NAME_ROW = """          {/* Emoji avatar választó */}
          <div>
            <div style={{ fontFamily:T.font, fontWeight:700, fontSize:11, color:T.inkMute, textTransform:'uppercase', letterSpacing:'0.10em', marginBottom:8 }}>Avatar</div>
            <div style={{ display:'grid', gridTemplateColumns:'repeat(6,1fr)', gap:6 }}>
              {AVATAR_EMOJIS.map(({ emoji, color }) => {
                const active = player.emoji === emoji;
                return (
                  <button key={emoji} onClick={() => onChange({ emoji, color })} style={{
                    aspectRatio:'1/1', borderRadius:12, border:'none', cursor:'pointer',
                    background: active ? color+'30' : T.surfaceMuted,
                    outline: active ? `2.5px solid ${color}` : '2px solid transparent',
                    fontSize:22, display:'grid', placeItems:'center',
                    transition:'all .12s', transform: active ? 'scale(1.15)' : 'scale(1)',
                  }}>{emoji}</button>
                );
              })}
              {/* "Nincs" gomb */}
              <button onClick={() => onChange({ emoji: null })} style={{
                aspectRatio:'1/1', borderRadius:12, border:'none', cursor:'pointer',
                background: !player.emoji ? T.inkMute+'22' : T.surfaceMuted,
                outline: !player.emoji ? `2.5px solid ${T.inkMute}` : '2px solid transparent',
                fontSize:14, color:T.inkMute, display:'grid', placeItems:'center',
                transition:'all .12s',
              }}>A</button>
            </div>
          </div>

          {/* Név input */}
          <div style={{ display:'flex', alignItems:'center', gap:12 }}>"""
assert html.count(OLD_NAME_ROW) == 1
html = html.replace(OLD_NAME_ROW, NEW_NAME_ROW, 1)

# ── 7. Global replace of .name.charAt(0).toUpperCase() patterns ──────────────
# Pattern: {varname.name.charAt(0).toUpperCase()}  →  {playerAvatar(varname)}
# Also:    {(varname.name||'?').charAt(0).toUpperCase()}  →  {playerAvatar(varname)}
# Also:    {(varname?.name||'?').charAt(0).toUpperCase()} →  {playerAvatar(varname)}

count_before = len(re.findall(r'\.name(?:\|\|\'.\')?\)?.charAt\(0\)\.toUpperCase\(\)', html))
print(f"Found {count_before} charAt(0) patterns to replace")

# Pattern 1: varname.name.charAt(0).toUpperCase()
html = re.sub(
    r'\{(\w+)\.name\.charAt\(0\)\.toUpperCase\(\)\}',
    lambda m: '{playerAvatar(' + m.group(1) + ')}',
    html
)

# Pattern 2: {(varname.name||'?').charAt(0).toUpperCase()}
html = re.sub(
    r"\{\((\w+)\.name\|\|'\.'\)\.charAt\(0\)\.toUpperCase\(\)\}",
    lambda m: '{playerAvatar(' + m.group(1) + ')}',
    html
)
# Pattern 3: {(varname?.name||'?').charAt(0).toUpperCase()}
html = re.sub(
    r"\{\((\w+)\?\.name\|+\|'[?]'\)\.charAt\(0\)\.toUpperCase\(\)\}",
    lambda m: '{playerAvatar(' + m.group(1) + ')}',
    html
)

# Manual fixes for remaining patterns with quotes
# {(p.name||'?').charAt(0).toUpperCase()} etc with actual '?'
html = re.sub(
    r"\{(\([^)]+\))\.charAt\(0\)\.toUpperCase\(\)\}",
    lambda m: '{(' + m.group(1) + ".charAt(0).toUpperCase())}",
    html
)

# Simpler broad replace: any remaining .name.charAt(0).toUpperCase() in JSX
# These are in the format: fontSize:X, color:'#fff' }}>{varname.name.charAt(0).toUpperCase()}</div>
html = re.sub(
    r">(\w+)\.name\.charAt\(0\)\.toUpperCase\(\)<",
    lambda m: '>{playerAvatar(' + m.group(1) + ')}<',
    html
)
html = re.sub(
    r">\((\w+)\.name\|\|'[^']+'\)\.charAt\(0\)\.toUpperCase\(\)<",
    lambda m: '>{playerAvatar(' + m.group(1) + ')}<',
    html
)
html = re.sub(
    r">\((\w+)\?\.name\|\|'[^']+'\)\.charAt\(0\)\.toUpperCase\(\)<",
    lambda m: '>{playerAvatar(' + m.group(1) + ')}<',
    html
)

count_after = len(re.findall(r'\.name(?:\|\|\'.\')?\)?.charAt\(0\)\.toUpperCase\(\)', html))
print(f"Remaining charAt(0) patterns: {count_after}")

assert len(html) > original_len
print(f"Total change: {len(html) - original_len:+d} chars")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written.")
