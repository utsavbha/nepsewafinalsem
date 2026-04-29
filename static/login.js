// ============================================================
//  NepSewa — login.js
// ============================================================

// ── Dark mode ──
// ── Dark mode — matches your other pages ──
const darkToggle = document.getElementById('darkToggle');

if (localStorage.getItem('theme') === 'light') {
  document.body.classList.add('light');
  darkToggle.checked = true;
}

darkToggle.addEventListener('change', () => {
  document.body.classList.toggle('light', darkToggle.checked);
  localStorage.setItem('theme', darkToggle.checked ? 'light' : 'dark');
});

// ── Tab switcher ──
let currentTab = 'login';

function switchTab(tab) {
  currentTab = tab;

  document.querySelectorAll('.tab').forEach((t, i) => {
    t.classList.toggle('active',
      (i === 0 && tab === 'login') || (i === 1 && tab === 'signup')
    );
  });

  document.getElementById('loginForm').classList.toggle('active', tab === 'login');
  document.getElementById('signupForm').classList.toggle('active', tab === 'signup');
  hideMsg();
}

// ── Messages ──
function showMsg(text, type = 'error') {
  const el = document.getElementById('msg');
  el.textContent   = (type === 'error' ? '⚠️  ' : '✅  ') + text;
  el.className     = 'msg ' + (type === 'error' ? 'error' : 'ok');
  el.style.display = 'block';
}

function hideMsg() {
  document.getElementById('msg').style.display = 'none';
}

// ── Password strength ──
function checkStrength(val) {
  const fill = document.getElementById('strengthFill');
  let score = 0;
  if (val.length >= 6)           score++;
  if (val.length >= 10)          score++;
  if (/[A-Z]/.test(val))         score++;
  if (/[0-9]/.test(val))         score++;
  if (/[^A-Za-z0-9]/.test(val)) score++;

  const colors = ['#ef4444','#f97316','#eab308','#84cc16','#22c55e'];
  fill.style.width      = (score / 5 * 100) + '%';
  fill.style.background = colors[Math.max(0, score - 1)];
}

// ── LOGIN ──
async function doLogin() {
  const email    = document.getElementById('l-email').value.trim();
  const password = document.getElementById('l-pass').value.trim();

  if (!email || !password) { showMsg('Please fill in all fields'); return; }

  const btn = document.getElementById('loginBtn');
  btn.disabled    = true;
  btn.textContent = 'Logging in…';
  hideMsg();

  // Get redirect URL from query parameters
  const urlParams = new URLSearchParams(window.location.search);
  const redirectUrl = urlParams.get('redirect') || '/profile';

  try {
    const res  = await fetch('/api/login', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ email, password, redirect_url: redirectUrl })
    });
    const data = await res.json();

    if (data.success) {
      showMsg('Login successful! Redirecting…', 'ok');
      setTimeout(() => window.location.href = data.redirect_url || redirectUrl, 1000);
    } else {
      showMsg(data.message || 'Invalid credentials');
    }
  } catch {
    showMsg('Server error. Please try again.');
  }

  btn.disabled    = false;
  btn.textContent = 'Login to NepSewa';
}

// ── SIGNUP ──
async function doSignup() {
  const name     = document.getElementById('s-name').value.trim();
  const email    = document.getElementById('s-email').value.trim();
  const password = document.getElementById('s-pass').value.trim();
  const confirm  = document.getElementById('s-confirm').value.trim();

  if (!name || !email || !password || !confirm) { showMsg('Please fill in all fields'); return; }
  if (password !== confirm)  { showMsg('Passwords do not match'); return; }
  if (password.length < 6)   { showMsg('Password must be at least 6 characters'); return; }

  const btn = document.getElementById('signupBtn');
  btn.disabled    = true;
  btn.textContent = 'Creating account…';
  hideMsg();

  try {
    const res  = await fetch('/api/signup', {
      method:  'POST',
      headers: { 'Content-Type': 'application/json' },
      body:    JSON.stringify({ name, email, password })
    });
    const data = await res.json();

    if (data.success) {
      showMsg('Account created! Please login.', 'ok');
      // Clear signup form and switch to login tab
      document.getElementById('s-name').value = '';
      document.getElementById('s-email').value = '';
      document.getElementById('s-pass').value = '';
      document.getElementById('s-confirm').value = '';
      // Pre-fill login email
      document.getElementById('l-email').value = email;
      setTimeout(() => switchTab('login'), 1500);
    } else {
      showMsg(data.message || 'Signup failed');
    }
  } catch {
    showMsg('Server error. Please try again.');
  }

  btn.disabled    = false;
  btn.textContent = 'Create Account';
}

// ── Enter key ──
document.addEventListener('keydown', (e) => {
  if (e.key !== 'Enter') return;
  currentTab === 'login' ? doLogin() : doSignup();
});