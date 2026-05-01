// ===== AUTH MODAL LOGIC (kept from original) =====
const authModal      = document.getElementById('authModal');
const loginButtons   = document.querySelectorAll('.btn-login');
const closeModalBtn  = document.querySelector('.modal .close');
const toggleFormBtn  = document.getElementById('toggleForm');
const formTitle      = document.getElementById('formTitle');
const authForm       = document.getElementById('authForm');
const toggleText     = document.getElementById('toggleText');

if (loginButtons.length) {
    loginButtons.forEach(btn => {
        btn.addEventListener('click', () => { authModal.style.display = 'block'; });
    });
}
if (closeModalBtn) {
    closeModalBtn.addEventListener('click', () => { authModal.style.display = 'none'; });
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
            
            data.professionals.forEach((p) => {
                // Calculate score for display (same algorithm as services page)
                const score = (parseFloat(p.rating) * 2) + p.experience + (p.completed_jobs * 0.005) - (parseFloat(p.cancellation_rate) * 10);
                const maxScore = 15; // rough max for bar normalisation
                const barPct = Math.min(100, Math.round((score / maxScore) * 100));

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
                    <button class="book-btn" onclick="openBookingModalByService('${p.service}')">Book Now</button>
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
                <p style="color: #ef4444;">Unable to load top professionals. Please refresh the page.</p>
            </div>
        `;
    }
}

// Load top professionals when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 DOM Content Loaded - Initializing...');
    
    // Show loading indicator
    showPageLoading();
    
    // Dark mode toggle
    const toggle = document.getElementById("darkToggle");
    console.log('🌙 Dark mode toggle element:', toggle);
    
    if (toggle) {
        if (localStorage.getItem("theme") === "light") {
            document.body.classList.add("light");
            toggle.checked = true;
            console.log('☀️ Applied light theme from localStorage');
        }

        toggle.addEventListener("change", () => {
            document.body.classList.toggle("light");
            const theme = document.body.classList.contains("light") ? "light" : "dark";
            localStorage.setItem("theme", theme);
            console.log('🎨 Theme changed to:', theme);
        });
        console.log('✅ Dark mode toggle initialized');
    } else {
        console.error('❌ Dark mode toggle element not found');
    }
    
    // Initialize all components
    Promise.all([
        loadTopProfessionals(),
        checkLoginStatus(),
        initializeProviderForm()
    ]).then(() => {
        hidePageLoading();
        console.log('🎉 All components initialized successfully');
    }).catch(error => {
        console.error('❌ Error during initialization:', error);
        hidePageLoading();
    });
});

function showPageLoading() {
    const loader = document.createElement('div');
    loader.id = 'pageLoader';
    loader.className = 'page-loading';
    loader.innerHTML = '<div class="spinner"></div>';
    document.body.appendChild(loader);
}

function hidePageLoading() {
    const loader = document.getElementById('pageLoader');
    if (loader) {
        loader.remove();
    }
}

function initializeProviderForm() {
    return new Promise((resolve) => {
        const form = document.getElementById('providerRegistrationForm');
        if (form) {
            form.addEventListener('submit', handleProviderRegistration);
            console.log('✅ Provider registration form initialized');
        }
        resolve();
    });
}

async function checkLoginStatus() {
    try {
        console.log('📡 Fetching login status from /api/me...');
        const response = await fetch('/api/me');
        const result = await response.json();
        console.log('🔐 Login status response:', result);
        
        const loginLink = document.getElementById('loginNavLink');
        if (loginLink) {
            if (result.success && result.user) {
                // User is logged in - show profile link
                loginLink.textContent = result.user.name;
                loginLink.href = '/profile';
                loginLink.title = 'Go to Profile';
                console.log('✅ User logged in:', result.user.name);
            } else {
                // User not logged in - show login link with redirect
                loginLink.textContent = 'Login';
                const currentUrl = encodeURIComponent(window.location.pathname + window.location.search);
                loginLink.href = `/login?redirect=${currentUrl}`;
                loginLink.title = 'Login to your account';
                console.log('ℹ️ User not logged in');
            }
        } else {
            console.error('❌ Login nav link element not found');
        }
    } catch (error) {
        console.error('❌ Error checking login status:', error);
    }
}

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

// ===== BOOKING FUNCTIONALITY =====

// Service data for home page booking
const serviceData = {
    'cleaning': {
        title: 'Home Cleaning',
        price: 'Rs 500.00 / Hour',
        priceDesc: 'Professional home cleaning service',
        workerInfo: 'Experienced cleaners with eco-friendly products',
        image: '/static/cleaning.png'
    },
    'plumbing': {
        title: 'Plumbing',
        price: 'Rs 800.00 / Hour',
        priceDesc: 'Expert plumbing repairs and installations',
        workerInfo: 'Licensed plumbers with 5+ years experience',
        image: '/static/plumber.png'
    },
    'electrical': {
        title: 'Electric Repair',
        price: 'Rs 700.00 / Hour',
        priceDesc: 'Safe and reliable electrical services',
        workerInfo: 'Certified electricians for all electrical needs',
        image: '/static/technician.png'
    },
    'ac-service': {
        title: 'AC Service',
        price: 'Rs 1000.00 / Hour',
        priceDesc: 'AC repair, maintenance and installation',
        workerInfo: 'Specialized AC technicians with warranty',
        image: '/static/air-conditioner.png'
    },
    'toilet-cleaning': {
        title: 'Toilet Cleaning',
        price: 'Rs 300.00 / Hour',
        priceDesc: 'Deep toilet and bathroom cleaning',
        workerInfo: 'Hygienic cleaning with sanitization',
        image: '/static/toilet.png'
    },
    'spa-massage': {
        title: 'Spa & Massage',
        price: 'Rs 1200.00 / Hour',
        priceDesc: 'Relaxing spa and massage services',
        workerInfo: 'Professional therapists at your home',
        image: '/static/facial-massage.png'
    },
    'hair-cutting': {
        title: 'Hair Cutting',
        price: 'Rs 400.00 / Hour',
        priceDesc: 'Professional hair cutting and styling',
        workerInfo: 'Experienced stylists with modern techniques',
        image: '/static/hair-cutting.png'
    },
    'makeup-artist': {
        title: 'Makeup Artist',
        price: 'Rs 1500.00 / Hour',
        priceDesc: 'Professional makeup for events and occasions',
        workerInfo: 'Expert makeup artists with premium products',
        image: '/static/facial-massage.png'
    },
    'photographer': {
        title: 'Photographer',
        price: 'Rs 2000.00 / Hour',
        priceDesc: 'Professional photography services',
        workerInfo: 'Skilled photographers for events and portraits',
        image: 'https://images.unsplash.com/photo-1502920917128-1aa500764cbd?w=400&h=300&fit=crop'
    },
    'gardener': {
        title: 'Gardener',
        price: 'Rs 600.00 / Hour',
        priceDesc: 'Garden maintenance and landscaping',
        workerInfo: 'Expert gardeners for all your garden needs',
        image: 'https://images.unsplash.com/photo-1416879595882-3373a0480b5b?w=400&h=300&fit=crop'
    },
    'maid-service': {
        title: 'Maid Service',
        price: 'Rs 450.00 / Hour',
        priceDesc: 'Daily household maintenance service',
        workerInfo: 'Reliable maids for regular household work',
        image: '/static/cleaning.png'
    },
    'technician': {
        title: 'Technician Service',
        price: 'Rs 800.00 / Hour',
        priceDesc: 'Technical repairs and maintenance',
        workerInfo: 'Skilled technicians for appliance repairs',
        image: '/static/technician.png'
    }
};

// Service name mapping
const serviceNameMapping = {
    'Home Cleaning': 'cleaning',
    'Cleaning': 'cleaning',
    'Plumbing': 'plumbing',  // Fixed: was 'plumber', now 'plumbing'
    'Plumber': 'plumbing',
    'Plumber Service': 'plumbing',
    'Electric Repair': 'electrical',
    'Electrical': 'electrical',
    'Electrician': 'electrical',
    'AC Service': 'ac-service',
    'AC Repair': 'ac-service',
    'Air Conditioning': 'ac-service',
    'Toilet Cleaning': 'toilet-cleaning',
    'Bathroom Cleaning': 'toilet-cleaning',
    'Spa & Massage': 'spa-massage',
    'Massage': 'spa-massage',
    'Spa': 'spa-massage',
    'Hair Cutting': 'hair-cutting',
    'Hair Cut': 'hair-cutting',
    'Barber': 'hair-cutting',
    'Makeup Artist': 'makeup-artist',
    'Makeup': 'makeup-artist',
    'Photographer': 'photographer',
    'Photography': 'photographer',
    'Gardener': 'gardener',
    'Garden': 'gardener',
    'Maid Service': 'maid-service',
    'Maid': 'maid-service',
    'Technician Service': 'technician',
    'Technician': 'technician'
};

// Function to map service name to service key
function getServiceKey(serviceName) {
    console.log('🔍 Mapping service name:', serviceName);
    
    // Direct mapping
    if (serviceNameMapping[serviceName]) {
        const key = serviceNameMapping[serviceName];
        console.log('✅ Direct mapping found:', serviceName, '→', key);
        return key;
    }
    
    // Try case-insensitive direct mapping
    for (const [mappedName, mappedKey] of Object.entries(serviceNameMapping)) {
        if (mappedName.toLowerCase() === serviceName.toLowerCase()) {
            console.log('✅ Case-insensitive mapping found:', serviceName, '→', mappedKey);
            return mappedKey;
        }
    }
    
    // Fallback: convert to lowercase and replace spaces with hyphens
    const key = serviceName.toLowerCase().replace(/\s+/g, '-');
    console.log('🔄 Trying fallback key:', key);
    
    if (serviceData[key]) {
        console.log('✅ Fallback mapping found:', serviceName, '→', key);
        return key;
    }
    
    // Check if it's a partial match
    for (const [mappedName, mappedKey] of Object.entries(serviceNameMapping)) {
        if (serviceName.toLowerCase().includes(mappedName.toLowerCase()) || 
            mappedName.toLowerCase().includes(serviceName.toLowerCase())) {
            console.log('✅ Partial mapping found:', serviceName, '→', mappedKey);
            return mappedKey;
        }
    }
    
    // Check against service data titles
    for (const [key, data] of Object.entries(serviceData)) {
        if (data.title.toLowerCase() === serviceName.toLowerCase() ||
            data.title.toLowerCase().includes(serviceName.toLowerCase()) ||
            serviceName.toLowerCase().includes(data.title.toLowerCase())) {
            console.log('✅ Service data title match:', serviceName, '→', key);
            return key;
        }
    }
    
    console.log('⚠️ No mapping found, using default: cleaning');
    // Default fallback
    return 'cleaning';
}

// Function to open booking modal by service name
function openBookingModalByService(serviceName) {
    console.log('🎯 Opening booking modal for service:', serviceName);
    
    // First, let's see what service we're dealing with
    if (!serviceName) {
        console.error('❌ No service name provided');
        showAlert('Service information missing', 'error');
        return;
    }
    
    const serviceKey = getServiceKey(serviceName);
    console.log('🔑 Mapped to service key:', serviceKey);
    
    // Check if we have data for this service
    if (!serviceData[serviceKey]) {
        console.error('❌ No service data found for key:', serviceKey);
        console.log('Available service keys:', Object.keys(serviceData));
        
        // Try to find a close match
        const fallbackKey = findClosestServiceMatch(serviceName);
        if (fallbackKey) {
            console.log('🔄 Using fallback service:', fallbackKey);
            openBookingModal(fallbackKey);
        } else {
            showAlert(`Service "${serviceName}" is not available for booking yet`, 'warning');
        }
        return;
    }
    
    openBookingModal(serviceKey);
}

// Helper function to find closest service match
function findClosestServiceMatch(serviceName) {
    const lowerService = serviceName.toLowerCase();
    
    // Check for partial matches in service data
    for (const [key, data] of Object.entries(serviceData)) {
        if (lowerService.includes(key) || key.includes(lowerService) || 
            data.title.toLowerCase().includes(lowerService) ||
            lowerService.includes(data.title.toLowerCase())) {
            return key;
        }
    }
    
    // Default fallbacks based on common service types
    if (lowerService.includes('clean')) return 'cleaning';
    if (lowerService.includes('plumb')) return 'plumbing';
    if (lowerService.includes('electric')) return 'electrical';
    if (lowerService.includes('hair')) return 'hair-cutting';
    if (lowerService.includes('makeup')) return 'makeup-artist';
    if (lowerService.includes('photo')) return 'photographer';
    if (lowerService.includes('garden')) return 'gardener';
    if (lowerService.includes('maid')) return 'maid-service';
    if (lowerService.includes('ac') || lowerService.includes('air')) return 'ac-service';
    if (lowerService.includes('spa') || lowerService.includes('massage')) return 'spa-massage';
    
    return null;
}

// Global variables for booking
let currentServiceType = '';
let selectedDate = '';
let selectedTime = '8AM - 9AM';
let currentBookingId = '';

// ===== BOOKING MODAL =====
async function openBookingModal(serviceKey) {
    console.log('📋 Opening booking modal for service key:', serviceKey);
    
    // Check if user is logged in before opening booking modal
    try {
        console.log('🔐 Checking login status...');
        const response = await fetch('/api/me', {
            method: 'GET',
            credentials: 'same-origin', // Include cookies
            headers: {
                'Cache-Control': 'no-cache'
            }
        });
        const result = await response.json();
        
        console.log('🔐 Login check result:', result);
        
        if (!result.success || !result.user) {
            console.log('❌ User not logged in - showing login prompt');
            // User not logged in - show login prompt
            showLoginPrompt();
            return;
        }
        
        console.log('✅ User is logged in:', result.user.name, '- proceeding with booking');
        // User is logged in - proceed with booking
        currentServiceType = serviceKey;
        const data = serviceData[serviceKey];
        
        if (!data) {
            console.error('❌ Service data not found for key:', serviceKey);
            showAlert('Service not available for booking', 'error');
            return;
        }
        
        console.log('📊 Service data:', data);
        
        document.getElementById("modalServiceTitle").innerText = data.title;
        document.getElementById("priceDisplay").innerText      = data.price;
        document.getElementById("priceDescription").innerText  = data.priceDesc;
        document.getElementById("workerInfo").innerText        = data.workerInfo;
        document.getElementById("serviceImage").src            = data.image;
        
        buildCalendar();
        selectedTime = '8AM - 9AM';
        document.querySelectorAll(".time-slot").forEach(el => el.classList.remove("active-time"));
        const firstSlot = document.querySelector(".time-slot");
        if (firstSlot) firstSlot.classList.add("active-time");
        
        const modal = document.getElementById("bookingModal");
        if (modal) {
            modal.classList.add("show");
            console.log('✅ Booking modal opened successfully');
        } else {
            console.error('❌ Booking modal element not found');
        }
        
    } catch (error) {
        console.error('❌ Error checking login status:', error);
        // On error, try to proceed anyway (might be a network issue)
        showAlert('Connection issue. Please try again.', 'warning');
    }
}

// ===== LOGIN PROMPT MODAL =====
function showLoginPrompt() {
    let modal = document.getElementById("loginPromptModal");
    if (!modal) {
        modal = document.createElement("div");
        modal.id = "loginPromptModal";
        modal.className = "modal";
        document.body.appendChild(modal);
    }
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width:400px;padding:40px 32px;text-align:center;">
            <span class="close-btn" onclick="closeLoginPrompt()">&times;</span>
            <div style="font-size:3rem;margin-bottom:16px;">🔒</div>
            <h2 style="font-size:1.3rem;margin-bottom:10px;">Login Required</h2>
            <p style="color:#94a3b8;margin-bottom:28px;">Please log in to your account to book services.</p>
            
            <button onclick="redirectToLogin()"
                style="width:100%;padding:14px;border:none;border-radius:12px;
                       background:linear-gradient(135deg,#6366f1,#06b6d4);
                       color:white;font-size:1rem;font-weight:600;cursor:pointer;
                       margin-bottom:14px;">
                Go to Login
            </button>
            
            <button onclick="closeLoginPrompt()"
                style="width:100%;padding:12px;border:1px solid #334155;border-radius:12px;
                       background:transparent;color:#94a3b8;font-size:0.9rem;
                       cursor:pointer;">
                Cancel
            </button>
        </div>
    `;
    modal.classList.add("show");
}

function closeLoginPrompt() {
    const modal = document.getElementById("loginPromptModal");
    if (modal) modal.classList.remove("show");
}

// ===== REDIRECT TO LOGIN WITH RETURN URL =====
function redirectToLogin() {
    // Store current page URL for redirect after login
    const returnUrl = encodeURIComponent(window.location.pathname + window.location.search);
    window.location.href = `/login?redirect=${returnUrl}`;
}

function closeModal() { 
    const modal = document.getElementById("bookingModal");
    if (modal) modal.classList.remove("show"); 
}

function selectDate(element, label) {
    document.querySelectorAll(".date-day").forEach(el => el.classList.remove("selected"));
    element.classList.add("selected");
    selectedDate = label;
    document.getElementById("selectedDate").innerText = selectedDate;
}

function selectTime(element, time) {
    document.querySelectorAll(".time-slot").forEach(el => el.classList.remove("active-time"));
    element.classList.add("active-time");
    selectedTime = time;
}

function previousImage() {}
function nextImage() {}

function proceedToBook() {
    const data = serviceData[currentServiceType];
    document.getElementById("confirmBadge").innerText      = data.title;
    document.getElementById("confirmTimingText").innerText = `${selectedTime}, ${selectedDate}`;
    document.getElementById("summaryService").innerText    = data.title;
    document.getElementById("summaryDateTime").innerText   = `${selectedDate} · ${selectedTime}`;
    document.getElementById("summaryPrice").innerText      = data.price;
    ["cf-name","cf-address","cf-phone","cf-landmark","cf-email","cf-note"].forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = "";
    });
    closeModal();
    document.getElementById("confirmModal").classList.add("show");
}

