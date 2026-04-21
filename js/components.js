/* =============================================================
   WAYTHROUGH PROJECT — Shared Components
   Nav and Footer are injected via JS so they live in one place.
   Edit them here; every page picks up the change automatically.
   ============================================================= */

// ── Determine path prefix based on page depth ──
// Pages in subdirectories need "../" to reach root assets
const depth = (function () {
    const path = window.location.pathname;
    // Count how many directories deep we are from root
    const segments = path.split('/').filter(s => s && !s.includes('.'));
    return segments.length;
})();
const root = depth === 0 ? './' : '../'.repeat(depth);

// ── SVG Icons (reusable) ──
const ICONS = {
    home: '<svg viewBox="0 0 24 24" fill="none" stroke="#fff" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><path d="M3 9l9-7 9 7v11a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V9z"/><polyline points="9 22 9 12 15 12 15 22"/></svg>',
    arrow: '<svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5"><line x1="5" y1="12" x2="19" y2="12"/><polyline points="12 5 19 12 12 19"/></svg>',
    youtube: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z"/><polygon points="9.545 15.568 15.818 12 9.545 8.432" fill="currentColor" class="yt-triangle"/></svg>',
    instagram: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>',
    tiktok: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>',
    facebook: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
};

// ── Theme Icons ──
const MOON_ICON = '<svg class="icon-moon" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 12.79A9 9 0 1 1 11.21 3 7 7 0 0 0 21 12.79z"/></svg>';
const SUN_ICON = '<svg class="icon-sun" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="5"/><line x1="12" y1="1" x2="12" y2="3"/><line x1="12" y1="21" x2="12" y2="23"/><line x1="4.22" y1="4.22" x2="5.64" y2="5.64"/><line x1="18.36" y1="18.36" x2="19.78" y2="19.78"/><line x1="1" y1="12" x2="3" y2="12"/><line x1="21" y1="12" x2="23" y2="12"/><line x1="4.22" y1="19.78" x2="5.64" y2="18.36"/><line x1="18.36" y1="5.64" x2="19.78" y2="4.22"/></svg>';

// ── Theme (dark mode) ──
function getStoredTheme() {
    try { return localStorage.getItem('theme'); } catch (e) { return null; }
}
function setStoredTheme(theme) {
    try { localStorage.setItem('theme', theme); } catch (e) { /* no-op */ }
}
function getPreferredTheme() {
    const stored = getStoredTheme();
    if (stored) return stored;
    return window.matchMedia('(prefers-color-scheme: dark)').matches ? 'dark' : 'light';
}
function applyTheme(theme) {
    document.documentElement.setAttribute('data-theme', theme);
}
// Apply theme immediately (before DOMContentLoaded) to avoid flash
applyTheme(getPreferredTheme());

function toggleTheme() {
    const current = document.documentElement.getAttribute('data-theme') || 'light';
    const next = current === 'dark' ? 'light' : 'dark';
    applyTheme(next);
    setStoredTheme(next);
}

// Listen for OS-level theme changes
window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change', (e) => {
    if (!getStoredTheme()) {
        applyTheme(e.matches ? 'dark' : 'light');
    }
});

// ── Render Skip Link ──
function renderSkipLink() {
    const skip = document.createElement('a');
    skip.href = '#main-content';
    skip.className = 'skip-link';
    skip.textContent = 'Skip to main content';
    document.body.prepend(skip);
}

// ── Search Icon SVG ──
const SEARCH_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><circle cx="11" cy="11" r="8"/><line x1="21" y1="21" x2="16.65" y2="16.65"/></svg>';
const CLOSE_ICON = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><line x1="18" y1="6" x2="6" y2="18"/><line x1="6" y1="6" x2="18" y2="18"/></svg>';

// ── HTML escaping (prevents XSS in dynamic content) ──
function escapeHTML(str) {
    const div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
}

// ── Search state ──
let searchIndex = null;
let searchOpen = false;

async function loadSearchIndex() {
    if (searchIndex) return searchIndex;
    try {
        const res = await fetch(root + 'js/search-index.json?v=16');
        if (!res.ok) throw new Error('Search index returned ' + res.status);
        searchIndex = await res.json();
        return searchIndex;
    } catch (e) {
        console.warn('Search index failed to load', e);
        return [];
    }
}

