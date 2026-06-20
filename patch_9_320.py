#!/usr/bin/env python3
"""v9.320 — Mobile UX: landscape mode, safe area sides, PWA install UX, EN translations"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ══════════════════════════════════════════════════════════════════════
# 1. status-bar: default → black-translucent (immersive, content under status bar)
# ══════════════════════════════════════════════════════════════════════
old_status_bar = '<meta name="apple-mobile-web-app-status-bar-style" content="default"/>'
new_status_bar = '<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent"/>'
assert old_status_bar in html, "FAIL: status bar"
html = html.replace(old_status_bar, new_status_bar, 1)

# ══════════════════════════════════════════════════════════════════════
# 2. Landscape CSS + safe-area left/right
# ══════════════════════════════════════════════════════════════════════
old_play_footer_css = "    .play-footer-inner { max-width:680px; margin:0 auto; width:100%; display:flex; align-items:stretch; justify-content:space-between; gap:12px; padding:0 18px; }"
new_play_footer_css = """    .play-footer-inner { max-width:680px; margin:0 auto; width:100%; display:flex; align-items:stretch; justify-content:space-between; gap:12px; padding:0 18px; }

    /* ── Landscape mode — compact layout ── */
    @media (orientation: landscape) and (max-height: 500px) {
      .appbar-shell { border-bottom-left-radius:16px; border-bottom-right-radius:16px; }
      .appbar-inner { min-height:40px; padding:6px max(18px, calc(env(safe-area-inset-left) + 14px)) 6px max(18px, calc(env(safe-area-inset-left) + 14px)); }
      .bottombar-shell { padding:6px 0 max(10px, calc(env(safe-area-inset-bottom) + 6px)); }
      .bottombar-inner { padding:0 max(16px, calc(env(safe-area-inset-left) + 10px)); }
      .home-inner { gap:16px; padding:20px max(20px, calc(env(safe-area-inset-left) + 12px)) 16px; }
      .home-actions { max-width:260px; gap:8px; }
      .screen-pad {
        padding-left:max(18px, calc(env(safe-area-inset-left) + 12px));
        padding-right:max(18px, calc(env(safe-area-inset-right) + 12px));
      }
      .play-footer-inner {
        padding:0 max(18px, calc(env(safe-area-inset-left) + 12px));
      }
      .grid-players { grid-template-columns:repeat(5,1fr); gap:8px; }
      .grid-games   { grid-template-columns:repeat(6,1fr); gap:8px; }
    }

    /* ── Safe-area horizontal padding (portrait, for side cutouts) ── */
    @media (orientation: portrait) {
      .screen-pad {
        padding-left:max(18px, calc(env(safe-area-inset-left) + 14px));
        padding-right:max(18px, calc(env(safe-area-inset-right) + 14px));
      }
    }"""
assert old_play_footer_css in html, "FAIL: play-footer css"
html = html.replace(old_play_footer_css, new_play_footer_css, 1)

# ══════════════════════════════════════════════════════════════════════
# 3. Add missing TR keys for install flow + quick game
# ══════════════════════════════════════════════════════════════════════

old_tr_hu_install = "    addToHome: 'Főképernyőre mentés', addToHomeDesc: 'Telepítsd appként — ingyen, App Store nélkül',"
new_tr_hu_install = """    addToHome: 'Főképernyőre mentés', addToHomeDesc: 'Telepítsd appként — ingyen, App Store nélkül',
    installTitle: 'Főképernyőre',
    installSubtitle: 'Telepítsd appként — ingyen, App Store nélkül',
    installHomeBtn: 'Telepítsd appként — ingyen',
    installBrowserPrompt: 'A böngésződ közvetlenül tudja telepíteni — nincs szükség App Store-ra.',
    quickGameSub: '2 véletlen játékos',
    iosStep1: 'Nyisd meg ezt az oldalt <b>Safari</b> böngészőben',
    iosStep2: 'Koppints a <b>Megosztás</b> ikonra (alul, középen)',
    iosStep3: 'Görgess le és válaszd: <b>„Főképernyőre"</b>',
    iosStep4: 'Koppints a <b>„Hozzáadás"</b> gombra',
    androidStep1: 'Koppints a böngésző <b>menüjére</b> (jobb felső sarok)',
    androidStep2: 'Válaszd: <b>„Hozzáadás a főképernyőhöz"</b> vagy <b>„Alkalmazás telepítése"</b>',
    androidStep3: 'Koppints a <b>„Hozzáadás"</b> / <b>„Telepítés"</b> gombra',"""
assert old_tr_hu_install in html, "FAIL: TR hu install"
html = html.replace(old_tr_hu_install, new_tr_hu_install, 1)

old_tr_en_install = "    addToHome: 'Add to Home Screen', addToHomeDesc: 'Install as app — free, no App Store needed',"
new_tr_en_install = """    addToHome: 'Add to Home Screen', addToHomeDesc: 'Install as app — free, no App Store needed',
    installTitle: 'Add to Home Screen',
    installSubtitle: 'Install as an app — free, no App Store needed',
    installHomeBtn: 'Install as app — free',
    installBrowserPrompt: 'Your browser can install it directly — no App Store needed.',
    quickGameSub: '2 random players',
    iosStep1: 'Open this page in <b>Safari</b>',
    iosStep2: 'Tap the <b>Share</b> icon (bottom center)',
    iosStep3: 'Scroll down and choose: <b>"Add to Home Screen"</b>',
    iosStep4: 'Tap <b>"Add"</b>',
    androidStep1: 'Tap the browser <b>menu</b> (top right corner)',
    androidStep2: 'Choose: <b>"Add to Home Screen"</b> or <b>"Install App"</b>',
    androidStep3: 'Tap <b>"Add"</b> / <b>"Install"</b>',"""
assert old_tr_en_install in html, "FAIL: TR en install"
html = html.replace(old_tr_en_install, new_tr_en_install, 1)

# ══════════════════════════════════════════════════════════════════════
# 4. InstallModal — replace hardcoded strings + translate steps
# ══════════════════════════════════════════════════════════════════════

old_ios_steps = """  const iosSteps = [
    { icon:'🌐', html:'Nyisd meg ezt az oldalt <b>Safari</b> böngészőben' },
    { icon:'⬆️', html:'Koppints a <b>Megosztás</b> ikonra (alul, középen)' },
    { icon:'➕', html:'Görgess le és válaszd: <b>„Főképernyőre"</b>' },
    { icon:'✅', html:'Koppints a <b>„Hozzáadás"</b> gombra' },
  ];
  const androidSteps = [
    { icon:'⋮', html:'Koppints a böngésző <b>menüjére</b> (jobb felső sarok)' },
    { icon:'➕', html:'Válaszd: <b>„Hozzáadás a főképernyőhöz"</b> vagy <b>„Alkalmazás telepítése"</b>' },
    { icon:'✅', html:'Koppints a <b>„Hozzáadás"</b> / <b>„Telepítés"</b> gombra' },
  ];"""
new_ios_steps = """  const iosSteps = [
    { icon:'🌐', html:t('iosStep1') },
    { icon:'⬆️', html:t('iosStep2') },
    { icon:'➕', html:t('iosStep3') },
    { icon:'✅', html:t('iosStep4') },
  ];
  const androidSteps = [
    { icon:'⋮', html:t('androidStep1') },
    { icon:'➕', html:t('androidStep2') },
    { icon:'✅', html:t('androidStep3') },
  ];"""
assert old_ios_steps in html, "FAIL: ios/android steps"
html = html.replace(old_ios_steps, new_ios_steps, 1)

old_install_title = """          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, marginTop:6 }}>Főképernyőre</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>Telepítsd appként — ingyen, App Store nélkül</div>"""
new_install_title = """          <div style={{ fontFamily:T.font, fontWeight:T.weightDisplay, fontSize:22, color:T.ink, textTransform:'uppercase', letterSpacing:T.letterDisplay, marginTop:6 }}>{t('installTitle')}</div>
          <div style={{ fontFamily:T.font, fontSize:13, color:T.inkSoft, marginTop:4 }}>{t('installSubtitle')}</div>"""
assert old_install_title in html, "FAIL: install title"
html = html.replace(old_install_title, new_install_title, 1)

old_install_prompt = "              A böngésződ közvetlenül tudja telepíteni — nincs szükség App Store-ra."
new_install_prompt = "              {t('installBrowserPrompt')}"
assert old_install_prompt in html, "FAIL: install prompt text"
html = html.replace(old_install_prompt, new_install_prompt, 1)

old_install_btn = ">📲 Telepítés most</PrimaryButton>"
new_install_btn = ">{t('installNow')}</PrimaryButton>"
assert old_install_btn in html, "FAIL: install btn"
html = html.replace(old_install_btn, new_install_btn, 1)

# ══════════════════════════════════════════════════════════════════════
# 5. Home screen — Quick Game subtext, install button subtext
# ══════════════════════════════════════════════════════════════════════

old_quick_sub = ">2 véletlen játékos</div>"
new_quick_sub = ">{t('quickGameSub')}</div>"
assert old_quick_sub in html, "FAIL: quick game sub"
html = html.replace(old_quick_sub, new_quick_sub, 1)

old_install_home_sub = ">Telepítsd appként — ingyen</div>"
new_install_home_sub = ">{t('installHomeBtn')}</div>"
assert old_install_home_sub in html, "FAIL: install home sub"
html = html.replace(old_install_home_sub, new_install_home_sub, 1)

# ══════════════════════════════════════════════════════════════════════
# 6. Csatlakozás hardcoded string in ObserverWatching AppBar
# ══════════════════════════════════════════════════════════════════════
old_join_appbar = '{status !== \'watching\' && <AppBar title="Csatlakozás"'
new_join_appbar = "{status !== 'watching' && <AppBar title={t('joinScreen')}"
assert old_join_appbar in html, "FAIL: join appbar"
html = html.replace(old_join_appbar, new_join_appbar, 1)

html = html.replace("const APP_VERSION = 'v9.319';", "const APP_VERSION = 'v9.320';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.320 — Mobile UX: landscape CSS, safe-area sides, black-translucent, PWA install EN, TR keys")
