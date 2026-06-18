#!/usr/bin/env python3
"""patch_9_149.py — Splash gyűrű fix: fill-mode backwards + opacity 0 start"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.148';" in content
content = content.replace("const APP_VERSION = 'v9.148';", "const APP_VERSION = 'v9.149';")

# ── 1. Add animation-fill-mode: backwards so rings are invisible during delay ──
OLD_RING_CSS = """    .splash-ring {
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

NEW_RING_CSS = """    .splash-ring {
      position: absolute;
      top: 50%;
      left: 50%;
      width: 220px;
      height: 220px;
      margin: -110px 0 0 -110px;
      border-radius: 50%;
      border: 1.5px solid rgba(150,80,255,0.35);
      animation: splashRingExpand 4s ease-out infinite;
      animation-fill-mode: backwards;
    }"""

assert OLD_RING_CSS in content, "ring CSS not found"
content = content.replace(OLD_RING_CSS, NEW_RING_CSS, 1)

# ── 2. Keyframe starts at opacity 0, fades in fast, then expands and fades out ──
OLD_RING_KF = """    @keyframes splashRingExpand {
      0%   { transform: scale(0.5); opacity: 0.8; }
      100% { transform: scale(3.0); opacity: 0; }
    }"""

NEW_RING_KF = """    @keyframes splashRingExpand {
      0%   { transform: scale(0.5); opacity: 0; }
      8%   { opacity: 0.75; }
      100% { transform: scale(3.2); opacity: 0; }
    }"""

assert OLD_RING_KF in content, "ring keyframe not found"
content = content.replace(OLD_RING_KF, NEW_RING_KF, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.149 ready")
