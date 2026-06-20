#!/usr/bin/env python3
"""v9.379 — Fix splash animations: shock rings fill, letter slam lassabb/drámaibb, jobb flash"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Shock rings: both → forwards (ne legyenek láthatók a zuhanás alatt) ─────
old_shock_anim = """.splash-shock:nth-child(3) { animation:splashShock 0.70s cubic-bezier(0.1,0.6,0.3,1) 0.70s both; }
    .splash-shock:nth-child(4) { animation:splashShock 0.80s cubic-bezier(0.1,0.6,0.3,1) 0.78s both; border-width:2px; }
    .splash-shock:nth-child(5) { animation:splashShock 0.90s cubic-bezier(0.1,0.6,0.3,1) 0.86s both; border-width:1.5px; border-color:rgba(0,0,0,0.15); }
    .splash-shock:nth-child(6) { animation:splashShock 1.10s cubic-bezier(0.1,0.6,0.3,1) 0.94s both; border-width:1px;   border-color:rgba(0,0,0,0.08); }"""

new_shock_anim = """.splash-shock:nth-child(3) { animation:splashShock 0.80s cubic-bezier(0.1,0.5,0.2,1) 0.68s forwards; border-width:3px; border-color:rgba(0,0,0,0.40); }
    .splash-shock:nth-child(4) { animation:splashShock 1.00s cubic-bezier(0.1,0.5,0.2,1) 0.72s forwards; border-width:2px; border-color:rgba(0,0,0,0.25); }
    .splash-shock:nth-child(5) { animation:splashShock 1.20s cubic-bezier(0.1,0.5,0.2,1) 0.76s forwards; border-width:2px; border-color:rgba(0,0,0,0.15); }
    .splash-shock:nth-child(6) { animation:splashShock 1.50s cubic-bezier(0.1,0.5,0.2,1) 0.80s forwards; border-width:1.5px; border-color:rgba(0,0,0,0.08); }"""

assert old_shock_anim in html, "FAIL: shock anim"
html = html.replace(old_shock_anim, new_shock_anim, 1)

# ── 2. Shock keyframe: kezdjen opacity:0-ból hogy ne látsszon a zuhanás alatt ──
old_shock_kf = "@keyframes splashShock { 0%{transform:scale(1);opacity:0.85} 100%{transform:scale(28);opacity:0} }"
new_shock_kf  = "@keyframes splashShock { 0%{transform:scale(1);opacity:0} 8%{opacity:0.9} 100%{transform:scale(30);opacity:0} }"

assert old_shock_kf in html, "FAIL: shock keyframe"
html = html.replace(old_shock_kf, new_shock_kf, 1)

# ── 3. Letter slam: lassabb, drámaibb (0.35s → 0.55s, nagyobb mozgás) ─────────
old_letter_kf = """@keyframes splashLetterSlam {
      0%  { transform:translateY(40px) scaleY(1.4); opacity:0; }
      55% { transform:translateY(-4px) scaleY(0.92); opacity:1; }
      80% { transform:translateY(2px) scaleY(1.03); }
      100%{ transform:translateY(0) scaleY(1); opacity:1; }
    }"""

new_letter_kf = """@keyframes splashLetterSlam {
      0%  { transform:translateY(60px) scaleY(1.6) scaleX(0.8); opacity:0; }
      50% { transform:translateY(-6px) scaleY(0.88) scaleX(1.05); opacity:1; }
      75% { transform:translateY(3px) scaleY(1.04) scaleX(0.98); }
      100%{ transform:translateY(0) scaleY(1) scaleX(1); opacity:1; }
    }"""

assert old_letter_kf in html, "FAIL: letter keyframe"
html = html.replace(old_letter_kf, new_letter_kf, 1)

# ── 4. Letter slam timing: lassabb, kevesebb stagger hogy együttesebb legyen ───
old_letter_js = """  var letters = document.querySelectorAll('.splash-letter');
  var base = 0.9, stagger = 0.055;
  letters.forEach(function(el, i) {
    el.style.animation = 'splashLetterSlam 0.35s cubic-bezier(0.22,1,0.36,1) ' + (base + i*stagger).toFixed(3) + 's both';
  });

  // Idle glow after letters finish
  var logo = document.getElementById('splash-logo');
  var idleAt = base + letters.length * stagger + 0.4;"""

new_letter_js = """  var letters = document.querySelectorAll('.splash-letter');
  var base = 0.95, stagger = 0.06;
  letters.forEach(function(el, i) {
    el.style.animation = 'splashLetterSlam 0.55s cubic-bezier(0.22,1,0.36,1) ' + (base + i*stagger).toFixed(3) + 's both';
  });

  // Idle glow after letters finish
  var logo = document.getElementById('splash-logo');
  var idleAt = base + letters.length * stagger + 0.6;"""

assert old_letter_js in html, "FAIL: letter js"
html = html.replace(old_letter_js, new_letter_js, 1)

# ── 5. Flash: kicsit erősebb, kicsit hosszabb ──────────────────────────────────
old_flash_kf = "@keyframes splashFlash { 0%{opacity:0} 15%{opacity:0.75} 100%{opacity:0} }"
new_flash_kf  = "@keyframes splashFlash { 0%{opacity:0} 12%{opacity:0.88} 100%{opacity:0} }"

assert old_flash_kf in html, "FAIL: flash keyframe"
html = html.replace(old_flash_kf, new_flash_kf, 1)

old_flash_css = """    #splash-flash {
      position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none;
      animation: splashFlash 0.5s ease-out 0.7s both;
    }"""

new_flash_css = """    #splash-flash {
      position:absolute; inset:0; background:#fff; opacity:0; pointer-events:none;
      animation: splashFlash 0.65s ease-out 0.68s forwards;
    }"""

assert old_flash_css in html, "FAIL: flash css"
html = html.replace(old_flash_css, new_flash_css, 1)

# ── 6. Minimum display idő: 3s → 3.2s (letter animáció hosszabb lett) ─────────
html = html.replace('}, 3000);', '}, 3200);', 1)

html = html.replace("const APP_VERSION = 'v9.378';", "const APP_VERSION = 'v9.379';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.379 — Splash fixes: shock rings, letter slam, flash")
