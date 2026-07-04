with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add EventsThemeContext before EventCalendarView
OLD1 = "function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {"

NEW1 = """const EventsThemeCtx = React.createContext(null);
function useEvT() { return React.useContext(EventsThemeCtx) || T; }

function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. In EventCalendarView: add const T = useEvT() at the top
OLD2 = """function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {
  const HU_DAYS = ['H','K','Sz','Cs','P','Sz','V'];"""

NEW2 = """function EventCalendarView({ events, calMonth, setCalMonth, setDetail }) {
  const T = useEvT();
  const HU_DAYS = ['H','K','Sz','Cs','P','Sz','V'];"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. In EventForm: add const T = useEvT() at the top
OLD3 = """function EventForm({ initial, onSave, onCancel }) {
  const [title, setTitle] = React.useState(initial?.title || '');"""

NEW3 = """function EventForm({ initial, onSave, onCancel }) {
  const T = useEvT();
  const [title, setTitle] = React.useState(initial?.title || '');"""

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Wrap EventLogScreen's return with EventsThemeCtx.Provider
# Find the return statement of EventLogScreen
OLD4 = """  const EV_TABS = ['past','list','calendar'];
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
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }} {...evSwipeHandlers}>"""

NEW4 = """  const EV_TABS = ['past','list','calendar'];
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
    <EventsThemeCtx.Provider value={evT}>
    <div style={{ flex:1, display:'flex', flexDirection:'column', background:T.bg, overflow:'hidden' }} {...evSwipeHandlers}>"""

assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. Close the Provider — find the closing of EventLogScreen's main return div
# The return ends with </div>\n  );\n}\n\nfunction EventForm
OLD5 = """      </div>; })()}
    </div>
  );
}

// ── Shared event form (used in admin screen) ──────────────────────────────────
function EventForm({ initial, onSave, onCancel }) {
  const T = useEvT();"""

NEW5 = """      </div>; })()}
    </div>
    </EventsThemeCtx.Provider>
  );
}

// ── Shared event form (used in admin screen) ──────────────────────────────────
function EventForm({ initial, onSave, onCancel }) {
  const T = useEvT();"""

assert OLD5 in content, "OLD5 not found"
content = content.replace(OLD5, NEW5, 1)

import re
content = re.sub(r'v9\.745', 'v9.746', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.746")
