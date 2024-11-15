const CACHE_NAME = 'app-cache-v1';
const urlsToCache = [
    '/',
    '/index.html',
    '/static/js/app.js',
    '/static/icons/icon-32.png',
    '/manifest.json',
    '/styles/main.css',
    '/scripts/main.js',
    '/images/logo.png'
];

// Install the service worker
self.addEventListener('install', event => {
    event.waitUntil(
        caches.open(CACHE_NAME).then(async cache => {
            try {
                // Attempt to add all URLs to the cache
                await cache.addAll(urlsToCache);
                console.log('All resources cached successfully');
            } catch (error) {
                console.warn('Failed to cache some resources:', error);
            }
        })
    );
});

// Cache and return requests
self.addEventListener('fetch', event => {
    event.respondWith(
        caches.match(event.request)
            .then(response => {
                // Cache hit - return response
                if (response) {
                    return response;
                }
                // Fetch from network if not cached
                return fetch(event.request);
            })
            .catch(() => caches.match('/')) // Serve home page or offline page if offline
    );
});

// Update the service worker
self.addEventListener('activate', event => {
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames.map(cacheName => {
                    if (cacheName !== CACHE_NAME) {
                        return caches.delete(cacheName);
                    }
                })
            );
        })
    );
});
