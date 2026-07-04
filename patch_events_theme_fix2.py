with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Fix EventCalendarView - use window.__evT properly (avoid shadowing issue)
OLD1 = """function EventCalendarView({ events, calMonth, setCalMonth, setDetail, evT: calEvT }) {
  const T = calEvT || window.__evT || T;
  const HU_DAYS"""
NEW1 = """function EventCalendarView({ events, calMonth, setCalMonth, setDetail, evT: calEvT }) {
  const T = calEvT || window.__evT || THEMES['warm'];
  const HU_DAYS"""
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Fix EventForm - use window.__evT properly
OLD2 = """function EventForm({ initial, onSave, onCancel, evT: formEvT }) {
  const T = formEvT || window.__evT || T;
  const [title"""
NEW2 = """function EventForm({ initial, onSave, onCancel, evT: formEvT }) {
  const T = formEvT || window.__evT || THEMES['warm'];
  const [title"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Add useEventsTheme hook before EventCalendarView
OLD3 = "function EventCalendarView({ events, calMonth, setCalMonth, setDetail, evT: calEvT }) {"
NEW3 = """function useEventsTheme() {
  const [evT, setEvT] = React.useState(() => {
    const key = localStorage.getItem('boh_events_theme') || 'ice';
    return THEMES[key] || THEMES['ice'] || THEMES['warm'];
  });
  React.useEffect(() => {
    if (typeof window.onEventsTheme === 'function') {
      const unsub = window.onEventsTheme(key => {
        const th = THEMES[key] || THEMES['ice'] || THEMES['warm'];
        setEvT(th);
        window.__evT = th;
        try { localStorage.setItem('boh_events_theme', key); } catch(e) {}
      });
      return () => unsub();
    }
  }, []);
  React.useEffect(() => { window.__evT = evT; }, [evT]);
  return evT;
}

function EventCalendarView({ events, calMonth, setCalMonth, setDetail, evT: calEvT }) {"""
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Replace EventLogScreen's inline evT state+effect with useEventsTheme()
OLD4 = """  const [evT, setEvT] = React.useState(() => {
    const key = localStorage.getItem('boh_events_theme') || 'ice';
    return THEMES[key] || THEMES['ice'] || T;
  });
  React.useEffect(() => {
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
NEW4 = """  const evT = useEventsTheme();
  // Shadow global T with reactive events theme inside this component
  const T = evT;"""
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. EventCreateScreen: add evT and pass to EventForm and use for T
OLD5 = """function EventCreateScreen({ go }) {
  const [saving, setSaving] = React.useState(false);

  function saveNew(data, done) {
    setSaving(true);
    const col = evDb();
    const entry = { ...data, rsvp: {}, createdAt: new Date().toISOString() };
    if (col) { col.add(entry).finally(() => { done(); setSaving(false); go('log'); }); }
    else { evSave([{ id: Date.now(), ...entry }, ...evLoad()]); done(); setSaving(false); go('log'); }
  }

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Új esemény" onBack={() => go('log')} />
      <div style={{ flex:1, overflowY:'auto', padding:'16px 16px 32px' }}>
        <EventForm onSave={saveNew} onCancel={() => go('log')} />
      </div>
    </div>
  );
}"""
NEW5 = """function EventCreateScreen({ go }) {
  const [saving, setSaving] = React.useState(false);
  const evT = useEventsTheme();
  const T = evT;

  function saveNew(data, done) {
    setSaving(true);
    const col = evDb();
    const entry = { ...data, rsvp: {}, createdAt: new Date().toISOString() };
    if (col) { col.add(entry).finally(() => { done(); setSaving(false); go('log'); }); }
    else { evSave([{ id: Date.now(), ...entry }, ...evLoad()]); done(); setSaving(false); go('log'); }
  }

  return (
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }}>
      <AppBar title="Új esemény" onBack={() => go('log')} />
      <div style={{ flex:1, overflowY:'auto', padding:'16px 16px 32px' }}>
        <EventForm onSave={saveNew} onCancel={() => go('log')} evT={evT} />
      </div>
    </div>
  );
}"""
assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

import re
content = re.sub(r'v9\.747', 'v9.748', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.748")
