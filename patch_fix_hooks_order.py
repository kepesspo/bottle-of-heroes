with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove useRef calls from after the early return
OLD1 = """  const EV_TABS = ['past','list','calendar'];
  const evSwipeRef = React.useRef(null);
  const evSwipeStart = React.useRef(null);
  const evSwipeHandlers = {"""
NEW1 = """  const EV_TABS = ['past','list','calendar'];
  const evSwipeHandlers = {"""
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Add the useRef calls at the top of EventLogScreen, after the other hooks, before the early return
OLD2 = """  const evT = useEventsTheme();
  // Shadow global T with reactive events theme inside this component
  const T = evT;

  // Subscribe to Firestore events collection, ordered by createdAt desc"""
NEW2 = """  const evT = useEventsTheme();
  // Shadow global T with reactive events theme inside this component
  const T = evT;
  const evSwipeRef = React.useRef(null);
  const evSwipeStart = React.useRef(null);

  // Subscribe to Firestore events collection, ordered by createdAt desc"""
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

import re
content = re.sub(r'v9\.748', 'v9.749', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.749")