function closeConfirmModal() { 
    const modal = document.getElementById("confirmModal");
    if (modal) modal.classList.remove("show"); 
}

// ===== CALENDAR BUILDER =====
function buildCalendar() {
    const picker = document.querySelector('.date-picker');
    if (!picker) return;
    
    const today = new Date();
    const currentMonth = today.getMonth();
    const currentYear = today.getFullYear();
    
    // Generate next 7 days
    let calendarHTML = '<div class="calendar-days">';
    for (let i = 0; i < 7; i++) {
        const date = new Date(today);
        date.setDate(today.getDate() + i);
        
        const dayName = date.toLocaleDateString('en', { weekday: 'short' });
        const dayNum = date.getDate();
        const monthName = date.toLocaleDateString('en', { month: 'short' });
        const fullDate = `${dayName}, ${monthName} ${dayNum}`;
        
        const isToday = i === 0;
        calendarHTML += `
            <div class="date-day ${isToday ? 'selected' : ''}" 
                 onclick="selectDate(this, '${fullDate}')">
                <div class="day-name">${dayName}</div>
                <div class="day-num">${dayNum}</div>
                <div class="day-month">${monthName}</div>
            </div>
        `;
    }
    calendarHTML += '</div>';
    
    picker.innerHTML = calendarHTML;
    
    // Set initial selected date
    const todayFormatted = new Date().toLocaleDateString('en', { 
        weekday: 'short', 
        month: 'short', 
        day: 'numeric' 
    });
    selectedDate = todayFormatted;
    document.getElementById("selectedDate").innerText = selectedDate;
}

