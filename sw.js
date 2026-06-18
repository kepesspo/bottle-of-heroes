self.addEventListener('install', () => self.skipWaiting());
self.addEventListener('activate', e => e.waitUntil(self.clients.claim()));
self.addEventListener('fetch', () => {});

self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.matchAll({ type: 'window', includeUncontrolled: true }).then(cs => {
    const focused = cs.find(c => c.focused);
    if (focused) return focused.focus();
    if (cs.length) return cs[0].focus();
    return clients.openWindow('/bottle-of-heroes/');
  }));
});
