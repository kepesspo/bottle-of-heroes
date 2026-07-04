with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = """  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Események" onBack={deepLink ? null : () => go('home')} right={
        <button onClick={() => go('create')} style={{ width:38, height:38, borderRadius:11, border:'none', background:T.mint, display:'grid', placeItems:'center', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
      } />
      {/* View switcher — full width, stats style */}
      <div style={{ padding:'10px 16px 0' }}>"""

NEW = """  const EV_TABS = ['past','list','calendar'];
  const evSwipeRef = React.useRef(null);
  const evSwipeStart = React.useRef(null);
  const evSwipeHandlers = {
    onTouchStart: e => { evSwipeStart.current = e.touches[0].clientX; },
    onTouchEnd: e => {
      if (evSwipeStart.current === null) return;
      const dx = e.changedTouches[0].clientX - evSwipeStart.current;
      evSwipeStart.current = null;
      if (Math.abs(dx) < 50) return;
      const idx = EV_TABS.indexOf(evView);
      if (dx < 0 && idx < EV_TABS.length - 1) setEvView(EV_TABS[idx + 1]);
      if (dx > 0 && idx > 0) setEvView(EV_TABS[idx - 1]);
    },
  };

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }} {...evSwipeHandlers}>
      <AppBar title="Események" onBack={deepLink ? null : () => go('home')} right={
        <button onClick={() => go('create')} style={{ width:38, height:38, borderRadius:11, border:'none', background:T.mint, display:'grid', placeItems:'center', cursor:'pointer', WebkitTapHighlightColor:'transparent' }}>
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#fff" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round"><line x1="12" y1="5" x2="12" y2="19"/><line x1="5" y1="12" x2="19" y2="12"/></svg>
        </button>
      } />
      {/* View switcher — full width, stats style */}
      <div style={{ padding:'10px 16px 0' }}>"""

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

import re
content = re.sub(r'v9\.743', 'v9.744', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.744")
