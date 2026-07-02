import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = '''      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', gap:2 }}>
        {cells.map((d,i) => {
          const entries = d ? (evDays[d] || []) : [];
          const hasEv = entries.length > 0;
          const isTod = isToday(d);
          const firstEv = entries[0];
          return (
            <div key={i} onClick={() => { if(hasEv) setDetail(firstEv.ev.id); }}
              style={{ borderRadius:8, display:'flex', flexDirection:'column', alignItems:'center', paddingTop:4, paddingBottom:3, minHeight:36, background: isTod ? '#E8631A' : 'transparent', cursor: hasEv ? 'pointer' : 'default' }}>
              {d && <>
                <span style={{ fontFamily:T.font, fontWeight:(isTod||hasEv)?900:400, fontSize:12, color: isTod?'#fff':hasEv?T.ink:T.sub, lineHeight:1, marginBottom:2 }}>{d}</span>
                {entries.slice(0,2).map(({ev,role},ri) => {
                  const isSingle = role==='single';
                  const isStart = role==='start';
                  const isEnd = role==='end';
                  const isMid = role==='mid';
                  const isMultiDay = !isSingle;
                  const barColor = isTod ? 'rgba(255,255,255,0.7)' : EV_COLOR;
                  return (
                    <div key={ri} style={{
                      position:'relative', overflow:'hidden',
                      width: isSingle ? '70%' : '100%',
                      height:5, marginBottom:1,
                      background: barColor,
                      borderRadius: isSingle ? 3 : isStart ? '3px 0 0 3px' : isEnd ? '0 3px 3px 0' : 0,
                      marginLeft: isEnd||isMid ? 0 : undefined,
                      marginRight: isStart||isMid ? 0 : undefined,
                    }}>
                      {isMultiDay && <div style={{ position:'absolute', top:0, left:0, right:0, bottom:0, background:'repeating-linear-gradient(90deg, transparent 0px, transparent 5px, rgba(255,255,255,0.45) 5px, rgba(255,255,255,0.45) 7px)' }} />}
                    </div>
                  );
                })}
                {entries.length > 2 && <span style={{ fontFamily:T.font, fontSize:8, color: isTod?'rgba(255,255,255,0.8)':T.sub, lineHeight:1 }}>+{entries.length-2}</span>}
              </>}
            </div>
          );
        })}
      </div>'''

NEW = '''      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', gap:2 }}>
        {cells.map((d,i) => {
          const entries = d ? (evDays[d] || []) : [];
          const hasEv = entries.length > 0;
          const isTod = isToday(d);
          const firstEv = entries[0];
          // is any entry a multi-day span?
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
          );
        })}
      </div>'''

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.691', 'v9.692', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.692")
