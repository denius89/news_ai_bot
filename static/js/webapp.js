// PulseAI WebApp JavaScript

// Icon mapping for categories and subcategories
const iconMap = {
    // Crypto
    'bitcoin': 'bitcoin',  // Will use crypto icon
    'ethereum': 'ethereum',  // Will use crypto icon
    'altcoins': 'coins',
    'defi': 'trending-up',
    'nft': 'layers',
    'gamefi': 'gamepad-2',
    'exchanges': 'building-2',
    'regulation': 'shield',
    'security': 'shield-check',
    'market_trends': 'trending-up',
    
    // Sports
    'football': 'trophy',
    'basketball': 'trophy',
    'tennis': 'trophy',
    'ufc_mma': 'zap',
    'cricket': 'trophy',
    'baseball': 'trophy',
    'badminton': 'trophy',
    'table_tennis': 'trophy',
    'esports': 'gamepad-2',
    'other': 'trophy',
    
    // Markets
    'stocks': 'trending-up',
    'commodities': 'package',
    'forex': 'refresh-cw',
    'bonds': 'receipt',
    'central_banks': 'building',
    'ipos': 'rocket',
    'earnings': 'dollar-sign',
    'economic_data': 'bar-chart-3',
    'funds_etfs': 'package',
    'trends': 'trending-up',
    
    // Tech
    'ai': 'brain',
    'bigtech': 'cpu',
    'startups': 'rocket',
    'hardware': 'cpu',
    'software': 'code',
    'cybersecurity': 'shield',
    'gadgets': 'smartphone',
    'blockchain_tech': 'link',
    'conferences': 'users',
    'space_robotics': 'rocket',
    
    // World
    'elections': 'vote',
    'geopolitics': 'globe',
    'conflicts': 'alert-triangle',
    'energy': 'zap',
    'climate': 'leaf',
    'diplomacy': 'handshake',
    'organizations': 'building',
    'sanctions': 'shield-x',
    'migration': 'users',
    'global_risks': 'alert-circle'
};

