// tracker/static/tracker/js/behavior.js

(function () {
    const endpoint = '/log-behavior/';
    const batchInterval = 10000; // send every 10 seconds
    const idleThreshold = 30000;

    let behaviorQueue = [];
    let lastMouseLog = Date.now();
    let lastScrollTime = null;
    let lastClickTime = null;
    let idleTimer;

    // --- Add to queue ---
    function queueBehavior(event) {
        behaviorQueue.push(event);
    }

    // --- Mouse movement (sampled) ---
    document.addEventListener('mousemove', (e) => {
        const now = Date.now();
        if (now - lastMouseLog > 500) {
            queueBehavior({ type: 'mousemove', x: e.clientX, y: e.clientY, time: now });
            lastMouseLog = now;
        }
    });

    // --- Click ---
    document.addEventListener('click', (e) => {
        const now = Date.now();
        queueBehavior({ type: 'click', x: e.clientX, y: e.clientY, element: e.target.tagName, time: now });

        if (lastScrollTime && now - lastScrollTime < 800) {
            queueBehavior({ type: 'impulsive_action', time: now });
        }

        lastClickTime = now;
        resetIdleTimer();
    });

    // --- Scroll ---
    window.addEventListener('scroll', () => {
        const now = Date.now();
        const scrollDepth = Math.round((window.scrollY + window.innerHeight) / document.body.scrollHeight * 100);
        queueBehavior({ type: 'scroll', depth: scrollDepth, time: now });

        if (lastScrollTime && now - lastScrollTime < 500) {
            queueBehavior({ type: 'rapid_scroll', time: now });
        }

        lastScrollTime = now;
        resetIdleTimer();
    });

    // --- Visibility (tab) change ---
    document.addEventListener('visibilitychange', () => {
        queueBehavior({ type: document.hidden ? 'tab_blur' : 'tab_focus', time: Date.now() });
    });

    // --- Hover tracking ---
    const tags = ['P', 'H1', 'H2', 'H3', 'A', 'BUTTON'];
    tags.forEach(tag => {
        document.querySelectorAll(tag).forEach(el => {
            el.addEventListener('mouseenter', () => {
                queueBehavior({ type: 'hover', element: tag, time: Date.now() });
            });
        });
    });

    // --- Idle detection ---
    function resetIdleTimer() {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(() => {
            queueBehavior({ type: 'idle', time: Date.now() });
        }, idleThreshold);
    }

    ['mousemove', 'keydown', 'scroll', 'click'].forEach(event => {
        document.addEventListener(event, resetIdleTimer);
    });
    resetIdleTimer();

    // --- Batch sender ---
    function sendBatch() {
        if (!behaviorQueue.length) return;

        const payload = {
            type: 'batch',
            events: behaviorQueue
        };

        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        }).catch(err => {
            console.error('Behavior log batch error:', err);
        });

        behaviorQueue = [];
    }

    setInterval(sendBatch, batchInterval);

    // --- Startup test ping (optional) ---
    fetch(endpoint, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ type: 'startup_ping', time: Date.now() })
    }).then(res => res.json()).then(console.log).catch(console.error);
})();
