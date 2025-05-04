// /tracker/static/tracker/js/fingerprint.js

function detectAdblocker() {
    const bait = document.createElement('div');
    bait.className = 'adsbox';
    bait.style.position = 'absolute';
    bait.style.height = '1px';
    bait.style.width = '1px';
    bait.style.left = '-10000px';
    document.body.appendChild(bait);
    const detected = window.getComputedStyle(bait).display === 'none';
    document.body.removeChild(bait);
    return detected;
}

function detectIncognitoMode() {
    return new Promise((resolve) => {
        const fs = window.RequestFileSystem || window.webkitRequestFileSystem;
        if (!fs) return resolve(false); // assume not incognito if unsupported
        fs(window.TEMPORARY, 100, () => resolve(false), () => resolve(true));
    });
}

async function sendFingerprint() {
    const incognito = await detectIncognitoMode();

    const data = {
        fingerprint_hash: crypto.randomUUID(),
        timezone: Intl.DateTimeFormat().resolvedOptions().timeZone,
        screen_resolution: `${window.screen.width}x${window.screen.height}`,
        color_depth: window.screen.colorDepth,
        languages: navigator.languages,
        platform: navigator.platform,
        touch_support: 'ontouchstart' in window || navigator.maxTouchPoints > 0,
        adblocker: detectAdblocker(),
        incognito: incognito
    };

    fetch('/api/fingerprint-log/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    });
}

window.addEventListener('load', sendFingerprint);
