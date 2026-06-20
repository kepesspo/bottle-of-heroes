#!/usr/bin/env python3
"""v9.381 — Splash: JS setTimeout vezérli az összes effektet, nem CSS delay"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. CSS: töröljük az animation delay-eket a shock/flash/letter elemekről ────
old_flash_css = """    #splash-flash {
      position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none;
      animation: splashFlash 0.65s ease-out 0.68s forwards;
    }
    .splash-shock {
      position:absolute; top:50%; left:50%; width:10px; height:10px; margin:-5px 0 0 -5px;
      border-radius:50%; border:3px solid rgba(0,0,0,0.28); opacity:0; pointer-events:none;
    }
    .splash-shock:nth-child(3) { animation:splashShock 0.80s cubic-bezier(0.1,0.5,0.2,1) 0.68s forwards; border-width:3px; border-color:rgba(0,0,0,0.40); }
    .splash-shock:nth-child(4) { animation:splashShock 1.00s cubic-bezier(0.1,0.5,0.2,1) 0.72s forwards; border-width:2px; border-color:rgba(0,0,0,0.25); }
    .splash-shock:nth-child(5) { animation:splashShock 1.20s cubic-bezier(0.1,0.5,0.2,1) 0.76s forwards; border-width:2px; border-color:rgba(0,0,0,0.15); }
    .splash-shock:nth-child(6) { animation:splashShock 1.50s cubic-bezier(0.1,0.5,0.2,1) 0.80s forwards; border-width:1.5px; border-color:rgba(0,0,0,0.08); }"""

new_flash_css = """    #splash-flash {
      position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none;
    }
    .splash-shock {
      position:absolute; top:50%; left:50%; width:10px; height:10px; margin:-5px 0 0 -5px;
      border-radius:50%; opacity:0; pointer-events:none;
    }
    .splash-shock:nth-child(3) { border:3px solid rgba(0,0,0,0.40); }
    .splash-shock:nth-child(4) { border:2px solid rgba(0,0,0,0.25); }
    .splash-shock:nth-child(5) { border:2px solid rgba(0,0,0,0.15); }
    .splash-shock:nth-child(6) { border:1.5px solid rgba(0,0,0,0.08); }"""

assert old_flash_css in html, "FAIL: flash+shock css"
html = html.replace(old_flash_css, new_flash_css, 1)

# CSS tagline: animation delay törlése (JS vezérli)
old_tagline_css = """    #splash-tagline {
      margin-top:10px; font-family:'Nunito',-apple-system,system-ui,sans-serif; font-size:11px;
      letter-spacing:4px; text-transform:uppercase; color:var(--splash-ink-soft,#4A5878);
      opacity:0; animation:splashTagline 0.5s ease-out 2.2s forwards;
    }"""

new_tagline_css = """    #splash-tagline {
      margin-top:10px; font-family:'Nunito',-apple-system,system-ui,sans-serif; font-size:11px;
      letter-spacing:4px; text-transform:uppercase; color:var(--splash-ink-soft,#4A5878);
      opacity:0;
    }"""

assert old_tagline_css in html, "FAIL: tagline css"
html = html.replace(old_tagline_css, new_tagline_css, 1)

# ── 2. Init script: JS setTimeout-tal triggereljük minden effektet ──────────────
old_init_effects = """  // Letter slam — staggered
  var letters = document.querySelectorAll('.splash-letter');
  var base = 0.95, stagger = 0.06;
  letters.forEach(function(el, i) {
    el.style.animation = 'splashLetterSlam 0.55s cubic-bezier(0.22,1,0.36,1) ' + (base + i*stagger).toFixed(3) + 's both';
  });

  // Idle glow after letters finish
  var logo = document.getElementById('splash-logo');
  var idleAt = base + letters.length * stagger + 0.6;
  if (logo) setTimeout(function() {
    if (logo) logo.style.animation = 'splashLogoIdle 3s ease-in-out infinite';
  }, idleAt * 1000);

  if (localStorage.getItem('boh_splash') !== '0') splash.style.display = '';"""

new_init_effects = """  if (localStorage.getItem('boh_splash') !== '0') {
    splash.style.display = '';

    // ── JS-vezérelt animációk ──
    var logo   = document.getElementById('splash-logo');
    var flash  = document.getElementById('splash-flash');
    var shocks = document.querySelectorAll('.splash-shock');
    var letters = document.querySelectorAll('.splash-letter');

    // Impact: 700ms — flash + shockwave gyűrűk
    setTimeout(function() {
      if (flash) flash.style.animation = 'splashFlash 0.65s ease-out forwards';
      shocks.forEach(function(el, i) {
        setTimeout(function() {
          el.style.animation = 'splashShock ' + (0.8 + i * 0.2) + 's cubic-bezier(0.1,0.5,0.2,1) forwards';
        }, i * 50);
      });
    }, 700);

    // Letter slam: 900ms — staggered becsapódás
    setTimeout(function() {
      letters.forEach(function(el, i) {
        setTimeout(function() {
          el.style.animation = 'splashLetterSlam 0.55s cubic-bezier(0.22,1,0.36,1) both';
        }, i * 60);
      });
    }, 900);

    // Tagline: 2200ms
    setTimeout(function() {
      var tagline = document.getElementById('splash-tagline');
      if (tagline) tagline.style.animation = 'splashTagline 0.5s ease-out forwards';
    }, 2200);

    // Idle glow: 2600ms
    setTimeout(function() {
      if (logo) logo.style.animation = 'splashLogoIdle 3s ease-in-out infinite';
    }, 2600);
  }"""

assert old_init_effects in html, "FAIL: init effects"
html = html.replace(old_init_effects, new_init_effects, 1)

html = html.replace("const APP_VERSION = 'v9.380';", "const APP_VERSION = 'v9.381';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.381 — Splash: JS setTimeout vezérli az összes effektet")
