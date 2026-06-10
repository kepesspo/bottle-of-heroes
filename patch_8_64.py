#!/usr/bin/env python3
"""v8.64: Firestore undefined fix — img:null alapérték + syncRoom sanitize"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

# ── 1. handleSecretTap: img:null hozzáadása ──────────────────────────────────
OLD_SECRET = """        return { id:'p'+Date.now()+i, name:p.nickname||p.name, color, drinks:0, points:0, profileId:p.id };"""
NEW_SECRET = """        return { id:'p'+Date.now()+i, name:p.nickname||p.name, color, drinks:0, points:0, profileId:p.id, img:null };"""

assert OLD_SECRET in content, "handleSecretTap not found"
content = content.replace(OLD_SECRET, NEW_SECRET, 1)
print("✓ handleSecretTap: img:null")

# ── 2. addPlayer: img:null hozzáadása ────────────────────────────────────────
OLD_ADD = """    const np = { id:'p'+Date.now(), name:'', color, drinks:0, points:0 };"""
NEW_ADD = """    const np = { id:'p'+Date.now(), name:'', color, drinks:0, points:0, img:null };"""

assert OLD_ADD in content, "addPlayer not found"
content = content.replace(OLD_ADD, NEW_ADD, 1)
print("✓ addPlayer: img:null")

# ── 3. syncRoom wrapper: undefined → null sanitize ───────────────────────────
OLD_SYNC = """  window.syncRoom = function(code, data) {
    return db.collection('rooms').doc(code).update(data).catch(function(e){ console.warn('syncRoom', e); });
  };"""

NEW_SYNC = """  window.syncRoom = function(code, data) {
    // Firestore nem fogad el undefined értéket — rekurzívan null-ra cseréljük
    function sanitize(obj) {
      if (obj === undefined) return null;
      if (obj === null || typeof obj !== 'object') return obj;
      if (Array.isArray(obj)) return obj.map(sanitize);
      var r = {};
      Object.keys(obj).forEach(function(k) { r[k] = sanitize(obj[k]); });
      return r;
    }
    return db.collection('rooms').doc(code).update(sanitize(data)).catch(function(e){ console.warn('syncRoom', e); });
  };"""

assert OLD_SYNC in content, "syncRoom not found"
content = content.replace(OLD_SYNC, NEW_SYNC, 1)
print("✓ syncRoom: undefined→null sanitize")

# ── 4. Version bump ───────────────────────────────────────────────────────────
OLD_VER = "const APP_VERSION = 'v8.63';"
NEW_VER = "const APP_VERSION = 'v8.64';"
assert OLD_VER in content
content = content.replace(OLD_VER, NEW_VER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)
print("✓ v8.64 saved")
