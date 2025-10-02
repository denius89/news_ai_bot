// PulseAI WebApp JavaScript
document.addEventListener('DOMContentLoaded', function() {
    console.log("WebApp JS loaded");
    
    // Get all tab buttons and content sections
    const tabButtons = document.querySelectorAll('.webapp-nav .nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
    // Function to update icon colors
    function updateIconColors() {
        tabButtons.forEach(btn => {
            const svg = btn.querySelector('svg');
            if (svg) {
                if (btn.classList.contains('active')) {
                    svg.setAttribute('stroke', '#2E5BFF');
                } else {
                    svg.setAttribute('stroke', '#6b7280');
                }
            }
        });
    }
    
    // Function to switch tabs
    function switchTab(targetTab) {
        // Remove active class from all buttons and contents
        tabButtons.forEach(btn => btn.classList.remove('active'));
        tabContents.forEach(content => content.classList.remove('active'));
        
        // Add active class to clicked button
        const activeButton = document.querySelector(`[data-tab="${targetTab}"]`);
        if (activeButton) {
            activeButton.classList.add('active');
        }
        
        // Show corresponding content
        const activeContent = document.getElementById(targetTab);
        if (activeContent) {
            activeContent.classList.add('active');
        }
        
        // Update icon colors
        updateIconColors();
        
        // Update URL hash without scrolling
        history.replaceState(null, null, `#${targetTab}`);
    }
    
    // Add click event listeners to tab buttons
    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');
            switchTab(targetTab);
        });
    });
    
    // Handle initial load and URL hash
    function initializeTab() {
        const hash = window.location.hash.substring(1);
        const validTabs = ['subscriptions', 'notifications', 'calendar'];
        
        if (hash && validTabs.includes(hash)) {
            switchTab(hash);
        } else {
            // Default to subscriptions
            switchTab('subscriptions');
        }
    }
    
    // Initialize Lucide icons first
    if (typeof lucide !== 'undefined' && lucide.createIcons) {
        lucide.createIcons();
        console.log('Lucide icons initialized');
        
        // Small delay to ensure icons are rendered before initializing tabs
        setTimeout(() => {
            initializeTab();
            updateIconColors();
        }, 100);
    } else {
        // Fallback if Lucide is not available
        initializeTab();
    }
    
    // Handle browser back/forward buttons
    window.addEventListener('hashchange', initializeTab);
    
    console.log('PulseAI WebApp initialized');
});
