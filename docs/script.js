// NthLayer Demo Site JavaScript

// Smooth scroll for anchor links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Add fade-in animation on scroll
const observerOptions = {
    threshold: 0.1,
    rootMargin: '0px 0px -50px 0px'
};

const observer = new IntersectionObserver((entries) => {
    entries.forEach(entry => {
        if (entry.isIntersecting) {
            entry.target.style.opacity = '1';
            entry.target.style.transform = 'translateY(0)';
        }
    });
}, observerOptions);

// Observe all steps
document.querySelectorAll('.step').forEach(step => {
    step.style.opacity = '0';
    step.style.transform = 'translateY(20px)';
    step.style.transition = 'opacity 0.6s ease, transform 0.6s ease';
    observer.observe(step);
});

// Add active state to nav links
window.addEventListener('scroll', () => {
    const sections = document.querySelectorAll('section[id]');
    const scrollPosition = window.scrollY + 100;

    sections.forEach(section => {
        const sectionTop = section.offsetTop;
        const sectionHeight = section.offsetHeight;
        const sectionId = section.getAttribute('id');
        
        if (scrollPosition >= sectionTop && scrollPosition < sectionTop + sectionHeight) {
            document.querySelectorAll('.nav-links a').forEach(link => {
                link.classList.remove('active');
                if (link.getAttribute('href') === `#${sectionId}`) {
                    link.classList.add('active');
                }
            });
        }
    });
});

// Dashboard tab switching
const dashboardUrls = {
    'payment-api': 'https://nthlayer.grafana.net/public-dashboards/b85f7be155184779ad4200b20f0411b4',
    'checkout-service': 'https://nthlayer.grafana.net/public-dashboards/64b290b48321499c885998958eec7c87',
    'notification-worker': 'https://nthlayer.grafana.net/public-dashboards/cfe879ff590141279b6ab570fc2aaab0',
    'analytics-stream': 'https://nthlayer.grafana.net/public-dashboards/c20f9658441c47358127b6dae28663b5',
    'identity-service': 'https://nthlayer.grafana.net/public-dashboards/c20f9658441c47358127b6dae28663b5',
    'search-api': 'https://nthlayer.grafana.net/public-dashboards/20afe15ca3f24da98025abf093ae96f4'
};

document.querySelectorAll('.dashboard-tab').forEach(tab => {
    tab.addEventListener('click', function() {
        const dashboardId = this.getAttribute('data-dashboard');
        const iframe = document.getElementById('dashboard-iframe');
        const overlay = document.querySelector('.dashboard-overlay a');
        
        // Update active tab
        document.querySelectorAll('.dashboard-tab').forEach(t => t.classList.remove('active'));
        this.classList.add('active');
        
        // Update iframe source
        if (iframe && dashboardUrls[dashboardId]) {
            iframe.src = dashboardUrls[dashboardId];
            if (overlay) {
                overlay.href = dashboardUrls[dashboardId];
            }
        }
    });
});

// Log demo page load (for analytics)
console.log('🚀 NthLayer Demo Site Loaded');
console.log('📊 GitHub: https://github.com/rsionnach/nthlayer');
