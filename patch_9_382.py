#!/usr/bin/env python3
"""v9.382 — Splash timing finomítás: flash/shock korábban, gördülékenyebb átmenet"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Logo drop gyorsabb: 0.7s → 0.55s, settle 0.25s → 0.2s ─────────────────
old_logo_wrap_anim = """      animation: impactDrop 0.7s cubic-bezier(0.25,0.1,0.25,1.4) 0s both,
                 impactSettle 0.25s ease-out 0.7s both;"""
new_logo_wrap_anim = """      animation: impactDrop 0.55s cubic-bezier(0.3,0,0.4,1) 0s both,
                 impactSettle 0.2s ease-out 0.55s both;"""

assert old_logo_wrap_anim in html, "FAIL: logo wrap anim"
html = html.replace(old_logo_wrap_anim, new_logo_wrap_anim, 1)

# ── 2. Impact effektek: 700ms → 520ms (logo eléri a célt ~85%*0.55s=0.47s) ────
old_impact_timer = """    // Impact: 700ms — flash + shockwave gyűrűk
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
    }, 2600);"""

new_impact_timer = """    // Impact: 520ms — logo eléri a célt, flash + shockwave egyszerre
    setTimeout(function() {
      if (flash) flash.style.animation = 'splashFlash 0.6s ease-out forwards';
      shocks.forEach(function(el, i) {
        setTimeout(function() {
          el.style.animation = 'splashShock ' + (0.75 + i * 0.18) + 's cubic-bezier(0.1,0.5,0.2,1) forwards';
        }, i * 40);
      });
    }, 520);

    // Letter slam: 700ms — közvetlenül az impact után
    setTimeout(function() {
      letters.forEach(function(el, i) {
        setTimeout(function() {
          el.style.animation = 'splashLetterSlam 0.5s cubic-bezier(0.22,1,0.36,1) both';
        }, i * 55);
      });
    }, 700);

    // Tagline: 1900ms
    setTimeout(function() {
      var tagline = document.getElementById('splash-tagline');
      if (tagline) tagline.style.animation = 'splashTagline 0.5s ease-out forwards';
    }, 1900);

    // Idle glow: 2300ms
    setTimeout(function() {
      if (logo) logo.style.animation = 'splashLogoIdle 3s ease-in-out infinite';
    }, 2300);"""

assert old_impact_timer in html, "FAIL: impact timer"
html = html.replace(old_impact_timer, new_impact_timer, 1)

# ── 3. Minimum display idő: 3500ms → 3000ms (minden animáció lerövidült) ───────
html = html.replace('}, 3500);', '}, 3000);', 1)

html = html.replace("const APP_VERSION = 'v9.381';", "const APP_VERSION = 'v9.382';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.382 — Splash timing szinkronizálva, gördülékenyebb")