// ===== FORM VALIDATION HELPERS =====
function showError(fieldId, message) {
    const field = document.getElementById(fieldId);
    const errorId = fieldId.replace('cf-', 'error-');
    let errorEl = document.getElementById(errorId);
    
    if (field) {
        field.style.borderColor = '#ef4444';
        if (errorEl) {
            errorEl.textContent = message;
            errorEl.style.display = 'block';
        }
    }
}

function clearError(fieldId) {
    const field = document.getElementById(fieldId);
    const errorId = fieldId.replace('cf-', 'error-');
    let errorEl = document.getElementById(errorId);
    
    if (field) {
        field.style.borderColor = '';
        if (errorEl) {
            errorEl.textContent = '';
            errorEl.style.display = 'none';
        }
    }
}

// ===== CONFIRM BOOKING =====
async function confirmBooking() {
    const name     = document.getElementById("cf-name").value.trim();
    const addr     = document.getElementById("cf-address").value.trim();
    const phone    = document.getElementById("cf-phone").value.trim();
    const landmark = document.getElementById("cf-landmark")?.value.trim() || "";
    const email    = document.getElementById("cf-email")?.value.trim() || "";
    const note     = document.getElementById("cf-note")?.value.trim() || "";

    ["cf-name","cf-address","cf-phone"].forEach(clearError);

    let valid = true;
    if (!name)  { showError("cf-name",    "Full name is required"); valid = false; }
    if (!addr)  { showError("cf-address", "Address is required");   valid = false; }
    if (!phone) { showError("cf-phone",   "Phone number required"); valid = false; }
    else if (!/^[9][0-9]{9}$/.test(phone)) { showError("cf-phone", "Enter a valid Nepal number (98XXXXXXXX)"); valid = false; }
    if (!valid) return;

    const btn = document.querySelector(".confirm-book-btn");
    btn.disabled  = true;
    btn.innerText = "Saving booking...";

    try {
        const res    = await fetch('/api/book', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name, address: addr, phone, landmark, email, note,
                service:   currentServiceType,
                provider:  "Auto-assigned",
                date_time: `${selectedDate} · ${selectedTime}`
            })
        });
        const result = await res.json();

        if (!result.success) {
            showAlert("Could not save booking: " + (result.message || "Unknown error"), 'error');
            btn.disabled  = false;
            btn.innerText = "Confirm Booking";
            return;
        }

        currentBookingId = result.booking_id;
        btn.disabled  = false;
        btn.innerText = "Confirm Booking";
        closeConfirmModal();

        // Show success message and redirect to payment
        showAlert("Booking confirmed! Redirecting to payment...", 'success');
        
        // STEP 2 — Show payment options
        setTimeout(() => {
            showPaymentModal(currentBookingId);
        }, 1500);

    } catch (err) {
        showAlert("Network error. Please check your connection.", 'error');
        btn.disabled  = false;
        btn.innerText = "Confirm Booking";
    }
}

