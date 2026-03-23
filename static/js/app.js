// ============================================
// AI Real Estate — Frontend Logic
// ============================================

document.addEventListener('DOMContentLoaded', () => {
    initLocationDropdown();
    initValidation();
    initSliderLabel();
    initBudgetFormatting();
    initTheme();
    loadHistory();
    init3DEffects();
});

// ===== Premium 3D Effects =====
function init3DEffects() {
    document.querySelectorAll('.metric-box, .glass-card:not(#resultSection)').forEach(box => {
        box.addEventListener('mousemove', e => {
            const rect = box.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = ((y - centerY) / centerY) * -5;
            const rotateY = ((x - centerX) / centerX) * 5;
            box.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.02, 1.02, 1.02)`;
        });
        box.addEventListener('mouseleave', () => {
            box.style.transform = `perspective(1000px) rotateX(0) rotateY(0) scale3d(1, 1, 1)`;
        });
    });
}

// ===== Theme & Dark Mode =====
function initTheme() {
    const isDark = localStorage.getItem('darkMode') === 'true';
    const toggle = document.getElementById('darkModeToggle');
    if (isDark) {
        document.body.classList.add('dark-mode');
        if (toggle) toggle.checked = true;
    }
}

function toggleDarkMode() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('darkMode', isDark);
    showToast('Theme Updated', `Switched to ${isDark ? 'Dark' : 'Light'} Mode`, 'success');
}

// ===== Toast Notifications =====
function showToast(title, message, type = 'info') {
    const container = document.getElementById('toastContainer');
    if (!container) return;
    
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.innerHTML = `
        <div class="toast-title">${title}</div>
        <div class="toast-msg">${message}</div>
    `;
    container.appendChild(toast);
    
    // Trigger animation
    requestAnimationFrame(() => {
        setTimeout(() => toast.classList.add('show'), 10);
    });
    
    // Remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 400);
    }, 4000);
}

// ===== History Management =====
function saveToHistory(data) {
    let history = JSON.parse(localStorage.getItem('predictHistory') || '[]');
    history.unshift({
        city: data.city,
        bhk: data.bhk,
        price: data.price,
        time: new Date().toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})
    });
    if (history.length > 6) history.pop(); // Keep last 6
    localStorage.setItem('predictHistory', JSON.stringify(history));
    loadHistory();
}

function loadHistory() {
    const section = document.getElementById('historySection');
    const list = document.getElementById('historyList');
    if (!section || !list) return;
    
    const history = JSON.parse(localStorage.getItem('predictHistory') || '[]');
    
    if (history.length === 0) {
        section.classList.add('hidden');
        return;
    }
    
    section.classList.remove('hidden');
    list.innerHTML = '';
    history.forEach(item => {
        const card = document.createElement('div');
        card.className = 'history-card';
        card.innerHTML = `
            <div class="history-details">
                <p><strong>${item.bhk} BHK</strong> in ${item.city}</p>
                <p style="font-size:11px; margin-bottom:0;">${item.time}</p>
            </div>
            <div class="history-price">${item.price}</div>
        `;
        list.appendChild(card);
    });
}

function clearHistory() {
    localStorage.removeItem('predictHistory');
    loadHistory();
    showToast('History Cleared', 'Your recent estimates have been removed.', 'info');
}

function copyEstimateToClipboard() {
    const price = document.getElementById('predictedPrice').textContent;
    const city = document.getElementById('city').value;
    const bhk = document.getElementById('bhk').value;
    const text = `My ${bhk} BHK property in ${city} is estimated at ${price} by AI Real Estate.`;
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied!', 'Estimate copied to clipboard', 'success');
    }).catch(err => {
        showToast('Error', 'Failed to copy to clipboard', 'error');
    });
}

// ===== City → Location AJAX =====
function initLocationDropdown() {
    const citySelect = document.getElementById('city');
    if (!citySelect) return;

    citySelect.addEventListener('change', fetchLocations);
    // Load locations for default city on page load
    fetchLocations();
}

async function fetchLocations() {
    const city = document.getElementById('city').value;
    const locationSelect = document.getElementById('location');

    locationSelect.innerHTML = '<option value="">Loading...</option>';
    locationSelect.disabled = true;

    try {
        const res = await fetch(`/api/locations?city=${encodeURIComponent(city)}`);
        const locations = await res.json();

        locationSelect.innerHTML = '';
        locations.forEach(loc => {
            const opt = document.createElement('option');
            opt.value = loc;
            opt.textContent = loc;
            locationSelect.appendChild(opt);
        });
    } catch (err) {
        locationSelect.innerHTML = '<option value="">Error loading locations</option>';
    }

    locationSelect.disabled = false;
}

// ===== BHK–Area Validation =====
function initValidation() {
    const bhkSelect = document.getElementById('bhk');
    const areaInput = document.getElementById('area_sqft');
    if (!bhkSelect || !areaInput) return;

    const validate = () => validateBhkArea();
    bhkSelect.addEventListener('change', validate);
    areaInput.addEventListener('input', validate);
    validate(); // initial check
}

function validateBhkArea() {
    const bhk = parseInt(document.getElementById('bhk').value);
    const area = parseInt(document.getElementById('area_sqft').value);
    const msgEl = document.getElementById('validationMsg');
    const predictBtn = document.getElementById('predictBtn');

    if (!BHK_RANGES || !BHK_RANGES[bhk]) return;

    const [minArea, maxArea] = BHK_RANGES[bhk];

    if (area < minArea) {
        msgEl.textContent = `⚠️ Area too small for ${bhk} BHK (min ${minArea} sqft)`;
        msgEl.className = 'validation-msg invalid';
        predictBtn.disabled = true;
        predictBtn.style.opacity = '0.5';
    } else if (area > maxArea) {
        msgEl.textContent = `⚠️ Area too large for ${bhk} BHK (max ${maxArea} sqft)`;
        msgEl.className = 'validation-msg invalid';
        predictBtn.disabled = true;
        predictBtn.style.opacity = '0.5';
    } else {
        msgEl.textContent = '✅ Good selection';
        msgEl.className = 'validation-msg valid';
        predictBtn.disabled = false;
        predictBtn.style.opacity = '1';
    }
}

// ===== Property Age Slider Label =====
function initSliderLabel() {
    const slider = document.getElementById('property_age');
    const label = document.getElementById('ageValue');
    if (!slider || !label) return;

    const updateSliderFill = () => {
        label.textContent = slider.value;
        const val = ((slider.value - slider.min) / (slider.max - slider.min)) * 100;
        slider.style.setProperty('--val', `${val}%`);
    };

    slider.addEventListener('input', updateSliderFill);
    updateSliderFill(); // Initial setup
}

// ===== Budget Formatting =====
function initBudgetFormatting() {
    const budgetInput = document.getElementById('budget');
    const display = document.getElementById('budgetDisplay');
    if (!budgetInput || !display) return;

    const update = () => {
        const raw = budgetInput.value.replace(/,/g, '').trim();
        const num = parseInt(raw);
        if (!isNaN(num) && num > 0) {
            display.textContent = `₹ ${num.toLocaleString('en-IN')}`;
            display.style.color = '#94a3b8';
        } else {
            display.textContent = 'Invalid budget';
            display.style.color = '#f87171';
        }
    };

    budgetInput.addEventListener('input', update);
    update();
}

// ===== Predict Price =====
async function predictPrice() {
    const emptyState = document.getElementById('emptyState');
    const loadingState = document.getElementById('loadingState');
    const resultsContainer = document.getElementById('resultsContainer');
    const predictBtn = document.getElementById('predictBtn');

    // Reset Mood
    const isDark = document.body.classList.contains('dark-mode');
    document.body.className = `dashboard-body ${isDark ? 'dark-mode' : ''}`;

    // Show loading
    emptyState.classList.add('hidden');
    resultsContainer.classList.add('hidden');
    loadingState.classList.remove('hidden');
    predictBtn.disabled = true;
    predictBtn.style.opacity = '0.5';

    // Gather data
    const budgetRaw = document.getElementById('budget').value.replace(/,/g, '').trim();
    const budgetNum = parseInt(budgetRaw);

    const payload = {
        city: document.getElementById('city').value,
        location: document.getElementById('location').value,
        area_sqft: parseInt(document.getElementById('area_sqft').value),
        bhk: parseInt(document.getElementById('bhk').value),
        property_age: parseInt(document.getElementById('property_age').value),
        parking: document.getElementById('parking').checked ? 1 : 0,
        lift: document.getElementById('lift').checked ? 1 : 0,
        balcony: document.getElementById('balcony').checked ? 1 : 0,
        budget: !isNaN(budgetNum) ? budgetNum : null
    };

    if (!payload.city || !payload.location || isNaN(payload.area_sqft) || isNaN(payload.bhk) || isNaN(payload.property_age) || payload.budget === null) {
        showToast('Incomplete Data', 'Please fill out all fields before predicting.', 'error');
        loadingState.classList.add('hidden');
        emptyState.classList.remove('hidden');
        predictBtn.disabled = false;
        predictBtn.style.opacity = '1';
        return;
    }

    if (payload.area_sqft <= 0 || payload.property_age <= 0 || payload.budget <= 0) {
        showToast('Invalid Entries', 'Area, Age, and Budget must be greater than 0.', 'error');
        loadingState.classList.add('hidden');
        emptyState.classList.remove('hidden');
        predictBtn.disabled = false;
        predictBtn.style.opacity = '1';
        return;
    }

    try {
        const res = await fetch('/api/predict', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });

        const data = await res.json();

        if (data.error) {
            showToast('Prediction Failed', data.error, 'error');
            loadingState.classList.add('hidden');
            emptyState.classList.remove('hidden');
            predictBtn.disabled = false;
            predictBtn.style.opacity = '1';
            return;
        }

        // Populate metrics
        document.getElementById('predictedPrice').textContent = data.prediction;
        document.getElementById('priceRange').textContent = `${data.lower} – ${data.upper}`;
        document.getElementById('priceSqft').textContent = data.price_sqft;

        // Save to History
        saveToHistory({
            city: payload.city,
            bhk: payload.bhk,
            price: data.prediction
        });
        showToast('Success', 'Property valuation complete!', 'success');

        // Verdict
        const verdictCard = document.getElementById('verdictCard');
        if (data.verdict) {
            const icons = { over: '⚠️', good: '✅', fair: 'ℹ️' };
            verdictCard.className = `verdict-card verdict-${data.verdict_type}`;
            verdictCard.innerHTML = `<span>${icons[data.verdict_type] || ''}</span> ${data.verdict}`;
            verdictCard.classList.remove('hidden');
            
            // Dynamic Mood Background
            const isDark = document.body.classList.contains('dark-mode');
            document.body.className = `dashboard-body mood-${data.verdict_type} ${isDark ? 'dark-mode' : ''}`;
        } else {
            verdictCard.classList.add('hidden');
            const isDark = document.body.classList.contains('dark-mode');
            document.body.className = `dashboard-body ${isDark ? 'dark-mode' : ''}`;
        }

        // Confidence Ring
        document.getElementById('confidenceValueText').textContent = `${data.confidence}%`;
        const ring = document.getElementById('confidenceRing');
        ring.style.strokeDasharray = `0, 100`;
        setTimeout(() => {
            ring.style.strokeDasharray = `${data.confidence}, 100`;
        }, 100);

        // Budget Comparison Vis
        const budgetComparisonContainer = document.getElementById('budgetComparison');
        if (payload.budget) {
            document.getElementById('bcBudgetVal').textContent = `₹ ${(payload.budget).toLocaleString('en-IN')}`;
            document.getElementById('bcPredVal').textContent = data.prediction;
            
            // Calculate widths
            const maxVal = Math.max(payload.budget, data.prediction_raw);
            const budgetPct = (payload.budget / maxVal) * 100;
            const predPct = (data.prediction_raw / maxVal) * 100;
            
            document.getElementById('bcBarBudget').style.width = '0%';
            document.getElementById('bcBarPred').style.width = '0%';
            budgetComparisonContainer.classList.remove('hidden');
            
            setTimeout(() => {
                document.getElementById('bcBarBudget').style.width = `${budgetPct}%`;
                document.getElementById('bcBarPred').style.width = `${predPct}%`;
            }, 300);
        } else {
            budgetComparisonContainer.classList.add('hidden');
        }

        // Show results
        loadingState.classList.add('hidden');
        resultsContainer.classList.remove('hidden');

        // Animate metric boxes
        document.querySelectorAll('.metric-box').forEach((box, i) => {
            box.style.opacity = '0';
            box.style.transform = 'translateY(20px)';
            setTimeout(() => {
                box.style.transition = 'all 0.5s ease';
                box.style.opacity = '1';
                box.style.transform = 'translateY(0)';
            }, 150 * (i + 1));
        });


    } catch (err) {
        showToast('Network Error', 'Please check your connection and try again.', 'error');
        loadingState.classList.add('hidden');
        emptyState.classList.remove('hidden');
    }

    predictBtn.disabled = false;
    predictBtn.style.opacity = '1';
}

// ===== Mobile Sidebar Toggle =====
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    sidebar.classList.toggle('open');
}

// Close sidebar when clicking outside on mobile
document.addEventListener('click', (e) => {
    const sidebar = document.getElementById('sidebar');
    const toggle = document.getElementById('sidebarToggle');
    if (!sidebar || !toggle) return;

    if (sidebar.classList.contains('open') &&
        !sidebar.contains(e.target) &&
        !toggle.contains(e.target)) {
        sidebar.classList.remove('open');
    }
});


