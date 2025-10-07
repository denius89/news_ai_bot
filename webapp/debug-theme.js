// Debug script for theme testing
console.log('🔍 Debugging theme system...');

// Check if theme utility is loaded
if (typeof window !== 'undefined') {
  console.log('✅ Window object available');
  
  // Check localStorage
  const storedTheme = localStorage.getItem('pulseai-theme');
  console.log('📦 Stored theme:', storedTheme);
  
  // Check current HTML class
  const htmlClass = document.documentElement.className;
  console.log('🏷️ HTML class:', htmlClass);
  
  // Check CSS variables
  const rootStyles = getComputedStyle(document.documentElement);
  const bgColor = rootStyles.getPropertyValue('--color-bg');
  const textColor = rootStyles.getPropertyValue('--color-text');
  console.log('🎨 CSS Variables:');
  console.log('  --color-bg:', bgColor);
  console.log('  --color-text:', textColor);
  
  // Test theme toggle
  function testThemeToggle() {
    console.log('🔄 Testing theme toggle...');
    
    // Simulate theme toggle
    const currentTheme = document.documentElement.classList.contains('dark') ? 'dark' : 'light';
    console.log('Current theme:', currentTheme);
    
    // Toggle
    if (currentTheme === 'light') {
      document.documentElement.classList.remove('light');
      document.documentElement.classList.add('dark');
    } else {
      document.documentElement.classList.remove('dark');
      document.documentElement.classList.add('light');
    }
    
    // Check new values
    const newBgColor = getComputedStyle(document.documentElement).getPropertyValue('--color-bg');
    const newTextColor = getComputedStyle(document.documentElement).getPropertyValue('--color-text');
    console.log('New values:');
    console.log('  --color-bg:', newBgColor);
    console.log('  --color-text:', newTextColor);
  }
  
  // Expose test function
  window.testThemeToggle = testThemeToggle;
  console.log('🧪 Run testThemeToggle() to test theme switching');
}

// Check if React app is loaded
if (typeof React !== 'undefined') {
  console.log('⚛️ React is available');
} else {
  console.log('❌ React not found');
}

// Check if theme utility functions exist
if (typeof window !== 'undefined' && window.PulseAI && window.PulseAI.theme) {
  console.log('🎯 PulseAI theme utility available');
  console.log('Current theme:', window.PulseAI.theme.get());
} else {
  console.log('❌ PulseAI theme utility not found');
}