function performSearch(query) {
    if (!searchIndex || !query.trim()) return [];
    const terms = query.toLowerCase().trim().split(/\s+/);
    const scored = searchIndex.map(item => {
        const haystack = (item.title + ' ' + item.desc + ' ' + item.keywords).toLowerCase();
        let score = 0;
        for (const term of terms) {
            if (item.title.toLowerCase().includes(term)) score += 3;
            if (item.keywords.toLowerCase().includes(term)) score += 2;
            if (item.desc.toLowerCase().includes(term)) score += 1;
        }
        return { ...item, score };
    }).filter(item => item.score > 0);
    scored.sort((a, b) => b.score - a.score);
    return scored.slice(0, 6);
}

let searchActiveIndex = -1; // tracks arrow-key highlighted result

function openSearch() {
    const overlay = document.getElementById('searchOverlay');
    const input = document.getElementById('searchInput');
    if (!overlay) return;
    searchOpen = true;
    searchActiveIndex = -1;
    overlay.classList.add('active');
    overlay.setAttribute('aria-hidden', 'false');
    overlay.removeAttribute('inert');
    document.getElementById('searchToggle').setAttribute('aria-expanded', 'true');
    input.focus();
    loadSearchIndex();
    document.addEventListener('keydown', handleSearchKeys);
}

function closeSearch() {
    const overlay = document.getElementById('searchOverlay');
    const input = document.getElementById('searchInput');
    const toggle = document.getElementById('searchToggle');
    if (!overlay || !input || !toggle) return;
    searchOpen = false;
    searchActiveIndex = -1;
    overlay.classList.remove('active');
    overlay.setAttribute('aria-hidden', 'true');
    overlay.setAttribute('inert', '');
    input.value = '';
    input.removeAttribute('aria-activedescendant');
    document.getElementById('searchResults').innerHTML = '';
    document.getElementById('searchLive').textContent = '';
    toggle.setAttribute('aria-expanded', 'false');
    toggle.focus(); // return focus to trigger button
    document.removeEventListener('keydown', handleSearchKeys);
}

function handleSearchKeys(e) {
    if (e.key === 'Escape') { closeSearch(); return; }

    const items = document.querySelectorAll('.search-result-item');
    if (!items.length) return;

    if (e.key === 'ArrowDown') {
        e.preventDefault();
        searchActiveIndex = Math.min(searchActiveIndex + 1, items.length - 1);
        updateActiveResult(items);
    } else if (e.key === 'ArrowUp') {
        e.preventDefault();
        searchActiveIndex = Math.max(searchActiveIndex - 1, -1);
        updateActiveResult(items);
        if (searchActiveIndex === -1) document.getElementById('searchInput').focus();
    } else if (e.key === 'Enter' && searchActiveIndex >= 0 && items[searchActiveIndex]) {
        e.preventDefault();
        items[searchActiveIndex].click();
    }
}

function updateActiveResult(items) {
    const input = document.getElementById('searchInput');
    items.forEach((item, i) => {
        if (i === searchActiveIndex) {
            item.classList.add('active');
            item.setAttribute('aria-selected', 'true');
            item.focus();
            input.setAttribute('aria-activedescendant', item.id);
        } else {
            item.classList.remove('active');
            item.setAttribute('aria-selected', 'false');
        }
    });
    if (searchActiveIndex === -1) {
        input.removeAttribute('aria-activedescendant');
    }
}

function renderSearchResults(results) {
    const container = document.getElementById('searchResults');
    const liveRegion = document.getElementById('searchLive');
    searchActiveIndex = -1;

    if (!results.length) {
        container.innerHTML = '<div class="search-no-results">No matching resources found. Try a different keyword.</div>';
        liveRegion.textContent = 'No matching resources found.';
        return;
    }
    container.innerHTML = results.map((r, i) => `
        <a href="${root}${encodeURI(r.url)}" class="search-result-item" role="option" id="search-result-${i}" aria-selected="false" tabindex="-1">
            <div class="search-result-title">${escapeHTML(r.title)}</div>
            <div class="search-result-desc">${escapeHTML(r.desc)}</div>
        </a>
    `).join('');
    liveRegion.textContent = results.length + ' result' + (results.length === 1 ? '' : 's') + ' found. Use arrow keys to navigate.';
}

