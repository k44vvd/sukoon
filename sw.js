// سدرة: service worker (offline basics, share-to-Wamda, push notifications)
const V = 'sukoon-v2';
const STATIC = /\/(fonts|images|tafsir|frames|adhan|js\/ort)\/|quran\.json$|\.(png|jpg|woff2?|ttf)$/;
self.addEventListener('install', e => { self.skipWaiting(); });
self.addEventListener('activate', e => { e.waitUntil((async () => { const ks = await caches.keys(); await Promise.all(ks.filter(k => k.startsWith('sukoon-') && k !== V && k !== 'sukoon-share').map(k => caches.delete(k))); await self.clients.claim(); })()); });
self.addEventListener('fetch', e => {
  const u = new URL(e.request.url);
  if (e.request.method === 'POST' && u.searchParams.has('share-target')) {
    e.respondWith((async () => { try { const fd = await e.request.formData(); const f = fd.get('video'); if (f && f.size) { const c = await caches.open('sukoon-share'); await c.put('./__shared-video', new Response(f, { headers: { 'Content-Type': f.type || 'video/mp4', 'X-Name': encodeURIComponent(f.name || 'video.mp4') } })); } } catch (err) {} return Response.redirect('./?shared=1#/reels', 303); })());
    return;
  }
  if (e.request.method !== 'GET' || u.origin !== location.origin) return;
  if (e.request.mode === 'navigate') { e.respondWith(fetch(e.request).then(r => { const cp = r.clone(); caches.open(V).then(c => c.put('./', cp)); return r; }).catch(() => caches.match('./'))); return; }
  if (STATIC.test(u.pathname)) e.respondWith(caches.match(e.request).then(hit => hit || fetch(e.request).then(r => { if (r.ok) { const cp = r.clone(); caches.open(V).then(c => c.put(e.request, cp)); } return r; })));
});
self.addEventListener('push', e => {
  let d = {}; try { d = e.data ? e.data.json() : {}; } catch { d = { title: 'سدرة', body: e.data ? e.data.text() : '' }; }
  e.waitUntil(self.registration.showNotification(d.title || 'سدرة', { body: d.body || '', icon: 'icon-192.png', badge: 'icon-192.png', tag: d.tag || undefined, renotify: !!d.tag, dir: 'rtl', lang: 'ar', data: { url: d.url || './#/home' } }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close(); const url = new URL((e.notification.data && e.notification.data.url) || './', self.registration.scope).href;
  e.waitUntil((async () => { const cs = await self.clients.matchAll({ type: 'window', includeUncontrolled: true }); for (const c of cs) { if (c.url.startsWith(self.registration.scope)) { await c.focus(); c.navigate(url).catch(() => {}); return; } } await self.clients.openWindow(url); })());
});
