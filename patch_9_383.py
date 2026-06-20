#!/usr/bin/env python3
"""v9.383 — Splash: animáció a React mount UTÁN indul, Babel freeze megszűnik"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# ── 1. Logo wrap: töröljük a CSS animációt (JS indítja majd) ──────────────────
old_logo_wrap = """    #splash-logo-wrap {
      position:relative; z-index:2;
      animation: impactDrop 0.55s cubic-bezier(0.3,0,0.4,1) 0s both,
                 impactSettle 0.2s ease-out 0.55s both;
    }"""

new_logo_wrap = """    #splash-logo-wrap {
      position:relative; z-index:2;
    }"""

assert old_logo_wrap in html, "FAIL: logo wrap css"
html = html.replace(old_logo_wrap, new_logo_wrap, 1)

# ── 2. Init script: csak hátteret állít be, animációt NEM indít ────────────────
old_init_body = """  if (localStorage.getItem('boh_splash') !== '0') {
    splash.style.display = '';

    // ── JS-vezérelt animációk ──
    var logo   = document.getElementById('splash-logo');
    var flash  = document.getElementById('splash-flash');
    var shocks = document.querySelectorAll('.splash-shock');
    var letters = document.querySelectorAll('.splash-letter');

    // Impact: 520ms — logo eléri a célt, flash + shockwave egyszerre
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
    }, 2300);
  }"""

new_init_body = """  if (localStorage.getItem('boh_splash') !== '0') {
    splash.style.display = '';
    // Animáció a React mount után indul (window._startSplashAnim hívásra vár)
    window._startSplashAnim = function() {
      var logo    = document.getElementById('splash-logo');
      var logoW   = document.getElementById('splash-logo-wrap');
      var flash   = document.getElementById('splash-flash');
      var shocks  = document.querySelectorAll('.splash-shock');
      var letters = document.querySelectorAll('.splash-letter');
      if (!logo) return;

      // Logo zuhan
      logoW.style.animation = 'impactDrop 0.55s cubic-bezier(0.3,0,0.4,1) 0s both, impactSettle 0.2s ease-out 0.55s both';

      // Impact: flash + shockwave
      setTimeout(function() {
        if (flash) flash.style.animation = 'splashFlash 0.6s ease-out forwards';
        shocks.forEach(function(el, i) {
          setTimeout(function() {
            el.style.animation = 'splashShock ' + (0.75 + i * 0.18) + 's cubic-bezier(0.1,0.5,0.2,1) forwards';
          }, i * 40);
        });
      }, 520);

      // Betűk slam
      setTimeout(function() {
        letters.forEach(function(el, i) {
          setTimeout(function() {
            el.style.animation = 'splashLetterSlam 0.5s cubic-bezier(0.22,1,0.36,1) both';
          }, i * 55);
        });
      }, 700);

      // Tagline
      setTimeout(function() {
        var tagline = document.getElementById('splash-tagline');
        if (tagline) tagline.style.animation = 'splashTagline 0.5s ease-out forwards';
      }, 1900);

      // Idle glow
      setTimeout(function() {
        if (logo) logo.style.animation = 'splashLogoIdle 3s ease-in-out infinite';
      }, 2300);
    };
  }"""

assert old_init_body in html, "FAIL: init body"
html = html.replace(old_init_body, new_init_body, 1)

# ── 3. React mount: _startSplashAnim() + timer egyszerre indul ────────────────
old_dismiss = """// Hide splash: wait for BOTH React ready AND minimum display time (3s)
window._splashReactReady = false;
window._splashTimerDone  = false;
window._hideSplash = function() {
  if (!window._splashReactReady || !window._splashTimerDone) return;
  const splash = document.getElementById('splash');
  if (splash) {
    splash.classList.add('hidden');
    setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 600);
  }
};
// Minimum 3s — covers logo drop (0.7s) + letter slams (0.9s–2.1s) + tagline (2.7s) + buffer
setTimeout(function() {
  window._splashTimerDone = true;
  window._hideSplash();
}, 3500);
const _origRender = ReactDOM.createRoot;
ReactDOM.createRoot = function(container, opts) {
  const root = _origRender.call(this, container, opts);
  const _origRootRender = root.render.bind(root);
  root.render = function(element) {
    _origRootRender(element);
    requestAnimationFrame(() => {
      window._splashReactReady = true;
      window._hideSplash();
    });
  };
  return root;
};

setTimeout(function() { ReactDOM.createRoot(document.getElementById('root')).render(<Root />); }, 1000);"""

new_dismiss = """// Splash: animáció React mount után indul, elrejtés 3s-al később
window._splashTimerDone  = false;
window._splashReactReady = false;
window._hideSplash = function() {
  if (!window._splashReactReady || !window._splashTimerDone) return;
  const splash = document.getElementById('splash');
  if (splash) {
    splash.classList.add('hidden');
    setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 600);
  }
};
const _origRender = ReactDOM.createRoot;
ReactDOM.createRoot = function(container, opts) {
  const root = _origRender.call(this, container, opts);
  const _origRootRender = root.render.bind(root);
  root.render = function(element) {
    _origRootRender(element);
    requestAnimationFrame(() => {
      // Babel kész, React mountolt — most indítjuk az animációt
      if (typeof window._startSplashAnim === 'function') window._startSplashAnim();
      window._splashReactReady = true;
      // 3s az animáció lejátszásához
      setTimeout(function() {
        window._splashTimerDone = true;
        window._hideSplash();
      }, 3000);
    });
  };
  return root;
};

ReactDOM.createRoot(document.getElementById('root')).render(<Root />);"""

assert old_dismiss in html, "FAIL: dismiss block"
html = html.replace(old_dismiss, new_dismiss, 1)

html = html.replace("const APP_VERSION = 'v9.382';", "const APP_VERSION = 'v9.383';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.383 — Splash animáció React mount után indul, freeze megszűnik")
