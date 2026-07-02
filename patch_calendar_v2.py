with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = '''function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {
  const HU_DAYS = ['H','K','Sz','Cs','P','Sz','V'];
  const HU_MONTHS = ['Január','Február','Március','Április','Május','Június','Július','Augusztus','Szeptember','Október','November','December'];
  const year = calMonth.getFullYear(), month = calMonth.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month+1, 0);
  const startOffset = (firstDay.getDay()+6) % 7;
  const cells = [];
  for(let i=0;i<startOffset;i++) cells.push(null);
  for(let d=1;d<=lastDay.getDate();d++) cells.push(d);
  const evDays = {};
  events.forEach(ev => {
    if(!ev.date) return;
    const d = new Date(ev.date);
    if(d.getFullYear()===year && d.getMonth()===month) {
      const day = d.getDate();
      if(!evDays[day]) evDays[day]=[];
      evDays[day].push(ev);
    }
  });
  const today = new Date();
  const isToday = (d) => d && today.getFullYear()===year && today.getMonth()===month && today.getDate()===d;
  return (
    <div style={{ flex:1, overflowY:'auto', padding:'12px 16px 32px' }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:12 }}>
        <button onClick={() => setCalMonth(new Date(year, month-1, 1))} style={{ width:36, height:36, borderRadius:10, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:17, color:T.ink }}>{HU_MONTHS[month]} {year}</div>
        <button onClick={() => setCalMonth(new Date(year, month+1, 1))} style={{ width:36, height:36, borderRadius:10, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="16" height="16" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', marginBottom:4 }}>
        {HU_DAYS.map((d,i) => <div key={i} style={{ textAlign:'center', fontFamily:T.font, fontWeight:700, fontSize:11, color:T.sub, padding:'4px 0' }}>{d}</div>)}
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', gap:4 }}>
        {cells.map((d,i) => {
          const hasEv = d && evDays[d] && evDays[d].length > 0;
          const isTod = isToday(d);
          return (
            <div key={i} onClick={() => { if(hasEv) setDetail(evDays[d][0].id); }}
              style={{ aspectRatio:'1', borderRadius:12, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', background: isTod ? '#E8631A' : hasEv ? T.surface : 'transparent', boxShadow: (isTod||hasEv) ? T.shadow : 'none', cursor: hasEv ? 'pointer' : 'default', gap:2 }}>
              {d && <>
                <span style={{ fontFamily:T.font, fontWeight:(isTod||hasEv)?900:500, fontSize:14, color: isTod?'#fff':hasEv?T.ink:T.sub, lineHeight:1 }}>{d}</span>
                {hasEv && !isTod && <div style={{ width:5, height:5, borderRadius:'50%', background:'#E8631A' }} />}
                {hasEv && isTod && <div style={{ width:5, height:5, borderRadius:'50%', background:'rgba(255,255,255,0.7)' }} />}
              </>}
            </div>
          );
        })}
      </div>
      {Object.keys(evDays).length > 0 && (
        <div style={{ marginTop:16 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:13, color:T.sub, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:8 }}>Ezen a hónapon</div>
          {Object.entries(evDays).sort(([a],[b])=>Number(a)-Number(b)).flatMap(([,evs])=>evs).map(ev => (
            <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ display:'flex', alignItems:'center', gap:12, padding:'12px 14px', background:T.surface, borderRadius:14, marginBottom:8, boxShadow:T.shadow, cursor:'pointer' }}>
              <div style={{ width:40, height:40, borderRadius:10, background:'#E8631A', display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                <span style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:'#fff', lineHeight:1 }}>{new Date(ev.date).getDate()}</span>
              </div>
              <div style={{ flex:1, minWidth:0 }}>
                <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                <div style={{ fontFamily:T.font, fontSize:12, color:T.sub, marginTop:2 }}>{new Date(ev.date).toLocaleTimeString('hu-HU',{hour:'2-digit',minute:'2-digit'})}{ev.location?' · '+ev.location.split(',')[0]:''}</div>
              </div>
              <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}'''

