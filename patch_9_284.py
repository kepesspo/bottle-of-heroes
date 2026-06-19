#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. PlayerEditSheet: add transition to translateY so keyboard shift is smooth
old = """        transform: `translateY(${shiftY}px)`,
      }}>"""
new = """        transform: `translateY(${shiftY}px)`,
        transition: 'transform 0.25s ease',
      }}>"""
assert old in html, "FAIL: modal transform"
html = html.replace(old, new, 1)

# ── 2. Stats: compact horizontal rows instead of 2-col grid with big numbers
old = """  return (
    <div style={{ background:T.bgSoft, borderRadius:14, padding:'12px 14px', display:'grid', gridTemplateColumns:'1fr 1fr', gap:10 }}>
      {items.map(it => (
        <div key={it.label} style={{ display:'flex', flexDirection:'column', gap:2 }}>
          <div style={{ fontFamily:T.font, fontSize:11, color:T.inkMute, fontWeight:600 }}>{it.emoji} {it.label}</div>
          <div style={{ fontFamily:T.font, fontSize:17, fontWeight:900, color:T.ink }}>{it.value}</div>
        </div>
      ))}
    </div>
  );"""
new = """  return (
    <div style={{ background:T.bgSoft, borderRadius:14, padding:'8px 12px', display:'flex', flexDirection:'column', gap:0 }}>
      {items.map((it, i) => (
        <div key={it.label} style={{ display:'flex', alignItems:'center', justifyContent:'space-between', padding:'5px 0', borderBottom: i < items.length-1 ? `1px solid ${T.inkMute}18` : 'none' }}>
          <div style={{ fontFamily:T.font, fontSize:12, color:T.inkMute, fontWeight:600 }}>{it.emoji} {it.label}</div>
          <div style={{ fontFamily:T.font, fontSize:13, fontWeight:900, color:T.ink }}>{it.value}</div>
        </div>
      ))}
    </div>
  );"""
assert old in html, "FAIL: stats grid"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.283';", "const APP_VERSION = 'v9.284';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.284 — modal transition smooth, stat kompakt sorok")