// Focus trap: keep Tab within the search overlay when open
function trapFocusInSearch(e) {
    if (!searchOpen || e.key !== 'Tab') return;
    const overlay = document.getElementById('searchOverlay');
    const focusable = overlay.querySelectorAll('input:not([disabled]), button:not([disabled]), a[href]:not([disabled]), [tabindex]:not([tabindex="-1"]):not([disabled]):not([aria-disabled="true"])');
    if (!focusable.length) return;
    const first = focusable[0];
    const last = focusable[focusable.length - 1];
    if (e.shiftKey && document.activeElement === first) {
        e.preventDefault();
        last.focus();
    } else if (!e.shiftKey && document.activeElement === last) {
        e.preventDefault();
        first.focus();
    }
}

// ── Render Navigation ──
function renderNav() {
    const nav = document.createElement('nav');
    nav.className = 'nav';
    nav.id = 'nav';
    nav.setAttribute('aria-label', 'Main navigation');
    nav.innerHTML = `
        <div class="container nav-inner">
            <a href="${root}index.html" class="nav-logo">
                <picture aria-hidden="true">
                    <source srcset="${root}images/logo-icon.webp" type="image/webp">
                    <img src="${root}images/logo-icon.png" alt="" class="nav-logo-img" width="72" height="39">
                </picture>
                Waythrough Project
            </a>
            <ul class="nav-links">
                <li><a href="${root}resources/index.html">Resources</a></li>
                <li><a href="${root}resources/where-to-start.html">Where to Start</a></li>
                <li><a href="${root}blog/index.html">Blog</a></li>
                <li><a href="${root}videos/index.html">Videos</a></li>
                <li><a href="${root}resources/ask.html">Ask a Question</a></li>
                <li><a href="${root}index.html#about">About</a></li>
            </ul>
            <div class="nav-actions">
                <button class="search-toggle" id="searchToggle" aria-label="Search resources" aria-expanded="false">
                    <span aria-hidden="true">${SEARCH_ICON}</span>
                </button>
                <button class="theme-toggle" id="themeToggle" aria-label="Toggle dark mode">
                    <span aria-hidden="true">${MOON_ICON}${SUN_ICON}</span>
                </button>
                <button class="hamburger" id="hamburger" aria-label="Toggle menu" aria-expanded="false">
                    <span></span><span></span><span></span>
                </button>
            </div>
        </div>
    `;
    // Search overlay
    const searchOverlay = document.createElement('div');
    searchOverlay.className = 'search-overlay';
    searchOverlay.id = 'searchOverlay';
    searchOverlay.setAttribute('aria-hidden', 'true');
    searchOverlay.setAttribute('inert', '');
    searchOverlay.setAttribute('role', 'dialog');
    searchOverlay.setAttribute('aria-label', 'Search resources');
    searchOverlay.innerHTML = `
        <div class="search-container">
            <div class="search-input-wrap">
                <span class="search-input-icon" aria-hidden="true">${SEARCH_ICON}</span>
                <label for="searchInput" class="sr-only">Search resources</label>
                <input type="text" id="searchInput" class="search-input" placeholder="Search resources (e.g. Section 8, disability, voucher...)" autocomplete="off" role="combobox" aria-controls="searchResults" aria-expanded="false" aria-autocomplete="list">
                <button class="search-close" id="searchClose" aria-label="Close search">${CLOSE_ICON}</button>
            </div>
            <div class="search-results" id="searchResults" role="listbox" aria-label="Search results"></div>
            <div id="searchLive" class="sr-only" aria-live="polite" aria-atomic="true"></div>
        </div>
        <div class="search-backdrop" id="searchBackdrop"></div>
    `;
    // Prefetch search index in background
    const prefetchLink = document.createElement('link');
    prefetchLink.rel = 'prefetch';
    prefetchLink.href = root + 'js/search-index.json?v=16';
    document.head.append(prefetchLink);

    document.body.prepend(nav);
    nav.after(searchOverlay);

    // Mobile nav
    const mobile = document.createElement('div');
    mobile.className = 'mobile-nav';
    mobile.id = 'mobileNav';
    mobile.setAttribute('aria-hidden', 'true');
    mobile.innerHTML = `
        <ul>
            <li><a href="${root}resources/index.html">Resources</a></li>
            <li><a href="${root}resources/where-to-start.html">Where to Start</a></li>
            <li><a href="${root}blog/index.html">Blog</a></li>
            <li><a href="${root}videos/index.html">Videos</a></li>
            <li><a href="${root}resources/ask.html">Ask a Question</a></li>
            <li><a href="${root}index.html#about">About</a></li>
        </ul>
    `;
    searchOverlay.after(mobile);

    // Hamburger toggle
    const hamburger = document.getElementById('hamburger');
    hamburger.addEventListener('click', () => {
        const isOpen = mobile.classList.toggle('active');
        hamburger.setAttribute('aria-expanded', isOpen);
        mobile.setAttribute('aria-hidden', !isOpen);
    });
    // Close mobile nav on link click
    mobile.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => {
            mobile.classList.remove('active');
            hamburger.setAttribute('aria-expanded', 'false');
            mobile.setAttribute('aria-hidden', 'true');
        });
    });

    // Search toggle
    const searchToggle = document.getElementById('searchToggle');
    const searchInput = document.getElementById('searchInput');
    const searchClose = document.getElementById('searchClose');
    const searchBackdrop = document.getElementById('searchBackdrop');

    searchToggle.addEventListener('click', () => {
        if (searchOpen) closeSearch();
        else openSearch();
    });
    searchClose.addEventListener('click', closeSearch);
    searchBackdrop.addEventListener('click', closeSearch);

    // Theme toggle
    document.getElementById('themeToggle').addEventListener('click', toggleTheme);
    document.addEventListener('keydown', trapFocusInSearch);

    let searchDebounce = null;
    searchInput.addEventListener('input', () => {
        clearTimeout(searchDebounce);
        searchDebounce = setTimeout(async () => {
            await loadSearchIndex();
            const query = searchInput.value;
            if (query.trim().length < 2) {
                document.getElementById('searchResults').innerHTML = '';
                searchInput.setAttribute('aria-expanded', 'false');
                document.getElementById('searchLive').textContent = '';
                return;
            }
            const results = performSearch(query);
            renderSearchResults(results);
            searchInput.setAttribute('aria-expanded', results.length > 0 ? 'true' : 'false');
        }, 200);
    });

    // Keyboard shortcut: Ctrl+K or Cmd+K to open search
    document.addEventListener('keydown', (e) => {
        if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
            e.preventDefault();
            if (searchOpen) closeSearch();
            else openSearch();
        }
    });
}

