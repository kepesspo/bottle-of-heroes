#!/usr/bin/env python3
"""v9.375 — 4 splash screen stílusok + választó a beállításokban
  1. impact  — logó zuhan, flash + shockwave gyűrűk, betű slam (az eddigi)
  2. pulse   — logó szívdobogásszerűen lüktet 3x, minden ütésnél gyűrű
  3. reveal  — shimmer fénycsík söpör végig a logón, cím fade-in
  4. stamp   — logó lebélyegzés, remegés, cím keret berajzolódik
"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════
# 1. REPLACE SPLASH CSS
# ══════════════════════════════════════════════════════════════

old_css_start = """    /* ── CINEMATIC IMPACT SPLASH ── */
    #splash {"""
old_css_end = """    @keyframes splashLogoIdle {
      0%,100% { filter: drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.6)); }
      50%      { filter: drop-shadow(0 0 48px var(--splash-glow,rgba(140,60,255,0.9))) drop-shadow(0 8px 32px rgba(0,0,0,0.5)); }
    }"""

# Find and cut out the whole old splash CSS block
idx_start = html.index(old_css_start)
idx_end   = html.index(old_css_end) + len(old_css_end)
old_splash_css = html[idx_start:idx_end]

new_splash_css = """    /* ══ SPLASH SCREEN — shared base ══ */
    #splash {
      position: fixed;
      inset: 0;
      z-index: 99999;
      display: flex;
      flex-direction: column;
      align-items: center;
      justify-content: center;
      background: #F4C57E;
      transition: opacity 0.6s ease;
      overflow: hidden;
    }
    #splash.hidden { opacity:0; pointer-events:none; }
    #splash-bg { position:absolute; inset:0; }

    /* shared logo wrap */
    #splash-logo-wrap { position:relative; z-index:2; }
    #splash-logo { width:160px; height:160px; display:block; }

    /* shared title */
    #splash-title-wrap { position:relative; z-index:2; margin-top:18px; display:flex; flex-direction:column; align-items:center; gap:2px; }
    .splash-word { display:flex; gap:1px; }
    .splash-letter { display:inline-block; font-family:'Arial Black','Arial Bold',Arial,sans-serif; font-weight:900; font-size:28px; letter-spacing:3px; }
    .splash-word-of .splash-letter { font-size:16px; letter-spacing:6px; }
    #splash-tagline { margin-top:10px; font-family:Arial,sans-serif; font-size:11px; letter-spacing:4px; text-transform:uppercase; }

    /* ── STYLE 1: IMPACT ── */
    #splash[data-style="impact"] #splash-flash {
      position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none;
      animation: splashFlash 0.5s ease-out 0.7s both;
    }
    #splash[data-style="impact"] .splash-shock {
      position:absolute; top:50%; left:50%; width:10px; height:10px; margin:-5px 0 0 -5px;
      border-radius:50%; border:3px solid rgba(0,0,0,0.3); opacity:0; pointer-events:none;
    }
    #splash[data-style="impact"] .splash-shock:nth-child(3) { animation:splashShock 0.70s cubic-bezier(0.1,0.6,0.3,1) 0.70s both; }
    #splash[data-style="impact"] .splash-shock:nth-child(4) { animation:splashShock 0.80s cubic-bezier(0.1,0.6,0.3,1) 0.78s both; border-width:2px; }
    #splash[data-style="impact"] .splash-shock:nth-child(5) { animation:splashShock 0.90s cubic-bezier(0.1,0.6,0.3,1) 0.86s both; border-width:1.5px; border-color:rgba(0,0,0,0.15); }
    #splash[data-style="impact"] .splash-shock:nth-child(6) { animation:splashShock 1.10s cubic-bezier(0.1,0.6,0.3,1) 0.94s both; border-width:1px; border-color:rgba(0,0,0,0.08); }
    #splash[data-style="impact"] #splash-logo-wrap {
      animation: impactDrop 0.7s cubic-bezier(0.25,0.1,0.25,1.4) 0s both,
                 impactSettle 0.25s ease-out 0.7s both;
    }
    #splash[data-style="impact"] #splash-logo {
      filter: drop-shadow(0 4px 8px rgba(0,0,0,0.25));
      animation: impactGlow 0.6s ease-out 0.72s forwards;
    }
    #splash[data-style="impact"] .splash-letter { color:rgba(0,0,0,0.75); opacity:0; transform:translateY(40px) scaleY(1.4); }
    #splash[data-style="impact"] .splash-word-of .splash-letter { color:rgba(0,0,0,0.4); }
    #splash[data-style="impact"] #splash-tagline { color:rgba(0,0,0,0.35); opacity:0; animation:splashTagline 0.5s ease-out 2.2s forwards; }

    /* ── STYLE 2: PULSE ── */
    #splash[data-style="pulse"] #splash-logo-wrap {
      animation: pulseBounce 2.4s cubic-bezier(0.36,0.07,0.19,0.97) 0.2s both;
    }
    #splash[data-style="pulse"] #splash-logo {
      filter: drop-shadow(0 4px 16px var(--splash-glow,rgba(140,60,255,0.5)));
    }
    #splash[data-style="pulse"] .splash-shock {
      position:absolute; top:50%; left:50%; width:10px; height:10px; margin:-5px 0 0 -5px;
      border-radius:50%; border:2px solid var(--splash-ring,rgba(0,0,0,0.25)); opacity:0; pointer-events:none;
    }
    #splash[data-style="pulse"] .splash-shock:nth-child(3) { animation:pulseRing 0.8s ease-out 0.35s both; }
    #splash[data-style="pulse"] .splash-shock:nth-child(4) { animation:pulseRing 0.8s ease-out 1.05s both; }
    #splash[data-style="pulse"] .splash-shock:nth-child(5) { animation:pulseRing 0.8s ease-out 1.75s both; }
    #splash[data-style="pulse"] .splash-shock:nth-child(6) { animation:pulseRing 0.8s ease-out 1.80s both; border-color:rgba(0,0,0,0.12); }
    #splash[data-style="pulse"] .splash-letter { color:rgba(0,0,0,0.75); opacity:0; animation:pulseTitleIn 0.5s ease-out 1.9s both; }
    #splash[data-style="pulse"] .splash-word-of .splash-letter { color:rgba(0,0,0,0.4); }
    #splash[data-style="pulse"] #splash-tagline { color:rgba(0,0,0,0.35); opacity:0; animation:splashTagline 0.5s ease-out 2.4s forwards; }

    /* ── STYLE 3: REVEAL ── */
    #splash[data-style="reveal"] #splash-logo-wrap { opacity:0; animation:revealFadeIn 0.01s 0s forwards; }
    #splash[data-style="reveal"] #splash-logo {
      filter: drop-shadow(0 4px 16px var(--splash-glow,rgba(140,60,255,0.5)));
    }
    #splash[data-style="reveal"] #splash-logo-wrap::after {
      content:''; position:absolute; inset:-10px; border-radius:50%;
      background: linear-gradient(105deg, transparent 30%, rgba(255,255,255,0.85) 50%, transparent 70%);
      background-size:300% 100%; background-position:120% 0;
      animation: revealSweep 0.9s cubic-bezier(0.4,0,0.2,1) 0.3s both;
    }
    #splash[data-style="reveal"] .splash-letter {
      color:rgba(0,0,0,0.75); opacity:0;
    }
    #splash[data-style="reveal"] .splash-word-of .splash-letter { color:rgba(0,0,0,0.4); }
    #splash[data-style="reveal"] #splash-tagline { color:rgba(0,0,0,0.35); opacity:0; animation:splashTagline 0.5s ease-out 2.0s forwards; }

    /* ── STYLE 4: STAMP ── */
    #splash[data-style="stamp"] #splash-logo-wrap {
      animation: stampDrop 0.25s cubic-bezier(0.5,0,1,1) 0.15s both,
                 stampShake 0.35s cubic-bezier(0.36,0.07,0.19,0.97) 0.4s both;
    }
    #splash[data-style="stamp"] #splash-logo {
      filter: drop-shadow(0 8px 24px rgba(0,0,0,0.35));
      animation: stampGlow 0.3s ease-out 0.4s forwards;
    }
    #splash[data-style="stamp"] #splash-title-wrap {
      position:relative; z-index:2; margin-top:18px;
    }
    #splash[data-style="stamp"] .splash-letter { color:rgba(0,0,0,0.75); opacity:0; }
    #splash[data-style="stamp"] .splash-word-of .splash-letter { color:rgba(0,0,0,0.4); }
    #splash[data-style="stamp"] #splash-tagline { color:rgba(0,0,0,0.35); opacity:0; animation:splashTagline 0.5s ease-out 1.8s forwards; }
    /* Decorative stamp border that draws in */
    #splash-stamp-frame {
      position:absolute; z-index:1;
      border:3px solid rgba(0,0,0,0.2); border-radius:24px;
      opacity:0;
    }

    /* ══ SHARED KEYFRAMES ══ */
    @keyframes splashFlash { 0%{opacity:0} 15%{opacity:0.75} 100%{opacity:0} }
    @keyframes splashShock { 0%{transform:scale(1);opacity:0.85} 100%{transform:scale(28);opacity:0} }
    @keyframes splashTagline { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
    @keyframes splashLetterSlam {
      0%  {transform:translateY(40px) scaleY(1.4);opacity:0}
      55% {transform:translateY(-4px) scaleY(0.92);opacity:1}
      80% {transform:translateY(2px) scaleY(1.03)}
      100%{transform:translateY(0) scaleY(1);opacity:1}
    }
    /* IMPACT */
    @keyframes impactDrop {
      0%  {transform:translateY(-120vh) scaleY(0.85)}
      85% {transform:translateY(8px) scaleY(1.08)}
      100%{transform:translateY(0) scaleY(1)}
    }
    @keyframes impactSettle {
      0%  {transform:scaleX(1.12) scaleY(0.88)}
      60% {transform:scaleX(0.97) scaleY(1.03)}
      100%{transform:scaleX(1) scaleY(1)}
    }
    @keyframes impactGlow {
      0%  {filter:drop-shadow(0 0 40px rgba(255,255,255,0.7)) drop-shadow(0 8px 24px rgba(0,0,0,0.3))}
      100%{filter:drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.25))}
    }
    /* PULSE */
    @keyframes pulseBounce {
      0%  {transform:scale(0.3);opacity:0}
      18% {transform:scale(1.18);opacity:1}
      30% {transform:scale(0.95)}
      42% {transform:scale(1.1)}
      54% {transform:scale(0.97)}
      64% {transform:scale(1.06)}
      74% {transform:scale(0.99)}
      82% {transform:scale(1.03)}
      90% {transform:scale(1)}
      100%{transform:scale(1)}
    }
    @keyframes pulseRing {
      0%  {transform:scale(1);opacity:0.7}
      100%{transform:scale(18);opacity:0}
    }
    @keyframes pulseTitleIn { from{opacity:0;transform:translateY(10px)} to{opacity:1;transform:translateY(0)} }
    /* REVEAL */
    @keyframes revealFadeIn { to{opacity:1} }
    @keyframes revealSweep {
      from{background-position:120% 0}
      to  {background-position:-20% 0}
    }
    @keyframes revealLetterIn {
      from{opacity:0;transform:translateX(-8px)}
      to  {opacity:1;transform:translateX(0)}
    }
    /* STAMP */
    @keyframes stampDrop {
      0%  {transform:translateY(-80vh) rotate(-3deg);opacity:0.8}
      100%{transform:translateY(0) rotate(0deg);opacity:1}
    }
    @keyframes stampShake {
      0%  {transform:translateX(0) scaleX(1.08) scaleY(0.92)}
      20% {transform:translateX(-6px)}
      40% {transform:translateX(5px)}
      60% {transform:translateX(-3px)}
      80% {transform:translateX(2px)}
      100%{transform:translateX(0)}
    }
    @keyframes stampGlow {
      from{filter:drop-shadow(0 0 32px rgba(255,255,255,0.6)) drop-shadow(0 8px 24px rgba(0,0,0,0.4))}
      to  {filter:drop-shadow(0 4px 16px var(--splash-glow,rgba(140,60,255,0.5))) drop-shadow(0 8px 24px rgba(0,0,0,0.2))}
    }
    @keyframes stampFrameIn {
      from{opacity:0;transform:scale(0.7)}
      to  {opacity:1;transform:scale(1)}
    }
    @keyframes stampLetterIn {
      from{opacity:0;transform:scale(1.4)}
      to  {opacity:1;transform:scale(1)}
    }
    /* shared idle glow */
    @keyframes splashLogoIdle {
      0%,100%{filter:drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.3))}
      50%    {filter:drop-shadow(0 0 48px var(--splash-glow,rgba(140,60,255,0.9))) drop-shadow(0 8px 32px rgba(0,0,0,0.2))}
    }"""

