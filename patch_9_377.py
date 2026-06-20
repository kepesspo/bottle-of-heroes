#!/usr/bin/env python3
"""v9.377 — Splash: logo 200px (=főképernyő), szöveg Nunito 900 stílus mint főképernyőn"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Logo méret: 160px → 200px ──────────────────────────────────────────────
old_logo_css = """    #splash-logo {
      width:160px; height:160px; display:block;
      filter: drop-shadow(0 4px 8px rgba(0,0,0,0.25));
      animation: impactGlow 0.6s ease-out 0.72s forwards;
    }"""

new_logo_css = """    #splash-logo {
      width:200px; height:200px; display:block;
      filter: drop-shadow(0 4px 8px rgba(0,0,0,0.25));
      animation: impactGlow 0.6s ease-out 0.72s forwards;
    }"""

assert old_logo_css in html, "FAIL: logo css"
html = html.replace(old_logo_css, new_logo_css, 1)

# ── 2. Szöveg stílus: Arial Black → Nunito, főképernyővel egyező ──────────────
old_letter_css = """    .splash-letter {
      display:inline-block; font-family:'Arial Black','Arial Bold',Arial,sans-serif;
      font-weight:900; font-size:28px; letter-spacing:3px;
      color:rgba(0,0,0,0.75); opacity:0; transform:translateY(40px) scaleY(1.4);
    }
    .splash-word-of .splash-letter { font-size:16px; letter-spacing:6px; color:rgba(0,0,0,0.4); }"""

new_letter_css = """    .splash-letter {
      display:inline-block; font-family:'Nunito',-apple-system,system-ui,sans-serif;
      font-weight:900; font-size:28px; letter-spacing:0.05em; text-transform:uppercase;
      color:var(--splash-ink,#1A2A4A); opacity:0; transform:translateY(40px) scaleY(1.4);
    }
    .splash-word-of .splash-letter { letter-spacing:0.08em; opacity:0; }"""

assert old_letter_css in html, "FAIL: letter css"
html = html.replace(old_letter_css, new_letter_css, 1)

# ── 3. Tagline szín is ink-ből ─────────────────────────────────────────────────
old_tagline_css = """    #splash-tagline {
      margin-top:10px; font-family:Arial,sans-serif; font-size:11px;
      letter-spacing:4px; text-transform:uppercase; color:rgba(0,0,0,0.35);
      opacity:0; animation:splashTagline 0.5s ease-out 2.2s forwards;
    }"""

new_tagline_css = """    #splash-tagline {
      margin-top:10px; font-family:'Nunito',-apple-system,system-ui,sans-serif; font-size:11px;
      letter-spacing:4px; text-transform:uppercase; color:var(--splash-ink-soft,#4A5878);
      opacity:0; animation:splashTagline 0.5s ease-out 2.2s forwards;
    }"""

assert old_tagline_css in html, "FAIL: tagline css"
html = html.replace(old_tagline_css, new_tagline_css, 1)

# ── 4. Splash HTML: BOTTLE OF HEROES egy szóközzel tagoltan (nem külön sorok) ──
# Hagyja meg a betűstruktúrát (slam animáció miatt), de törölje "OF" külön sort

old_title_html = """  <div id="splash-title-wrap">
    <div class="splash-word splash-word-bottle">
      <span class="splash-letter">B</span><span class="splash-letter">O</span><span class="splash-letter">T</span><span class="splash-letter">T</span><span class="splash-letter">L</span><span class="splash-letter">E</span>
    </div>
    <div class="splash-word splash-word-of">
      <span class="splash-letter">O</span><span class="splash-letter">F</span>
    </div>
    <div class="splash-word splash-word-heroes">
      <span class="splash-letter">H</span><span class="splash-letter">E</span><span class="splash-letter">R</span><span class="splash-letter">O</span><span class="splash-letter">E</span><span class="splash-letter">S</span>
    </div>
  </div>"""

new_title_html = """  <div id="splash-title-wrap">
    <div class="splash-word">
      <span class="splash-letter">B</span><span class="splash-letter">O</span><span class="splash-letter">T</span><span class="splash-letter">T</span><span class="splash-letter">L</span><span class="splash-letter">E</span><span class="splash-letter splash-space"> </span><span class="splash-letter">O</span><span class="splash-letter">F</span><span class="splash-letter splash-space"> </span><span class="splash-letter">H</span><span class="splash-letter">E</span><span class="splash-letter">R</span><span class="splash-letter">O</span><span class="splash-letter">E</span><span class="splash-letter">S</span>
    </div>
  </div>"""

assert old_title_html in html, "FAIL: title html"
html = html.replace(old_title_html, new_title_html, 1)

# ── 5. Space betű CSS ──────────────────────────────────────────────────────────
old_word_css = "    .splash-word { display:flex; gap:1px; }"
new_word_css = """    .splash-word { display:flex; gap:0; }
    .splash-letter.splash-space { width:0.35em; }"""

assert old_word_css in html, "FAIL: word css"
html = html.replace(old_word_css, new_word_css, 1)

# ── 6. Init script: add ink color CSS var per theme ───────────────────────────
# Add ink colors to themes object lookup
old_themes_js = """  var themes = {
    warm:  { bg:'#F4C57E', deep:'#E8B260', ring:'rgba(180,100,20,0.35)',  glow:'rgba(180,100,20,0.7)' },
    dark:  { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)',  glow:'rgba(80,110,220,0.7)' },
    peach: { bg:'#FFE8D8', deep:'#FFD8C0', ring:'rgba(180,70,0,0.35)',   glow:'rgba(210,80,20,0.7)' },
    lemon: { bg:'#F8F8D8', deep:'#F0F0B8', ring:'rgba(100,100,0,0.35)',  glow:'rgba(130,130,0,0.7)' },
    berry: { bg:'#F0E8F8', deep:'#E0D0F0', ring:'rgba(120,0,180,0.35)', glow:'rgba(150,20,200,0.7)' },
    ice:   { bg:'#E8F4FF', deep:'#D0E8FF', ring:'rgba(0,60,160,0.35)',   glow:'rgba(20,90,200,0.7)' },
    slate: { bg:'#E8EBF0', deep:'#D4D9E4', ring:'rgba(80,100,130,0.35)', glow:'rgba(90,110,150,0.7)' },
    jade:  { bg:'#E8F5EE', deep:'#D0EBD8', ring:'rgba(30,120,70,0.35)',  glow:'rgba(40,140,80,0.7)' },
  };"""

new_themes_js = """  var themes = {
    warm:  { bg:'#F4C57E', deep:'#E8B260', ring:'rgba(180,100,20,0.35)',  glow:'rgba(180,100,20,0.7)',  ink:'#1A2A4A', inkSoft:'#4A5878' },
    dark:  { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)',  glow:'rgba(80,110,220,0.7)',  ink:'#E8EEF8', inkSoft:'#9AA8C8' },
    peach: { bg:'#FFE8D8', deep:'#FFD8C0', ring:'rgba(180,70,0,0.35)',   glow:'rgba(210,80,20,0.7)',   ink:'#2A1500', inkSoft:'#6B3010' },
    lemon: { bg:'#F8F8D8', deep:'#F0F0B8', ring:'rgba(100,100,0,0.35)',  glow:'rgba(130,130,0,0.7)',   ink:'#1A1A00', inkSoft:'#4A4A10' },
    berry: { bg:'#F0E8F8', deep:'#E0D0F0', ring:'rgba(120,0,180,0.35)', glow:'rgba(150,20,200,0.7)',  ink:'#1A0030', inkSoft:'#4A2060' },
    ice:   { bg:'#E8F4FF', deep:'#D0E8FF', ring:'rgba(0,60,160,0.35)',   glow:'rgba(20,90,200,0.7)',   ink:'#001A3A', inkSoft:'#103060' },
    slate: { bg:'#E8EBF0', deep:'#D4D9E4', ring:'rgba(80,100,130,0.35)', glow:'rgba(90,110,150,0.7)',  ink:'#1A2030', inkSoft:'#404858' },
    jade:  { bg:'#E8F5EE', deep:'#D0EBD8', ring:'rgba(30,120,70,0.35)',  glow:'rgba(40,140,80,0.7)',   ink:'#001A0A', inkSoft:'#1A4A28' },
  };"""

assert old_themes_js in html, "FAIL: themes js"
html = html.replace(old_themes_js, new_themes_js, 1)

# Add ink CSS var injection alongside glow
old_cssvar = """  var s = document.createElement('style');
  s.textContent = ':root{--splash-glow:' + t.glow + ';--splash-ring:' + t.ring + ';}' +
    '@keyframes splashLogoIdle{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.3));}50%{filter:drop-shadow(0 0 48px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.2));}}';
  document.head.appendChild(s);"""

new_cssvar = """  var s = document.createElement('style');
  s.textContent = ':root{--splash-glow:' + t.glow + ';--splash-ring:' + t.ring + ';--splash-ink:' + t.ink + ';--splash-ink-soft:' + t.inkSoft + ';}' +
    '@keyframes splashLogoIdle{0%,100%{filter:drop-shadow(0 0 28px ' + t.glow + ') drop-shadow(0 8px 24px rgba(0,0,0,0.3));}50%{filter:drop-shadow(0 0 48px ' + t.glow + ') drop-shadow(0 8px 32px rgba(0,0,0,0.2));}}';
  document.head.appendChild(s);"""

assert old_cssvar in html, "FAIL: css var js"
html = html.replace(old_cssvar, new_cssvar, 1)

# ── 7. Version bump ────────────────────────────────────────────────────────────
html = html.replace("const APP_VERSION = 'v9.376';", "const APP_VERSION = 'v9.377';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.377 — Splash: logo 200px, Nunito font, tema ink szín, egy soros cím")