// ── Render Footer ──
function renderFooter() {
    const footer = document.createElement('footer');
    footer.className = 'footer';
    footer.innerHTML = `
        <div class="container">
            <div class="footer-grid">
                <div class="footer-brand">
                    <picture>
                        <source srcset="${root}images/logo-icon-md.webp" type="image/webp">
                        <img src="${root}images/logo-icon-md.png" alt="Waythrough Project" class="footer-logo" width="200" height="108" loading="lazy">
                    </picture>
                    <h3>Waythrough Project</h3>
                    <p>A free resource hub for navigating affordable housing and the barriers that stand in the way. Built on real experience working inside the system.</p>
                    <div class="footer-social" aria-label="Social media (coming soon)">
                        <span class="social-link" aria-hidden="true">${ICONS.youtube}</span>
                        <span class="social-link" aria-hidden="true">${ICONS.instagram}</span>
                        <span class="social-link" aria-hidden="true">${ICONS.tiktok}</span>
                        <span class="social-link" aria-hidden="true">${ICONS.facebook}</span>
                        <span class="social-link" aria-hidden="true">${ICONS.x}</span>
                        <span class="sr-only">Social media accounts coming soon</span>
                    </div>
                </div>
                <div class="footer-col">
                    <h4>Topics</h4>
                    <ul>
                        <li><a href="${root}resources/index.html">Housing Programs</a></li>
                        <li><a href="${root}resources/benefits.html">Benefits & Support</a></li>
                        <li><a href="${root}for-landlords/index.html">For Landlords</a></li>
                        <li><a href="${root}stories/index.html">Success Stories</a></li>
                        <li><a href="${root}resources/for-professionals.html">For Professionals</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Guides & Tools</h4>
                    <ul>
                        <li><a href="${root}resources/guides/how-to-apply-section-8.html">Apply for Section 8</a></li>
                        <li><a href="${root}resources/guides/document-checklist.html">Document Checklist</a></li>
                        <li><a href="${root}resources/tools/eligibility-screener.html">Eligibility Screener</a></li>
                        <li><a href="${root}resources/states/index.html">State Resources</a></li>
                        <li><a href="${root}resources/templates/index.html">Letter Templates</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Connect</h4>
                    <ul>
                        <li><a href="${root}resources/ask.html">Ask a Question</a></li>
                        <li><a href="${root}resources/community-answers.html">Community Q&A</a></li>
                        <li><a href="${root}es/index.html">Español</a></li>
                        <li><span class="footer-link-placeholder">YouTube — coming soon</span></li>
                        <li><span class="footer-link-placeholder">Instagram — coming soon</span></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; ${new Date().getFullYear()} Waythrough Project. All rights reserved.</p>
                <p>
                    <a href="${root}resources/accessibility.html" style="margin-right:16px;">Accessibility</a>
                    <a href="${root}privacy.html" style="margin-right:16px;">Privacy Policy</a>
                    <a href="${root}terms.html">Terms of Use</a>
                </p>
            </div>
        </div>
    `;
    document.body.append(footer);
}

