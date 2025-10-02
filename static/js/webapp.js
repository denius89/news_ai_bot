// PulseAI WebApp JavaScript
document.addEventListener('DOMContentLoaded', function() {
    // Get all tab buttons and content sections
    const tabButtons = document.querySelectorAll('.webapp-nav .nav-btn');
    const tabContents = document.querySelectorAll('.tab-content');
    
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
    
    // Initialize on load
    initializeTab();
    
    // Handle browser back/forward buttons
    window.addEventListener('hashchange', initializeTab);
    
    // Add smooth transitions
    tabContents.forEach(content => {
        content.style.transition = 'opacity 0.3s ease-in-out';
    });
    
    console.log('PulseAI WebApp initialized');
});
