import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Cell rendering: green for multi-day, orange for single-day, white stripe for multi-day
OLD1 = '''          // is any entry a multi-day span?
          const hasMulti = entries.some(e => e.role !== 'single');
          const cellBg = (isTod || hasEv) ? '#E8631A' : 'transparent';
          const textColor = (isTod || hasEv) ? '#fff' : T.sub;
          return (
            <div key={i} onClick={() => { if(hasEv) setDetail(firstEv.ev.id); }}
              style={{ position:'relative', borderRadius:8, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', minHeight:36, background: cellBg, cursor: hasEv ? 'pointer' : 'default', overflow:'hidden' }}>
              {d && <>
                <span style={{ fontFamily:T.font, fontWeight:(isTod||hasEv)?900:400, fontSize:12, color: textColor, lineHeight:1 }}>{d}</span>
                {/* Multi-day strip at bottom */}
                {hasMulti && (
                  <div style={{ position:'absolute', bottom:0, left:0, right:0, height:4, background:'rgba(255,255,255,0.38)' }} />
                )}
              </>}
            </div>
          );'''

NEW1 = '''          // is any entry a multi-day span?
          const hasMulti = hasEv && entries.some(e => e.role !== 'single');
          const hasSingle = hasEv && entries.some(e => e.role === 'single');
          const cellBg = isTod ? '#E8631A' : hasMulti ? '#25b572' : hasEv ? '#E8631A' : 'transparent';
          const textColor = (isTod || hasEv) ? '#fff' : T.sub;
          return (
            <div key={i} onClick={() => { if(hasEv) setDetail(firstEv.ev.id); }}
              style={{ position:'relative', borderRadius:8, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', minHeight:36, background: cellBg, cursor: hasEv ? 'pointer' : 'default', overflow:'hidden' }}>
              {d && <>
                <span style={{ fontFamily:T.font, fontWeight:(isTod||hasEv)?900:400, fontSize:12, color: textColor, lineHeight:1 }}>{d}</span>
                {/* Multi-day strip at bottom — darker green stripe */}
                {hasMulti && (
                  <div style={{ position:'absolute', bottom:0, left:0, right:0, height:5, background:'rgba(0,0,0,0.2)' }} />
                )}
              </>}
            </div>
          );'''

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Empty month placeholder
OLD2 = '''      {monthEvs.length > 0 && (
        <div style={{ marginTop:12 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.sub, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Ezen a hónapon</div>'''

NEW2 = '''      {monthEvs.length === 0 && (
        <div style={{ marginTop:24, textAlign:'center', padding:'20px 16px' }}>
          <div style={{ fontSize:32, marginBottom:8 }}>📅</div>
          <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.sub }}>Ebben a hónapban nincs esemény</div>
        </div>
      )}
      {monthEvs.length > 0 && (
        <div style={{ marginTop:12 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.sub, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Ezen a hónapon</div>'''

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

content = re.sub(r'v9\.692', 'v9.693', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.693")