// ── Ask a Question CTA ──
function renderAskCTA() {
    // Don't show on the ask page, homepage, or top-level index pages
    const path = window.location.pathname;
    if (path.includes('/ask')) return;
    if (path === '/' || path === '/index.html') return;
    // Skip resource index and blog index (but not their subpages)
    if (path === '/resources/' || path === '/resources/index.html') return;
    if (path === '/blog/' || path === '/blog/index.html') return;
    if (path === '/videos/' || path === '/videos/index.html') return;

    const main = document.querySelector('main');
    if (!main) return;

    const cta = document.createElement('div');
    cta.className = 'ask-cta';
    cta.innerHTML = `
        <div class="ask-cta-inner">
            <div class="ask-cta-text">
                <strong>Still have questions?</strong>
                <p>If something on this page didn't make sense or you're not sure how it applies to your situation, ask us. We read every question.</p>
            </div>
            <a href="${root}resources/ask.html" class="ask-cta-link">Ask a Question ${ICONS.arrow}</a>
        </div>
    `;
    main.append(cta);
}

// ── Back to Top Button ──
function renderBackToTop() {
    const btn = document.createElement('button');
    btn.className = 'back-to-top';
    btn.id = 'backToTop';
    btn.setAttribute('aria-label', 'Back to top');
    btn.innerHTML = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round"><polyline points="18 15 12 9 6 15"/></svg>';
    document.body.append(btn);

    window.addEventListener('scroll', () => {
        btn.classList.toggle('visible', window.scrollY > 400);
    }, { passive: true });
    btn.addEventListener('click', () => {
        window.scrollTo({ top: 0, behavior: 'smooth' });
    });
}

// ── Auto Reading Time ──
// Adds estimated reading time to any page with .post-content
function addReadingTime() {
    const content = document.querySelector('.post-content');
    const meta = document.querySelector('.page-meta');
    if (!content || !meta) return;
    // Don't add if already present
    if (meta.textContent.includes('min read')) return;
    const text = content.innerText || content.textContent;
    const words = text.trim().split(/\s+/).length;
    const minutes = Math.max(1, Math.round(words / 225));
    meta.textContent = meta.textContent.replace(/\s*$/, '') + ' · ' + minutes + ' min read';
}

