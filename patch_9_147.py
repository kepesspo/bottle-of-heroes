#!/usr/bin/env python3
"""patch_9_147.py — Splash: nagyobb logó, 4 pulzáló gyűrű"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.146';" in content
content = content.replace("const APP_VERSION = 'v9.146';", "const APP_VERSION = 'v9.147';")

# ── 1. Bigger logo ──
OLD_LOGO = """    #splash-logo {
      width: 128px;
      height: 128px;
      display: block;
      filter: drop-shadow(0 0 32px rgba(140,60,255,0.7)) drop-shadow(0 8px 24px rgba(0,0,0,0.6));
      animation: splashGlow 4s ease-in-out infinite;
    }"""

NEW_LOGO = """    #splash-logo {
      width: 180px;
      height: 180px;
      display: block;
      filter: drop-shadow(0 0 40px rgba(140,60,255,0.7)) drop-shadow(0 8px 24px rgba(0,0,0,0.6));
      animation: splashGlow 4s ease-in-out infinite;
    }"""

assert OLD_LOGO in content, "logo CSS not found"
content = content.replace(OLD_LOGO, NEW_LOGO, 1)

# ── 2. Replace 2-ring (::before/::after) system with 4 separate divs ──
OLD_RINGS_CSS = """    #splash-rings {
      position: absolute;
      width: 320px;
      height: 320px;
      border-radius: 50%;
    }
    #splash-rings::before, #splash-rings::after {
      content: '';
      position: absolute;
      inset: 0;
      border-radius: 50%;
      border: 1.5px solid rgba(150,80,255,0.3);
      animation: splashRingExpand 4s ease-out infinite;
    }
    #splash-rings::after { animation-delay: 2s; }"""

NEW_RINGS_CSS = """    .splash-ring {
      position: absolute;
      width: 220px;
      height: 220px;
      border-radius: 50%;
      border: 1.5px solid rgba(150,80,255,0.35);
      animation: splashRingExpand 4s ease-out infinite;
    }
    .splash-ring:nth-child(1) { animation-delay: 0s; }
    .splash-ring:nth-child(2) { animation-delay: 1s; }
    .splash-ring:nth-child(3) { animation-delay: 2s; }
    .splash-ring:nth-child(4) { animation-delay: 3s; }"""

assert OLD_RINGS_CSS in content, "rings CSS not found"
content = content.replace(OLD_RINGS_CSS, NEW_RINGS_CSS, 1)

# ── 3. Update splashRingExpand to start from logo size ──
OLD_RING_KF = """    @keyframes splashRingExpand {
      0%   { transform: scale(0.5); opacity: 0.7; }
      100% { transform: scale(2.0); opacity: 0; }
    }"""

NEW_RING_KF = """    @keyframes splashRingExpand {
      0%   { transform: scale(0.6); opacity: 0.75; }
      100% { transform: scale(2.8); opacity: 0; }
    }"""

assert OLD_RING_KF in content, "ring keyframe not found"
content = content.replace(OLD_RING_KF, NEW_RING_KF, 1)

# ── 4. Replace ring HTML: single div → 4 divs ──
OLD_RINGS_HTML = """  <div id="splash-rings"></div>"""
NEW_RINGS_HTML = """  <div class="splash-ring"></div>
  <div class="splash-ring"></div>
  <div class="splash-ring"></div>
  <div class="splash-ring"></div>"""

assert OLD_RINGS_HTML in content, "rings HTML not found"
content = content.replace(OLD_RINGS_HTML, NEW_RINGS_HTML, 1)

# ── 5. Fix the inline script that overrides ring color (uses old #splash-rings selector) ──
OLD_RING_SCRIPT = "  s.textContent = '#splash-rings::before,#splash-rings::after{border-color:' + t.ring + ';}'"
NEW_RING_SCRIPT = "  s.textContent = '.splash-ring{border-color:' + t.ring + ';}'"

assert OLD_RING_SCRIPT in content, "ring script not found"
content = content.replace(OLD_RING_SCRIPT, NEW_RING_SCRIPT, 1)

# ── 6. Fix inline script that references rings element (no longer needed by id) ──
OLD_RINGS_VAR = "  var rings  = document.getElementById('splash-rings');"
NEW_RINGS_VAR = ""
assert OLD_RINGS_VAR in content, "rings var not found"
content = content.replace(OLD_RINGS_VAR, NEW_RINGS_VAR, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.147 ready")
