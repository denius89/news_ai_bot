/**
 * WebApp debug JavaScript - вынесено из inline JS
 */

console.log('🔧 WebApp HTML loaded');
console.log('🔧 toggleSubscription function exists:', typeof window.toggleSubscription);
console.log('🔧 renderSubscriptions function exists:', typeof window.renderSubscriptions);
console.log('🔧 switchTab function exists:', typeof window.switchTab);

// Test if we can find subscription elements
setTimeout(() => {
    const subscriptionList = document.getElementById('subscription-list');
    console.log('🔧 subscription-list element found:', !!subscriptionList);
    if (subscriptionList) {
        console.log('🔧 subscription-list innerHTML length:', subscriptionList.innerHTML.length);
    }
}, 1000);
