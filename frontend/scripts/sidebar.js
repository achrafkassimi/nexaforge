/**
 * NexaForge — Shared Sidebar + Session Management
 * Include this script in every page (except login.html).
 * It handles: auth check, sidebar injection, user display, logout.
 */
(function () {
    const API = 'http://localhost:8000';
    const token = localStorage.getItem('token');

    // ── Auth guard ──────────────────────────────────────────────────────────
    if (!token) {
        window.location.href = 'login.html';
        return;
    }

    function parseJwt(t) {
        try { return JSON.parse(atob(t.split('.')[1])); } catch { return {}; }
    }

    const me = parseJwt(token);
    const myRole = me.role || '';
    const initials = (myRole.slice(0, 2) || 'U').toUpperCase();

    // ── Detect active page ──────────────────────────────────────────────────
    const page = window.location.pathname.split('/').pop() || 'dashboard.html';

    function navLink(href, icon, label) {
        const active = page === href ? 'active' : '';
        return `<a href="${href}" class="nav-item ${active}">${icon} ${label}</a>`;
    }

    // ── Inject sidebar HTML ─────────────────────────────────────────────────
    const container = document.getElementById('app-sidebar');
    if (container) {
        container.innerHTML = `
        <div class="sidebar">
            <div class="sidebar-logo">
                <div class="logo-mark">N</div>
                <span class="logo-name">NexaForge</span>
            </div>
            <nav class="nav-section">
                ${navLink('dashboard.html',      '⬛', 'Dashboard')}
                ${navLink('projects.html',       '📁', 'Projects')}
                ${navLink('kanban.html',         '🗂️', 'Kanban')}
                ${navLink('sprint_burndown.html','📉', 'Burndown')}
                ${navLink('agents.html',         '🤖', 'Agents')}
                ${navLink('users.html',          '👤', 'Users')}
                ${navLink('logs.html',           '📋', 'Logs')}
                ${navLink('settings.html',       '⚙️', 'Settings')}
            </nav>
            <div class="sidebar-footer">
                <div class="user-card">
                    <div class="user-avatar">${initials}</div>
                    <div>
                        <div class="user-info-name" id="sidebar-username">Loading...</div>
                        <div class="user-info-role">${myRole.replace('_', ' ')}</div>
                    </div>
                </div>
                <button class="logout-btn" onclick="nexaLogout()">⏻ Logout</button>
            </div>
        </div>`;

        // Load real user name from API
        fetch(`${API}/api/users/`, {
            headers: { 'Authorization': `Bearer ${token}` }
        })
        .then(r => r.json())
        .then(users => {
            const user = users.find(u => u.role === myRole);
            const nameEl = document.getElementById('sidebar-username');
            if (nameEl && user) nameEl.textContent = user.full_name;
            else if (nameEl) nameEl.textContent = myRole;
        })
        .catch(() => {
            const nameEl = document.getElementById('sidebar-username');
            if (nameEl) nameEl.textContent = myRole;
        });
    }

    // ── Logout ──────────────────────────────────────────────────────────────
    window.nexaLogout = function () {
        localStorage.removeItem('token');
        window.location.href = 'login.html';
    };

    // ── Expose helpers to all pages ─────────────────────────────────────────
    window.NexaAuth = {
        token,
        role: myRole,
        headers: {
            'Content-Type': 'application/json',
            'Authorization': `Bearer ${token}`
        },
        bearerHeaders: {
            'Authorization': `Bearer ${token}`
        },
        parseJwt
    };

    // ── Global toast ────────────────────────────────────────────────────────
    window.showToast = function (msg, type = 'success') {
        let el = document.getElementById('global-toast');
        if (!el) {
            el = document.createElement('div');
            el.id = 'global-toast';
            el.className = 'toast';
            document.body.appendChild(el);
        }
        el.textContent = msg;
        el.className = `toast show ${type}`;
        clearTimeout(el._timer);
        el._timer = setTimeout(() => el.classList.remove('show'), 3500);
    };
})();
