#!/usr/bin/env python3
"""
v9.596 — PRESET_PLAYERS modul szintre mozgatása (PlayerEditSheet is eléri)
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

assert html.count('v9.595') >= 1
html = html.replace('v9.595', 'v9.596', 1)

PRESET_BLOCK = """  const PRESET_PLAYERS = (() => {
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

MODULE_PRESET = """const PRESET_PLAYERS = (() => {
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

# Remove from App
assert html.count(PRESET_BLOCK) == 1, f"preset block: {html.count(PRESET_BLOCK)}"
html = html.replace(PRESET_BLOCK, '', 1)

# Add at module scope after INITIAL_PLAYERS
ANCHOR = """})();

// ─── Icons ────────────────────────────────────────────────────"""
assert html.count(ANCHOR) == 1, f"anchor: {html.count(ANCHOR)}"
html = html.replace(ANCHOR, '})();\n\n' + MODULE_PRESET + '\n\n// ─── Icons ────────────────────────────────────────────────────', 1)

assert html.count('const PRESET_PLAYERS') == 1
print(f"Final size: {len(html):,} chars")
with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
print("Written OK.")
