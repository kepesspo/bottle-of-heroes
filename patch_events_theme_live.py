with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# Add live evT state to EventLogScreen so theme changes are reactive
OLD = """function EventLogScreen({ go, goEdit, deepLink }) {
  const [events, setEvents] = React.useState(evLoad);
  const [loading, setLoading] = React.useState(true);
  const [detail, setDetail] = React.useState(null); // event id
  const [rsvpSheet, setRsvpSheet] = React.useState(false);
  const [rsvpStep, setRsvpStep] = React.useState('who');
  const [rsvpProfile, setRsvpProfile] = React.useState(null);
  const [profiles, setProfiles] = React.useState([]);
  const [evView, setEvView] = React.useState('list'); // 'list' | 'calendar'
  const [calMonth, setCalMonth] = React.useState(() => { const n=new Date(); return new Date(n.getFullYear(), n.getMonth(), 1); });

  // Subscribe to Firestore events collection, ordered by createdAt desc"""

NEW = """function EventLogScreen({ go, goEdit, deepLink }) {
  const [events, setEvents] = React.useState(evLoad);
  const [loading, setLoading] = React.useState(true);
  const [detail, setDetail] = React.useState(null); // event id
  const [rsvpSheet, setRsvpSheet] = React.useState(false);
  const [rsvpStep, setRsvpStep] = React.useState('who');
  const [rsvpProfile, setRsvpProfile] = React.useState(null);
  const [profiles, setProfiles] = React.useState([]);
  const [evView, setEvView] = React.useState('list'); // 'list' | 'calendar'
  const [calMonth, setCalMonth] = React.useState(() => { const n=new Date(); return new Date(n.getFullYear(), n.getMonth(), 1); });
  const [evT, setEvT] = React.useState(() => {
    const key = localStorage.getItem('boh_events_theme') || 'ice';
    return THEMES[key] || THEMES['ice'] || T;
  });
  React.useEffect(() => {
    if (typeof window.onEventsTheme === 'function') {
      const unsub = window.onEventsTheme(key => {
        const th = THEMES[key] || THEMES['ice'] || T;
        setEvT(th);
        try { localStorage.setItem('boh_events_theme', key); } catch(e) {}
      });
      return () => unsub();
    }
  }, []);

  // Subscribe to Firestore events collection, ordered by createdAt desc"""

assert OLD in content, "OLD not found"
content = content.replace(OLD, NEW, 1)

# Now replace all `T.` usages inside EventLogScreen with `evT.`
# Strategy: scope the replacement to just this function by doing it carefully
# We replace the specific block between EventLogScreen start and the next top-level function
# Instead, let's find the return block and do targeted replacements of T. -> evT. for the whole component
# The safest way: wrap the JSX with a local variable at the top of return

# Actually the cleanest fix: inside EventLogScreen, shadow T with evT by adding a line after the state declarations
# We already have evT state. Now we need to shadow T inside the component.
# Add: const T = evT; right before the first useEffect or return

OLD2 = """  React.useEffect(() => {
    if (typeof window.onEventsTheme === 'function') {
      const unsub = window.onEventsTheme(key => {
        const th = THEMES[key] || THEMES['ice'] || T;
        setEvT(th);
        try { localStorage.setItem('boh_events_theme', key); } catch(e) {}
      });
      return () => unsub();
    }
  }, []);

  // Subscribe to Firestore events collection, ordered by createdAt desc"""

NEW2 = """  React.useEffect(() => {
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
  const T = evT;

  // Subscribe to Firestore events collection, ordered by createdAt desc"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

import re
content = re.sub(r'v9\.744', 'v9.745', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.745")
