// Capture mouse movements
document.addEventListener('mousemove', function (e) {
    const payload = {
        type: 'mousemove',
        x: e.clientX,
        y: e.clientY,
        timestamp: Date.now()
    };
    navigator.sendBeacon('/api/behavior-log/', JSON.stringify(payload));
});

// Capture clicks
document.addEventListener('click', function (e) {
    const payload = {
        type: 'click',
        x: e.clientX,
        y: e.clientY,
        target: e.target.tagName,
        timestamp: Date.now()
    };
    navigator.sendBeacon('/api/behavior-log/', JSON.stringify(payload));
});

// Capture scroll depth
document.addEventListener('scroll', function () {
    const payload = {
        type: 'scroll',
        scrollY: window.scrollY,
        timestamp: Date.now()
    };
    navigator.sendBeacon('/api/behavior-log/', JSON.stringify(payload));
});
