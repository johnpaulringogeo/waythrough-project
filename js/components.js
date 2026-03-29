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
    youtube: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M23.498 6.186a3.016 3.016 0 0 0-2.122-2.136C19.505 3.545 12 3.545 12 3.545s-7.505 0-9.377.505A3.017 3.017 0 0 0 .502 6.186C0 8.07 0 12 0 12s0 3.93.502 5.814a3.016 3.016 0 0 0 2.122 2.136c1.871.505 9.376.505 9.376.505s7.505 0 9.377-.505a3.015 3.015 0 0 0 2.122-2.136C24 15.93 24 12 24 12s0-3.93-.502-5.814z"/><polygon points="9.545 15.568 15.818 12 9.545 8.432" fill="#0f172a"/></svg>',
    instagram: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12 2.163c3.204 0 3.584.012 4.85.07 3.252.148 4.771 1.691 4.919 4.919.058 1.265.069 1.645.069 4.849 0 3.205-.012 3.584-.069 4.849-.149 3.225-1.664 4.771-4.919 4.919-1.266.058-1.644.07-4.85.07-3.204 0-3.584-.012-4.849-.07-3.26-.149-4.771-1.699-4.919-4.92-.058-1.265-.07-1.644-.07-4.849 0-3.204.013-3.583.07-4.849.149-3.227 1.664-4.771 4.919-4.919 1.266-.057 1.645-.069 4.849-.069zM12 0C8.741 0 8.333.014 7.053.072 2.695.272.273 2.69.073 7.052.014 8.333 0 8.741 0 12c0 3.259.014 3.668.072 4.948.2 4.358 2.618 6.78 6.98 6.98C8.333 23.986 8.741 24 12 24c3.259 0 3.668-.014 4.948-.072 4.354-.2 6.782-2.618 6.979-6.98.059-1.28.073-1.689.073-4.948 0-3.259-.014-3.667-.072-4.947-.196-4.354-2.617-6.78-6.979-6.98C15.668.014 15.259 0 12 0zm0 5.838a6.162 6.162 0 1 0 0 12.324 6.162 6.162 0 0 0 0-12.324zM12 16a4 4 0 1 1 0-8 4 4 0 0 1 0 8zm6.406-11.845a1.44 1.44 0 1 0 0 2.881 1.44 1.44 0 0 0 0-2.881z"/></svg>',
    tiktok: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M12.525.02c1.31-.02 2.61-.01 3.91-.02.08 1.53.63 3.09 1.75 4.17 1.12 1.11 2.7 1.62 4.24 1.79v4.03c-1.44-.05-2.89-.35-4.2-.97-.57-.26-1.1-.59-1.62-.93-.01 2.92.01 5.84-.02 8.75-.08 1.4-.54 2.79-1.35 3.94-1.31 1.92-3.58 3.17-5.91 3.21-1.43.08-2.86-.31-4.08-1.03-2.02-1.19-3.44-3.37-3.65-5.71-.02-.5-.03-1-.01-1.49.18-1.9 1.12-3.72 2.58-4.96 1.66-1.44 3.98-2.13 6.15-1.72.02 1.48-.04 2.96-.04 4.44-.99-.32-2.15-.23-3.02.37-.63.41-1.11 1.04-1.36 1.75-.21.51-.15 1.07-.14 1.61.24 1.64 1.82 3.02 3.5 2.87 1.12-.01 2.19-.66 2.77-1.61.19-.33.4-.67.41-1.06.1-1.79.06-3.57.07-5.36.01-4.03-.01-8.05.02-12.07z"/></svg>',
    facebook: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M24 12.073c0-6.627-5.373-12-12-12s-12 5.373-12 12c0 5.99 4.388 10.954 10.125 11.854v-8.385H7.078v-3.47h3.047V9.43c0-3.007 1.792-4.669 4.533-4.669 1.312 0 2.686.235 2.686.235v2.953H15.83c-1.491 0-1.956.925-1.956 1.874v2.25h3.328l-.532 3.47h-2.796v8.385C19.612 23.027 24 18.062 24 12.073z"/></svg>',
    x: '<svg viewBox="0 0 24 24" fill="currentColor"><path d="M18.244 2.25h3.308l-7.227 8.26 8.502 11.24H16.17l-5.214-6.817L4.99 21.75H1.68l7.73-8.835L1.254 2.25H8.08l4.713 6.231zm-1.161 17.52h1.833L7.084 4.126H5.117z"/></svg>',
};