// Function to create icon (crypto or Lucide)
function createIcon(iconKey, className = 'w-5 h-5') {
    // Crypto icons mapping
    const cryptoIconMap = {
        'btc': 'bitcoin',
        'eth': 'ethereum',
        'bitcoin': 'bitcoin',
        'ethereum': 'ethereum'
    };
    
    if (cryptoIconMap[iconKey.toLowerCase()]) {
        // Use crypto icons for specific cryptocurrencies
        const cryptoIconName = cryptoIconMap[iconKey.toLowerCase()];
        return `<img src="https://cryptocurrency-icons.s3.us-east-2.amazonaws.com/32/color/${cryptoIconName}.png" 
                     alt="${iconKey}" class="${className} rounded-full" 
                     onerror="this.style.display='none'; this.nextElementSibling.style.display='inline';">
                <i data-lucide="coins" class="${className}" style="display:none;"></i>`;
    } else {
        // Use Lucide icons for everything else
        const iconName = iconMap[iconKey] || 'activity';
        return `<i data-lucide="${iconName}" class="${className}"></i>`;
    }
}

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
        console.log('🔧 switchTab called with:', targetTab);
        
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
        
        // Load data when switching to specific tabs
        if (targetTab === 'subscriptions') {
            console.log('🔧 Calling renderSubscriptions...');
            // Subscriptions are already loaded with mock data
            renderSubscriptions();
        } else if (targetTab === 'notifications') {
            // Load notifications from API
            loadNotifications();
        }
        
        // Update icon colors
        updateIconColors();
        
        // Update URL hash without scrolling
        history.replaceState(null, null, `#${targetTab}`);
    }
    
    // Export switchTab to global scope
    window.switchTab = switchTab;
    
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
    
    // Initialize categories loading
    loadCategories().then(() => {
        console.log('✅ Categories loaded, WebApp ready');
    }).catch(error => {
        console.error('❌ Failed to load categories:', error);
    });
    
    // === SUBSCRIPTIONS FUNCTIONALITY ===
    
    // Categories data
    // Categories will be loaded dynamically from API
    let categories = [];
    let categoriesData = {};
    let expandedCategories = new Set(); // Track which categories are expanded
    
    // Load user subscriptions (mock data for now)
    let userSubscriptions = ['crypto', 'economy']; // Default subscriptions

    // Load categories from API
    async function loadCategories() {
        try {
            console.log('🔄 Loading categories from API...');
            const response = await fetch('/api/categories');
            const data = await response.json();
            
            if (data.status === 'success') {
                categoriesData = data.data;
                console.log('✅ API categories data loaded:', Object.keys(categoriesData));
                
                // Convert to legacy format for compatibility
                categories = Object.entries(categoriesData).map(([id, categoryData]) => ({
                    id: id,
                    name: `${categoryData.emoji} ${categoryData.name}`,
                    description: `${categoryData.name} news and updates`
                }));
                
                console.log('✅ Categories loaded:', categories.length);
                return true;
            } else {
                throw new Error(data.message || 'Failed to load categories');
            }
        } catch (error) {
            console.error('❌ Error loading categories:', error);
            
            // Fallback to hardcoded categories
            categories = [
                {
                    id: 'crypto',
                    name: '📊 Crypto',
                    description: 'Latest cryptocurrency news and market updates'
                },
                {
                    id: 'economy',
                    name: '💰 Economy',
                    description: 'Economic analysis and financial market insights'
                },
                {
                    id: 'world',
                    name: '🌍 World',
                    description: 'Global news and international developments'
                },
                {
                    id: 'technology',
                    name: '⚙️ Technology',
                    description: 'Technology innovations and industry updates'
                },
                {
                    id: 'politics',
                    name: '🏛️ Politics',
                    description: 'Political news and government developments'
                }
            ];
            
            console.log('⚠️ Using fallback categories');
            return false;
        }
    }
    
    // Render subscriptions
    function renderSubscriptions() {
        console.log('🔧 renderSubscriptions called');
        console.log('🔧 categoriesData keys:', Object.keys(categoriesData));
        console.log('🔧 categories length:', categories.length);
        const subscriptionList = document.getElementById('subscription-list');
        if (!subscriptionList) {
            console.log('⚠️ subscription-list element not found');
            return;
        }
        console.log('✅ subscription-list found, rendering...');
        
        if (Object.keys(categoriesData).length === 0) {
            // Fallback to simple categories if no API data
            subscriptionList.innerHTML = categories.map(category => {
                const isSubscribed = userSubscriptions.includes(category.id);
                return `
                    <div class="subscription-card ${isSubscribed ? 'active' : ''}" data-category="${category.id}">
                        <div class="category-info">
                            <div class="category-name">${category.name}</div>
                            <div class="category-description">${category.description}</div>
                        </div>
                        <div class="category-toggle">
                            <input type="checkbox" ${isSubscribed ? 'checked' : ''} 
                                   onchange="toggleSubscription('${category.id}', this.checked)">
                            <span class="category-toggle-slider"></span>
                        </div>
                    </div>
                    `;
            }).join('');
            return;
        }

        // Render with subcategories
        subscriptionList.innerHTML = Object.entries(categoriesData).map(([categoryId, categoryData]) => {
            const isCategorySubscribed = userSubscriptions.includes(categoryId);
            const subcategories = Object.entries(categoryData.subcategories || {});
            
            return `
                <div class="subscription-category-group">
                    <div class="category-header" onclick="toggleCategoryExpansion('${categoryId}')">
                        <div class="category-info">
                            <div class="category-name">
                                <span class="expand-icon">▶</span>
                                ${createIcon(categoryId)} ${categoryData.name}
                            </div>
                            <div class="category-description">${categoryData.name} news and updates</div>
                        </div>
                        <div class="category-toggle" onclick="event.stopPropagation()">
                            <input type="checkbox" ${isCategorySubscribed ? 'checked' : ''}
                                   onchange="toggleCategorySubscription('${categoryId}', this.checked)">
                            <span class="category-toggle-slider"></span>
                        </div>
                    </div>
                    
                    ${subcategories.length > 0 ? `
                        <div class="subcategories" id="subcategories-${categoryId}">
                            ${subcategories.map(([subcategoryId, subcategoryData]) => {
                                const isSubscribed = userSubscriptions.includes(`${categoryId}:${subcategoryId}`);
                                return `
                                    <div class="subscription-card subcategory-card ${isSubscribed ? 'active' : ''}" 
                                         data-category="${categoryId}:${subcategoryId}">
                                        <div class="category-info">
                                            <div class="category-name">${createIcon(subcategoryId)} ${subcategoryData.name}</div>
                                            <div class="category-description">${subcategoryData.sources_count} sources</div>
                                        </div>
                                        <div class="category-toggle">
                                            <input type="checkbox" ${isSubscribed ? 'checked' : ''}
                                                   onchange="toggleSubscription('${categoryId}:${subcategoryId}', this.checked)">
                                            <span class="category-toggle-slider"></span>
                                        </div>
                                    </div>
                                `;
                            }).join('')}
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
        
        // Apply expansion state after rendering
        setTimeout(() => {
            Object.keys(categoriesData).forEach(categoryId => {
                const subcategoriesElement = document.getElementById(`subcategories-${categoryId}`);
                const expandIcon = document.querySelector(`[onclick="toggleCategoryExpansion('${categoryId}')"] .expand-icon`);
                
                if (subcategoriesElement && expandIcon) {
                    if (expandedCategories.has(categoryId)) {
                        subcategoriesElement.classList.add('expanded');
                        expandIcon.textContent = '▼';
                    } else {
                        subcategoriesElement.classList.remove('expanded');
                        expandIcon.textContent = '▶';
                    }
                }
            });
        }, 0);
        
        // Initialize Lucide icons after rendering
        if (typeof lucide !== 'undefined' && lucide.createIcons) {
            lucide.createIcons();
        }
    }
    
    // Toggle category subscription (all subcategories)
    window.toggleCategorySubscription = function(categoryId, isSubscribed) {
        const categoryData = categoriesData[categoryId];
        if (!categoryData) return;
        
        // Add/remove the main category itself
        if (isSubscribed) {
            if (!userSubscriptions.includes(categoryId)) {
                userSubscriptions.push(categoryId);
            }
        } else {
            const index = userSubscriptions.indexOf(categoryId);
            if (index > -1) {
                userSubscriptions.splice(index, 1);
            }
        }
        
        // Also handle subcategories if they exist
        if (categoryData.subcategories) {
            Object.keys(categoryData.subcategories).forEach(subcategoryId => {
                const fullId = `${categoryId}:${subcategoryId}`;
                if (isSubscribed) {
                    if (!userSubscriptions.includes(fullId)) {
                        userSubscriptions.push(fullId);
                    }
                } else {
                    const index = userSubscriptions.indexOf(fullId);
                    if (index > -1) {
                        userSubscriptions.splice(index, 1);
                    }
                }
            });
        }
        
        renderSubscriptions();
        updateSubscriptionStats();
    };

    // Update subscription statistics
    function updateSubscriptionStats() {
        const totalSubscriptions = userSubscriptions.length;
        console.log('📊 Updated subscription stats:', { total: totalSubscriptions, subscriptions: userSubscriptions });
        
        // Update any subscription counters in UI if they exist
        const subscriptionCounter = document.getElementById('subscription-counter');
        if (subscriptionCounter) {
            subscriptionCounter.textContent = totalSubscriptions;
        }
        
        // Update any subscription badges if they exist
        const subscriptionBadge = document.getElementById('subscription-badge');
        if (subscriptionBadge) {
            subscriptionBadge.textContent = totalSubscriptions;
            subscriptionBadge.style.display = totalSubscriptions > 0 ? 'block' : 'none';
        }
    }

    // Toggle category expansion/collapse
    window.toggleCategoryExpansion = function(categoryId) {
        const subcategoriesElement = document.getElementById(`subcategories-${categoryId}`);
        const expandIcon = document.querySelector(`[onclick="toggleCategoryExpansion('${categoryId}')"] .expand-icon`);
        
        if (!subcategoriesElement) return;
        
        if (expandedCategories.has(categoryId)) {
            // Collapse
            expandedCategories.delete(categoryId);
            subcategoriesElement.classList.remove('expanded');
            if (expandIcon) expandIcon.textContent = '▶';
        } else {
            // Expand
            expandedCategories.add(categoryId);
            subcategoriesElement.classList.add('expanded');
            if (expandIcon) expandIcon.textContent = '▼';
        }
    };

    // Export renderSubscriptions to global scope
    window.renderSubscriptions = renderSubscriptions;
    
    // Global state for loading and success indicators
    let savingSubscription = false;
    let saveSuccessTimeout = null;
    
    // Toggle subscription with API call and UX feedback
    window.toggleSubscription = async function(categoryId, isSubscribed) {
        console.log('🔧 toggleSubscription called:', { categoryId, isSubscribed, savingSubscription });
        
        if (savingSubscription) {
            console.log('⚠️ Already saving, ignoring request');
            return; // Prevent multiple simultaneous calls
        }
        
        console.log(`✅ Toggling subscription for ${categoryId}: ${isSubscribed}`);
        
        // Show loading state
        setSavingState(true);
        
        // Optimistic UI update
        const originalState = userSubscriptions.includes(categoryId);
        if (isSubscribed) {
            if (!userSubscriptions.includes(categoryId)) {
                userSubscriptions.push(categoryId);
            }
                } else {
            userSubscriptions = userSubscriptions.filter(id => id !== categoryId);
        }
        
        // Update UI immediately
        updateSubscriptionCard(categoryId, isSubscribed);
        
        try {
            // Make API call
            const response = await fetch('/api/subscriptions/update', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    user_id: 'demo-user-12345', // Demo user ID
                    category: categoryId,
                    enabled: isSubscribed
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const result = await response.json();
            console.log('Subscription updated:', result);
            
            // Show success state
            showSaveSuccess();
            
        } catch (error) {
            console.error('Error updating subscription:', error);
            
            // Revert optimistic update
            if (originalState) {
                if (!userSubscriptions.includes(categoryId)) {
                    userSubscriptions.push(categoryId);
                }
            } else {
                userSubscriptions = userSubscriptions.filter(id => id !== categoryId);
            }
            updateSubscriptionCard(categoryId, originalState);
            
            // Show error state
            showSaveError(error.message);
        } finally {
            // Hide loading state
            setSavingState(false);
            // Update subscription statistics
            updateSubscriptionStats();
        }
    };
    
    // Update subscription card UI
    function updateSubscriptionCard(categoryId, isSubscribed) {
        const card = document.querySelector(`[data-category="${categoryId}"]`);
        if (card) {
            if (isSubscribed) {
                card.classList.add('active');
            } else {
                card.classList.remove('active');
            }
        }
    }
    
    // Show loading state
    function setSavingState(isLoading) {
        savingSubscription = isLoading;
        const subscriptionCards = document.querySelectorAll('.subscription-card');
        
        subscriptionCards.forEach(card => {
            const toggle = card.querySelector('input[type="checkbox"]');
            if (toggle) {
                toggle.disabled = isLoading;
                card.style.opacity = isLoading ? '0.6' : '1';
            }
        });
        
        // Update save indicator
        updateSaveIndicator(isLoading ? 'loading' : 'none');
    }
    
    // Show success state
    function showSaveSuccess() {
        updateSaveIndicator('success');
        
        // Clear any existing timeout
        if (saveSuccessTimeout) {
            clearTimeout(saveSuccessTimeout);
        }
        
        // Hide success message after 3 seconds
        saveSuccessTimeout = setTimeout(() => {
            updateSaveIndicator('none');
        }, 3000);
    }
    
    // Show error state
    function showSaveError(message) {
        updateSaveIndicator('error', message);
        
        // Clear any existing timeout
        if (saveSuccessTimeout) {
            clearTimeout(saveSuccessTimeout);
        }
        
        // Hide error message after 5 seconds
        saveSuccessTimeout = setTimeout(() => {
            updateSaveIndicator('none');
        }, 5000);
    }
    
    // Update save indicator UI
    function updateSaveIndicator(state, message = '') {
        let indicator = document.getElementById('save-indicator');
        if (!indicator) {
            // Create indicator if it doesn't exist
            indicator = document.createElement('div');
            indicator.id = 'save-indicator';
            indicator.className = 'save-indicator';
            
            // Try to find subscriptions header, fallback to subscriptions section
            let targetElement = document.querySelector('#subscriptions .content-header');
            if (!targetElement) {
                targetElement = document.querySelector('#subscriptions');
            }
            
            if (targetElement) {
                targetElement.appendChild(indicator);
            } else {
                console.warn('Could not find subscriptions section to add save indicator');
                return;
            }
        }
        
        // Clear previous state
        indicator.className = 'save-indicator';
        indicator.textContent = '';
        indicator.style.display = 'block'; // Make sure it's visible
        
        switch (state) {
            case 'loading':
                indicator.className += ' loading';
                indicator.innerHTML = `
                    <div class="spinner"></div>
                    <span>Сохраняется...</span>
                `;
                break;
            case 'success':
                indicator.className += ' success';
                indicator.innerHTML = '✅ Сохранено';
                break;
            case 'error':
                indicator.className += ' error';
                indicator.innerHTML = `❌ Ошибка: ${message || 'Не удалось сохранить'}`;
                break;
            default:
                indicator.style.display = 'none';
        }
    }
    
    // === NOTIFICATIONS FUNCTIONALITY ===
    
    // Global state for notifications
    let notifications = [];
    let notificationsLoading = false;
    let notificationsError = null;
    
    // Notification settings
    let notificationSettings = {
        crypto: { enabled: true, telegram: true, webapp: true },
        economy: { enabled: true, telegram: true, webapp: true },
        world: { enabled: false, telegram: false, webapp: true },
        technology: { enabled: false, telegram: false, webapp: false },
        politics: { enabled: false, telegram: false, webapp: false }
    };
    
    // Load notifications from API
    async function loadNotifications() {
        notificationsLoading = true;
        notificationsError = null;
        renderNotifications(); // Show loading state
        
        try {
            const response = await fetch(`/api/user_notifications?user_id=demo-user-12345`);
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            const data = await response.json();
            notifications = data || [];
            
        } catch (error) {
            console.error('Error loading notifications:', error);
            notificationsError = error.message;
            
            // Fallback to mock data if API fails
            notifications = [
                {
                    id: 1,
                    title: 'New digest ready!',
                    message: 'Your morning digest with the latest crypto and economy news is ready to read.',
                    category: 'crypto',
                    read: false,
                    timestamp: new Date(Date.now() - 30 * 60 * 1000)
                },
                {
                    id: 2,
                    title: 'Important economic event',
                    message: 'Fed interest rate decision scheduled for today at 15:00 EST.',
                    category: 'economy',
                    read: false,
                    timestamp: new Date(Date.now() - 2 * 60 * 60 * 1000)
                },
                {
                    id: 3,
                    title: 'Bitcoin reaches new high',
                    message: 'Bitcoin has reached a new all-time high of $75,000.',
                    category: 'crypto',
                    read: true,
                    timestamp: new Date(Date.now() - 24 * 60 * 60 * 1000)
                }
            ];
        } finally {
            notificationsLoading = false;
            renderNotifications();
        }
    }
    
    // Mark notification as read
    async function markNotificationAsRead(notificationId) {
        const originalNotifications = [...notifications];
        
        // Optimistic update
        notifications = notifications.map(notification => 
            notification.id === notificationId 
                ? { ...notification, read: true }
                : notification
        );
        renderNotifications();
        
        try {
            const response = await fetch('/api/user_notifications/mark_read', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    notification_id: notificationId
                })
            });
            
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            
            console.log('Notification marked as read:', notificationId);
            
        } catch (error) {
            console.error('Error marking notification as read:', error);
            
            // Revert optimistic update
            notifications = originalNotifications;
            renderNotifications();
            
            // Show error message
            showNotificationError('Не удалось отметить как прочитанное');
        }
    }
    
    // Show notification error
    function showNotificationError(message) {
        const errorDiv = document.createElement('div');
        errorDiv.className = 'notification-error';
        errorDiv.innerHTML = `
            <div class="error-content">
                <span class="error-icon">⚠️</span>
                <span class="error-text">${message}</span>
            </div>
        `;
        
        const notificationsContainer = document.querySelector('#notifications .content');
        if (notificationsContainer) {
            notificationsContainer.insertBefore(errorDiv, notificationsContainer.firstChild);
            
            // Remove error after 5 seconds
            setTimeout(() => {
                if (errorDiv.parentNode) {
                    errorDiv.parentNode.removeChild(errorDiv);
                }
            }, 5000);
        }
    }
    
    // Render notifications with loading states
    function renderNotifications() {
        const unreadNotifications = document.getElementById('unread-notifications');
        const readNotifications = document.getElementById('read-notifications');
        const unreadBadge = document.getElementById('unread-badge');
        const navBadge = document.getElementById('nav-notification-badge');
        
        if (!unreadNotifications || !readNotifications) return;
        
        // Show loading state
        if (notificationsLoading) {
            unreadNotifications.innerHTML = `
                <div class="notification-loading">
                    <div class="loading-spinner"></div>
                    <span class="loading-text">Загрузка уведомлений...</span>
                </div>
            `;
            readNotifications.innerHTML = '';
            return;
        }
        
        // Show error state
        if (notificationsError) {
            unreadNotifications.innerHTML = `
                <div class="notification-error-state">
                    <div class="error-icon">⚠️</div>
                    <div class="error-message">Ошибка загрузки: ${notificationsError}</div>
                    <button class="retry-btn" onclick="loadNotifications()">Повторить</button>
                </div>
            `;
            readNotifications.innerHTML = '';
            return;
        }
        
        const unread = notifications.filter(n => !n.read);
        const read = notifications.filter(n => n.read);
        
        // Show empty state
        if (notifications.length === 0) {
            unreadNotifications.innerHTML = `
                <div class="notification-empty">
                    <div class="empty-icon">🔔</div>
                    <div class="empty-message">Пока нет уведомлений</div>
                    <div class="empty-subtitle">Ваши уведомления появятся здесь</div>
                </div>
            `;
            readNotifications.innerHTML = '';
            return;
        }
        
        // Render unread notifications
        unreadNotifications.innerHTML = unread.length > 0 ? unread.map(notification => `
            <div class="notification-item unread" data-id="${notification.id}">
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message || notification.text}</div>
                    <div class="notification-time">${formatTime(notification.timestamp || notification.created_at)}</div>
                </div>
                <div class="notification-actions">
                    <button class="mark-read-btn" onclick="markNotificationAsRead(${notification.id})" title="Отметить как прочитанное">
                        <span class="mark-read-icon">✓</span>
                    </button>
                </div>
            </div>
        `).join('') : '<div class="no-unread-notifications">Нет непрочитанных уведомлений</div>';
        
        // Render read notifications
        readNotifications.innerHTML = read.map(notification => `
            <div class="notification-item read" data-id="${notification.id}">
                <div class="notification-content">
                    <div class="notification-title">${notification.title}</div>
                    <div class="notification-message">${notification.message || notification.text}</div>
                    <div class="notification-time">${formatTime(notification.timestamp || notification.created_at)}</div>
                </div>
            </div>
        `).join('');
        
        // Update badges
        if (unreadBadge) unreadBadge.textContent = unread.length;
        if (navBadge) navBadge.textContent = unread.length;
    }
    
    // Render notification settings
    function renderNotificationSettings() {
        const settingsList = document.getElementById('notification-settings-list');
        if (!settingsList) return;
        
        // Use categoriesData if available, fallback to legacy categories
        const categoriesToRender = Object.keys(categoriesData).length > 0 ? 
            Object.entries(categoriesData).map(([id, data]) => ({
                id: id,
                name: `${data.emoji} ${data.name}`,
                description: `${data.name} news and updates`
            })) : categories;
        
        settingsList.innerHTML = categoriesToRender.map(category => {
            const settings = notificationSettings[category.id] || { enabled: false, telegram: false, webapp: false };
            return `
                <div class="notification-setting-card">
                    <div class="setting-header">
                        <div class="setting-title">${category.name}</div>
                        <div class="setting-description">${category.description}</div>
                    </div>
                    <div class="setting-options">
                        <div class="setting-option">
                            <label>
                                <span>Enable notifications</span>
                                <div class="setting-toggle">
                                    <input type="checkbox" ${settings.enabled ? 'checked' : ''} 
                                           onchange="updateNotificationSetting('${category.id}', 'enabled', this.checked)">
                                    <span class="setting-toggle-slider"></span>
                                </div>
                            </label>
                        </div>
                        <div class="setting-option ${!settings.enabled ? 'disabled' : ''}">
                            <label>
                                <span>Send to Telegram</span>
                                <div class="setting-toggle">
                                    <input type="checkbox" ${settings.telegram ? 'checked' : ''} 
                                           ${!settings.enabled ? 'disabled' : ''}
                                           onchange="updateNotificationSetting('${category.id}', 'telegram', this.checked)">
                                    <span class="setting-toggle-slider ${!settings.enabled ? 'disabled' : ''}"></span>
                                </div>
                            </label>
                        </div>
                        <div class="setting-option ${!settings.enabled ? 'disabled' : ''}">
                            <label>
                                <span>Show in WebApp</span>
                                <div class="setting-toggle">
                                    <input type="checkbox" ${settings.webapp ? 'checked' : ''} 
                                           ${!settings.enabled ? 'disabled' : ''}
                                           onchange="updateNotificationSetting('${category.id}', 'webapp', this.checked)">
                                    <span class="setting-toggle-slider ${!settings.enabled ? 'disabled' : ''}"></span>
                                </div>
                            </label>
                        </div>
                    </div>
                </div>
            `;
        }).join('');
    }
    
    // Mark notification as read
    window.markAsRead = function(notificationId) {
        const notification = notifications.find(n => n.id === notificationId);
        if (notification) {
            notification.read = true;
            renderNotifications();
        }
    };
    
    // Update notification setting
    window.updateNotificationSetting = function(categoryId, setting, value) {
        if (notificationSettings[categoryId]) {
            notificationSettings[categoryId][setting] = value;
            console.log(`Updated ${categoryId}.${setting} to ${value}`);
            
            // If main notification is disabled, disable other options
            if (setting === 'enabled' && !value) {
                notificationSettings[categoryId].telegram = false;
                notificationSettings[categoryId].webapp = false;
            }
            
            // Re-render settings to update disabled state
            renderNotificationSettings();
        }
    };
    
    // Handle notification mode switching (moved to DOMContentLoaded)
    function setupNotificationModeSwitching() {
        const notificationTabs = document.querySelectorAll('.tab-btn[data-mode]');
        notificationTabs.forEach(tab => {
            tab.addEventListener('click', function() {
                const mode = this.getAttribute('data-mode');
                
                // Update active tab
                notificationTabs.forEach(t => t.classList.remove('active'));
                this.classList.add('active');
                
                // Show/hide content
                const viewMode = document.getElementById('notifications-view');
                const settingsMode = document.getElementById('notifications-settings');
                
                if (mode === 'view') {
                    viewMode.classList.add('active');
                    settingsMode.classList.remove('active');
                } else if (mode === 'settings') {
                    viewMode.classList.remove('active');
                    settingsMode.classList.add('active');
                    renderNotificationSettings();
                }
            });
        });
    }
    
    // Format time
    function formatTime(timestamp) {
        const now = new Date();
        const diff = now - timestamp;
        const minutes = Math.floor(diff / (1000 * 60));
        const hours = Math.floor(diff / (1000 * 60 * 60));
        const days = Math.floor(diff / (1000 * 60 * 60 * 24));
        
        if (minutes < 60) {
            return `${minutes}m ago`;
        } else if (hours < 24) {
            return `${hours}h ago`;
        } else {
            return `${days}d ago`;
        }
    }
    
    // Enhanced tab switching
    const originalSwitchTab = switchTab;
    switchTab = function(targetTab) {
        originalSwitchTab(targetTab);
        
        // Load data when tabs are opened
        if (targetTab === 'subscriptions') {
            renderSubscriptions();
        } else if (targetTab === 'notifications') {
            renderNotifications();
            // Also ensure notification settings are rendered if in settings mode
            const settingsMode = document.getElementById('notifications-settings');
            if (settingsMode && settingsMode.classList.contains('active')) {
                renderNotificationSettings();
            }
        }
    };
    
    // Initialize data on first load
    setTimeout(() => {
        renderSubscriptions();
        renderNotifications();
        setupNotificationModeSwitching(); // Setup notification mode switching
    }, 200);
    
    console.log('PulseAI WebApp initialized');
});