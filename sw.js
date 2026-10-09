// W.A.G.E. v0.5 — offline shell, only same-origin public resources.
const VERSION='wage-joliet-pwa-v06';
const ASSETS=['./','./index.html','./manifest.webmanifest','./icon-192.png','./icon-512.png','./wage-cover.jpg'];
self.addEventListener('install',event=>event.waitUntil((async()=>{const cache=await caches.open(VERSION);await cache.addAll(ASSETS);await self.skipWaiting()})()));
self.addEventListener('activate',event=>event.waitUntil((async()=>{for(const key of await caches.keys()){if(key.startsWith('wage-joliet-pwa-')&&key!==VERSION)await caches.delete(key)}await self.clients.claim()})()));
self.addEventListener('fetch',event=>{const req=event.request;const url=new URL(req.url);if(req.method!=='GET'||url.origin!==self.location.origin)return;
 if(req.mode==='navigate'||url.pathname.endsWith('/data/current.json')){event.respondWith((async()=>{const cache=await caches.open(VERSION);try{const response=await fetch(req);if(response.ok)await cache.put(req,response.clone());return response}catch(err){const cached=await cache.match(req,{ignoreSearch:true});if(cached)return cached; if(req.mode==='navigate'){const fallback=await cache.match('./index.html');if(fallback)return fallback;}throw err}})());return;}
 event.respondWith((async()=>{const cache=await caches.open(VERSION);const cached=await cache.match(req);if(cached)return cached;try{const response=await fetch(req);if(response.ok)await cache.put(req,response.clone());return response}catch(e){return Response.error()}})());
});
