// =============================================
// AI Notes Generator - Main JavaScript
// =============================================

console.log("✅ AI Notes Generator Loaded Successfully");

// Global variables
let isDarkMode = false;

// Toggle Sidebar (for mobile)
function toggleSidebar() {
    const sidebar = document.querySelector('.sidebar');
    if (sidebar) {
        sidebar.classList.toggle('active');
    }
}

// Dark Mode Toggle
function toggleDarkMode() {
    isDarkMode = !isDarkMode;
    document.body.classList.toggle('dark-mode', isDarkMode);
    
    // Save preference
    localStorage.setItem('darkMode', isDarkMode);
    
    // Optional: Change icon if you have one
    const icon = document.getElementById('darkModeIcon');
    if (icon) {
        icon.classList.toggle('bi-sun', !isDarkMode);
        icon.classList.toggle('bi-moon', isDarkMode);
    }
}

// Load saved dark mode preference
function loadDarkModePreference() {
    const saved = localStorage.getItem('darkMode');
    if (saved === 'true') {
        document.body.classList.add('dark-mode');
        isDarkMode = true;
    }
}

// Copy text to clipboard
function copyToClipboard(text, message = "Copied to clipboard!") {
    navigator.clipboard.writeText(text).then(() => {
        showToast(message);
    }).catch(err => {
        console.error("Failed to copy:", err);
        alert("Failed to copy text");
    });
}

// Show toast notification
function showToast(message) {
    let toast = document.createElement('div');
    toast.className = 'toast-notification';
    toast.innerHTML = `
        <div class="toast-content">
            <i class="bi bi-check-circle"></i>
            <span>${message}</span>
        </div>
    `;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = '0';
        setTimeout(() => toast.remove(), 500);
    }, 2500);
}

// Add toast styles dynamically
function addToastStyles() {
    const style = document.createElement('style');
    style.innerHTML = `
        .toast-notification {
            position: fixed;
            bottom: 20px;
            right: 20px;
            background: #4F46E5;
            color: white;
            padding: 12px 20px;
            border-radius: 8px;
            box-shadow: 0 4px 15px rgba(0,0,0,0.2);
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 9999;
            transition: all 0.3s ease;
            font-size: 0.95rem;
        }
        .toast-notification i {
            font-size: 1.2rem;
        }
    `;
    document.head.appendChild(style);
}

// Initialize everything when page loads
document.addEventListener('DOMContentLoaded', function() {
    console.log("🚀 DOM fully loaded - Initializing scripts...");

    // Load dark mode preference
    loadDarkModePreference();

    // Add toast styles
    addToastStyles();

    // Make all copy buttons work (if any)
    document.querySelectorAll('.copy-btn').forEach(btn => {
        btn.addEventListener('click', function() {
            const targetId = this.getAttribute('data-copy');
            const textElement = document.getElementById(targetId);
            if (textElement) {
                copyToClipboard(textElement.innerText || textElement.value);
            }
        });
    });

    // Auto-hide flash messages after 4 seconds
    setTimeout(() => {
        const flashes = document.querySelectorAll('.alert');
        flashes.forEach(alert => {
            alert.style.transition = 'opacity 0.5s';
            alert.style.opacity = '0';
            setTimeout(() => alert.remove(), 500);
        });
    }, 4000);

    console.log("✅ All scripts initialized successfully");
});

// Keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K = Focus search (if exists)
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const searchInput = document.getElementById('searchInput');
        if (searchInput) searchInput.focus();
    }
});

// DARK MODE TOGGLE

const themeToggle = document.getElementById("themeToggle");

// Load saved theme
if (localStorage.getItem("theme") === "dark") {

    document.body.classList.add("dark-mode");

    if (themeToggle) {
        themeToggle.innerText = "☀ Light Mode";
    }
}

if (themeToggle) {

    themeToggle.addEventListener("click", () => {

        document.body.classList.toggle("dark-mode");

        const isDark =
            document.body.classList.contains("dark-mode");

        localStorage.setItem(
            "theme",
            isDark ? "dark" : "light"
        );

        themeToggle.innerText =
            isDark
                ? "☀ Light Mode"
                : "🌙 Dark Mode";
    });
}