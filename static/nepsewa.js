// ===== DARK MODE TOGGLE =====
const toggle = document.getElementById("darkToggle");

if (localStorage.getItem("theme") === "light") {
    document.body.classList.add("light");
    toggle.checked = true;
}

toggle.addEventListener("change", () => {
    document.body.classList.toggle("light");
    localStorage.setItem("theme", document.body.classList.contains("light") ? "light" : "dark");
});

// ===== AUTH MODAL LOGIC (kept from original) =====
const authModal      = document.getElementById('authModal');
const loginButtons   = document.querySelectorAll('.btn-login');
const closeModal     = document.querySelector('.modal .close');
const toggleFormBtn  = document.getElementById('toggleForm');
const formTitle      = document.getElementById('formTitle');
const authForm       = document.getElementById('authForm');
const toggleText     = document.getElementById('toggleText');

if (loginButtons.length) {
    loginButtons.forEach(btn => {
        btn.addEventListener('click', () => { authModal.style.display = 'block'; });
    });
}
if (closeModal) {
    closeModal.addEventListener('click', () => { authModal.style.display = 'none'; });
}
window.addEventListener('click', (e) => {
    if (authModal && e.target === authModal) authModal.style.display = 'none';
    

});
if (toggleFormBtn) {
    toggleFormBtn.addEventListener('click', () => {
        if (formTitle.innerText.includes('Login')) {
            formTitle.innerText = "Sign Up for NepSewa";
            authForm.innerHTML = `
                <input type="text"     placeholder="Full Name"         required>
                <input type="email"    placeholder="Email"             required>
                <input type="password" placeholder="Password"          required>
                <input type="password" placeholder="Confirm Password"  required>
                <button type="submit" class="btn">Sign Up</button>
            `;
            toggleText.innerHTML = 'Already have an account? <span id="toggleForm" style="cursor:pointer;color:var(--primary);">Login</span>';
        } else {
            formTitle.innerText = "Login to NepSewa";
            authForm.innerHTML = `
                <input type="email"    placeholder="Email"    required>
                <input type="password" placeholder="Password" required>
                <button type="submit" class="btn">Login</button>
            `;
            toggleText.innerHTML = 'Don\'t have an account? <span id="toggleForm" style="cursor:pointer;color:var(--primary);">Sign Up</span>';
        }
        document.getElementById('toggleForm').addEventListener('click', toggleFormBtn.click);
    });
}

// ===== HOME PAGE — TOP PROVIDERS via API =====
async function loadTopProfessionals() {
    const homeGrid = document.getElementById("homeProviderGrid");
    if (!homeGrid) return;

    try {
        const response = await fetch('/api/top-professionals');
        const data = await response.json();
        
        if (data.success && data.professionals.length > 0) {
            homeGrid.innerHTML = ''; // Clear existing content
            
            data.professionals.forEach(p => {
                // Calculate score for display (same algorithm as services page)
                const score = (parseFloat(p.rating) * 2) + p.experience + (p.completed_jobs * 0.005) - (parseFloat(p.cancellation_rate) * 10);
                const maxScore = 15; // rough max for bar normalisation
                const barPct = Math.min(100, Math.round((score / maxScore) * 100));
                const cancelPct = Math.round((p.cancellation_rate || 0) * 100);

                const card = document.createElement('div');
                card.className = 'pro-card';
                card.innerHTML = `
                    <img src="${p.image || 'https://via.placeholder.com/150'}" alt="${p.name}">
                    ${p.is_verified ? `
                    <div class="verified-badge">
                        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="12" height="12">
                            <polyline points="20 6 9 17 4 12"/>
                        </svg>
                        Verified
                    </div>` : ''}
                    <h3>${p.name}</h3>
                    <p class="service-type">${p.service} • ${p.location}</p>
                    <div class="pro-stats">
                        <div class="stat-item">
                            <span class="stat-num">⭐ ${p.rating}</span>
                            <span class="stat-lbl">Rating</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-num">${p.experience} yrs</span>
                            <span class="stat-lbl">Experience</span>
                        </div>
                        <div class="stat-item">
                            <span class="stat-num">${p.completed_jobs}</span>
                            <span class="stat-lbl">Jobs Done</span>
                        </div>
                    </div>
                    <div class="score-bar-wrap">
                        <div class="score-bar-bg">
                            <div class="score-bar-fill" style="width:${barPct}%"></div>
                        </div>
                        <span class="score-label">Excellence Score ${barPct}%</span>
                    </div>
                    <p class="response-time">⚡ Responds in ~${p.response_time_hours}h • ${p.review_count} reviews</p>
                    <button class="book-btn" onclick="window.location.href='/services'">Book Now</button>
                `;
                homeGrid.appendChild(card);
            });
        } else {
            // Fallback message if no professionals found
            homeGrid.innerHTML = `
                <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
                    <p style="color: #64748b;">Top professionals will appear here once you add more providers.</p>
                    <a href="/admin/add-providers" style="color: #6366f1;">Add More Providers</a>
                </div>
            `;
        }
    } catch (error) {
        console.error('Error loading top professionals:', error);
        homeGrid.innerHTML = `
            <div style="grid-column: 1/-1; text-align: center; padding: 40px;">
                <p style="color: #ef4444;">Unable to load top professionals.</p>
            </div>
        `;
    }
}

