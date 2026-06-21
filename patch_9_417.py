#!/usr/bin/env python3
"""v9.417 — CardBattleGame: ikon fix + kompakt UI + scroll"""

with open('index.html', 'r', encoding='utf-8') as f:
    src = f.read()

# 1. IMGS reference fix (already done in v9.416 if that ran)
OLD_IMG = "img:'cardbattle_icon.png', banner:'cardbattle_banner.png'"
NEW_IMG = "img:IMGS['cardbattle_icon.png'], banner:IMGS['cardbattle_banner.png']"
if OLD_IMG in src:
    src = src.replace(OLD_IMG, NEW_IMG, 1)
    print('img fix applied')
else:
    print('img already fixed')

# 2. CardChip — kisebb méret
OLD_CHIP = """  const CardChip = ({value, color, dim=false}) => (
    <div style={{
      width:42, height:56, borderRadius:11,
      background:'#fff', border:'2px solid '+(dim ? color+'55' : color),
      display:'flex', alignItems:'center', justifyContent:'center',
      fontFamily:T.font, fontWeight:900, fontSize:22, color: dim ? color+'88' : color,
      boxShadow: dim ? 'none' : '0 2px 8px rgba(0,0,0,.13)',
      position:'relative', flexShrink:0, userSelect:'none',
      opacity: dim ? 0.4 : 1,
    }}>
      <span style={{position:'absolute',top:4,left:6,fontSize:9,fontWeight:900,opacity:.6}}>{value}</span>
      {value}
      <span style={{position:'absolute',bottom:4,right:6,fontSize:9,fontWeight:900,opacity:.6,transform:'rotate(180deg)'}}>{value}</span>
    </div>
  );"""

NEW_CHIP = """  const CardChip = ({value, color, dim=false}) => (
    <div style={{
      width:36, height:48, borderRadius:9,
      background:'#fff', border:'2px solid '+(dim ? color+'55' : color),
      display:'flex', alignItems:'center', justifyContent:'center',
      fontFamily:T.font, fontWeight:900, fontSize:19, color: dim ? color+'88' : color,
      boxShadow: dim ? 'none' : '0 2px 6px rgba(0,0,0,.12)',
      position:'relative', flexShrink:0, userSelect:'none',
      opacity: dim ? 0.4 : 1,
    }}>
      <span style={{position:'absolute',top:3,left:5,fontSize:8,fontWeight:900,opacity:.6}}>{value}</span>
      {value}
      <span style={{position:'absolute',bottom:3,right:5,fontSize:8,fontWeight:900,opacity:.6,transform:'rotate(180deg)'}}>{value}</span>
    </div>
  );"""

assert OLD_CHIP in src, 'CardChip not found'
src = src.replace(OLD_CHIP, NEW_CHIP, 1)
print('CardChip resized')

# 3. Plan phase outer div: add overflowY:auto, tighter padding/gap
OLD_PLAN_DIV = "background:CB_BG,borderRadius:20,padding:'14px',display:'flex',flexDirection:'column',gap:12,touchAction:'none'"
NEW_PLAN_DIV = "background:CB_BG,borderRadius:20,padding:'12px',display:'flex',flexDirection:'column',gap:8,touchAction:'none',overflowY:'auto'"
assert OLD_PLAN_DIV in src, 'plan div not found'
src = src.replace(OLD_PLAN_DIV, NEW_PLAN_DIV, 1)
print('plan div updated')

# 4. Plan fejléc: kisebb padding/font
OLD_FEJLEC = "padding:'7px 18px',background:'rgba(255,255,255,.85)',borderRadius:999,boxShadow:'0 2px 8px rgba(0,0,0,.1)'}}>"\
             "\n            <div style={{width:9,height:9,borderRadius:'50%',background:pColor}} />\n"\
             "            <span style={{fontFamily:T.font,fontWeight:800,fontSize:15,color:T.ink}}>{pName} tervez</span>"
NEW_FEJLEC = "padding:'6px 14px',background:'rgba(255,255,255,.85)',borderRadius:999,boxShadow:'0 2px 8px rgba(0,0,0,.1)'}}>"\
             "\n            <div style={{width:8,height:8,borderRadius:'50%',background:pColor}} />\n"\
             "            <span style={{fontFamily:T.font,fontWeight:800,fontSize:14,color:T.ink}}>{pName} tervez</span>"
assert OLD_FEJLEC in src, 'fejlec not found'
src = src.replace(OLD_FEJLEC, NEW_FEJLEC, 1)
print('fejlec updated')

