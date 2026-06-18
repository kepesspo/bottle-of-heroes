#!/usr/bin/env python3
"""patch_9_145.py — Splash: háttér a mentett témának megfelelően"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.144';" in content
content = content.replace("const APP_VERSION = 'v9.144';", "const APP_VERSION = 'v9.145';")

# ── 1. Replace the fixed dark splash background with theme-aware colors ──
# The splash bg div currently has a hardcoded purple radial gradient.
# We replace it with an inline script that reads boh_theme from localStorage
# and applies the matching bg color + a subtle radial gradient overlay.

OLD_SPLASH_BG_CSS = """    #splash-bg {
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse at 50% 45%, #2A0A5E 0%, #0D0620 70%);
      animation: splashBgPulse 2.4s ease-in-out infinite;
    }"""

NEW_SPLASH_BG_CSS = """    #splash-bg {
      position: absolute;
      inset: 0;
      animation: splashBgPulse 2.4s ease-in-out infinite;
    }"""

assert OLD_SPLASH_BG_CSS in content, "splash bg CSS not found"
content = content.replace(OLD_SPLASH_BG_CSS, NEW_SPLASH_BG_CSS, 1)

# ── 2. Change splash root bg from hardcoded dark to transparent (bg set by script) ──
OLD_SPLASH_ROOT = "      background: #0D0620;"
NEW_SPLASH_ROOT = "      background: #F4C57E; /* overridden by inline script */"

assert OLD_SPLASH_ROOT in content, "splash root bg not found"
content = content.replace(OLD_SPLASH_ROOT, NEW_SPLASH_ROOT, 1)

# ── 3. Add inline script right after splash div to apply theme colors instantly ──
# Theme bg colors: warm=#F4C57E, dark=#2C3554, sky=#E4EEF8
# Glow/ring colors adapt too: warm=amber, dark=blue-purple, sky=blue

OLD_AFTER_SPLASH = """<!-- iOS 18+ haptic trigger -->"""

NEW_AFTER_SPLASH = """<script>
(function(){
  var theme = localStorage.getItem('boh_theme') || 'warm';
  var themes = {
    warm: { bg:'#F4C57E', deep:'#E8A040', ring:'rgba(180,100,20,0.35)', glow:'rgba(180,100,20,0.7)' },
    dark: { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)', glow:'rgba(80,110,220,0.7)' },
    sky:  { bg:'#E4EEF8', deep:'#C8D8EE', ring:'rgba(60,120,200,0.3)',  glow:'rgba(60,120,200,0.65)' },
  };
  var t = themes[theme] || themes.warm;
  var splash = document.getElementById('splash');
  var bg     = document.getElementById('splash-bg');
  var logo   = document.getElementById('splash-logo');
  var rings  = document.getElementById('splash-rings');
  if (splash) splash.style.background = t.bg;
  if (bg) bg.style.background = 'radial-gradient(ellipse at 50% 45%, ' + t.deep + ' 0%, ' + t.bg + ' 70%)';
  if (logo) logo.style.filter = 'drop-shadow(0 0 32px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.25))';
  // patch ring color via CSS var workaround: override ::before/::after border via a style tag
  var s = document.createElement('style');
  s.textContent = '#splash-rings::before,#splash-rings::after{border-color:' + t.ring + ';}';
  document.head.appendChild(s);
  // patch glow animation keyframes
  var s2 = document.createElement('style');
  s2.textContent = '@keyframes splashGlow{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.25))}50%{filter:drop-shadow(0 0 52px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.18))}}';
  document.head.appendChild(s2);
})();
</script>
<!-- iOS 18+ haptic trigger -->"""

assert OLD_AFTER_SPLASH in content, "haptic comment not found"
content = content.replace(OLD_AFTER_SPLASH, NEW_AFTER_SPLASH, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.145 ready")
