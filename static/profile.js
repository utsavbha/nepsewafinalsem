// ===== Dark mode — matches your site =====
const darkToggle = document.getElementById('darkToggle');

if (localStorage.getItem('theme') === 'light') {
    document.body.classList.add('light');
    darkToggle.checked = true;
}

darkToggle.addEventListener('change', () => {
    document.body.classList.toggle('light', darkToggle.checked);
    localStorage.setItem('theme', darkToggle.checked ? 'light' : 'dark');
});

// ===== Load profile from /api/me =====
async function loadProfile() {
    try {
        const res = await fetch('/api/me');

        if (res.status === 401) {
            window.location.href = '/login';
            return;
        }

        const data = await res.json();

        if (!data.success) {
            window.location.href = '/login';
            return;
        }

        const u = data.user;

        document.getElementById('avatar').innerText    = u.initials;
        document.getElementById('uName').innerText     = u.name;
        document.getElementById('uEmail').innerText    = u.email;
        document.getElementById('sBookings').innerText = u.total_bookings;
        document.getElementById('sSince').innerText    = formatDate(u.member_since);
        document.getElementById('dName').innerText     = u.name;
        document.getElementById('dEmail').innerText    = u.email;
        document.getElementById('dSince').innerText    = formatDate(u.member_since);
        document.getElementById('dId').innerText       = '#' + String(u.id).padStart(5, '0');
        document.getElementById('dBookings').innerText = u.total_bookings;

    } catch (e) {
        console.error('Failed to load profile:', e);
    }
}

function formatDate(iso) {
    if (!iso) return '—';
    const d = new Date(iso);
    return d.toLocaleDateString('en-US', {
        year: 'numeric',
        month: 'long',
        day: 'numeric'
    });
}

loadProfile();