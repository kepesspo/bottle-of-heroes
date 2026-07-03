import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add deep link detection alongside room detection
OLD1 = "  const _initRoom = React.useMemo(() => { try { return new URLSearchParams(window.location.search).get('room') || ''; } catch(e) { return ''; } }, []);\n  const [screen, setScreen] = useState(() => _initRoom ? 'observer' : 'home');"
NEW1 = """  const _initRoom = React.useMemo(() => { try { return new URLSearchParams(window.location.search).get('room') || ''; } catch(e) { return ''; } }, []);
  const _initScreen = React.useMemo(() => { try { return new URLSearchParams(window.location.search).get('screen') || ''; } catch(e) { return ''; } }, []);
  const _deepLink = _initScreen === 'events' || _initScreen === 'calendar';
  const [screen, setScreen] = useState(() => _initRoom ? 'observer' : _deepLink ? 'log' : 'home');"""
assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Pass deepLink prop to EventLogScreen
OLD2 = "        {screen==='log'      && <EventLogScreen go={go} goEdit={goEdit} />}"
NEW2 = "        {screen==='log'      && <EventLogScreen go={go} goEdit={goEdit} deepLink={_deepLink} />}"
assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Accept deepLink in EventLogScreen and hide back button when deep linked
OLD3 = "function EventLogScreen({ go, goEdit }) {"
NEW3 = "function EventLogScreen({ go, goEdit, deepLink }) {"
assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Conditionally show back button in AppBar
OLD4 = '      <AppBar title="Események" onBack={() => go(\'home\')} right={'
NEW4 = "      <AppBar title=\"Események\" onBack={deepLink ? null : () => go('home')} right={"
assert OLD4 in content, "OLD4 not found"
content = content.replace(OLD4, NEW4, 1)

# 5. Version bump
content = re.sub(r'v9\.710', 'v9.711', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.711")
