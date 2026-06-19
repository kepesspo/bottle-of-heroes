#!/usr/bin/env python3

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

old = """function SheetOverlay({ onClose, children }) {
  return (
    <div onClick={onClose} style={{
      position:'fixed', inset:0, background:'rgba(14,14,24,0.45)',
      zIndex:60, display:'flex', alignItems:'flex-end',
      animation:'fadeIn .2s',
    }}>
      <div onClick={e => e.stopPropagation()} style={{
        width:'100%', background:T.surface,
        borderTopLeftRadius:20, borderTopRightRadius:20,
        boxShadow:'0 -10px 40px rgba(0,0,0,0.2)',
        animation:'slideUp .3s cubic-bezier(.2,.9,.3,1)',
        maxHeight:'85%', overflowY:'auto',
      }}>
        <div style={{ display:'flex', justifyContent:'center', padding:'10px 0 6px' }}>
          <div style={{ width:44, height:5, borderRadius:3, background:T.inkMute, opacity:0.35 }} />
        </div>
        {children}
      </div>
    </div>
  );
}"""

new = """function SheetOverlay({ onClose, children }) {
  const [dragY, setDragY] = React.useState(0);
  const [closing, setClosing] = React.useState(false);
  const startYRef = React.useRef(null);
  const sheetRef = React.useRef(null);

  const dismiss = React.useCallback(() => {
    setClosing(true);
    setTimeout(onClose, 220);
  }, [onClose]);

  const onTouchStart = (e) => {
    // Only start drag from the handle area or when sheet is scrolled to top
    const sheet = sheetRef.current;
    if (sheet && sheet.scrollTop > 0) return;
    startYRef.current = e.touches[0].clientY;
  };
  const onTouchMove = (e) => {
    if (startYRef.current === null) return;
    const dy = e.touches[0].clientY - startYRef.current;
    if (dy > 0) {
      setDragY(dy);
    }
  };
  const onTouchEnd = () => {
    if (dragY > 80) {
      dismiss();
    } else {
      setDragY(0);
    }
    startYRef.current = null;
  };

  const translateY = closing ? '100%' : `${dragY}px`;
  const opacity = closing ? 0 : Math.max(0, 1 - dragY / 300);

  return (
    <div onClick={dismiss} style={{
      position:'fixed', inset:0, background:'rgba(14,14,24,0.45)',
      zIndex:60, display:'flex', alignItems:'flex-end',
      animation:'fadeIn .2s',
      opacity, transition: dragY === 0 ? 'opacity .22s' : 'none',
    }}>
      <div
        ref={sheetRef}
        onClick={e => e.stopPropagation()}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
        style={{
          width:'100%', background:T.surface,
          borderTopLeftRadius:20, borderTopRightRadius:20,
          boxShadow:'0 -10px 40px rgba(0,0,0,0.2)',
          animation: closing ? 'none' : 'slideUp .3s cubic-bezier(.2,.9,.3,1)',
          maxHeight:'85%', overflowY:'auto',
          transform: `translateY(${translateY})`,
          transition: dragY === 0 && !closing ? 'transform .22s cubic-bezier(.2,.9,.3,1)' : closing ? 'transform .22s ease-in' : 'none',
          willChange:'transform',
        }}>
        <div
          style={{ display:'flex', justifyContent:'center', padding:'10px 0 6px', cursor:'grab' }}
          onTouchStart={e => { startYRef.current = e.touches[0].clientY; }}
        >
          <div style={{ width:44, height:5, borderRadius:3, background:T.inkMute, opacity: 0.35 + Math.min(dragY/200, 0.3) }} />
        </div>
        {children}
      </div>
    </div>
  );
}"""

assert old in html, "FAIL: SheetOverlay"
html = html.replace(old, new, 1)

html = html.replace("const APP_VERSION = 'v9.299';", "const APP_VERSION = 'v9.300';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.300 — SheetOverlay swipe-to-dismiss minden bottomsheet-en")
