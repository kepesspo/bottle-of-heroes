import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

old = '''                {/* Right column: days only */}
                {daysLabel && (
                  <div style={{ background: daysLeft === 0 ? '#E8631A' : daysLeft <= 3 ? '#c07a10' : '#25b572', borderRadius:10, padding:'4px 10px', textAlign:'center', flexShrink:0 }}>
                    <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:'#fff', lineHeight:1 }}>{daysLabel}</div>
                  </div>
                )}'''

new = '''                {/* Right column: days only */}
                {daysLabel && (
                  <div style={{ background: daysLeft === 0 ? '#E8631A' : daysLeft <= 3 ? '#c07a10' : '#25b572', borderRadius:14, padding:'8px 14px', textAlign:'center', flexShrink:0, minWidth:62, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center' }}>
                    {daysLeft === 0 ? (
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:22, color:'#fff', lineHeight:1 }}>Ma!</div>
                    ) : daysLeft === 1 ? (
                      <div style={{ fontFamily:T.font, fontWeight:900, fontSize:19, color:'#fff', lineHeight:1 }}>Holnap</div>
                    ) : (
                      <React.Fragment>
                        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:32, color:'#fff', lineHeight:1 }}>{daysLeft}</div>
                        <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:'rgba(255,255,255,0.85)', lineHeight:1, marginTop:3 }}>nap</div>
                      </React.Fragment>
                    )}
                  </div>
                )}'''

assert old in content, "OLD string not found!"
content = content.replace(old, new, 1)

# version bump
content = re.sub(r'v9\.683', 'v9.684', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.684")
