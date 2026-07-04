with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove EventsThemeCtx and useEvT
OLD1 = """const EventsThemeCtx = React.createContext(null);
function useEvT() { return React.useContext(EventsThemeCtx) || T; }

function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {"""
NEW1 = "function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {"
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Remove const T = useEvT() from EventCalendarView
OLD2 = """function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {
  const T = useEvT();
  const HU_DAYS"""
NEW2 = """function EventCalendarView({ events, calMonth, setCalMonth, setDetail, evT: calEvT }) {
  const T = calEvT || window.__evT || T;
  const HU_DAYS"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Remove const T = useEvT() from EventForm
OLD3 = """function EventForm({ initial, onSave, onCancel }) {
  const T = useEvT();
  const [title"""
NEW3 = """function EventForm({ initial, onSave, onCancel, evT: formEvT }) {
  const T = formEvT || window.__evT || T;
  const [title"""
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Remove Provider wrapper from EventLogScreen return
OLD4 = """  return (
    <EventsThemeCtx.Provider value={evT}>
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }} {...evSwipeHandlers}>"""
NEW4 = """  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }} {...evSwipeHandlers}>"""
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. Remove Provider closing tag
OLD5 = """    </div>
    </EventsThemeCtx.Provider>
  );
}

// ── Shared event form (used in admin screen) ──────────────────────────────────"""
NEW5 = """    </div>
  );
}

// ── Shared event form (used in admin screen) ──────────────────────────────────"""
assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

# 6. Store evT on window so child components can use it, and pass evT to EventCalendarView and EventForm
# Find the EventCalendarView usage and add evT prop
OLD6 = "if (evView === 'calendar') return <EventCalendarView events={events} calMonth={calMonth} setCalMonth={setCalMonth} setDetail={setDetail} />;"
NEW6 = "if (evView === 'calendar') return <EventCalendarView events={events} calMonth={calMonth} setCalMonth={setCalMonth} setDetail={setDetail} evT={evT} />;"
assert OLD6 in content, "OLD6 not found"
content = content.replace(OLD6, NEW6, 1)

# 7. Set window.__evT whenever evT changes — add to the useEffect
OLD7 = """  React.useEffect(() => {
    if (typeof window.onEventsTheme === 'function') {
      const unsub = window.onEventsTheme(key => {
        const th = THEMES[key] || THEMES['ice'] || T;
        setEvT(th);
        try { localStorage.setItem('boh_events_theme', key); } catch(e) {}
      });
      return () => unsub();
    }
  }, []);
  // Shadow global T with reactive events theme inside this component
  const T = evT;"""
NEW7 = """  React.useEffect(() => {
    if (typeof window.onEventsTheme === 'function') {
      const unsub = window.onEventsTheme(key => {
        const th = THEMES[key] || THEMES['ice'] || T;
        setEvT(th);
        window.__evT = th;
        try { localStorage.setItem('boh_events_theme', key); } catch(e) {}
      });
      return () => unsub();
    }
  }, []);
  React.useEffect(() => { window.__evT = evT; }, [evT]);
  // Shadow global T with reactive events theme inside this component
  const T = evT;"""
assert OLD7 in content, "OLD7 not found"
content = content.replace(OLD7, NEW7, 1)

import re
content = re.sub(r'v9\.746', 'v9.747', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.747")
