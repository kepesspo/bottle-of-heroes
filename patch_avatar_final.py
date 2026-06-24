#!/usr/bin/env python3
"""
v9.599 — Avatar fix végső:
1. PRESET_PLAYERS avatar átrendelés a referencia kép alapján
2. Állás tab (RR standings) — kép
3. EndScreen podium — kép
4. EndScreen stat kártyák — kép
5. EndScreen leaderboard lista — kép
6. EndScreen ital egység lista — kép
7. Beer Pong match játékos körök (p1, p2) — kép
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.598') >= 1
html = html.replace('v9.598', 'v9.599', 1)

# ── 1. PRESET_PLAYERS átrendelés ─────────────────────────────────────────────
OLD_PRESET = """const PRESET_PLAYERS = (() => {
  const av = id => { const a = CHAR_AVATARS.find(x => x.id === id); return a ? { avatarId: a.id, img: a.img } : {}; };
  return [
    { id:'preset_sere',   name:'Sere Bence',       nickname:'Sere',   color:'#4FC3A1', ...av('char_ginger')  },
    { id:'preset_kecsi',  name:'Kecskés Dániel',   nickname:'Kecsi',  color:'#F87171', ...av('char_beard')   },
    { id:'preset_luca',   name:'Monoki Luca',       nickname:'Luca',   color:'#F472B6', ...av('char_girl')    },
    { id:'preset_toth',   name:'Tóth Bence',        nickname:'Tóth',   color:'#60A5FA', ...av('char_biz')     },
    { id:'preset_mark',   name:'Szécsi Márk',       nickname:'Márk',   color:'#FBBF24', ...av('char_asian')   },
    { id:'preset_dani',   name:'Szentpáli Dániel',  nickname:'Dani',   color:'#A78BFA', ...av('char_glasses') },
    { id:'preset_kkk',    name:'Tóth Gergő',        nickname:'KKK',    color:'#34D399', ...av('char_curly')   },
    { id:'preset_vivi',   name:'Kiss Vivien',        nickname:'Vivi',   color:'#FB923C', ...av('char_bun')     },
    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#818CF8', ...av('char_old')     },
    { id:'preset_gyula',  name:'Németh Gyula',       nickname:'Gyula',  color:'#EF4444', ...av('char_beard')   },
    { id:'preset_bacsi',  name:'Bacsinszki Dániel',  nickname:'Bacsi',  color:'#F97316', ...av('char_glasses') },
    { id:'preset_bb',     name:'Bíró Bence',           nickname:'BB',     color:'#8B5CF6', ...av('char_ginger')  },
  ];
})();"""
NEW_PRESET = """const PRESET_PLAYERS = (() => {
  const av = id => { const a = CHAR_AVATARS.find(x => x.id === id); return a ? { avatarId: a.id, img: a.img } : {}; };
  return [
    { id:'preset_sere',   name:'Sere Bence',       nickname:'Sere',   color:'#F87171', ...av('char_longhair') },
    { id:'preset_kecsi',  name:'Kecskés Dániel',   nickname:'Kecsi',  color:'#22C55E', ...av('char_spiky')    },
    { id:'preset_luca',   name:'Monoki Luca',       nickname:'Luca',   color:'#F472B6', ...av('char_girl')     },
    { id:'preset_toth',   name:'Tóth Bence',        nickname:'Tóth',   color:'#10B981', ...av('char_bigbeard') },
    { id:'preset_mark',   name:'Szécsi Márk',       nickname:'Márk',   color:'#A78BFA', ...av('char_blond')    },
    { id:'preset_dani',   name:'Szentpáli Dániel',  nickname:'Dani',   color:'#34D399', ...av('char_necktie')  },
    { id:'preset_kkk',    name:'Tóth Gergő',        nickname:'KKK',    color:'#16A34A', ...av('char_shades')   },
    { id:'preset_vivi',   name:'Kiss Vivien',        nickname:'Vivi',   color:'#FB923C', ...av('char_bun')      },
    { id:'preset_balazs', name:'Molnár Balázs',     nickname:'Balázs', color:'#4FC2A0', ...av('char_old')      },
    { id:'preset_gyula',  name:'Németh Gyula',       nickname:'Gyula',  color:'#F59E0B', ...av('char_bald')     },
    { id:'preset_bacsi',  name:'Bacsinszki Dániel',  nickname:'Bacsi',  color:'#C026D3', ...av('char_curlboy')  },
    { id:'preset_bb',     name:'Bíró Bence',           nickname:'BB',     color:'#14B8A6', ...av('char_biz')      },
  ];
})();"""
assert html.count(OLD_PRESET) == 1, f"preset: {html.count(OLD_PRESET)}"
html = html.replace(OLD_PRESET, NEW_PRESET, 1)

# helper — inline img check
def img_or_letter(src, size, letter_expr):
    return f"{{{src} ? <img src={{{src}}} style={{{{width:{size},height:{size},objectFit:'cover'}}}} /> : {letter_expr}}}"

# ── 2. Állás RR standings (24px kör) ─────────────────────────────────────────
OLD_RR = "<div style={{ width:24, height:24, borderRadius:'50%', background:s.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0 }}>{s.player.name.charAt(0).toUpperCase()}</div>"
NEW_RR = "<div style={{ width:24, height:24, borderRadius:'50%', background:s.player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:700, fontSize:12, color:'#fff', flexShrink:0, overflow:'hidden' }}>{s.player.img ? <img src={s.player.img} style={{width:24,height:24,objectFit:'cover'}} /> : s.player.name.charAt(0).toUpperCase()}</div>"
assert html.count(OLD_RR) == 1, f"rr: {html.count(OLD_RR)}"
html = html.replace(OLD_RR, NEW_RR, 1)

# ── 3. EndScreen podium (avatarSize kör) ─────────────────────────────────────
OLD_PODIUM = "<div style={{ width:avatarSize, height:avatarSize, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:avatarFontSize, color:'#fff', boxShadow:`0 0 0 3px ${tone}, 0 4px 14px rgba(0,0,0,0.18)`, animation:'popIn .4s cubic-bezier(.2,.9,.3,1.4)', marginBottom:6 }}>{p.name.charAt(0).toUpperCase()}</div>"
NEW_PODIUM = "<div style={{ width:avatarSize, height:avatarSize, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:avatarFontSize, color:'#fff', boxShadow:`0 0 0 3px ${tone}, 0 4px 14px rgba(0,0,0,0.18)`, animation:'popIn .4s cubic-bezier(.2,.9,.3,1.4)', marginBottom:6, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:avatarSize,height:avatarSize,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
assert html.count(OLD_PODIUM) == 1, f"podium: {html.count(OLD_PODIUM)}"
html = html.replace(OLD_PODIUM, NEW_PODIUM, 1)

# ── 4. EndScreen stat kártyák (52px kör) ─────────────────────────────────────
OLD_STAT = "<div style={{ width:52, height:52, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff' }}>{player.name.charAt(0).toUpperCase()}</div>"
NEW_STAT = "<div style={{ width:52, height:52, borderRadius:'50%', background:player.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff', overflow:'hidden' }}>{player.img ? <img src={player.img} style={{width:52,height:52,objectFit:'cover'}} /> : player.name.charAt(0).toUpperCase()}</div>"
assert html.count(OLD_STAT) == 1, f"stat: {html.count(OLD_STAT)}"
html = html.replace(OLD_STAT, NEW_STAT, 1)

# ── 5. EndScreen leaderboard lista (30px kör) ────────────────────────────────
OLD_LEAD = "<div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>"
NEW_LEAD = "<div style={{ width:30, height:30, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:30,height:30,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
assert html.count(OLD_LEAD) == 1, f"lead: {html.count(OLD_LEAD)}"
html = html.replace(OLD_LEAD, NEW_LEAD, 1)

# ── 6. EndScreen ital egység lista (28px kör) ────────────────────────────────
OLD_UNITS = "<div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0 }}>{p.name.charAt(0).toUpperCase()}</div>"
NEW_UNITS = "<div style={{ width:28, height:28, borderRadius:'50%', background:p.color, display:'grid', placeItems:'center', fontFamily:T.font, fontWeight:900, fontSize:12, color:'#fff', flexShrink:0, overflow:'hidden' }}>{p.img ? <img src={p.img} style={{width:28,height:28,objectFit:'cover'}} /> : p.name.charAt(0).toUpperCase()}</div>"
assert html.count(OLD_UNITS) == 1, f"units: {html.count(OLD_UNITS)}"
html = html.replace(OLD_UNITS, NEW_UNITS, 1)

# ── 7. Beer Pong match P1 (80px kör) ─────────────────────────────────────────
OLD_P1 = """              {currentMatch.p1.name.charAt(0).toUpperCase()}
            </div>"""
NEW_P1 = """              {currentMatch.p1.img ? <img src={currentMatch.p1.img} style={{width:80,height:80,objectFit:'cover',borderRadius:'50%'}} /> : currentMatch.p1.name.charAt(0).toUpperCase()}
            </div>"""
assert html.count(OLD_P1) == 1, f"p1: {html.count(OLD_P1)}"
html = html.replace(OLD_P1, NEW_P1, 1)

# ── 8. Beer Pong match P2 (80px kör) ─────────────────────────────────────────
OLD_P2 = """              {currentMatch.p2.name.charAt(0).toUpperCase()}
            </div>"""
NEW_P2 = """              {currentMatch.p2.img ? <img src={currentMatch.p2.img} style={{width:80,height:80,objectFit:'cover',borderRadius:'50%'}} /> : currentMatch.p2.name.charAt(0).toUpperCase()}
            </div>"""
assert html.count(OLD_P2) == 1, f"p2: {html.count(OLD_P2)}"
html = html.replace(OLD_P2, NEW_P2, 1)

print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
