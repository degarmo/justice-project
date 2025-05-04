// tracker/static/tracker/js/behavior.js

(function () {
    const endpoint = '/log-behavior/';
    let mouseMoves = [];
    let clickEvents = [];
    let lastMouseLog = Date.now();
    let lastScrollTime = null;
    let lastClickTime = null;
    let idleTimer;
    const idleThreshold = 30000; // 30 seconds

    // --- Mouse movement tracking (sampled every 500ms) ---
    document.addEventListener('mousemove', (e) => {
        const now = Date.now();
        if (now - lastMouseLog > 500) {
            mouseMoves.push({ x: e.clientX, y: e.clientY, time: now });
            lastMouseLog = now;
        }
    });

    // --- Click tracking ---
    document.addEventListener('click', (e) => {
        const now = Date.now();
        clickEvents.push({ x: e.clientX, y: e.clientY, element: e.target.tagName, time: now });

        // ✅ Send click behavior
        sendBehavior({ type: 'click', x: e.clientX, y: e.clientY, element: e.target.tagName, time: now });

        // Impulsive click+scroll check
        if (lastScrollTime && now - lastScrollTime < 800) {
            sendBehavior({ type: 'impulsive_action', time: now });
        }

        lastClickTime = now;
        resetIdleTimer();
    });


    // --- Scroll tracking ---
    window.addEventListener('scroll', () => {
        const now = Date.now();
        const scrollDepth = Math.round((window.scrollY + window.innerHeight) / document.body.scrollHeight * 100);

        sendBehavior({ type: 'scroll', depth: scrollDepth, time: now });

        // Rapid scroll detection
        if (lastScrollTime && now - lastScrollTime < 500) {
            sendBehavior({ type: 'rapid_scroll', time: now });
        }

        lastScrollTime = now;
        resetIdleTimer();
    });

    // --- Tab focus/blur detection ---
    document.addEventListener('visibilitychange', () => {
        const now = Date.now();
        sendBehavior({ type: document.hidden ? 'tab_blur' : 'tab_focus', time: now });
    });

    function sendBehavior(data) {
        console.log("Sending behavior:", data);
        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        }).then(res => console.log("Response:", res.status));
    }
    
    // --- Idle detection ---
    function resetIdleTimer() {
        clearTimeout(idleTimer);
        idleTimer = setTimeout(() => {
            sendBehavior({ type: 'idle', time: Date.now() });
        }, idleThreshold);
    }
    ['mousemove', 'keydown', 'scroll', 'click'].forEach(event => {
        document.addEventListener(event, resetIdleTimer);
    });
    resetIdleTimer();

    // --- Hover tracking for curiosity markers ---
    const curiosityElements = ['P', 'H1', 'H2', 'H3', 'A', 'BUTTON'];
    curiosityElements.forEach(tag => {
        document.querySelectorAll(tag).forEach(el => {
            el.addEventListener('mouseenter', () => {
                sendBehavior({ type: 'hover', element: tag, time: Date.now() });
            });
        });
    });

    // --- Periodic mouse path sender (every 10s) ---
    setInterval(() => {
        if (mouseMoves.length) {
            sendBehavior({ type: 'mouse_path', path: mouseMoves });
            mouseMoves = [];
        }
    }, 10000);

    // --- Send data to backend ---
    function sendBehavior(data) {
        fetch(endpoint, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(data)
        });
        fetch('/log-behavior/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        }).catch(err => {
            console.error('Behavior log error:', err);
        });
    }
    fetch('/log-behavior/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ type: 'test_click', timestamp: Date.now() })
      })
      .then(res => res.json())
      .then(console.log)
      .catch(console.error);
      
})();