// Load top professionals when page loads
document.addEventListener('DOMContentLoaded', function() {
    loadTopProfessionals();
});

// ===== HOME PAGE — TOP PROVIDERS via API =====
document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('providerRegistrationForm');
    if (form) {
        form.addEventListener('submit', handleProviderRegistration);
    }
});

function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorEl = document.getElementById(`error-${fieldId}`);
    if (field && errorEl) {
        field.style.borderColor = '#ef4444';
        errorEl.textContent = message;
        errorEl.classList.add('show');
    }
}

function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorEl = document.getElementById(`error-${fieldId}`);
    if (field && errorEl) {
        field.style.borderColor = 'rgba(255,255,255,0.2)';
        errorEl.textContent = '';
        errorEl.classList.remove('show');
    }
}

function clearAllErrors() {
    ['provider-name', 'provider-phone', 'provider-service', 'provider-location', 'provider-experience'].forEach(clearError);
}

async function handleProviderRegistration(e) {
    e.preventDefault();
    
    clearAllErrors();
    
    // Get form data
    const name = document.getElementById('provider-name').value.trim();
    const phone = document.getElementById('provider-phone').value.trim();
    const service = document.getElementById('provider-service').value;
    const location = document.getElementById('provider-location').value;
    const experience = document.getElementById('provider-experience').value;
    
    // Get availability
    const availabilityCheckboxes = document.querySelectorAll('.availability-checkboxes input[type="checkbox"]:checked');
    const availability = Array.from(availabilityCheckboxes).map(cb => cb.value);
    
    // Validation
    let isValid = true;
    
    if (!name) {
        showError('provider-name', 'Full name is required');
        isValid = false;
    }
    
    if (!phone) {
        showError('provider-phone', 'Phone number is required');
        isValid = false;
    } else if (!/^98\d{8}$/.test(phone)) {
        showError('provider-phone', 'Phone must be 10 digits starting with 98');
        isValid = false;
    }
    
    if (!service) {
        showError('provider-service', 'Please select a service');
        isValid = false;
    }
    
    if (!location) {
        showError('provider-location', 'Please select a location');
        isValid = false;
    }
    
    if (!experience) {
        showError('provider-experience', 'Please select experience level');
        isValid = false;
    }
    
    if (availability.length === 0) {
        alert('Please select at least one available day');
        isValid = false;
    }
    
    if (!isValid) return;
    
    // Submit form
    const submitBtn = document.querySelector('.register-btn');
    const resultDiv = document.getElementById('registration-result');
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Registering...';
    resultDiv.innerHTML = '';
    
    try {
        const response = await fetch('/api/register-provider', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name,
                phone,
                service,
                location,
                experience,
                availability
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            resultDiv.className = 'success';
            resultDiv.innerHTML = `
                ✅ ${data.message}<br>
                <small>You can now be found in the <a href="/services" style="color: #22c55e;">services section</a></small>
            `;
            
            // Reset form
            document.getElementById('providerRegistrationForm').reset();
            
            // Check Monday-Saturday by default
            document.querySelectorAll('.availability-checkboxes input[type="checkbox"]').forEach((cb, index) => {
                cb.checked = index < 6; // First 6 are Mon-Sat
            });
            
        } else {
            resultDiv.className = 'error';
            resultDiv.innerHTML = `❌ ${data.message}`;
        }
        
    } catch (error) {
        resultDiv.className = 'error';
        resultDiv.innerHTML = `❌ Network error. Please try again.`;
    }
    
    submitBtn.disabled = false;
    submitBtn.textContent = 'Register as Provider';
}
