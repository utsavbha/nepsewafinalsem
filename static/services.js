// ============================================================
//  NepSewa — services.js  (eSewa Payment Integration)
// ============================================================

// ===== DARK MODE =====
const toggle = document.getElementById("darkToggle");
if (localStorage.getItem("theme") === "light") {
    document.body.classList.add("light");
    toggle.checked = true;
}
toggle.addEventListener("change", () => {
    document.body.classList.toggle("light");
    localStorage.setItem("theme", document.body.classList.contains("light") ? "light" : "dark");
});

// ===== ERROR HELPERS =====
function showError(inputId, message) {
    const input = document.getElementById(inputId);
    const key   = inputId.split("-")[1];
    const error = document.getElementById("error-" + key);
    if (!input || !error) return;
    input.classList.add("input-error");
    error.innerText = message;
    error.classList.add("show");
}
function clearError(inputId) {
    const input = document.getElementById(inputId);
    const key   = inputId.split("-")[1];
    const error = document.getElementById("error-" + key);
    if (!input || !error) return;
    input.classList.remove("input-error");
    error.innerText = "";
    error.classList.remove("show");
}

// ===== CALENDAR =====
const DAY_NAMES   = ["Sun","Mon","Tue","Wed","Thu","Fri","Sat"];
const MONTH_NAMES = ["Jan","Feb","Mar","Apr","May","Jun","Jul","Aug","Sep","Oct","Nov","Dec"];

function getUpcomingDays(count = 6) {
    const days = [], now = new Date();
    for (let i = 0; i < count; i++) {
        const d = new Date(now.getFullYear(), now.getMonth(), now.getDate() + i);
        days.push({
            dayName: DAY_NAMES[d.getDay()],
            date: d.getDate(),
            month: MONTH_NAMES[d.getMonth()],
            label: `${DAY_NAMES[d.getDay()]}, ${MONTH_NAMES[d.getMonth()]} ${d.getDate()}`
        });
    }
    return days;
}

function buildCalendar() {
    const picker = document.querySelector(".date-picker");
    if (!picker) return;
    const days = getUpcomingDays(6);
    picker.innerHTML = "";
    days.forEach((day, i) => {
        const div = document.createElement("div");
        div.className = "date-day" + (i === 0 ? " selected" : "");
        div.innerHTML = `
            <span class="day">${day.dayName}</span>
            <span class="date">${day.date}</span>
            <span class="month-label" style="font-size:10px;color:#999;">${day.month}</span>
        `;
        div.addEventListener("click", () => selectDate(div, day.label));
        picker.appendChild(div);
    });
    selectedDate = days[0].label;
    const el = document.getElementById("selectedDate");
    if (el) el.innerText = selectedDate;
}

// ===== STATE =====
let currentServiceType = '';
let selectedDate       = '';
let selectedTime       = '8AM - 9AM';
let currentBookingId   = '';
let activeServiceKey   = '';
let selectedDay        = '';
let currentSort        = 'score';
let allProviders       = []; // Cache for providers
let availableLocations = []; // Cache for locations
let availableServices  = []; // Cache for services
let serviceData        = {}; // Cache for service metadata

