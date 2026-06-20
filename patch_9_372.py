#!/usr/bin/env python3
"""v9.372 — Fix splash: restore theme-color bg, keep logo drop + flash + shockwave + letter slam"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Fix #splash background: dark → theme color ──────────────────────────────
old_splash_bg_css = """    #splash {
      position: fixed;
      inset: 0;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #0a0a0f;
      transition: opacity 0.6s ease;
      overflow: hidden;
    }"""

new_splash_bg_css = """    #splash {
      position: fixed;
      inset: 0;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #F4C57E; /* overridden by inline script */
      transition: opacity 0.6s ease;
      overflow: hidden;
    }"""

assert old_splash_bg_css in html, "FAIL: splash bg css"
html = html.replace(old_splash_bg_css, new_splash_bg_css, 1)

# ── 2. Fix #splash-bg: dark radial → theme radial (will be set by JS) ──────────
old_splashbg_css = """    /* Radial ambient bg — fades in after impact */
    #splash-bg {
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse at 50% 52%, #1a1230 0%, #0a0a0f 70%);
      opacity: 0;
      animation: splashBgReveal 0.4s ease-out 0.72s forwards;
    }"""

new_splashbg_css = """    /* Radial ambient bg — set by JS per theme */
    #splash-bg {
      position: absolute;
      inset: 0;
    }"""

assert old_splashbg_css in html, "FAIL: splash-bg css"
html = html.replace(old_splashbg_css, new_splashbg_css, 1)

# ── 3. Remove splashBgReveal keyframe ──────────────────────────────────────────
old_bgreveal = """    @keyframes splashBgReveal {
      from { opacity: 0; }
      to   { opacity: 1; }
    }"""

new_bgreveal = ""

html = html.replace(old_bgreveal, new_bgreveal, 1)

# ── 4. Fix inline JS: restore theme bg + radial gradient, remove dark bg logic ──
old_js = """  // Inject CSS custom property for glow color (used in keyframes)
  var s = document.createElement('style');
  s.textContent = ':root{--splash-glow:' + t.glow + ';--splash-ring:' + t.ring + ';}' +
    '@keyframes splashLogoIdle{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.6));}50%{filter:drop-shadow(0 0 48px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.5));}}' +
    // Transition background from dark to theme color after impact
    '@keyframes splashBgColor{0%{background:#0a0a0f}100%{background:' + t.bg + '}}';
  document.head.appendChild(s);

  // Bg color transition: dark → theme, triggered after impact
  if (splash) {
    splash.style.background = '#0a0a0f';
    splash.style.animation = 'splashBgColor 1.2s ease-out 0.8s forwards';
  }"""

new_js = """  // Set theme colors
  var bg = document.getElementById('splash-bg');
  if (splash) splash.style.background = t.bg;
  if (bg) bg.style.background = 'radial-gradient(ellipse at 50% 45%, ' + t.deep + ' 0%, ' + t.bg + ' 70%)';

  // Inject CSS custom property for glow color (used in keyframes)
  var s = document.createElement('style');
  s.textContent = ':root{--splash-glow:' + t.glow + ';--splash-ring:' + t.ring + ';}' +
    '@keyframes splashLogoIdle{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.3));}50%{filter:drop-shadow(0 0 48px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.2));}}';
  document.head.appendChild(s);"""

assert old_js in html, "FAIL: old js block"
html = html.replace(old_js, new_js, 1)

# ── 5. Also fix the flash color — on a light bg white flash is invisible,
#       use a bright white with slight theme tint instead (keep as-is, it works)
# ── Actually make flash slightly dimmer so it doesn't blow out on light themes
old_flash_anim = """    @keyframes splashFlash {
      0%   { opacity: 0; }
      15%  { opacity: 0.92; }
      100% { opacity: 0; }
    }"""

new_flash_anim = """    @keyframes splashFlash {
      0%   { opacity: 0; }
      15%  { opacity: 0.75; }
      100% { opacity: 0; }
    }"""

html = html.replace(old_flash_anim, new_flash_anim, 1)

# ── 6. Fix logo glow — on light bg use theme glow from the start ───────────────
old_logo_glow_anim = """    @keyframes splashLogoGlow {
      0%   { filter: drop-shadow(0 0 60px rgba(255,255,255,0.9)) drop-shadow(0 8px 24px rgba(0,0,0,0.8)); }
      100% { filter: drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.6)); }
    }"""

new_logo_glow_anim = """    @keyframes splashLogoGlow {
      0%   { filter: drop-shadow(0 0 40px rgba(255,255,255,0.8)) drop-shadow(0 8px 24px rgba(0,0,0,0.4)); }
      100% { filter: drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.3)); }
    }"""

html = html.replace(old_logo_glow_anim, new_logo_glow_anim, 1)

# ── 7. Also fix logo initial filter (dark drop-shadow too heavy on light bg) ───
old_logo_filter = """      filter: drop-shadow(0 0 0px rgba(255,255,255,0)) drop-shadow(0 4px 8px rgba(0,0,0,0.8));"""
new_logo_filter = """      filter: drop-shadow(0 0 0px rgba(255,255,255,0)) drop-shadow(0 4px 8px rgba(0,0,0,0.3));"""

html = html.replace(old_logo_filter, new_logo_filter, 1)

# ── 8. Fix shock rings color — white on light bg is barely visible, use dark ───
old_shock_css = """    /* Shockwave rings — burst outward on impact */
    .splash-shock {
      position: absolute;
      top: 50%; left: 50%;
      width: 10px; height: 10px;
      margin: -5px 0 0 -5px;
      border-radius: 50%;
      border: 3px solid rgba(255,255,255,0.9);
      opacity: 0;
      pointer-events: none;
    }
    .splash-shock:nth-child(1) { animation: splashShock 0.7s cubic-bezier(0.1,0.6,0.3,1) 0.70s both; }
    .splash-shock:nth-child(2) { animation: splashShock 0.8s cubic-bezier(0.1,0.6,0.3,1) 0.78s both; border-width:2px; }
    .splash-shock:nth-child(3) { animation: splashShock 0.9s cubic-bezier(0.1,0.6,0.3,1) 0.86s both; border-width:1.5px; border-color:rgba(255,255,255,0.5); }
    .splash-shock:nth-child(4) { animation: splashShock 1.1s cubic-bezier(0.1,0.6,0.3,1) 0.94s both; border-width:1px; border-color:rgba(255,255,255,0.25); }"""

new_shock_css = """    /* Shockwave rings — burst outward on impact */
    .splash-shock {
      position: absolute;
      top: 50%; left: 50%;
      width: 10px; height: 10px;
      margin: -5px 0 0 -5px;
      border-radius: 50%;
      border: 3px solid rgba(0,0,0,0.35);
      opacity: 0;
      pointer-events: none;
    }
    .splash-shock:nth-child(1) { animation: splashShock 0.7s cubic-bezier(0.1,0.6,0.3,1) 0.70s both; }
    .splash-shock:nth-child(2) { animation: splashShock 0.8s cubic-bezier(0.1,0.6,0.3,1) 0.78s both; border-width:2px; }
    .splash-shock:nth-child(3) { animation: splashShock 0.9s cubic-bezier(0.1,0.6,0.3,1) 0.86s both; border-width:1.5px; border-color:rgba(0,0,0,0.2); }
    .splash-shock:nth-child(4) { animation: splashShock 1.1s cubic-bezier(0.1,0.6,0.3,1) 0.94s both; border-width:1px; border-color:rgba(0,0,0,0.12); }"""

assert old_shock_css in html, "FAIL: shock css"
html = html.replace(old_shock_css, new_shock_css, 1)

# ── 9. Fix flash color — use rgba(255,255,255,0.75) on light bg = bright white still visible
# (flash already dimmed in step 5, good)

# ── 10. Fix letter color — on light bg white text is invisible ─────────────────
old_letter_color = """      color: #fff;
      text-shadow: 0 0 0px rgba(255,255,255,0);"""

new_letter_color = """      color: rgba(0,0,0,0.75);
      text-shadow: 0 2px 8px rgba(0,0,0,0.15);"""

html = html.replace(old_letter_color, new_letter_color, 1)

old_of_color = """      color: rgba(255,255,255,0.6);"""
new_of_color = """      color: rgba(0,0,0,0.45);"""

html = html.replace(old_of_color, new_of_color, 1)

# ── 11. Fix tagline color ───────────────────────────────────────────────────────
old_tagline_color = """      color: rgba(255,255,255,0.35);"""
new_tagline_color = """      color: rgba(0,0,0,0.4);"""

html = html.replace(old_tagline_color, new_tagline_color, 1)

# ── 12. Version bump ────────────────────────────────────────────────────────────
html = html.replace("const APP_VERSION = 'v9.371';", "const APP_VERSION = 'v9.372';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.372 — Splash: theme bg restored, logo drop + flash + shock + letter slam kept")