html = html.replace(old_splash_css, new_splash_css, 1)

# ══════════════════════════════════════════════════════════════
# 2. REPLACE SPLASH HTML
# ══════════════════════════════════════════════════════════════

old_splash_html = """<div id="splash" style="display:none">
  <div id="splash-bg"></div>
  <div id="splash-flash"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div id="splash-logo-wrap">"""

new_splash_html = """<div id="splash" style="display:none" data-style="impact">
  <div id="splash-bg"></div>
  <div id="splash-flash"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div class="splash-shock"></div>
  <div id="splash-logo-wrap">"""

assert old_splash_html in html, "FAIL: splash HTML"
html = html.replace(old_splash_html, new_splash_html, 1)

# ══════════════════════════════════════════════════════════════
# 3. REPLACE INIT SCRIPT
# ══════════════════════════════════════════════════════════════

old_script = """(function(){
  var theme = localStorage.getItem('boh_theme') || 'warm';
  var themes = {
    warm:  { bg:'#F4C57E', deep:'#E8B260', ring:'rgba(180,100,20,0.35)',  glow:'rgba(180,100,20,0.7)' },
    dark:  { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)',  glow:'rgba(80,110,220,0.7)' },
    peach: { bg:'#FFE8D8', deep:'#FFD8C0', ring:'rgba(180,70,0,0.35)',   glow:'rgba(210,80,20,0.7)' },
    lemon: { bg:'#F8F8D8', deep:'#F0F0B8', ring:'rgba(100,100,0,0.35)',  glow:'rgba(130,130,0,0.7)' },
    berry: { bg:'#F0E8F8', deep:'#E0D0F0', ring:'rgba(120,0,180,0.35)', glow:'rgba(150,20,200,0.7)' },
    ice:   { bg:'#E8F4FF', deep:'#D0E8FF', ring:'rgba(0,60,160,0.35)',   glow:'rgba(20,90,200,0.7)' },
    slate: { bg:'#E8EBF0', deep:'#D4D9E4', ring:'rgba(80,100,130,0.35)', glow:'rgba(90,110,150,0.7)' },
    jade:  { bg:'#E8F5EE', deep:'#D0EBD8', ring:'rgba(30,120,70,0.35)',  glow:'rgba(40,140,80,0.7)' },
  };
  var t = themes[theme] || themes.warm;
  var splash = document.getElementById('splash');

  // Set theme colors
  var bg = document.getElementById('splash-bg');
  if (splash) splash.style.background = t.bg;
  if (bg) bg.style.background = 'radial-gradient(ellipse at 50% 45%, ' + t.deep + ' 0%, ' + t.bg + ' 70%)';

  // Inject CSS custom property for glow color (used in keyframes)
  var s = document.createElement('style');
  s.textContent = ':root{--splash-glow:' + t.glow + ';--splash-ring:' + t.ring + ';}' +
    '@keyframes splashLogoIdle{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.3));}50%{filter:drop-shadow(0 0 48px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.2));}}';
  document.head.appendChild(s);

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
  }
})();"""

