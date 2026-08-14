// =========================================
// Fraud Detection Dashboard Script
// =========================================

// -------------------------------
// Sidebar Navigation & Tab Switching
// -------------------------------

function showSection(sectionId) {

    const sections = document.querySelectorAll(".page");

    sections.forEach(function (section) {
        section.classList.add("hidden");
    });

    const targetSection = document.getElementById(sectionId);
    if (targetSection) {
        targetSection.classList.remove("hidden");
    }

    const menuItems = document.querySelectorAll(".sidebar li");
    menuItems.forEach(function (item) {
        item.classList.remove("active");
    });

    const activeNav = document.getElementById("nav-" + sectionId);
    if (activeNav) {
        activeNav.classList.add("active");
    }
}

// -------------------------------
// Page Load Initialization
// -------------------------------

window.addEventListener("DOMContentLoaded", function () {

    const initialTab = window.ACTIVE_TAB || "dashboard";
    if (document.getElementById(initialTab)) {
        showSection(initialTab);
    }

    initLocationChart();
    initPieChart();
    initCounters();
    updateClock();
    initParticles();
    initStaggeredCards();
    initFormLoader();
    initTypingEffect();
});

function initParticles() {
    if (window.particlesJS) {
        particlesJS("particles-js", {
            "particles": {
                "number": { "value": 60, "density": { "enable": true, "value_area": 800 } },
                "color": { "value": "#6366f1" },
                "shape": { "type": "circle" },
                "opacity": { "value": 0.3, "random": false },
                "size": { "value": 3, "random": true },
                "line_linked": { "enable": true, "distance": 150, "color": "#6366f1", "opacity": 0.2, "width": 1 },
                "move": { "enable": true, "speed": 1.5, "direction": "none", "random": true, "straight": false, "out_mode": "out", "bounce": false }
            },
            "interactivity": {
                "detect_on": "canvas",
                "events": {
                    "onhover": { "enable": true, "mode": "grab" },
                    "onclick": { "enable": true, "mode": "push" },
                    "resize": true
                },
                "modes": {
                    "grab": { "distance": 140, "line_linked": { "opacity": 0.5 } },
                    "push": { "particles_nb": 4 }
                }
            },
            "retina_detect": true
        });
    }
}

function initStaggeredCards() {
    const cards = document.querySelectorAll('.card');
    cards.forEach((card, index) => {
        card.classList.add(`stagger-${(index % 4) + 1}`);
    });
}

function initFormLoader() {
    const form = document.getElementById("predictForm");
    if (form) {
        form.addEventListener("submit", function() {
            const btnText = document.getElementById("btnText");
            const btnLoader = document.getElementById("btnLoader");
            const submitBtn = document.getElementById("submitBtn");
            if (btnText) btnText.innerText = "Analyzing Vectors...";
            if (btnLoader) btnLoader.classList.remove("hidden");
            if (submitBtn) {
                submitBtn.classList.remove("pulse-button");
                submitBtn.style.opacity = "0.7";
                submitBtn.style.pointerEvents = "none";
            }
        });
    }
}

// -------------------------------
// Live Animations Upgrades
// -------------------------------

function initTypingEffect() {
    const el = document.getElementById("welcomeText");
    if (!el) return;
    const text = el.getAttribute("data-text") || "";
    el.innerText = "";
    let i = 0;
    const speed = 60;
    function type() {
        if (i < text.length) {
            el.innerHTML += text.charAt(i);
            i++;
            setTimeout(type, speed);
        }
    }
    setTimeout(type, 300);
}



// -------------------------------
// Location Bar Chart
// -------------------------------