// ===== SERVICE DATA (will be loaded from API) =====
const defaultServiceData = {
    maid:         { title:"Maid Service",       price:"Rs. 500 / Hour",  priceDesc:"Rs. 500 for 1 hour · Rs. 1,500 for 3 hours · Rs. 2,500 for full day",      workerInfo:"Our maids handle daily household work including sweeping, mopping, washing dishes, and basic cooking. All background-checked and trained.",           image:"https://homeworknepal.com/wp-content/uploads/2024/05/Housemaid.jpg",                                                                                          serviceKey:"maid" },
    technician:   { title:"Technician Service", price:"Rs. 300 / Hour",  priceDesc:"Rs. 300 for 1 hour · Rs. 800 for 3 hours · Parts charged separately",       workerInfo:"Our technicians repair TVs, washing machines, refrigerators and microwaves. 30-day service warranty included.",                                           image:"https://homeworknepal.com/wp-content/uploads/2022/09/electrician-electric-electricity-2755683-1024x681.jpg",                                                  serviceKey:"technician" },
    plumber:      { title:"Plumber Service",    price:"Rs. 500 / Hour",  priceDesc:"Rs. 500 for 1 hour · Rs. 1,500 for 3 hours · Emergency: Rs. 800 flat",       workerInfo:"Our plumbers fix leaking taps, blocked drains, broken pipes and bathroom fittings. Available for urgent repairs too.",                                   image:"https://nnps.com.np/wp-content/uploads/2023/06/imgs-1.jpg",                                                                                                   serviceKey:"plumber" },
    electrician:  { title:"Electrician Service",price:"Rs. 500 / Hour",  priceDesc:"Rs. 500 for 1 hour · Rs. 1,500 for 3 hours · Wiring jobs quoted separately", workerInfo:"Switch repairs, fan and light installations, power socket fitting, and circuit troubleshooting. Safety check included.",                                   image:"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTXwC_BznDpwyR2eeQpC7mAQTTisL33B2Mt3g&s",                                                              serviceKey:"electrician" },
    haircutting:  { title:"Hair Cutting",       price:"Rs. 200 / Person",priceDesc:"Rs. 200 per person · Rs. 500 for family of 3 · Home visit included",         workerInfo:"Professional haircut at home. Our barbers bring all their own tools. Suitable for men and kids.",                                                       image:"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcQBOJdrtttgPWstF4HcMoxCwE8pU2dNwZEYQg&s",                                                              serviceKey:"haircutting" },
    gardener:     { title:"Gardener Service",   price:"Rs. 1,000 / Day", priceDesc:"Rs. 1,000 full day · Rs. 600 half day · Tools brought by gardener",           workerInfo:"Lawn mowing, plant trimming, weeding, watering and basic garden maintenance.",                                                                           image:"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcTC99OjYEYoOEna34FkVD741eZRu7AUVtSO3w&s",                                                              serviceKey:"gardener" },
    makeup:       { title:"Makeup Artist",      price:"Rs. 500 / Hour",  priceDesc:"Rs. 500 basic look · Rs. 1,200 bridal/party makeup · Products by artist",    workerInfo:"Home visits for weddings, parties, photoshoots and daily events. Professional makeup kit included.",                                                     image:"https://encrypted-tbn0.gstatic.com/images?q=tbn:ANd9GcRaaYzEvMXuqWZ5Hp5Q14B9vqRFu5fQvlfBEA&s",                                                              serviceKey:"makeup" },
    photographer: { title:"Photographer",       price:"Rs. 500 / Hour",  priceDesc:"Rs. 500 for 1 hour · Rs. 1,200 for 3 hours · Edited photos within 2 days",   workerInfo:"Family events, product shoots, birthdays, ceremonies. Camera and lighting provided. Digital delivery in 2 days.",                                       image:"https://img.freepik.com/free-photo/young-stylish-photographer-holds-professional-camera-taking-photos_8353-6506.jpg",                                          serviceKey:"photographer" },
    cleaning:     { title:"Home Cleaning",      price:"Rs. 500 / Hour",  priceDesc:"Rs. 500 for 1 hour · Rs. 1,500 for 3 hours · Rs. 2,500 for deep clean",       workerInfo:"Kitchens, bathrooms, bedrooms and living rooms cleaned thoroughly. Cleaning supplies and equipment brought.",                                           image:"https://sunflowermaids.com/wp-content/uploads/2021/08/Signs-of-a-Bad-Cleaning-Lady.jpg",                                                                      serviceKey:"cleaning" },
    ac:           { title:"AC Repair & Service",price:"Rs. 500 / Hour",  priceDesc:"Rs. 500 general service · Rs. 800 repair visit · Gas refill extra",           workerInfo:"Regular servicing, filter cleaning, gas refilling and fault repairs for all major AC brands. No hidden charges.",                                       image:"https://clareservices.com/wp-content/uploads/2020/07/air-conditioning-repair-service-hyderabad.jpg",                                                          serviceKey:"ac" },
};