new_script = """(function(){
  var theme      = localStorage.getItem('boh_theme') || 'warm';
  var splashStyle = localStorage.getItem('boh_splash_style') || 'impact';
  var themes = {
    warm:  { bg:'#F4C57E', deep:'#E8B260', ring:'rgba(180,100,20,0.35)',  glow:'rgba(180,100,20,0.7)' },
    dark:  { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)',  glow:'rgba(80,110,220,0.7)' },
    peach: { bg:'#FFE8D8', deep:'#FFD8C0', ring:'rgba(180,70,0,0.35)',   glow:'rgba(210,80,20,0.7)' },
    lemon: { bg:'#F8F8D8', deep:'#F0F0B8', ring:'rgba(100,100,0,0.35)',  glow:'rgba(130,130,0,0.7)' },
    berry: { bg:'#F0E8F8', deep:'#E0D0F0', ring:'rgba(120,0,180,0.35)', glow:'rgba(150,20,200,0.7)' },
    ice:   { bg:'#E8F4FF', deep:'#D0E8FF', ring:'rgba(0,60,160,0.35)',   glow:'rgba(20,90,200,0.7)' },
    slate: { bg:'#E8EBF0', deep:'#D4D9E4', ring:'rgba(80,100,130,0.35)', glow:'rgba(90,110,150,0.7)' },
    jade:  { bg:'#E8F5EE', deep:'#D0EBD8', ring:'rgba(30,120,70,0.35)',  glow:'rgba(40,140,80,0.7)' },
  };
  var t = themes[theme] || themes.warm;
  var splash = document.getElementById('splash');
  if (!splash) return;

  // Set style attribute
  splash.setAttribute('data-style', splashStyle);

  // Set theme colors
  var bg = document.getElementById('splash-bg');
  splash.style.background = t.bg;
  if (bg) bg.style.background = 'radial-gradient(ellipse at 50% 45%, ' + t.deep + ' 0%, ' + t.bg + ' 70%)';

  // CSS custom properties for glow/ring
  var s = document.createElement('style');
  s.textContent = ':root{--splash-glow:' + t.glow + ';--splash-ring:' + t.ring + ';}' +
    '@keyframes splashLogoIdle{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.3));}50%{filter:drop-shadow(0 0 48px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.2));}}';
  document.head.appendChild(s);

  var logo    = document.getElementById('splash-logo');
  var letters = document.querySelectorAll('.splash-letter');
  var idleAt  = 2.8;

  if (splashStyle === 'impact') {
    // Letters slam in staggered
    var base = 0.9, stagger = 0.055;
    letters.forEach(function(el, i) {
      el.style.animation = 'splashLetterSlam 0.35s cubic-bezier(0.22,1,0.36,1) ' + (base + i*stagger).toFixed(3) + 's both';
    });
    idleAt = base + letters.length * stagger + 0.4;

  } else if (splashStyle === 'pulse') {
    // All letters appear together after last pulse
    letters.forEach(function(el) {
      el.style.animation = 'pulseTitleIn 0.5s ease-out 1.9s both';
    });
    idleAt = 2.5;

  } else if (splashStyle === 'reveal') {
    // Logo visible instantly, sweep runs via CSS
    // Letters reveal left-to-right staggered
    var base = 1.3, stagger = 0.06;
    letters.forEach(function(el, i) {
      el.style.animation = 'revealLetterIn 0.3s ease-out ' + (base + i*stagger).toFixed(3) + 's both';
    });
    idleAt = base + letters.length * stagger + 0.3;

  } else if (splashStyle === 'stamp') {
    // Stamp frame appears
    var frame = document.getElementById('splash-stamp-frame');
    if (frame) {
      // Size frame to wrap logo + title
      frame.style.animation = 'stampFrameIn 0.3s cubic-bezier(0.34,1.56,0.64,1) 0.6s both';
    }
    // Letters appear together with scale-in
    var base = 0.75, stagger = 0.04;
    letters.forEach(function(el, i) {
      el.style.animation = 'stampLetterIn 0.25s cubic-bezier(0.34,1.56,0.64,1) ' + (base + i*stagger).toFixed(3) + 's both';
    });
    idleAt = 1.5;
  }

  // Switch logo to idle glow after animation
  if (logo) {
    setTimeout(function() {
      if (logo) logo.style.animation = 'splashLogoIdle 3s ease-in-out infinite';
    }, idleAt * 1000);
  }

  // Ha splash ki van kapcsolva, ne jelenjen meg
  var splashEnabled = localStorage.getItem('boh_splash') !== '0';
  if (splashEnabled) {
    splash.style.display = '';
  }
})();"""

