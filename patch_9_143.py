#!/usr/bin/env python3
"""patch_9_143.py — Splash screen: pulsing logo while app loads"""

import base64

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.142';" in content
content = content.replace("const APP_VERSION = 'v9.142';", "const APP_VERSION = 'v9.143';")

# Read icon base64
with open('icon-192.png', 'rb') as f:
    icon_b64 = 'data:image/png;base64,' + base64.b64encode(f.read()).decode()

# ── 1. Add splash CSS in <style> section ──
OLD_STYLE_END = "#root {\n      height: 100%;\n      width: 100%;\n      display: flex;\n      flex-direction: column;\n      align-items: stretch;\n    }"

NEW_STYLE_END = """#root {
      height: 100%;
      width: 100%;
      display: flex;
      flex-direction: column;
      align-items: stretch;
    }

    #splash {
      position: fixed;
      inset: 0;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #1A0A2E;
      transition: opacity 0.4s ease;
    }
    #splash.hidden {
      opacity: 0;
      pointer-events: none;
    }
    #splash-logo {
      width: 120px;
      height: 120px;
      border-radius: 28px;
      animation: splashPulse 1.2s ease-in-out infinite;
    }
    #splash-text {
      margin-top: 24px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 13px;
      font-weight: 600;
      letter-spacing: 0.12em;
      color: rgba(255,255,255,0.45);
      text-transform: uppercase;
    }
    @keyframes splashPulse {
      0%   { transform: scale(1);    opacity: 1;    box-shadow: 0 0 0 0 rgba(255,255,255,0.18); }
      50%  { transform: scale(1.08); opacity: 0.85; box-shadow: 0 0 0 18px rgba(255,255,255,0); }
      100% { transform: scale(1);    opacity: 1;    box-shadow: 0 0 0 0 rgba(255,255,255,0); }
    }"""

assert OLD_STYLE_END in content, "style end not found"
content = content.replace(OLD_STYLE_END, NEW_STYLE_END, 1)

# ── 2. Add splash HTML after <body> tag ──
OLD_BODY = """<body>
<!-- iOS 18+ haptic trigger -->"""

NEW_BODY = """<body>
<!-- Splash screen -->
<div id="splash">
  <img id="splash-logo" src=\"""" + icon_b64 + """\" alt="Bottle of Heroes" />
  <div id="splash-text">Betöltés...</div>
</div>
<!-- iOS 18+ haptic trigger -->"""

assert OLD_BODY in content, "body tag not found"
content = content.replace(OLD_BODY, NEW_BODY, 1)

# ── 3. Hide splash once React mounts — hook into App's first render ──
# Find where ReactDOM renders the app and add splash hide logic
OLD_RENDER = "ReactDOM.createRoot(document.getElementById('root')).render("

NEW_RENDER = """// Hide splash after React renders
const _origRender = ReactDOM.createRoot;
ReactDOM.createRoot = function(container, opts) {
  const root = _origRender.call(this, container, opts);
  const _origRootRender = root.render.bind(root);
  root.render = function(element) {
    _origRootRender(element);
    requestAnimationFrame(() => {
      const splash = document.getElementById('splash');
      if (splash) {
        splash.classList.add('hidden');
        setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 500);
      }
    });
  };
  return root;
};

ReactDOM.createRoot(document.getElementById('root')).render("""

assert OLD_RENDER in content, "render not found"
content = content.replace(OLD_RENDER, NEW_RENDER, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.143 ready")
