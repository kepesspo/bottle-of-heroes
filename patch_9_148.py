#!/usr/bin/env python3
"""patch_9_148.py — Splash: gyűrűk középre pozicionálva, inline delay, nincs fix kör"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.147';" in content
content = content.replace("const APP_VERSION = 'v9.147';", "const APP_VERSION = 'v9.148';")

# ── 1. Fix ring CSS: centered + fix keyframe conflict with translate ──
OLD_RINGS_CSS = """    .splash-ring {
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

NEW_RINGS_CSS = """    .splash-ring {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 220px;
      height: 220px;
      margin: -110px 0 0 -110px;
      border-radius: 50%;
      border: 1.5px solid rgba(150,80,255,0.35);
      animation: splashRingExpand 4s ease-out infinite;
    }"""

assert OLD_RINGS_CSS in content, "rings CSS not found"
content = content.replace(OLD_RINGS_CSS, NEW_RINGS_CSS, 1)

# ── 2. Fix keyframe: was using scale which overrides nothing now (no translate conflict) ──
OLD_RING_KF = """    @keyframes splashRingExpand {
      0%   { transform: scale(0.6); opacity: 0.75; }
      100% { transform: scale(2.8); opacity: 0; }
    }"""

NEW_RING_KF = """    @keyframes splashRingExpand {
      0%   { transform: scale(0.5); opacity: 0.8; }
      100% { transform: scale(3.0); opacity: 0; }
    }"""

assert OLD_RING_KF in content, "ring keyframe not found"
content = content.replace(OLD_RING_KF, NEW_RING_KF, 1)

# ── 3. Replace ring HTML: add inline animation-delay so nth-child issue disappears ──
OLD_RINGS_HTML = """  <div class="splash-ring"></div>
  <div class="splash-ring"></div>
  <div class="splash-ring"></div>
  <div class="splash-ring"></div>"""

NEW_RINGS_HTML = """  <div class="splash-ring" style="animation-delay:0s"></div>
  <div class="splash-ring" style="animation-delay:1s"></div>
  <div class="splash-ring" style="animation-delay:2s"></div>
  <div class="splash-ring" style="animation-delay:3s"></div>"""

assert OLD_RINGS_HTML in content, "rings HTML not found"
content = content.replace(OLD_RINGS_HTML, NEW_RINGS_HTML, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.148 ready")