// ===== LEFT PANEL — service click =====
async function selectService(el) {
    document.querySelectorAll(".svc-item").forEach(i => i.classList.remove("active"));
    el.classList.add("active");
    const key  = el.dataset.key;
    activeServiceKey = key;
    const data = serviceData[key];

    document.getElementById("bannerImg").src         = data.image;
    document.getElementById("bannerTitle").innerText = data.title;
    document.getElementById("bannerDesc").innerText  = data.workerInfo;
    document.getElementById("bannerPrice").innerText = data.price;
    document.getElementById("bannerBookBtn").onclick = () => openBookingModal(key);
    document.getElementById("svcBanner").classList.add("show");

    document.getElementById("filterBar").style.display = "flex";
    document.getElementById("sortRow").style.display   = "flex";
    document.getElementById("placeholder").style.display  = "none";
    document.getElementById("providerGrid").style.display = "grid";

    selectedDay = ""; currentSort = "score";
    document.querySelectorAll(".day-pill").forEach(p => p.classList.remove("active"));
    document.querySelectorAll(".sort-pill").forEach(b => b.classList.toggle("active", b.dataset.sort === "score"));
    document.getElementById("locationSelect").value = "";
    document.getElementById("ratingSelect").value   = "0";
    
    // Load locations if not already loaded
    if (availableLocations.length === 0) {
        await loadLocations();
    }
    
    await runAlgorithm();
}

// ===== FILTERS =====
document.getElementById("locationSelect").addEventListener("change", runAlgorithm);
document.getElementById("ratingSelect").addEventListener("change", runAlgorithm);

document.querySelectorAll(".day-pill").forEach(pill => {
    pill.addEventListener("click", () => {
        const day = pill.dataset.day;
        if (selectedDay === day) { selectedDay = ""; pill.classList.remove("active"); }
        else { selectedDay = day; document.querySelectorAll(".day-pill").forEach(p => p.classList.remove("active")); pill.classList.add("active"); }
        runAlgorithm();
    });
});

document.querySelectorAll(".sort-pill").forEach(btn => {
    btn.addEventListener("click", () => {
        document.querySelectorAll(".sort-pill").forEach(b => b.classList.remove("active"));
        btn.classList.add("active");
        currentSort = btn.dataset.sort;
        runAlgorithm();
    });
});

// ===== API FUNCTIONS =====
async function loadServices() {
    try {
        const response = await fetch('/api/services');
        const data = await response.json();
        if (data.success) {
            availableServices = data.services;
            // Build serviceData object for compatibility
            serviceData = {};
            data.services.forEach(service => {
                serviceData[service.service_key] = {
                    title: service.title,
                    price: service.price,
                    priceDesc: service.price + " · Professional service with quality guarantee",
                    workerInfo: service.description,
                    image: service.image,
                    serviceKey: service.service_key
                };
            });
            updateServicesList();
            return true;
        }
    } catch (error) {
        console.error('Error loading services:', error);
        // Fallback to default data
        serviceData = defaultServiceData;
        return false;
    }
}

