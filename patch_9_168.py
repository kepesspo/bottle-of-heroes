#!/usr/bin/env python3
"""patch_9_168.py — Mist téma: gradient + ívelt formák háttér"""

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

assert "const APP_VERSION = 'v9.167';" in content
content = content.replace("const APP_VERSION = 'v9.167';", "const APP_VERSION = 'v9.168';")

# ── 1. Add 'mist' theme to THEMES ──
OLD_THEMES_END = """  sky: {
    bg: '#E4EEF8',"""

NEW_THEMES_END = """  mist: {
    bg: '#B8C8D8',
    bgSoft: '#C8D6E4',
    bgDeep: '#8FA8BC',
    surface: 'rgba(255,255,255,0.72)',
    surfaceMuted: 'rgba(255,255,255,0.45)',
    ink: '#1C2B38',
    inkSoft: '#3D5268',
    inkMute: '#7A96AA',
    mint: '#3DA888',
    mintSoft: '#C8EAE0',
    mintDeep: '#2D9070',
    coral: '#D96060',
    coralSoft: '#F2D8D8',
    purple: '#6A80C8',
    yellow: '#D4A830',
    blue: '#4A80CC',
    pink: '#C870A8',
    font: '"Nunito", -apple-system, system-ui, sans-serif',
    weightDisplay: 900,
    weightTitle: 800,
    weightBody: 600,
    letter: '-0.01em',
    letterDisplay: '-0.02em',
    shadow: '0 2px 0 rgba(20,40,60,0.06), 0 6px 20px rgba(20,40,60,0.10)',
    shadowLift: '0 4px 0 rgba(20,40,60,0.08), 0 12px 32px rgba(20,40,60,0.14)',
    bgShapes: true,
  },
  sky: {
    bg: '#E4EEF8',"""

assert OLD_THEMES_END in content, "THEMES end not found"
content = content.replace(OLD_THEMES_END, NEW_THEMES_END, 1)

# ── 2. Add MistBackground component before App function ──
OLD_APP_FN = "function BottleApp() {"

NEW_APP_FN = """function MistBackground() {
  return React.createElement('div', {
    style: {
      position: 'fixed', inset: 0, zIndex: 0, pointerEvents: 'none',
      background: 'linear-gradient(145deg, #C8D8E8 0%, #A8BED0 35%, #90AABE 60%, #B0C4D4 100%)',
      overflow: 'hidden',
    }
  },
    React.createElement('svg', {
      style: { position:'absolute', inset:0, width:'100%', height:'100%' },
      viewBox: '0 0 390 844', preserveAspectRatio: 'xMidYMid slice',
      xmlns: 'http://www.w3.org/2000/svg',
    },
      React.createElement('defs', null,
        React.createElement('filter', { id:'mist-blur' },
          React.createElement('feGaussianBlur', { stdDeviation: '28' })
        )
      ),
      // Large curved blob top-right
      React.createElement('ellipse', { cx:'340', cy:'80', rx:'220', ry:'160', fill:'rgba(255,255,255,0.18)', filter:'url(#mist-blur)' }),
      // Elegant S-curve shape (paper fold)
      React.createElement('path', {
        d: 'M -40 200 C 80 100, 200 320, 160 480 C 120 640, 320 700, 420 620',
        fill: 'none', stroke: 'rgba(255,255,255,0.55)', strokeWidth: '1.5',
      }),
      React.createElement('path', {
        d: 'M -20 220 C 100 120, 220 340, 180 500 C 140 660, 340 720, 440 640',
        fill: 'none', stroke: 'rgba(255,255,255,0.25)', strokeWidth: '0.8',
      }),
      // Second fold
      React.createElement('path', {
        d: 'M 200 -20 C 360 60, 280 260, 180 360 C 80 460, 200 640, 420 760',
        fill: 'none', stroke: 'rgba(255,255,255,0.40)', strokeWidth: '1.2',
      }),
      // Soft bottom blob
      React.createElement('ellipse', { cx:'80', cy:'780', rx:'200', ry:'140', fill:'rgba(255,255,255,0.12)', filter:'url(#mist-blur)' }),
      // Subtle surface sheen top
      React.createElement('path', {
        d: 'M 0 0 C 120 40, 280 10, 390 60 L 390 0 Z',
        fill: 'rgba(255,255,255,0.14)',
      }),
    )
  );
}

function BottleApp() {"""

assert OLD_APP_FN in content, "App function not found"
content = content.replace(OLD_APP_FN, NEW_APP_FN, 1)

# ── 3. Render MistBackground inside the main app div when mist theme active ──
OLD_APP_ROOT = '    <div style={{ minHeight:\'100dvh\', width:\'100%\', position:\'relative\', fontFamily:T.font, color:T.ink, WebkitFontSmoothing:\'antialiased\', background:T.bg }} data-theme={appTheme}>'
NEW_APP_ROOT = '    <div style={{ minHeight:\'100dvh\', width:\'100%\', position:\'relative\', fontFamily:T.font, color:T.ink, WebkitFontSmoothing:\'antialiased\', background: T.bgShapes ? \'transparent\' : T.bg }} data-theme={appTheme}>\n      {T.bgShapes && <MistBackground />}'

assert OLD_APP_ROOT in content, "app root not found"
content = content.replace(OLD_APP_ROOT, NEW_APP_ROOT, 1)

# ── 4. Add mist theme to settings selector ──
OLD_THEME_BTNS = "[['warm','☀️',t('themeWarm')],['sky','🌤️',t('themeSky')],['dark','🌙',t('themeDark')]]"
NEW_THEME_BTNS = "[['warm','☀️',t('themeWarm')],['sky','🌤️',t('themeSky')],['dark','🌙',t('themeDark')],['mist','🌊','Mist']]"
assert OLD_THEME_BTNS in content, "theme btns not found"
content = content.replace(OLD_THEME_BTNS, NEW_THEME_BTNS, 1)

# ── 5. Update splash to handle mist theme ──
OLD_SPLASH_THEMES = """  var themes = {
    warm: { bg:'#F4C57E', deep:'#E8A040', ring:'rgba(180,100,20,0.35)', glow:'rgba(180,100,20,0.7)' },
    dark: { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)', glow:'rgba(80,110,220,0.7)' },
    sky:  { bg:'#E4EEF8', deep:'#C8D8EE', ring:'rgba(60,120,200,0.3)',  glow:'rgba(60,120,200,0.65)' },
  };"""
NEW_SPLASH_THEMES = """  var themes = {
    warm: { bg:'#F4C57E', deep:'#E8A040', ring:'rgba(180,100,20,0.35)', glow:'rgba(180,100,20,0.7)' },
    dark: { bg:'#2C3554', deep:'#1E2640', ring:'rgba(80,110,220,0.35)', glow:'rgba(80,110,220,0.7)' },
    sky:  { bg:'#E4EEF8', deep:'#C8D8EE', ring:'rgba(60,120,200,0.3)',  glow:'rgba(60,120,200,0.65)' },
    mist: { bg:'#B8C8D8', deep:'#8FA8BC', ring:'rgba(60,100,150,0.3)',  glow:'rgba(70,110,160,0.65)' },
  };"""
assert OLD_SPLASH_THEMES in content, "splash themes not found"
content = content.replace(OLD_SPLASH_THEMES, NEW_SPLASH_THEMES, 1)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("OK — v9.168 ready")