NEW = '''function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {
  const HU_DAYS = ['H','K','Sz','Cs','P','Sz','V'];
  const HU_MONTHS = ['Január','Február','Március','Április','Május','Június','Július','Augusztus','Szeptember','Október','November','December'];
  const year = calMonth.getFullYear(), month = calMonth.getMonth();
  const firstDay = new Date(year, month, 1);
  const lastDay = new Date(year, month+1, 0);
  const startOffset = (firstDay.getDay()+6) % 7;
  const cells = [];
  for(let i=0;i<startOffset;i++) cells.push(null);
  for(let d=1;d<=lastDay.getDate();d++) cells.push(d);

  // Build per-day event info including multi-day spans
  // evDays[day] = list of {ev, role: 'single'|'start'|'mid'|'end'}
  const evDays = {};
  const monthEvs = []; // events that touch this month
  events.forEach(ev => {
    if(!ev.date) return;
    const start = new Date(ev.date);
    start.setHours(0,0,0,0);
    const end = ev.dateTo ? (() => { const e=new Date(ev.dateTo); e.setHours(0,0,0,0); return e; })() : new Date(start);
    // check if event touches this month
    const mStart = new Date(year, month, 1);
    const mEnd = new Date(year, month+1, 0);
    if(end < mStart || start > mEnd) return;
    monthEvs.push(ev);
    const isMulti = end > start;
    for(let day=1; day<=lastDay.getDate(); day++) {
      const cur = new Date(year, month, day);
      if(cur < start || cur > end) continue;
      const role = !isMulti ? 'single' : cur.getTime()===start.getTime() ? 'start' : cur.getTime()===end.getTime() ? 'end' : 'mid';
      if(!evDays[day]) evDays[day]=[];
      evDays[day].push({ev, role});
    }
  });

  const today = new Date();
  const isToday = (d) => d && today.getFullYear()===year && today.getMonth()===month && today.getDate()===d;

  const SPAN_COLORS = ['#E8631A','#25b572','#5b7cf6','#c07a10','#d63884'];
  // assign stable color index per event id
  const colorMap = {};
  let ci = 0;
  monthEvs.forEach(ev => { if(colorMap[ev.id]===undefined) colorMap[ev.id]=ci++; });

  return (
    <div style={{ flex:1, overflowY:'auto', padding:'8px 12px 32px' }}>
      <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between', marginBottom:8 }}>
        <button onClick={() => setCalMonth(new Date(year, month-1, 1))} style={{ width:32, height:32, borderRadius:10, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="15 18 9 12 15 6"/></svg>
        </button>
        <div style={{ fontFamily:T.font, fontWeight:900, fontSize:15, color:T.ink }}>{HU_MONTHS[month]} {year}</div>
        <button onClick={() => setCalMonth(new Date(year, month+1, 1))} style={{ width:32, height:32, borderRadius:10, border:'none', background:T.surface, cursor:'pointer', display:'grid', placeItems:'center', boxShadow:T.shadow }}>
          <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke={T.ink} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
        </button>
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', marginBottom:2 }}>
        {HU_DAYS.map((d,i) => <div key={i} style={{ textAlign:'center', fontFamily:T.font, fontWeight:700, fontSize:10, color:T.sub, padding:'2px 0' }}>{d}</div>)}
      </div>
      <div style={{ display:'grid', gridTemplateColumns:'repeat(7,1fr)', gap:2 }}>
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
                  const col = SPAN_COLORS[colorMap[ev.id] % SPAN_COLORS.length];
                  const isSingle = role==='single';
                  const isStart = role==='start';
                  const isEnd = role==='end';
                  const isMid = role==='mid';
                  return (
                    <div key={ri} style={{
                      width: isSingle ? '70%' : '100%',
                      height:4, marginBottom:1,
                      background: isTod ? 'rgba(255,255,255,0.7)' : col,
                      borderRadius: isSingle ? 3 : isStart ? '3px 0 0 3px' : isEnd ? '0 3px 3px 0' : 0,
                      marginLeft: isEnd||isMid ? 0 : undefined,
                      marginRight: isStart||isMid ? 0 : undefined,
                    }} />
                  );
                })}
                {entries.length > 2 && <span style={{ fontFamily:T.font, fontSize:8, color: isTod?'rgba(255,255,255,0.8)':T.sub, lineHeight:1 }}>+{entries.length-2}</span>}
              </>}
            </div>
          );
        })}
      </div>
      {monthEvs.length > 0 && (
        <div style={{ marginTop:12 }}>
          <div style={{ fontFamily:T.font, fontWeight:900, fontSize:12, color:T.sub, textTransform:'uppercase', letterSpacing:'0.07em', marginBottom:6 }}>Ezen a hónapon</div>
          {monthEvs.map(ev => {
            const col = SPAN_COLORS[colorMap[ev.id] % SPAN_COLORS.length];
            const isMulti = ev.dateTo && new Date(ev.dateTo).toDateString()!==new Date(ev.date).toDateString();
            const dateLabel = isMulti
              ? `${new Date(ev.date).toLocaleDateString('hu-HU',{month:'short',day:'numeric'})} – ${new Date(ev.dateTo).toLocaleDateString('hu-HU',{month:'short',day:'numeric'})}`
              : `${new Date(ev.date).getDate()}. ${ev.allDay?'Egész nap':new Date(ev.date).toLocaleTimeString('hu-HU',{hour:'2-digit',minute:'2-digit'})}`;
            return (
              <div key={ev.id} onClick={() => setDetail(ev.id)} style={{ display:'flex', alignItems:'center', gap:10, padding:'10px 12px', background:T.surface, borderRadius:12, marginBottom:6, boxShadow:T.shadow, cursor:'pointer' }}>
                <div style={{ width:4, alignSelf:'stretch', borderRadius:4, background:col, flexShrink:0 }} />
                <div style={{ width:34, height:34, borderRadius:8, background:col, display:'flex', flexDirection:'column', alignItems:'center', justifyContent:'center', flexShrink:0 }}>
                  <span style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:'#fff', lineHeight:1 }}>{new Date(ev.date).getDate()}</span>
                </div>
                <div style={{ flex:1, minWidth:0 }}>
                  <div style={{ fontFamily:T.font, fontWeight:900, fontSize:14, color:T.ink, overflow:'hidden', textOverflow:'ellipsis', whiteSpace:'nowrap' }}>{ev.title}</div>
                  <div style={{ fontFamily:T.font, fontSize:11, color:T.sub, marginTop:1 }}>{dateLabel}{ev.location?' · '+ev.location.split(',')[0]:''}</div>
                </div>
                <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke={T.sub} strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polyline points="9 18 15 12 9 6"/></svg>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}'''

assert OLD in content, "OLD string not found!"
content = content.replace(OLD, NEW, 1)

import re
content = re.sub(r'v9\.684', 'v9.685', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.685")