function initLocationChart() {
    const riskCanvas = document.getElementById("riskChart");
    if (!riskCanvas) return;

    const labels = (window.LOCATION_LABELS && window.LOCATION_LABELS.length > 0)
        ? window.LOCATION_LABELS
        : ["Hyderabad", "Mumbai", "Delhi", "Bangalore"];

    const values = (window.LOCATION_VALUES && window.LOCATION_VALUES.length > 0)
        ? window.LOCATION_VALUES
        : [0, 0, 0, 0];

    new Chart(riskCanvas, {
        type: "bar",
        data: {
            labels: labels,
            datasets: [{
                label: "Transaction Count",
                data: values,
                backgroundColor: [
                    "rgba(99, 102, 241, 0.75)",
                    "rgba(59, 130, 246, 0.75)",
                    "rgba(16, 185, 129, 0.75)",
                    "rgba(245, 158, 11, 0.75)"
                ],
                borderColor: [
                    "#6366f1",
                    "#3b82f6",
                    "#10b981",
                    "#f59e0b"
                ],
                borderWidth: 1.5,
                borderRadius: 8
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: { display: false }
            },
            scales: {
                y: {
                    beginAtZero: true,
                    ticks: { color: "#9ca3af", precision: 0 },
                    grid: { color: "rgba(255, 255, 255, 0.05)" }
                },
                x: {
                    ticks: { color: "#9ca3af" },
                    grid: { display: false }
                }
            }
        }
    });
}

// -------------------------------
// Risk Classification Pie Chart
// -------------------------------

function initPieChart() {
    const pieCanvas = document.getElementById("pieChart");
    if (!pieCanvas) return;

    const pieData = (window.PIE_DATA && window.PIE_DATA.length === 3)
        ? window.PIE_DATA
        : [0, 0, 0];

    new Chart(pieCanvas, {
        type: "doughnut",
        data: {
            labels: ["Approved (Safe)", "Suspicious", "High Risk (Fraud)"],
            datasets: [{
                data: pieData,
                backgroundColor: [
                    "rgba(16, 185, 129, 0.8)",
                    "rgba(245, 158, 11, 0.8)",
                    "rgba(239, 68, 68, 0.8)"
                ],
                borderColor: [
                    "#10b981",
                    "#f59e0b",
                    "#ef4444"
                ],
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            plugins: {
                legend: {
                    position: "bottom",
                    labels: { color: "#f3f4f6", padding: 16 }
                }
            }
        }
    });
}

// -------------------------------
// Animated Counters
// -------------------------------

function animateCounter(id) {
    const obj = document.getElementById(id);
    if (!obj) return;

    const endValue = parseInt(obj.innerText.trim(), 10);
    if (isNaN(endValue) || endValue <= 0) return;

    let start = 0;
    const duration = 400;
    const stepTime = Math.max(10, Math.floor(duration / endValue));

    const timer = setInterval(function () {
        start++;
        obj.innerHTML = start;

        if (start >= endValue) {
            obj.innerHTML = endValue;
            clearInterval(timer);
        }
    }, stepTime);
}

function initCounters() {
    animateCounter("totalCounter");
    animateCounter("fraudCounter");
    animateCounter("safeCounter");
}

// -------------------------------
// Table Search Filter
// -------------------------------

function searchTable() {
    const input = document.getElementById("searchInput");
    if (!input) return;

    const filter = input.value.toUpperCase();
    const table = document.getElementById("transactionTable");
    if (!table) return;

    const rows = table.getElementsByTagName("tbody")[0].getElementsByTagName("tr");

    for (let i = 0; i < rows.length; i++) {
        let textContent = rows[i].innerText || rows[i].textContent;

        if (textContent.toUpperCase().indexOf(filter) > -1) {
            rows[i].style.display = "";
        } else {
            rows[i].style.display = "none";
        }
    }
}

// -------------------------------
// Confirm Logout
// -------------------------------

function confirmLogout() {
    return confirm("Are you sure you want to log out?");
}

// -------------------------------
// Real-Time Clock
// -------------------------------

function updateClock() {
    const clock = document.getElementById("clock");
    if (!clock) return;

    const now = new Date();
    clock.innerHTML = now.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' });
}

setInterval(updateClock, 1000);