function updateServicesList() {
    console.log('🔧 updateServicesList called with', availableServices.length, 'services');
    const leftPanel = document.querySelector('.panel-left');
    if (!leftPanel) {
        console.error('❌ Left panel not found');
        return;
    }
    
    // Find the services container (after the title)
    const title = leftPanel.querySelector('.panel-left-title');
    if (!title) {
        console.error('❌ Panel title not found');
        return;
    }
    
    // Remove existing service items
    const existingItems = leftPanel.querySelectorAll('.svc-item');
    console.log('🗑️ Removing', existingItems.length, 'existing items');
    existingItems.forEach(item => item.remove());
    
    // Add services from database
    availableServices.forEach(service => {
        const serviceItem = document.createElement('div');
        serviceItem.className = 'svc-item';
        serviceItem.dataset.key = service.service_key;
        serviceItem.onclick = () => selectService(serviceItem);
        
        serviceItem.innerHTML = `
            <img class="svc-thumb" src="${service.image}" alt="${service.title}">
            <div class="svc-info">
                <h4>${service.title}</h4>
                <p>${service.price}</p>
                <small style="color:#64748b;font-size:10px;">${service.provider_count} providers · ⭐ ${service.avg_rating}</small>
            </div>
        `;
        
        leftPanel.appendChild(serviceItem);
    });
    
    // Add "Become a Provider" button at the end
    console.log('➕ Adding Become a Provider button');
    const providerSignupItem = document.createElement('div');
    providerSignupItem.className = 'svc-item provider-signup-item';
    providerSignupItem.onclick = () => {
        console.log('🔗 Redirecting to provider registration');
        window.location.href = '/register-provider';
    };
    
    providerSignupItem.innerHTML = `
        <img class="svc-thumb" src="https://cdn-icons-png.flaticon.com/512/3135/3135715.png" alt="Become Provider">
        <div class="svc-info">
            <h4>Become a Provider</h4>
            <p>Join our network</p>
            <small style="color:#6366f1;font-size:10px;font-weight:600;">✨ Start earning today</small>
        </div>
    `;
    
    leftPanel.appendChild(providerSignupItem);
    console.log('✅ Provider signup button added successfully');
}

async function loadLocations() {
    try {
        const response = await fetch('/api/locations');
        const data = await response.json();
        if (data.success) {
            availableLocations = data.locations;
            updateLocationSelect();
        }
    } catch (error) {
        console.error('Error loading locations:', error);
    }
}

function updateLocationSelect() {
    const select = document.getElementById("locationSelect");
    // Clear existing options except "All Locations"
    select.innerHTML = '<option value="">All Locations</option>';
    
    availableLocations.forEach(location => {
        const option = document.createElement('option');
        option.value = location;
        option.textContent = location;
        select.appendChild(option);
    });
}

async function runAlgorithm() {
    if (!activeServiceKey) return;
    
    const location = document.getElementById("locationSelect").value;
    const minRating = parseFloat(document.getElementById("ratingSelect").value) || 0;
    
    try {
        // Build API URL with parameters
        const params = new URLSearchParams({
            service_key: activeServiceKey,
            sort: currentSort
        });
        
        if (location) params.append('location', location);
        if (selectedDay) params.append('day_name', selectedDay);
        if (minRating > 0) params.append('min_rating', minRating.toString());
        
        const response = await fetch(`/api/providers?${params}`);
        const data = await response.json();
        
        if (data.success) {
            renderProviders(data.providers, location);
        } else {
            console.error('Error fetching providers:', data.message);
            renderProviders([], location);
        }
    } catch (error) {
        console.error('Error in runAlgorithm:', error);
        renderProviders([], location);
    }
}