assert old_script in html, "FAIL: old init script"
html = html.replace(old_script, new_script, 1)

# ══════════════════════════════════════════════════════════════
# 4. ADD stamp-frame div to splash HTML (after tagline, before closing </div>)
# ══════════════════════════════════════════════════════════════

old_tagline = '  <div id="splash-tagline">Ivós kalandjáték</div>\n\n</div>'
new_tagline = '  <div id="splash-tagline">Ivós kalandjáték</div>\n  <div id="splash-stamp-frame"></div>\n\n</div>'

assert old_tagline in html, "FAIL: tagline anchor"
html = html.replace(old_tagline, new_tagline, 1)

# ══════════════════════════════════════════════════════════════
# 5. ADD SPLASH STYLE SELECTOR TO SETTINGS
# ══════════════════════════════════════════════════════════════

old_splash_state = "  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');\n  const toggleSplash = () => {\n    const next = !splashOn;\n    setSplashOn(next);\n    try { localStorage.setItem('boh_splash', next ? '1' : '0'); } catch(e) {}\n  };"

new_splash_state = """  const [splashOn, setSplashOn] = React.useState(() => localStorage.getItem('boh_splash') !== '0');
  const toggleSplash = () => {
    const next = !splashOn;
    setSplashOn(next);
    try { localStorage.setItem('boh_splash', next ? '1' : '0'); } catch(e) {}
  };
  const [splashStyle, setSplashStyleState] = React.useState(() => localStorage.getItem('boh_splash_style') || 'impact');
  const setSplashStyle = (s) => {
    setSplashStyleState(s);
    try { localStorage.setItem('boh_splash_style', s); } catch(e) {}
  };"""

