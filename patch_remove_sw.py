import re

with open('index.html', 'r', encoding='utf-8') as f:
    content = f.read()

OLD = '''// ── Service Worker + Notification permission ──
if ('serviceWorker' in navigator) {
  const _swVer = APP_VERSION.replace('v','');
  navigator.serviceWorker.register(`./sw.js?v=${_swVer}`).catch(() => {});
}
window._bohRequestNotifPermission = function() {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'default') {
    Notification.requestPermission().catch(() => {});
  }
};
window._bohShowNotif = function(title, body) {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  if ('serviceWorker' in navigator) {
    navigator.serviceWorker.ready.then(reg => {
      return reg.showNotification(title, { body, icon: './icon-192.png', badge: './icon-192.png', tag: 'bp-notif', renotify: true, vibrate: [200, 100, 200] });
    }).catch(() => { try { new Notification(title, { body }); } catch(e) {} });
  } else {
    try { new Notification(title, { body }); } catch(e) {}
  }
};'''

NEW = '''// ── Service Worker unregister (caching removed) ──
if ('serviceWorker' in navigator) {
  navigator.serviceWorker.getRegistrations().then(regs => { regs.forEach(r => r.unregister()); });
}
window._bohRequestNotifPermission = function() {
  if (!('Notification' in window)) return;
  if (Notification.permission === 'default') {
    Notification.requestPermission().catch(() => {});
  }
};
window._bohShowNotif = function(title, body) {
  if (!('Notification' in window) || Notification.permission !== 'granted') return;
  try { new Notification(title, { body }); } catch(e) {}
};'''

assert OLD in content, "OLD not found!"
content = content.replace(OLD, NEW, 1)

content = re.sub(r'v9\.685', 'v9.686', content, count=2)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(content)

print("Done! v9.686")