function renderProviders(list, preferredLocation) {
    const grid    = document.getElementById("providerGrid");
    const countEl = document.getElementById("resultCount");
    const maxScore = list.length > 0 ? (list[0]._score || 1) : 1;
    countEl.textContent = list.length === 0 ? "" : `${list.length} provider${list.length > 1 ? "s" : ""} found`;
    grid.innerHTML = "";
    if (list.length === 0) {
        grid.innerHTML = `<div class="no-results"><div class="no-icon">🔍</div><p>No providers found.</p><p style="margin-top:6px;font-size:12px;color:#64748b;">Try removing the day filter or changing location.</p></div>`;
        return;
    }
    list.forEach((p, idx) => {
        const barPct = Math.min(100, Math.round(((p._score||0)/maxScore)*100));
        const cancelPct = Math.round((p.cancellation_rate || 0) * 100);
        const isTop = idx === 0 && currentSort === "score";
        const card = document.createElement("div");
        card.className = "pro-card-new";
        card.innerHTML = `
            ${isTop ? '<div class="top-match-ribbon">🏆 Top Match</div>' : ''}
            <img src="${p.image || 'https://via.placeholder.com/150'}" alt="${p.name}" style="margin-top:${isTop?'20px':'0'}">
            ${p.is_verified ? `<div class="verified-badge"><svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" width="10" height="10"><polyline points="20 6 9 17 4 12"/></svg> Verified</div>` : '<div style="height:20px;"></div>'}
            <h4>${p.name}</h4>
            <p class="pro-loc">📍 ${p.location}</p>
            <div class="pro-stats-row">
                <div class="ps"><span class="ps-num">⭐ ${p.rating}</span><span class="ps-lbl">Rating</span></div>
                <div class="ps"><span class="ps-num">${p.experience}yr</span><span class="ps-lbl">Exp.</span></div>
                <div class="ps"><span class="ps-num">${p.completed_jobs}</span><span class="ps-lbl">Jobs</span></div>
                <div class="ps"><span class="ps-num">${cancelPct}%</span><span class="ps-lbl">Cancel</span></div>
            </div>
            <div class="score-bar-wrap">
                <div class="score-bar-bg"><div class="score-bar-fill" style="width:${barPct}%"></div></div>
                <span class="score-lbl">Match ${barPct}%</span>
            </div>
            <p class="pro-response">⚡ ~${p.response_time_hours}h response · ${p.review_count} reviews</p>
            <button class="book-now-btn" onclick="openBookingModal('${activeServiceKey}')">Book Now</button>
        `;
        grid.appendChild(card);
    });
}

// ===== BOOKING MODAL =====
async function openBookingModal(serviceKey) {
    // Check if user is logged in before opening booking modal
    try {
        const response = await fetch('/api/me');
        const result = await response.json();
        
        if (!result.success) {
            // User not logged in - show login prompt
            showLoginPrompt();
            return;
        }
        
        // User is logged in - proceed with booking
        currentServiceType = serviceKey;
        const data = serviceData[serviceKey];
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
        document.getElementById("bookingModal").classList.add("show");
        
    } catch (error) {
        console.error('Error checking login status:', error);
        showLoginPrompt();
    }
}
function showDetails(service) { openBookingModal(service); }

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

function closeModal() { document.getElementById("bookingModal").classList.remove("show"); }

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
function nextImage()     {}

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

function closeConfirmModal() { document.getElementById("confirmModal").classList.remove("show"); }

// ============================================================
//  STEP 1 — CONFIRM BOOKING  (saves to orders.json)
// ============================================================
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
            alert("Could not save booking: " + (result.message || "Unknown error"));
            btn.disabled  = false;
            btn.innerText = "Confirm Booking";
            return;
        }

        currentBookingId = result.booking_id;
        btn.disabled  = false;
        btn.innerText = "Confirm Booking";
        closeConfirmModal();

        // STEP 2 — Show payment options
        showPaymentModal(currentBookingId);

    } catch (err) {
        alert("Network error. Is Flask running?");
        btn.disabled  = false;
        btn.innerText = "Confirm Booking";
    }
}

// ============================================================
//  STEP 2 — PAYMENT MODAL
// ============================================================
function showPaymentModal(bookingId) {
    let modal = document.getElementById("paymentModal");
    if (!modal) { modal = document.createElement("div"); modal.id = "paymentModal"; modal.className = "modal"; document.body.appendChild(modal); }

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

// ============================================================
//  eSewa Payment Integration
//  Flow: JS → Flask /api/esewa/initiate → gets form data
//        → submit form to eSewa → user pays → eSewa
//        redirects to /payment/success?data=<base64> → Flask decodes
// ============================================================
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
            // Create and submit eSewa v2 payment form
            const form = document.createElement('form');
            form.method = 'POST';
            form.action = data.esewa_url;

           const fields = {
    'amount':                   data.amount,       // already a string from Flask
    'tax_amount':               '0',
    'total_amount':             data.amount,       // must exactly match what was signed
    'transaction_uuid':         bookingId,
    'product_code':             data.merchant_code,
    'product_service_charge':   '0',
    'product_delivery_charge':  '0',
    'success_url':              data.success_url,
    'failure_url':              data.failure_url,
    'signed_field_names':       'total_amount,transaction_uuid,product_code',
    'signature':                data.signature
};
            for (const [key, value] of Object.entries(fields)) {
                const input = document.createElement('input');
                input.type  = 'hidden';
                input.name  = key;
                input.value = value;
                form.appendChild(input);
            }

            document.body.appendChild(form);
            form.submit();
        } else {
            alert("❌ eSewa Error: " + (data.message || "Could not initiate payment"));
            btn.disabled  = false;
            btn.innerHTML = `<svg width="24" height="24" viewBox="0 0 100 40" style="fill:white;">
                                <rect x="5" y="8" width="90" height="24" rx="4" fill="white"/>
                                <text x="50" y="24" text-anchor="middle" font-family="Arial, sans-serif" 
                                      font-size="12" font-weight="bold" fill="#60a917">eSewa</text>
                             </svg>
                             Pay with eSewa`;
        }
    } catch (err) {
        alert("Network error. Please try again.");
        btn.disabled  = false;
        btn.innerHTML = `<svg width="24" height="24" viewBox="0 0 100 40" style="fill:white;">
                            <rect x="5" y="8" width="90" height="24" rx="4" fill="white"/>
                            <text x="50" y="24" text-anchor="middle" font-family="Arial, sans-serif" 
                                  font-size="12" font-weight="bold" fill="#60a917">eSewa</text>
                         </svg>
                         Pay with eSewa`;
    }
}

// ============================================================
//  CASH ON ARRIVAL
// ============================================================
async function payWithCash(bookingId) {
    try {
        await fetch('/api/orders/update', {
            method:  'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ booking_id: bookingId, status: "confirmed" })
        });
    } catch(e) {}

    closePaymentModal();

    // Show success popup
    let modal = document.getElementById("successModal");
    if (!modal) { modal = document.createElement("div"); modal.id = "successModal"; modal.className = "modal"; document.body.appendChild(modal); }
    modal.innerHTML = `
        <div class="modal-content" style="max-width:400px;padding:40px 32px;text-align:center;">
            <div style="font-size:3rem;margin-bottom:16px;">✅</div>
            <h2 style="font-size:1.3rem;margin-bottom:10px;color:#22c55e;">Booking Confirmed!</h2>
            <p style="color:#94a3b8;margin-bottom:8px;">Pay cash when our professional arrives.</p>
            <p style="color:#6366f1;font-weight:600;font-size:1.1rem;margin:16px 0;">ID: ${bookingId}</p>
            <p style="color:#64748b;font-size:0.85rem;margin-bottom:28px;">We will contact you shortly to confirm your appointment.</p>
            <button onclick="document.getElementById('successModal').classList.remove('show')"
                style="padding:12px 30px;background:linear-gradient(135deg,#6366f1,#06b6d4);
                       border:none;border-radius:10px;color:white;font-weight:600;cursor:pointer;">Done</button>
        </div>
    `;
    modal.classList.add("show");
}

// ===== CLOSE MODALS ON OUTSIDE CLICK =====
window.onclick = function(event) {
    ["bookingModal","confirmModal","paymentModal","successModal","loginPromptModal"].forEach(id => {
        const m = document.getElementById(id);
        if (m && event.target === m) {
            m.classList.remove("show");
        }
    });
};

// ===== INITIALIZE PAGE =====
document.addEventListener('DOMContentLoaded', async function() {
    console.log('🚀 Initializing NepSewa Services Page...');
    
    // Load services from database
    const servicesLoaded = await loadServices();
    if (servicesLoaded) {
        console.log('✅ Services loaded from database');
    } else {
        console.log('⚠️ Using fallback service data');
    }
    
    // Load locations
    await loadLocations();
    console.log('✅ Locations loaded');
    
    console.log('🎉 Page initialization complete!');
    
    // Force update services list to ensure provider button is added
    console.log('🔄 Force updating services list...');
    updateServicesList();
});