// ===== PAYMENT MODAL =====
function showPaymentModal(bookingId) {
    let modal = document.getElementById("paymentModal");
    if (!modal) { 
        modal = document.createElement("div"); 
        modal.id = "paymentModal"; 
        modal.className = "modal"; 
        document.body.appendChild(modal); 
    }

    const data = serviceData[currentServiceType];
    modal.innerHTML = `
        <div class="modal-content" style="max-width:420px;padding:40px 32px;text-align:center;">
            <span class="close-btn" onclick="closePaymentModal()">&times;</span>
            <div style="font-size:2.5rem;margin-bottom:12px;">💳</div>
            <h2 style="font-size:1.2rem;margin-bottom:6px;">Choose Payment Method</h2>
            <p style="color:#94a3b8;font-size:0.85rem;margin-bottom:4px;">Booking ID: <strong style="color:#6366f1;">${bookingId}</strong></p>
            <p style="color:#94a3b8;font-size:0.85rem;margin-bottom:28px;">${data.title} · ${data.price}</p>

            <button id="esewaPayBtn" onclick="payWithEsewa('${bookingId}')"
                style="width:100%;padding:14px;border:none;border-radius:12px;
                       background:linear-gradient(135deg,#60a917,#7aba2a);
                       color:white;font-size:1rem;font-weight:600;cursor:pointer;
                       margin-bottom:14px;display:flex;align-items:center;
                       justify-content:center;gap:10px;transition:0.3s;">
                <svg width="24" height="24" viewBox="0 0 100 40" style="fill:white;">
                    <rect x="5" y="8" width="90" height="24" rx="4" fill="white"/>
                    <text x="50" y="24" text-anchor="middle" font-family="Arial, sans-serif" 
                          font-size="12" font-weight="bold" fill="#60a917">eSewa</text>
                </svg>
                Pay with eSewa
            </button>

            <button onclick="payWithCash('${bookingId}')"
                style="width:100%;padding:14px;border:1px solid #334155;border-radius:12px;
                       background:transparent;color:#94a3b8;font-size:0.9rem;
                       cursor:pointer;transition:0.3s;">
                💵 Pay Cash on Arrival
            </button>

            <p style="margin-top:18px;font-size:0.75rem;color:#475569;">
                Your booking is saved. Payment completes the confirmation.
            </p>
        </div>
    `;
    modal.classList.add("show");
}

