#!/usr/bin/env python3
"""v9.376 — Keep only Impact splash, remove pulse/reveal/stamp CSS+JS+settings picker"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Replace the bloated 4-style CSS with clean Impact-only CSS ──────────────

old_css_marker_start = "    /* ══ SPLASH SCREEN — shared base ══ */"
old_css_marker_end   = "    /* shared idle glow */\n    @keyframes splashLogoIdle {\n      0%,100%{filter:drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.3))}\n      50%    {filter:drop-shadow(0 0 48px var(--splash-glow,rgba(140,60,255,0.9))) drop-shadow(0 8px 32px rgba(0,0,0,0.2))}\n    }"

idx_s = html.index(old_css_marker_start)
idx_e = html.index(old_css_marker_end) + len(old_css_marker_end)
old_big_css = html[idx_s:idx_e]

new_clean_css = """    /* ── IMPACT SPLASH ── */
    #splash {
      position: fixed; inset: 0; z-index: 99999;
      display: flex; flex-direction: column; align-items: center; justify-content: center;
      background: #F4C57E;
      transition: opacity 0.6s ease; overflow: hidden;
    }
    #splash.hidden { opacity:0; pointer-events:none; }
    #splash-bg { position:absolute; inset:0; }
    #splash-flash {
      position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none;
      animation: splashFlash 0.5s ease-out 0.7s both;
    }
    .splash-shock {
      position:absolute; top:50%; left:50%; width:10px; height:10px; margin:-5px 0 0 -5px;
      border-radius:50%; border:3px solid rgba(0,0,0,0.28); opacity:0; pointer-events:none;
    }
    .splash-shock:nth-child(3) { animation:splashShock 0.70s cubic-bezier(0.1,0.6,0.3,1) 0.70s both; }
    .splash-shock:nth-child(4) { animation:splashShock 0.80s cubic-bezier(0.1,0.6,0.3,1) 0.78s both; border-width:2px; }
    .splash-shock:nth-child(5) { animation:splashShock 0.90s cubic-bezier(0.1,0.6,0.3,1) 0.86s both; border-width:1.5px; border-color:rgba(0,0,0,0.15); }
    .splash-shock:nth-child(6) { animation:splashShock 1.10s cubic-bezier(0.1,0.6,0.3,1) 0.94s both; border-width:1px;   border-color:rgba(0,0,0,0.08); }
    #splash-logo-wrap {
      position:relative; z-index:2;
      animation: impactDrop 0.7s cubic-bezier(0.25,0.1,0.25,1.4) 0s both,
                 impactSettle 0.25s ease-out 0.7s both;
    }
    #splash-logo {
      width:160px; height:160px; display:block;
      filter: drop-shadow(0 4px 8px rgba(0,0,0,0.25));
      animation: impactGlow 0.6s ease-out 0.72s forwards;
    }
    #splash-title-wrap {
      position:relative; z-index:2; margin-top:18px;
      display:flex; flex-direction:column; align-items:center; gap:2px;
    }
    .splash-word { display:flex; gap:1px; }
    .splash-letter {
      display:inline-block; font-family:'Arial Black','Arial Bold',Arial,sans-serif;
      font-weight:900; font-size:28px; letter-spacing:3px;
      color:rgba(0,0,0,0.75); opacity:0; transform:translateY(40px) scaleY(1.4);
    }
    .splash-word-of .splash-letter { font-size:16px; letter-spacing:6px; color:rgba(0,0,0,0.4); }
    #splash-tagline {
      margin-top:10px; font-family:Arial,sans-serif; font-size:11px;
      letter-spacing:4px; text-transform:uppercase; color:rgba(0,0,0,0.35);
      opacity:0; animation:splashTagline 0.5s ease-out 2.2s forwards;
    }

    @keyframes impactDrop {
      0%  { transform:translateY(-120vh) scaleY(0.85); }
      85% { transform:translateY(8px) scaleY(1.08); }
      100%{ transform:translateY(0) scaleY(1); }
    }
    @keyframes impactSettle {
      0%  { transform:scaleX(1.12) scaleY(0.88); }
      60% { transform:scaleX(0.97) scaleY(1.03); }
      100%{ transform:scaleX(1) scaleY(1); }
    }
    @keyframes impactGlow {
      0%  { filter:drop-shadow(0 0 40px rgba(255,255,255,0.7)) drop-shadow(0 8px 24px rgba(0,0,0,0.3)); }
      100%{ filter:drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.25)); }
    }
    @keyframes splashFlash { 0%{opacity:0} 15%{opacity:0.75} 100%{opacity:0} }
    @keyframes splashShock { 0%{transform:scale(1);opacity:0.85} 100%{transform:scale(28);opacity:0} }
    @keyframes splashLetterSlam {
      0%  { transform:translateY(40px) scaleY(1.4); opacity:0; }
      55% { transform:translateY(-4px) scaleY(0.92); opacity:1; }
      80% { transform:translateY(2px) scaleY(1.03); }
      100%{ transform:translateY(0) scaleY(1); opacity:1; }
    }
    @keyframes splashTagline { from{opacity:0;transform:translateY(6px)} to{opacity:1;transform:translateY(0)} }
    @keyframes splashLogoIdle {
      0%,100%{ filter:drop-shadow(0 0 28px var(--splash-glow,rgba(140,60,255,0.7))) drop-shadow(0 8px 24px rgba(0,0,0,0.3)); }
      50%    { filter:drop-shadow(0 0 48px var(--splash-glow,rgba(140,60,255,0.9))) drop-shadow(0 8px 32px rgba(0,0,0,0.2)); }
    }"""

html = html.replace(old_big_css, new_clean_css, 1)

# ── 2. Clean up splash HTML — remove data-style attr + stamp-frame ─────────────
html = html.replace('<div id="splash" style="display:none" data-style="impact">',
                    '<div id="splash" style="display:none">', 1)
html = html.replace('  <div id="splash-stamp-frame"></div>\n', '', 1)

# ── 3. Simplify init script — remove style branching ──────────────────────────
old_init = """(function(){
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

new_init = """(function(){
  var theme  = localStorage.getItem('boh_theme') || 'warm';
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

  // Theme colors
  var bg = document.getElementById('splash-bg');
  splash.style.background = t.bg;
  if (bg) bg.style.background = 'radial-gradient(ellipse at 50% 45%, ' + t.deep + ' 0%, ' + t.bg + ' 70%)';

  // CSS custom properties
  var s = document.createElement('style');
  s.textContent = ':root{--splash-glow:' + t.glow + ';--splash-ring:' + t.ring + ';}' +
    '@keyframes splashLogoIdle{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.3));}50%{filter:drop-shadow(0 0 48px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.2));}}';
  document.head.appendChild(s);

  // Letter slam — staggered
  var letters = document.querySelectorAll('.splash-letter');
  var base = 0.9, stagger = 0.055;
  letters.forEach(function(el, i) {
    el.style.animation = 'splashLetterSlam 0.35s cubic-bezier(0.22,1,0.36,1) ' + (base + i*stagger).toFixed(3) + 's both';
  });

  // Idle glow after letters finish
  var logo = document.getElementById('splash-logo');
  var idleAt = base + letters.length * stagger + 0.4;
  if (logo) setTimeout(function() {
    if (logo) logo.style.animation = 'splashLogoIdle 3s ease-in-out infinite';
  }, idleAt * 1000);

  if (localStorage.getItem('boh_splash') !== '0') splash.style.display = '';
})();"""

assert old_init in html, "FAIL: old init script"
html = html.replace(old_init, new_init, 1)

# ── 4. Remove splash style picker from settings UI ─────────────────────────────
old_style_state = """  const [splashStyle, setSplashStyleState] = React.useState(() => localStorage.getItem('boh_splash_style') || 'impact');
  const setSplashStyle = (s) => {
    setSplashStyleState(s);
    try { localStorage.setItem('boh_splash_style', s); } catch(e) {}
  };"""

assert old_style_state in html, "FAIL: splash style state"
html = html.replace(old_style_state, '', 1)

old_picker_ui = """              {splashOn && (
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
                          border: splashStyle===key ? '2px solid ' + T.mint : '2px solid transparent',
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

assert old_picker_ui in html, "FAIL: picker UI"
html = html.replace(old_picker_ui, '', 1)

# ── 5. Version bump ────────────────────────────────────────────────────────────
html = html.replace("const APP_VERSION = 'v9.375';", "const APP_VERSION = 'v9.376';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.376 — Impact only, cleaned up")
