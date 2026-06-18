#!/usr/bin/env python3
"""patch_9_153.py — Splash: ikon 3x pulzál a hero entry után"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.152';" in content
content = content.replace("const APP_VERSION = 'v9.152';", "const APP_VERSION = 'v9.153';")

OLD_WRAP = """    #splash-logo-wrap {
      position: relative;
      z-index: 1;
      animation: splashHeroEntry 0.75s cubic-bezier(0.34,1.56,0.64,1) both;
    }"""

NEW_WRAP = """    #splash-logo-wrap {
      position: relative;
      z-index: 1;
      animation: splashHeroEntry 0.75s cubic-bezier(0.34,1.56,0.64,1) both,
                 splashIconPulse 0.65s ease-in-out 0.9s 3;
    }"""

assert OLD_WRAP in content, "wrap not found"
content = content.replace(OLD_WRAP, NEW_WRAP, 1)

OLD_ENTRY_KF = """    @keyframes splashHeroEntry {
      0%   { transform: scale(0) rotate(-15deg); opacity: 0; }
      60%  { transform: scale(1.13) rotate(4deg); opacity: 1; }
      80%  { transform: scale(0.95) rotate(-2deg); }
      100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }"""

NEW_ENTRY_KF = """    @keyframes splashHeroEntry {
      0%   { transform: scale(0) rotate(-15deg); opacity: 0; }
      60%  { transform: scale(1.13) rotate(4deg); opacity: 1; }
      80%  { transform: scale(0.95) rotate(-2deg); }
      100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    @keyframes splashIconPulse {
      0%   { transform: scale(1); }
      45%  { transform: scale(1.13); }
      100% { transform: scale(1); }
    }"""

assert OLD_ENTRY_KF in content, "entry keyframe not found"
content = content.replace(OLD_ENTRY_KF, NEW_ENTRY_KF, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.153 ready")
