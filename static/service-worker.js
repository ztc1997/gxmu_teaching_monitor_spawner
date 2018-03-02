var version = 1;

var cacheName = 'gxmu_teaching_monitor_spawner-v1';

var filesToCache = [
    '/',
    '/static/conwork.js',
    '/static/website.js',
    '/static/site.css',
    '/static/ghpages-materialize.css',
    '/static/logo.jpg',
    '/static/iconoclast.jpg',
    '/static/favicons/favicon.ico',
    '/static/favicons/favicon-144.jpg',
    '/static/favicons/favicon-152.jpg',
    '/static/favicons/logo.jpg'
];

self.addEventListener('activate', function (event) {
    event.waitUntil(
        caches.open(cacheName).then(function (cache) {
            cache.keys().then(function (cacheNames) {
                return Promise.all(
                    cacheNames.map(function (cacheName) {
                        if (filesToCache.includes(cacheName)) {
                            // 删除旧版本缓存的文件
                            return cache.delete(cacheName);
                        }
                    })
                );
            });
        })
    );
});

self.addEventListener('fetch', function (event) {
    event.respondWith(
        caches.open(cacheName).then(function (cache) {
            return cache.match(event.request).then(function (response) {
                return response || fetch(event.request).then(function (response) {
                    cache.put(event.request, response.clone());
                    return response;
                });
            });
        })
    );
});
