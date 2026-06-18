#!/usr/bin/env python3
"""patch_9_144.py — Splash screen: király hero-entry animáció"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.143';" in content
content = content.replace("const APP_VERSION = 'v9.143';", "const APP_VERSION = 'v9.144';")

# ── 1. Replace splash CSS ──
OLD_SPLASH_CSS = """    #splash {
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

NEW_SPLASH_CSS = """    #splash {
      position: fixed;
      inset: 0;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #0D0620;
      transition: opacity 0.5s ease;
      overflow: hidden;
    }
    #splash.hidden {
      opacity: 0;
      pointer-events: none;
    }
    #splash-bg {
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse at 50% 45%, #2A0A5E 0%, #0D0620 70%);
      animation: splashBgPulse 2.4s ease-in-out infinite;
    }
    #splash-rings {
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
      animation: splashRingExpand 2.4s ease-out infinite;
    }
    #splash-rings::after { animation-delay: 1.2s; }
    #splash-logo-wrap {
      position: relative;
      z-index: 1;
      animation: splashHeroEntry 0.75s cubic-bezier(0.34,1.56,0.64,1) both;
    }
    #splash-logo {
      width: 128px;
      height: 128px;
      border-radius: 30px;
      display: block;
      filter: drop-shadow(0 0 32px rgba(140,60,255,0.7)) drop-shadow(0 8px 24px rgba(0,0,0,0.6));
      animation: splashGlow 2.4s ease-in-out infinite;
    }
    #splash-shine {
      position: absolute;
      inset: 0;
      border-radius: 30px;
      background: linear-gradient(135deg, rgba(255,255,255,0.32) 0%, rgba(255,255,255,0) 55%);
      pointer-events: none;
    }
    #splash-text {
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
    }
    @keyframes splashHeroEntry {
      0%   { transform: scale(0) rotate(-15deg); opacity: 0; }
      60%  { transform: scale(1.13) rotate(4deg); opacity: 1; }
      80%  { transform: scale(0.95) rotate(-2deg); }
      100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    @keyframes splashGlow {
      0%,100% { filter: drop-shadow(0 0 28px rgba(140,60,255,0.65)) drop-shadow(0 8px 24px rgba(0,0,0,0.6)); }
      50%      { filter: drop-shadow(0 0 52px rgba(190,90,255,0.98)) drop-shadow(0 8px 32px rgba(0,0,0,0.5)); }
    }
    @keyframes splashBgPulse {
      0%,100% { opacity: 1; }
      50%      { opacity: 0.7; }
    }
    @keyframes splashRingExpand {
      0%   { transform: scale(0.5); opacity: 0.7; }
      100% { transform: scale(2.0); opacity: 0; }
    }
    @keyframes splashTextFade {
      from { opacity: 0; transform: translateY(10px); }
      to   { opacity: 1; transform: translateY(0); }
    }"""

assert OLD_SPLASH_CSS in content, "splash CSS not found"
content = content.replace(OLD_SPLASH_CSS, NEW_SPLASH_CSS, 1)

# ── 2. Replace splash HTML: add bg, rings, wrap, shine elements ──
OLD_SPLASH_HTML = """<div id="splash">
  <img id="splash-logo" src="""

NEW_SPLASH_HTML = """<div id="splash">
  <div id="splash-bg"></div>
  <div id="splash-rings"></div>
  <div id="splash-logo-wrap">
    <img id="splash-logo" src="""

assert OLD_SPLASH_HTML in content, "splash HTML open not found"
content = content.replace(OLD_SPLASH_HTML, NEW_SPLASH_HTML, 1)

OLD_SPLASH_CLOSE = """" alt="Bottle of Heroes" />
  <div id="splash-text">Betöltés...</div>
</div>"""

NEW_SPLASH_CLOSE = """" alt="Bottle of Heroes" />
    <div id="splash-shine"></div>
  </div>
  <div id="splash-text">Betöltés...</div>
</div>"""

assert OLD_SPLASH_CLOSE in content, "splash HTML close not found"
content = content.replace(OLD_SPLASH_CLOSE, NEW_SPLASH_CLOSE, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.144 ready")