assert old_splash_state in html, "FAIL: splash state"
html = html.replace(old_splash_state, new_splash_state, 1)

# Add selector UI after the splash toggle row
old_splash_toggle_ui = """              {/* Splash screen toggle */}
              <div style={{ width:1, background:T.inkMute+'25', margin:'20px 0' }} />
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                <div>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Splash screen</div>
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{t('splashSub')}</div>
                </div>
                <Toggle on={splashOn} onChange={toggleSplash} />
              </div>"""

new_splash_toggle_ui = """              {/* Splash screen toggle */}
              <div style={{ width:1, background:T.inkMute+'25', margin:'20px 0' }} />
              <div style={{ display:'flex', alignItems:'center', justifyContent:'space-between' }}>
                <div>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:14, color:T.ink }}>Splash screen</div>
                  <div style={{ fontFamily:T.font, fontSize:12, color:T.inkSoft, marginTop:2 }}>{t('splashSub')}</div>
                </div>
                <Toggle on={splashOn} onChange={toggleSplash} />
              </div>
              {splashOn && (
                <div style={{ marginTop:14 }}>
                  <div style={{ fontFamily:T.font, fontWeight:700, fontSize:12, color:T.inkSoft, textTransform:'uppercase', letterSpacing:'0.1em', marginBottom:10 }}>Splash stílus</div>
                  <div style={{ display:'grid', gridTemplateColumns:'1fr 1fr', gap:8 }}>
                    {[
                      ['impact','💥','Impact','Logó zuhan, flash, betűk'],
                      ['pulse', '💗','Pulse', 'Szívdobogás + gyűrűk'],
                      ['reveal','✨','Reveal','Fénycsík söpör végig'],
                      ['stamp', '🔨','Stamp', 'Lebélyegzés + remegés'],
                    ].map(([key, icon, name, desc]) => (
                      <button key={key} onClick={() => setSplashStyle(key)}
                        style={{ padding:'12px 10px', borderRadius:14,
                          border: splashStyle===key ? \`2px solid \${T.mint}\` : '2px solid transparent',
                          background: splashStyle===key ? T.mintSoft : T.surfaceMuted,
                          cursor:'pointer', textAlign:'left' }}>
                        <div style={{ fontSize:20, marginBottom:4 }}>{icon}</div>
                        <div style={{ fontFamily:T.font, fontWeight:800, fontSize:13, color: splashStyle===key ? T.mintDeep : T.ink }}>{name}</div>
                        <div style={{ fontFamily:T.font, fontSize:11, color:T.inkSoft, marginTop:2, lineHeight:1.3 }}>{desc}</div>
                      </button>
                    ))}
                  </div>
                </div>
              )}"""

assert old_splash_toggle_ui in html, "FAIL: splash toggle UI"
html = html.replace(old_splash_toggle_ui, new_splash_toggle_ui, 1)

# ══════════════════════════════════════════════════════════════
# 6. VERSION BUMP
# ══════════════════════════════════════════════════════════════
html = html.replace("const APP_VERSION = 'v9.374';", "const APP_VERSION = 'v9.375';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.375 — 4 splash stílusok + választó a beállításokban")
