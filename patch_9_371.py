#!/usr/bin/env python3
"""v9.371 — Cinematic IMPACT splash screen: logo drops from sky, shockwave rings, letter slam"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Replace splash CSS (lines 53–124) ──────────────────────────────────────
old_css = """    #splash {
      position: fixed;
      inset: 0;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #F4C57E; /* overridden by inline script */
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
      animation: splashBgPulse 4s ease-in-out infinite;
    }
    .splash-ring {
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
    }
    #splash-logo-wrap {
      position: relative;
      z-index: 1;
      animation: splashHeroEntry 0.75s cubic-bezier(0.34,1.56,0.64,1) both,
                 splashIconPulse 0.65s ease-in-out 0.9s 3;
    }
    #splash-logo {
      width: 180px;
      height: 180px;
      display: block;
      filter: drop-shadow(0 0 40px rgba(140,60,255,0.7)) drop-shadow(0 8px 24px rgba(0,0,0,0.6));
      animation: splashGlow 4s ease-in-out infinite;
    }


    @keyframes splashHeroEntry {
      0%   { transform: scale(0) rotate(-15deg); opacity: 0; }
      60%  { transform: scale(1.13) rotate(4deg); opacity: 1; }
      80%  { transform: scale(0.95) rotate(-2deg); }
      100% { transform: scale(1) rotate(0deg); opacity: 1; }
    }
    @keyframes splashIconPulse {
      0%   { transform: scale(1); }
      45%  { transform: scale(1.13); }
      100% { transform: scale(1); }
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
      0%   { transform: scale(0.5); opacity: 0; }
      8%   { opacity: 0.75; }
      100% { transform: scale(3.2); opacity: 0; }
    }"""

new_css = """    /* ── CINEMATIC IMPACT SPLASH ── */
    #splash {
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
    }
    #splash.hidden {
      opacity: 0;
      pointer-events: none;
    }
    /* Radial ambient bg — fades in after impact */
    #splash-bg {
      position: absolute;
      inset: 0;
      background: radial-gradient(ellipse at 50% 52%, #1a1230 0%, #0a0a0f 70%);
      opacity: 0;
      animation: splashBgReveal 0.4s ease-out 0.72s forwards;
    }
    /* White flash overlay on impact */
    #splash-flash {
      position: absolute;
      inset: 0;
      background: #fff;
      opacity: 0;
      pointer-events: none;
      animation: splashFlash 0.5s ease-out 0.7s both;
    }
    /* Shockwave rings — burst outward on impact */
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
    .splash-shock:nth-child(4) { animation: splashShock 1.1s cubic-bezier(0.1,0.6,0.3,1) 0.94s both; border-width:1px; border-color:rgba(255,255,255,0.25); }
    /* Logo — drops from top with gravity, impacts center */
    #splash-logo-wrap {
      position: relative;
      z-index: 2;
      animation: splashLogoDrop 0.7s cubic-bezier(0.25,0.1,0.25,1.4) 0s both,
                 splashLogoSettle 0.25s ease-out 0.7s both;
    }
    #splash-logo {
      width: 160px;
      height: 160px;
      display: block;
      filter: drop-shadow(0 0 0px rgba(255,255,255,0)) drop-shadow(0 4px 8px rgba(0,0,0,0.8));
      animation: splashLogoGlow 0.6s ease-out 0.72s forwards;
    }
    /* Title — "BOTTLE OF HEROES" letter slam */
    #splash-title-wrap {
      position: relative;
      z-index: 2;
      margin-top: 18px;
      display: flex;
      flex-direction: column;
      align-items: center;
      gap: 2px;
    }
    .splash-word {
      display: flex;
      gap: 1px;
    }
    .splash-letter {
      display: inline-block;
      font-family: 'Arial Black', 'Arial Bold', Arial, sans-serif;
      font-weight: 900;
      font-size: 28px;
      letter-spacing: 3px;
      color: #fff;
      text-shadow: 0 0 0px rgba(255,255,255,0);
      opacity: 0;
      transform: translateY(40px) scaleY(1.4);
    }
    .splash-word-of .splash-letter {
      font-size: 16px;
      letter-spacing: 6px;
      color: rgba(255,255,255,0.6);
    }
    /* Tagline */
    #splash-tagline {
      margin-top: 10px;
      font-family: Arial, sans-serif;
      font-size: 11px;
      letter-spacing: 4px;
      color: rgba(255,255,255,0.35);
      text-transform: uppercase;
      opacity: 0;
      animation: splashTagline 0.5s ease-out 2.2s forwards;
    }

    /* ── Keyframes ── */
    @keyframes splashLogoDrop {
      0%   { transform: translateY(-120vh) scaleY(0.85); opacity: 1; }
      85%  { transform: translateY(8px) scaleY(1.08); }
      100% { transform: translateY(0px) scaleY(1); }
    }
    @keyframes splashLogoSettle {
      0%   { transform: scaleX(1.12) scaleY(0.88); }
      60%  { transform: scaleX(0.97) scaleY(1.03); }
      100% { transform: scaleX(1) scaleY(1); }
    }
    @keyframes splashLogoGlow {
      0%   { filter: drop-shadow(0 0 60px rgba(255,255,255,0.9)) drop-shadow(0 8px 24px rgba(0,0,0,0.8)); }
      100% { filter: drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.6)); }
    }
    @keyframes splashFlash {
      0%   { opacity: 0; }
      15%  { opacity: 0.92; }
      100% { opacity: 0; }
    }
    @keyframes splashShock {
      0%   { transform: scale(1); opacity: 0.9; }
      100% { transform: scale(28); opacity: 0; }
    }
    @keyframes splashBgReveal {
      from { opacity: 0; }
      to   { opacity: 1; }
    }
    @keyframes splashLetterSlam {
      0%   { transform: translateY(40px) scaleY(1.4); opacity: 0; }
      55%  { transform: translateY(-4px) scaleY(0.92); opacity: 1; }
      80%  { transform: translateY(2px) scaleY(1.03); }
      100% { transform: translateY(0) scaleY(1); opacity: 1; }
    }
    @keyframes splashTagline {
      from { opacity: 0; transform: translateY(6px); }
      to   { opacity: 1; transform: translateY(0); }
    }
    @keyframes splashLogoIdle {
      0%,100% { filter: drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.6)); }
      50%      { filter: drop-shadow(0 0 48px var(--splash-glow,rgba(140,60,255,0.9))) drop-shadow(0 8px 32px rgba(0,0,0,0.5)); }
    }"""

assert old_css in html, "FAIL: old splash CSS not found"
html = html.replace(old_css, new_css, 1)

# ── 2. Replace splash HTML ─────────────────────────────────────────────────────
old_html = """<div id="splash" style="display:none">
  <div id="splash-bg"></div>
  <div class="splash-ring" style="animation-delay:0s"></div>
  <div class="splash-ring" style="animation-delay:1s"></div>
  <div class="splash-ring" style="animation-delay:2s"></div>
  <div class="splash-ring" style="animation-delay:3s"></div>
  <div id="splash-logo-wrap">"""

new_html = """<div id="splash" style="display:none">
  <div id="splash-bg"></div>
  <div id="splash-flash"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div id="splash-logo-wrap">"""

assert old_html in html, "FAIL: old splash HTML not found"
html = html.replace(old_html, new_html, 1)

# ── 3. Add title + tagline after closing </div> of logo-wrap (before </div> of splash) ──
old_after_logo = """  </div>

