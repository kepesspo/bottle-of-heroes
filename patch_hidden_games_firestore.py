import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Add Firestore helpers for hiddenGames after the game_stats block (before closing IIFE)
OLD1 = "    return db.collection('game_stats').get().then(function(snap) {\n      var result = {};\n      snap.docs.forEach(function(d) { result[d.id] = d.data(); });\n      return result;\n    }).catch(function() { return {}; });\n  };\n})();"

NEW1 = """    return db.collection('game_stats').get().then(function(snap) {
      var result = {};
      snap.docs.forEach(function(d) { result[d.id] = d.data(); });
      return result;
    }).catch(function() { return {}; });
  };

  window.getHiddenGames = function() {
    return db.collection('config').doc('hiddenGames').get().then(function(d) {
      return d.exists ? (d.data().ids || []) : [];
    }).catch(function() { return []; });
  };

  window.setHiddenGames = function(ids) {
    return db.collection('config').doc('hiddenGames').set({ ids: ids }).catch(function(e) { console.warn('setHiddenGames', e); });
  };

  window.onHiddenGames = function(cb) {
    return db.collection('config').doc('hiddenGames').onSnapshot(function(d) {
      cb(d.exists ? (d.data().ids || []) : []);
    });
  };
})();"""

assert OLD1 in content, "OLD1 not found"
content = content.replace(OLD1, NEW1, 1)

# 2. Replace the AdminGames component to use Firestore
OLD2 = """// ── Admin: Games tab ──────────────────────────────────────────────────────────
const HIDDEN_GAMES_KEY = 'hiddenGames';
function getHiddenGames() {
  try { return JSON.parse(localStorage.getItem(HIDDEN_GAMES_KEY) || '[]'); } catch(e) { return []; }
}
function setHiddenGames(list) {
  localStorage.setItem(HIDDEN_GAMES_KEY, JSON.stringify(list));
}
function AdminGames() {
  const [hidden, setHidden] = React.useState(() => getHiddenGames());

  function toggle(id) {
    const next = hidden.includes(id) ? hidden.filter(x => x !== id) : [...hidden, id];
    setHiddenGames(next);
    setHidden(next);
  }

  function showAll() {
    setHiddenGames([]);
    setHidden([]);
  }"""

NEW2 = """// ── Admin: Games tab ──────────────────────────────────────────────────────────
function AdminGames() {
  const [hidden, setHidden] = React.useState([]);
  const [saving, setSaving] = React.useState(false);

  React.useEffect(() => {
    if (typeof window.onHiddenGames === 'function') {
      const unsub = window.onHiddenGames(ids => setHidden(ids));
      return () => unsub();
    } else {
      window.getHiddenGames && window.getHiddenGames().then(ids => setHidden(ids));
    }
  }, []);

  function toggle(id) {
    const next = hidden.includes(id) ? hidden.filter(x => x !== id) : [...hidden, id];
    setSaving(true);
    window.setHiddenGames(next).finally(() => setSaving(false));
  }

  function showAll() {
    setSaving(true);
    window.setHiddenGames([]).finally(() => setSaving(false));
  }"""

assert OLD2 in content, "OLD2 not found"
content = content.replace(OLD2, NEW2, 1)

# 3. Update the visibleGames filter to use Firestore-backed hidden list
# We need a global state hook for hiddenGames in GamesScreen
# Replace the _hiddenGames line to use a React state that subscribes to Firestore

OLD3 = "  const _hiddenGames = getHiddenGames();\n  const visibleGames = GAMES.filter(g => !_hiddenGames.includes(g.id)).filter(gameMatchesFilter).sort((a,b) => (a.comingSoon?1:0) - (b.comingSoon?1:0));"

NEW3 = "  const [_hiddenGames, _setHiddenGames] = React.useState([]);\n  React.useEffect(() => {\n    if (typeof window.onHiddenGames === 'function') {\n      const unsub = window.onHiddenGames(ids => _setHiddenGames(ids));\n      return () => unsub();\n    } else {\n      window.getHiddenGames && window.getHiddenGames().then(ids => _setHiddenGames(ids));\n    }\n  }, []);\n  const visibleGames = GAMES.filter(g => !_hiddenGames.includes(g.id)).filter(gameMatchesFilter).sort((a,b) => (a.comingSoon?1:0) - (b.comingSoon?1:0));"

assert OLD3 in content, "OLD3 not found"
content = content.replace(OLD3, NEW3, 1)

# 4. Version bump
content = re.sub(r'v9\.702', 'v9.703', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.703")