# 5. Slot row: kisebb padding és minHeight
OLD_SLOT = "display:'flex', alignItems:'center', gap:12, padding:'10px 14px',\n              background:'#fff',\n              borderRadius:16,"
NEW_SLOT = "display:'flex', alignItems:'center', gap:10, padding:'7px 12px',\n              background:'#fff',\n              borderRadius:13,"
assert OLD_SLOT in src, 'slot row not found'
src = src.replace(OLD_SLOT, NEW_SLOT, 1)
print('slot row updated')

OLD_MINHEIGHT = "transition:'border .1s,box-shadow .1s',\n              minHeight:62,"
NEW_MINHEIGHT = "transition:'border .1s',\n              minHeight:48,"
assert OLD_MINHEIGHT in src, 'minHeight not found'
src = src.replace(OLD_MINHEIGHT, NEW_MINHEIGHT, 1)
print('minHeight updated')

OLD_SLOTLABEL = "fontFamily:T.font,fontWeight:700,fontSize:13,color:T.inkSoft,minWidth:42"
NEW_SLOTLABEL = "fontFamily:T.font,fontWeight:700,fontSize:12,color:T.inkSoft,minWidth:38"
assert OLD_SLOTLABEL in src, 'slot label not found'
src = src.replace(OLD_SLOTLABEL, NEW_SLOTLABEL, 1)
print('slot label updated')

# 6. Kéz section: kompaktabb
OLD_KEZ_HEADER = "marginTop:4}}>\\n          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:'rgba(0,0,0,.45)',textTransform:'uppercase',letterSpacing:'.08em',marginBottom:8}}>Kézben</div>\\n          <div style={{display:'flex',gap:10,flexWrap:'wrap'}}>"
# Use simpler find
OLD_KEZ = "        {/* Kéz kártyái */}\n        <div style={{marginTop:4}}>\n          <div style={{fontFamily:T.font,fontSize:11,fontWeight:700,color:'rgba(0,0,0,.45)',textTransform:'uppercase',letterSpacing:'.08em',marginBottom:8}}>Kézben</div>\n          <div style={{display:'flex',gap:10,flexWrap:'wrap'}}>"
NEW_KEZ = "        {/* Kéz kártyái */}\n        <div style={{marginTop:2}}>\n          <div style={{fontFamily:T.font,fontSize:10,fontWeight:700,color:'rgba(0,0,0,.4)',textTransform:'uppercase',letterSpacing:'.08em',marginBottom:5}}>Kézben</div>\n          <div style={{display:'flex',gap:8,flexWrap:'wrap'}}>"
assert OLD_KEZ in src, 'kez section not found'
src = src.replace(OLD_KEZ, NEW_KEZ, 1)
print('kez section updated')

# 7. Kész gomb: kisebb padding
OLD_KESZ_BTN = "marginTop:4,padding:'15px',borderRadius:16,border:'none',\n            background:pColor,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:16,"
NEW_KESZ_BTN = "marginTop:2,padding:'12px',borderRadius:13,border:'none',\n            background:pColor,color:'#fff',fontFamily:T.font,fontWeight:900,fontSize:15,"
assert OLD_KESZ_BTN in src, 'kész btn not found'
src = src.replace(OLD_KESZ_BTN, NEW_KESZ_BTN, 1)
print('kész btn updated')

# 8. Reveal + Done: overflowY:auto és tighter gap
OLD_REV = "background:CB_BG,borderRadius:20,padding:'14px',display:'flex',flexDirection:'column',gap:12,overflowY:'auto'"
NEW_REV = "background:CB_BG,borderRadius:20,padding:'12px',display:'flex',flexDirection:'column',gap:8,overflowY:'auto'"
assert OLD_REV in src, 'reveal div not found'
src = src.replace(OLD_REV, NEW_REV, 1)
print('reveal div updated')

OLD_DONE = "background:CB_BG,borderRadius:20,padding:'14px',display:'flex',flexDirection:'column',gap:14"
NEW_DONE = "background:CB_BG,borderRadius:20,padding:'12px',display:'flex',flexDirection:'column',gap:10,overflowY:'auto'"
assert OLD_DONE in src, 'done div not found'
src = src.replace(OLD_DONE, NEW_DONE, 1)
print('done div updated')

# 9. version bump
assert "const APP_VERSION = 'v9.416';" in src
src = src.replace("const APP_VERSION = 'v9.416';", "const APP_VERSION = 'v9.417';", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(src)

print('v9.417 OK')