// ── Auto Table of Contents for Guides ──
// Generates a TOC from h2 headings inside .post-content on guide pages
function addTableOfContents() {
    const content = document.querySelector('.post-content');
    if (!content) return;
    // Only on guide pages (breadcrumbs with "Resources")
    const isGuide = document.querySelector('.breadcrumbs');
    if (!isGuide) return;

    const headings = content.querySelectorAll('h2');
    if (headings.length < 3) return; // only show TOC for longer guides

    // Assign IDs to headings
    headings.forEach((h, i) => {
        if (!h.id) {
            h.id = 'section-' + (i + 1);
        }
    });

    const toc = document.createElement('aside');
    toc.className = 'toc';
    toc.setAttribute('aria-label', 'Table of contents');
    let tocHTML = '<div class="toc-title">In This Guide</div><ol class="toc-list">';
    headings.forEach(h => {
        // Skip "Related Resources" heading
        if (h.textContent.trim() === 'Related Resources') return;
        tocHTML += '<li><a href="#' + h.id + '">' + escapeHTML(h.textContent.trim()) + '</a></li>';
    });
    tocHTML += '</ol>';
    toc.innerHTML = tocHTML;

    // Insert before the first paragraph
    const firstP = content.querySelector('p');
    if (firstP) {
        firstP.after(toc);
    } else {
        content.prepend(toc);
    }
}


// ── Initialize shared behaviors ──
function initShared() {
    // Prefetch search index in background
    loadSearchIndex();

    // Navbar scroll shadow
    const nav = document.getElementById('nav');
    if (nav) {
        window.addEventListener('scroll', () => {
            nav.classList.toggle('scrolled', window.scrollY > 20);
        }, { passive: true });
    }

    // Scroll-reveal animations
    const fadeEls = document.querySelectorAll('.fade-in');
    if ('IntersectionObserver' in window) {
        const observer = new IntersectionObserver((entries) => {
            entries.forEach(entry => {
                if (entry.isIntersecting) entry.target.classList.add('visible');
            });
        }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
        fadeEls.forEach(el => observer.observe(el));
        // Fallback: if observer hasn't fired after 800ms, force visibility
        setTimeout(() => {
            fadeEls.forEach(el => {
                if (!el.classList.contains('visible')) el.classList.add('visible');
            });
        }, 800);
    } else {
        // No IntersectionObserver support — show everything immediately
        fadeEls.forEach(el => el.classList.add('visible'));
    }

    // Functionality features
    renderBackToTop();
    addReadingTime();
    addTableOfContents();

    // Fix anchor scroll for fixed nav
    function scrollToHash(hash) {
        var target = document.querySelector(hash);
        if (target) {
            var navHeight = 64;
            var y = target.getBoundingClientRect().top + window.pageYOffset - navHeight - 16;
            window.scrollTo({ top: y, behavior: 'smooth' });
        }
    }

    // On page load with a hash
    if (window.location.hash) {
        setTimeout(function () { scrollToHash(window.location.hash); }, 100);
    }

    // On same-page anchor clicks (e.g. clicking About while on homepage)
    document.addEventListener('click', function (e) {
        var link = e.target.closest('a[href*="#"]');
        if (!link) return;
        var href = link.getAttribute('href');
        var hashIndex = href.indexOf('#');
        if (hashIndex === -1) return;
        var hash = href.slice(hashIndex);
        var pagePath = href.slice(0, hashIndex);
        // Only handle if same page (empty path, or path matches current page)
        var isSamePage = !pagePath
            || pagePath === window.location.pathname
            || pagePath === window.location.pathname.replace(/\/$/, '') + '/index.html'
            || pagePath.replace(/^\.\//, '') === 'index.html' && window.location.pathname === '/';
        if (isSamePage && document.querySelector(hash)) {
            e.preventDefault();
            history.pushState(null, '', hash);
            scrollToHash(hash);
        }
    });
}

// ── Boot ──
document.addEventListener('DOMContentLoaded', () => {
    renderSkipLink();
    renderNav();
    renderAskCTA();
    renderFooter();

    // Add skip-link target: find <main> or first content section
    const main = document.querySelector('main') || document.querySelector('.welcome') || document.querySelector('.page-header');
    if (main && !main.id) {
        main.id = 'main-content';
    } else if (!document.getElementById('main-content') && main) {
        // main already has an id, add an anchor before it
        const anchor = document.createElement('div');
        anchor.id = 'main-content';
        main.prepend(anchor);
    }

    initShared();