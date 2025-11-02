/**
 * Service Worker for Meeting Scheduler PWA
 * Provides offline functionality and caching
 */

const CACHE_VERSION = 'meeting-scheduler-v1';
const STATIC_CACHE = `${CACHE_VERSION}-static`;
const DYNAMIC_CACHE = `${CACHE_VERSION}-dynamic`;
const MAX_DYNAMIC_CACHE_SIZE = 50;

// Assets to cache on install
const STATIC_ASSETS = [
    '/',
    '/calendar/',
    '/groups/',
    '/login/',
    '/static/calendar_app/manifest.json',
    // Add other critical static assets here
];

/**
 * Limit cache size by removing oldest entries
 */
const limitCacheSize = (cacheName, maxSize) => {
    caches.open(cacheName).then(cache => {
        cache.keys().then(keys => {
            if (keys.length > maxSize) {
                cache.delete(keys[0]).then(() => limitCacheSize(cacheName, maxSize));
            }
        });
    });
};

/**
 * Install event - cache static assets
 */
self.addEventListener('install', event => {
    console.log('[Service Worker] Installing...');
    event.waitUntil(
        caches.open(STATIC_CACHE)
            .then(cache => {
                console.log('[Service Worker] Caching static assets');
                return cache.addAll(STATIC_ASSETS);
            })
            .then(() => self.skipWaiting())
            .catch(err => console.error('[Service Worker] Cache failed:', err))
    );
});

/**
 * Activate event - clean up old caches
 */
self.addEventListener('activate', event => {
    console.log('[Service Worker] Activating...');
    event.waitUntil(
        caches.keys().then(cacheNames => {
            return Promise.all(
                cacheNames
                    .filter(cacheName => cacheName.startsWith('meeting-scheduler-') &&
                                        cacheName !== STATIC_CACHE &&
                                        cacheName !== DYNAMIC_CACHE)
                    .map(cacheName => {
                        console.log('[Service Worker] Deleting old cache:', cacheName);
                        return caches.delete(cacheName);
                    })
            );
        }).then(() => self.clients.claim())
    );
});

/**
 * Fetch event - serve from cache, fallback to network
 * Strategy: Cache first, then network (for static assets)
 *          Network first, then cache (for dynamic content)
 */
self.addEventListener('fetch', event => {
    const { request } = event;
    const url = new URL(request.url);

    // Skip cross-origin requests
    if (url.origin !== location.origin) {
        return;
    }

    // Skip POST, PUT, DELETE requests (don't cache mutations)
    if (request.method !== 'GET') {
        return;
    }

    // Cache-first strategy for static assets
    if (request.url.includes('/static/')) {
        event.respondWith(
            caches.match(request).then(cachedResponse => {
                return cachedResponse || fetch(request).then(networkResponse => {
                    return caches.open(STATIC_CACHE).then(cache => {
                        cache.put(request, networkResponse.clone());
                        return networkResponse;
                    });
                });
            }).catch(() => {
                // Return offline page or default response
                return new Response('Offline - Static resource unavailable', {
                    status: 503,
                    statusText: 'Service Unavailable'
                });
            })
        );
        return;
    }

    // Network-first strategy for dynamic content (HTML pages, API calls)
    event.respondWith(
        fetch(request)
            .then(networkResponse => {
                // Cache successful responses
                if (networkResponse.ok) {
                    return caches.open(DYNAMIC_CACHE).then(cache => {
                        cache.put(request, networkResponse.clone());
                        limitCacheSize(DYNAMIC_CACHE, MAX_DYNAMIC_CACHE_SIZE);
                        return networkResponse;
                    });
                }
                return networkResponse;
            })
            .catch(() => {
                // Network failed, try cache
                return caches.match(request).then(cachedResponse => {
                    if (cachedResponse) {
                        return cachedResponse;
                    }
                    // Return offline page for navigation requests
                    if (request.mode === 'navigate') {
                        return caches.match('/').then(response => {
                            return response || new Response(
                                '<h1>Offline</h1><p>You are currently offline. Please check your internet connection.</p>',
                                {
                                    headers: { 'Content-Type': 'text/html' }
                                }
                            );
                        });
                    }
                    // Return generic offline response
                    return new Response('Offline', {
                        status: 503,
                        statusText: 'Service Unavailable'
                    });
                });
            })
    );
});

/**
 * Background sync event (for future offline form submission support)
 */
self.addEventListener('sync', event => {
    console.log('[Service Worker] Background sync:', event.tag);
    if (event.tag === 'sync-unavailability') {
        event.waitUntil(
            // Implement sync logic here
            Promise.resolve()
        );
    }
});

/**
 * Push notification event (for future notification support)
 */
self.addEventListener('push', event => {
    console.log('[Service Worker] Push received');
    if (event.data) {
        const data = event.data.json();
        const options = {
            body: data.body || 'New notification from Meeting Scheduler',
            icon: '/static/calendar_app/icons/icon-192x192.png',
            badge: '/static/calendar_app/icons/icon-72x72.png',
            vibrate: [200, 100, 200],
            data: data.url ? { url: data.url } : {}
        };

        event.waitUntil(
            self.registration.showNotification(data.title || 'Meeting Scheduler', options)
        );
    }
});

/**
 * Notification click event
 */
self.addEventListener('notificationclick', event => {
    console.log('[Service Worker] Notification clicked');
    event.notification.close();

    if (event.notification.data && event.notification.data.url) {
        event.waitUntil(
            clients.openWindow(event.notification.data.url)
        );
    }
});
