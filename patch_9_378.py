#!/usr/bin/env python3
"""v9.378 — Splash minimum display time: vár amíg az animáció végigmegy (~3s)"""

with open('index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Replace the splash dismissal logic — add minimum time + React-ready flag
old_dismiss = """// Hide splash after React renders
const _origRender = ReactDOM.createRoot;
ReactDOM.createRoot = function(container, opts) {
  const root = _origRender.call(this, container, opts);
  const _origRootRender = root.render.bind(root);
  root.render = function(element) {
    _origRootRender(element);
    requestAnimationFrame(() => {
      const splash = document.getElementById('splash');
      if (splash) {
        splash.classList.add('hidden');
        setTimeout(() => { if (splash.parentNode) splash.parentNode.removeChild(splash); }, 500);
      }
    });
  };
  return root;
};"""

new_dismiss = """// Hide splash: wait for BOTH React ready AND minimum display time (3s)
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
}, 3000);
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
};"""

assert old_dismiss in html, "FAIL: old dismiss code"
html = html.replace(old_dismiss, new_dismiss, 1)

html = html.replace("const APP_VERSION = 'v9.377';", "const APP_VERSION = 'v9.378';")

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Done: v9.378 — Splash minimum 3s display time")