function closePaymentModal() {
    const m = document.getElementById("paymentModal");
    if (m) m.classList.remove("show");
}

// ===== PAYMENT METHODS =====
async function payWithEsewa(bookingId) {
    const btn = document.getElementById("esewaPayBtn");
    btn.disabled  = true;
    btn.innerText = "⏳ Redirecting to eSewa...";

    try {
        const res = await fetch('/api/esewa/initiate', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ booking_id: bookingId })
        });
        const data = await res.json();

        if (data.success) {
            // Create and submit eSewa payment form
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = data.esewa_url;

            const fields = {
                'amount': data.amount,
                'tax_amount': '0',
                'total_amount': data.amount,
                'transaction_uuid': data.transaction_uuid,
                'product_code': data.product_code,
                'product_service_charge': '0',
                'product_delivery_charge': '0',
                'success_url': data.success_url,
                'failure_url': data.failure_url,
                'signed_field_names': 'total_amount,transaction_uuid,product_code',
                'signature': data.signature
            };

            Object.entries(fields).forEach(([key, value]) => {
                const input = document.createElement('input');
                input.type = 'hidden';
                input.name = key;
                input.value = value;
                form.appendChild(input);
            });

            document.body.appendChild(form);
            form.submit();
        } else {
            showAlert("Payment setup failed: " + data.message, 'error');
            btn.disabled = false;
            btn.innerText = "Pay with eSewa";
        }
    } catch (error) {
        showAlert("Payment error. Please try again.", 'error');
        btn.disabled = false;
        btn.innerText = "Pay with eSewa";
    }
}

async function payWithCash(bookingId) {
    try {
        const res = await fetch('/api/payment/cash', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ booking_id: bookingId })
        });
        const data = await res.json();

        if (data.success) {
            closePaymentModal();
            showAlert("Booking confirmed! You can pay cash when the service provider arrives.", 'success');
            
            // Redirect to orders page after a delay
            setTimeout(() => {
                window.location.href = '/orders';
            }, 3000);
        } else {
            showAlert("Payment setup failed: " + data.message, 'error');
        }
    } catch (error) {
        showAlert("Payment error. Please try again.", 'error');
    }
}