</div>
<script>
(function(){
  var theme = localStorage.getItem('boh_theme') || 'warm';"""

new_after_logo = """  </div>
  <div id="splash-title-wrap">
    <div class="splash-word splash-word-bottle">
      <span class="splash-letter">B</span><span class="splash-letter">O</span><span class="splash-letter">T</span><span class="splash-letter">T</span><span class="splash-letter">L</span><span class="splash-letter">E</span>
    </div>
    <div class="splash-word splash-word-of">
      <span class="splash-letter">O</span><span class="splash-letter">F</span>
    </div>
    <div class="splash-word splash-word-heroes">
      <span class="splash-letter">H</span><span class="splash-letter">E</span><span class="splash-letter">R</span><span class="splash-letter">O</span><span class="splash-letter">E</span><span class="splash-letter">S</span>
    </div>
  </div>
  <div id="splash-tagline">Ivós kalandjáték</div>

</div>
<script>
(function(){
  var theme = localStorage.getItem('boh_theme') || 'warm';"""

assert old_after_logo in html, "FAIL: after-logo anchor not found"
html = html.replace(old_after_logo, new_after_logo, 1)

# ── 4. Replace splash init script body (theme colors + letter animation trigger) ──
old_script_body = """  var t = themes[theme] || themes.warm;
  var splash = document.getElementById('splash');
  var bg     = document.getElementById('splash-bg');
  var logo   = document.getElementById('splash-logo');

  if (splash) splash.style.background = t.bg;
  if (bg) bg.style.background = 'radial-gradient(ellipse at 50% 45%, ' + t.deep + ' 0%, ' + t.bg + ' 70%)';
  if (logo) logo.style.filter = 'drop-shadow(0 0 32px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.25))';
  // patch ring color via CSS var workaround: override ::before/::after border via a style tag
  var s = document.createElement('style');
  s.textContent = '.splash-ring{border-color:' + t.ring + ';}';
  document.head.appendChild(s);
  // patch glow animation keyframes
  var s2 = document.createElement('style');
  s2.textContent = '@keyframes splashGlow{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.25))}50%{filter:drop-shadow(0 0 52px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.18))}}';
  document.head.appendChild(s2);
  // Ha splash ki van kapcsolva, ne jelenjen meg
  var splashEnabled = localStorage.getItem('boh_splash') !== '0';
  if (splashEnabled) {
    splash.style.display = '';
  }"""

new_script_body = """  var t = themes[theme] || themes.warm;
  var splash = document.getElementById('splash');

  // Inject CSS custom property for glow color (used in keyframes)
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
  }

  // Letter slam animation — staggered per letter
  var letters = document.querySelectorAll('.splash-letter');
  var baseDelay = 0.9; // seconds after page load
  var stagger = 0.055;
  letters.forEach(function(el, i) {
    el.style.animation = 'splashLetterSlam 0.35s cubic-bezier(0.22,1,0.36,1) ' + (baseDelay + i * stagger).toFixed(3) + 's both';
  });

  // After letters finish, switch logo to idle glow pulse
  var logo = document.getElementById('splash-logo');
  if (logo) {
    var lettersDone = baseDelay + letters.length * stagger + 0.4;
    setTimeout(function() {
      if (logo) logo.style.animation = 'splashLogoIdle 3s ease-in-out infinite';
    }, lettersDone * 1000);
  }

  // Ha splash ki van kapcsolva, ne jelenjen meg
  var splashEnabled = localStorage.getItem('boh_splash') !== '0';
  if (splashEnabled) {
    splash.style.display = '';
  }"""

assert old_script_body in html, "FAIL: old script body not found"
html = html.replace(old_script_body, new_script_body, 1)

# ── 5. Version bump ────────────────────────────────────────────────────────────
html = html.replace("const APP_VERSION = 'v9.370';", "const APP_VERSION = 'v9.371';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.371 — Cinematic IMPACT splash screen")