// ── Render Navigation ──
function renderNav() {
    const nav = document.createElement('nav');
    nav.className = 'nav';
    nav.id = 'nav';
    nav.innerHTML = `
        <div class="container nav-inner">
            <a href="${root}index.html" class="nav-logo">
                <div class="nav-logo-icon">${ICONS.home}</div>
                Waythrough Project
            </a>
            <ul class="nav-links">
                <li><a href="${root}resources/index.html">Resources</a></li>
                <li><a href="${root}blog/index.html">Blog</a></li>
                <li><a href="${root}videos/index.html">Videos</a></li>
                <li><a href="${root}index.html#about">About</a></li>
            </ul>
            <button class="hamburger" id="hamburger" aria-label="Toggle menu">
                <span></span><span></span><span></span>
            </button>
        </div>
    `;
    document.body.prepend(nav);

    // Mobile nav
    const mobile = document.createElement('div');
    mobile.className = 'mobile-nav';
    mobile.id = 'mobileNav';
    mobile.innerHTML = `
        <ul>
            <li><a href="${root}resources/index.html">Resources</a></li>
            <li><a href="${root}blog/index.html">Blog</a></li>
            <li><a href="${root}videos/index.html">Videos</a></li>
            <li><a href="${root}index.html#about">About</a></li>
        </ul>
    `;
    nav.after(mobile);

    // Hamburger toggle
    document.getElementById('hamburger').addEventListener('click', () => {
        mobile.classList.toggle('active');
    });
    // Close mobile nav on link click
    mobile.querySelectorAll('a').forEach(a => {
        a.addEventListener('click', () => mobile.classList.remove('active'));
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
                    <h3>Waythrough Project</h3>
                    <p>A free resource hub for navigating affordable housing and the barriers that stand in the way. Built on real experience working inside the system.</p>
                    <div class="footer-social">
                        <a href="#" aria-label="YouTube">${ICONS.youtube}</a>
                        <a href="#" aria-label="Instagram">${ICONS.instagram}</a>
                        <a href="#" aria-label="TikTok">${ICONS.tiktok}</a>
                        <a href="#" aria-label="Facebook">${ICONS.facebook}</a>
                        <a href="#" aria-label="X">${ICONS.x}</a>
                    </div>
                </div>
                <div class="footer-col">
                    <h4>Topics</h4>
                    <ul>
                        <li><a href="${root}resources/index.html">Housing Programs</a></li>
                        <li><a href="${root}resources/benefits.html">Benefits & Support</a></li>
                        <li><a href="${root}resources/employment.html">Employment</a></li>
                        <li><a href="${root}resources/mental-health.html">Mental Health</a></li>
                        <li><a href="${root}resources/substance-use.html">Substance Use</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Guides</h4>
                    <ul>
                        <li><a href="${root}resources/guides/how-to-apply-section-8.html">Apply for Section 8</a></li>
                        <li><a href="${root}resources/guides/how-to-apply-hud-vash.html">Apply for HUD-VASH</a></li>
                        <li><a href="${root}resources/guides/document-checklist.html">Document Checklist</a></li>
                        <li><a href="${root}resources/guides/how-to-request-reasonable-accommodation.html">Reasonable Accommodation</a></li>
                    </ul>
                </div>
                <div class="footer-col">
                    <h4>Connect</h4>
                    <ul>
                        <li><a href="${root}resources/ask.html">Ask a Question</a></li>
                        <li><a href="#">YouTube</a></li>
                        <li><a href="#">Instagram</a></li>
                        <li><a href="#">TikTok</a></li>
                        <li><a href="#">Facebook</a></li>
                    </ul>
                </div>
            </div>
            <div class="footer-bottom">
                <p>&copy; ${new Date().getFullYear()} Waythrough Project. All rights reserved.</p>
                <p>
                    <a href="#" style="margin-right:16px;">Privacy Policy</a>
                    <a href="#">Terms of Use</a>
                </p>
            </div>
        </div>
    `;
    document.body.append(footer);
}

// ── Render Newsletter CTA (optional, include on any page) ──
function renderNewsletter(targetSelector) {
    const target = targetSelector
        ? document.querySelector(targetSelector)
        : null;

    const section = document.createElement('section');
    section.className = 'cta-section';
    section.id = 'newsletter';
    section.innerHTML = `
        <div class="container">
            <div class="cta-inner fade-in">
                <h2>Stay Connected. Stay Informed.</h2>
                <p>Get weekly tips, new resource alerts, and affordable housing news delivered straight to your inbox. No spam, no sales &mdash; just help.</p>
                <form class="cta-form" onsubmit="event.preventDefault(); this.querySelector('button').textContent='Subscribed!'; this.querySelector('input').value='';">
                    <input type="email" placeholder="Enter your email address" required>
                    <button type="submit">Subscribe</button>
                </form>
            </div>
        </div>
    `;
    if (target) {
        target.after(section);
    } else {
        // Insert before footer
        const footer = document.querySelector('.footer');
        if (footer) footer.before(section);
        else document.body.append(section);
    }
}

// ── Initialize shared behaviors ──
function initShared() {
    // Navbar scroll shadow
    const nav = document.getElementById('nav');
    if (nav) {
        window.addEventListener('scroll', () => {
            nav.classList.toggle('scrolled', window.scrollY > 20);
        });
    }

    // Scroll-reveal animations
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) entry.target.classList.add('visible');
        });
    }, { threshold: 0.1, rootMargin: '0px 0px -40px 0px' });
    document.querySelectorAll('.fade-in').forEach(el => observer.observe(el));
}

// ── Boot ──
document.addEventListener('DOMContentLoaded', () => {
    renderNav();
    renderFooter();

    // Auto-add newsletter if page has the data attribute
    if (document.body.dataset.newsletter !== 'false') {
        renderNewsletter();
    }
    initShared();
});
