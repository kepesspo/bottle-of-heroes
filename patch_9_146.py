#!/usr/bin/env python3
"""patch_9_146.py — Splash: nincs szöveg, nincs border-radius/shine, lassabb pulzálás"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.145';" in content
content = content.replace("const APP_VERSION = 'v9.145';", "const APP_VERSION = 'v9.146';")

# ── 1. Remove border-radius from logo (no app-icon look) ──
OLD_LOGO_CSS = """    #splash-logo {
      width: 128px;
      height: 128px;
      border-radius: 30px;
      display: block;
      filter: drop-shadow(0 0 32px rgba(140,60,255,0.7)) drop-shadow(0 8px 24px rgba(0,0,0,0.6));
      animation: splashGlow 2.4s ease-in-out infinite;
    }"""

NEW_LOGO_CSS = """    #splash-logo {
      width: 128px;
      height: 128px;
      display: block;
      filter: drop-shadow(0 0 32px rgba(140,60,255,0.7)) drop-shadow(0 8px 24px rgba(0,0,0,0.6));
      animation: splashGlow 4s ease-in-out infinite;
    }"""

assert OLD_LOGO_CSS in content, "logo CSS not found"
content = content.replace(OLD_LOGO_CSS, NEW_LOGO_CSS, 1)

# ── 2. Remove shine div CSS (no glass overlay) ──
OLD_SHINE_CSS = """    #splash-shine {
      position: absolute;
      inset: 0;
      border-radius: 30px;
      background: linear-gradient(135deg, rgba(255,255,255,0.32) 0%, rgba(255,255,255,0) 55%);
      pointer-events: none;
    }"""

NEW_SHINE_CSS = ""

assert OLD_SHINE_CSS in content, "shine CSS not found"
content = content.replace(OLD_SHINE_CSS, NEW_SHINE_CSS, 1)

# ── 3. Remove text CSS ──
OLD_TEXT_CSS = """    #splash-text {
      position: relative;
      z-index: 1;
      margin-top: 28px;
      font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
      font-size: 12px;
      font-weight: 700;
      letter-spacing: 0.22em;
      color: rgba(200,160,255,0.55);
      text-transform: uppercase;
      animation: splashTextFade 0.5s 0.55s ease both;
    }"""

NEW_TEXT_CSS = ""

assert OLD_TEXT_CSS in content, "text CSS not found"
content = content.replace(OLD_TEXT_CSS, NEW_TEXT_CSS, 1)

# ── 4. Slow down bg and ring animations ──
OLD_BG_ANIM  = "      animation: splashBgPulse 2.4s ease-in-out infinite;"
NEW_BG_ANIM  = "      animation: splashBgPulse 4s ease-in-out infinite;"
assert OLD_BG_ANIM in content, "bg anim not found"
content = content.replace(OLD_BG_ANIM, NEW_BG_ANIM, 1)

OLD_RING_ANIM = "      animation: splashRingExpand 2.4s ease-out infinite;"
NEW_RING_ANIM = "      animation: splashRingExpand 4s ease-out infinite;"
assert OLD_RING_ANIM in content, "ring anim not found"
content = content.replace(OLD_RING_ANIM, NEW_RING_ANIM, 1)

OLD_RING_DELAY = "    #splash-rings::after { animation-delay: 1.2s; }"
NEW_RING_DELAY = "    #splash-rings::after { animation-delay: 2s; }"
assert OLD_RING_DELAY in content, "ring delay not found"
content = content.replace(OLD_RING_DELAY, NEW_RING_DELAY, 1)

# ── 5. Remove TextFade keyframes ──
OLD_TEXTFADE = """    @keyframes splashTextFade {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
    }"""
assert OLD_TEXTFADE in content, "textfade not found"
content = content.replace(OLD_TEXTFADE, "", 1)

# ── 6. Remove shine div from HTML ──
OLD_SHINE_HTML = """    <div id="splash-shine"></div>
  </div>"""
NEW_SHINE_HTML = """  </div>"""
assert OLD_SHINE_HTML in content, "shine HTML not found"
content = content.replace(OLD_SHINE_HTML, NEW_SHINE_HTML, 1)

# ── 7. Remove text div from HTML ──
OLD_TEXT_HTML = """  <div id="splash-text">Betöltés...</div>"""
assert OLD_TEXT_HTML in content, "text HTML not found"
content = content.replace(OLD_TEXT_HTML, "", 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.146 ready")
