document.addEventListener('DOMContentLoaded', function() {
    // --- 0. Global Accent Color Theme ---
    const savedAccent = localStorage.getItem('accent-color') || 'yellow';
    if (savedAccent !== 'yellow') {
        document.body.classList.add(`theme-${savedAccent}`);
    }

    // Color picker settings
    const colorDots = document.querySelectorAll('.color-dot');
    if (colorDots.length > 0) {
        colorDots.forEach(dot => {
            if (dot.getAttribute('data-theme') === savedAccent) {
                dot.classList.add('active');
            }
            dot.addEventListener('click', function() {
                const theme = this.getAttribute('data-theme');
                document.body.classList.remove('theme-green', 'theme-blue', 'theme-purple');
                if (theme !== 'yellow') {
                    document.body.classList.add(`theme-${theme}`);
                }
                localStorage.setItem('accent-color', theme);
                colorDots.forEach(d => d.classList.remove('active'));
                this.classList.add('active');
            });
        });
    }

    // --- 1. Falling Coins Animation ---
    const path = window.location.pathname.replace(/\/$/, "").toLowerCase();
    const disabledPaths = [
        '/add-expense',
        '/manage-expense',
        '/expense-report',
        '/contact',
        '/user-dashboard',
        '/edit-profile',
        '/admin'
    ];

    if (!disabledPaths.includes(path) && !path.startsWith('/edit-expense')) {
        const coinsContainer = document.getElementById('coins-container') || (function() {
            const container = document.createElement('div');
            container.id = 'coins-container';
            document.body.appendChild(container);
            return container;
        })();

        const isMobile = window.innerWidth <= 768;
        const initialCoins = isMobile ? 3 : 8;
        const coinIntervalTime = isMobile ? 2400 : 800;

        function createCoin(isInitial = false) {
            const coinWrapper = document.createElement('div');
            coinWrapper.className = 'coin-wrapper';
            
            const coin = document.createElement('div');
            coin.className = 'coin';
            coinWrapper.appendChild(coin);
            
            // Random horizontal position
            const randomX = Math.random() * window.innerWidth;
            coinWrapper.style.left = randomX + 'px';
            coinWrapper.style.top = '-50px';
            
            // Random animation duration (4-8s for desktop, 8-15s for mobile to fall slower)
            const duration = isMobile ? (8 + Math.random() * 7) : (4 + Math.random() * 4);
            coinWrapper.style.animation = `fall ${duration}s linear forwards`;
            
            // If it's an initial coin, use a negative delay to make it start mid-fall
            // If not, use a positive delay for a natural sequence
            const delay = isInitial ? -(Math.random() * duration) : Math.random() * 2;
            coinWrapper.style.animationDelay = `${delay}s`;
            
            coinsContainer.appendChild(coinWrapper);
            
            // Remove coin after animation completes
            // For initial coins, we need to adjust the timeout
            const timeoutDuration = isInitial ? (duration + delay) : (duration + delay);
            setTimeout(() => {
                coinWrapper.remove();
            }, timeoutDuration * 1000);
        }

        // Initial burst to fill the screen immediately on page load
        // This makes the effect feel like it was already running
        for (let i = 0; i < initialCoins; i++) {
            createCoin(true);
        }

        // Continue creating coins at regular intervals
        const coinInterval = setInterval(() => createCoin(false), coinIntervalTime);

        // Stop creating new coins after 15 seconds
        setTimeout(() => {
            clearInterval(coinInterval);
            
            // Wait for remaining coins to finish falling before clearing (8s on desktop, 15s on mobile)
            const cleanupDelay = isMobile ? 15000 : 8000;
            setTimeout(() => {
                if (coinsContainer) {
                    coinsContainer.style.transition = 'opacity 2s ease';
                    coinsContainer.style.opacity = '0';
                    setTimeout(() => {
                        coinsContainer.innerHTML = '';
                        coinsContainer.style.opacity = '1';
                    }, 2000);
                }
            }, cleanupDelay); 
        }, 15000); 
    }

    // --- 2. Hamburger Menu Toggle ---
    const hamburger = document.getElementById('hamburger');
    const navLinks = document.querySelector('.nav-links');
    
    if (hamburger && navLinks) {
        hamburger.addEventListener('click', function() {
            hamburger.classList.toggle('active');
            navLinks.classList.toggle('active-menu');
            
            // Toggle visibility of mobile user link based on menu state
            const mobileUserLink = document.querySelector('.mobile-user-link');
            if (mobileUserLink) {
                if (hamburger.classList.contains('active')) {
                    mobileUserLink.classList.add('hidden-icon');
                } else {
                    mobileUserLink.classList.remove('hidden-icon');
                }
            }
        });

        // Close menu when a link is clicked
        const links = navLinks.querySelectorAll('a');
        links.forEach(link => {
            link.addEventListener('click', function() {
                hamburger.classList.remove('active');
                navLinks.classList.remove('active-menu');
                
                const mobileUserLink = document.querySelector('.mobile-user-link');
                if (mobileUserLink) {
                    mobileUserLink.classList.remove('hidden-icon');
                }
            });
        });
    }

    // --- 3. Logout functionality ---
    const logoutBtn = document.getElementById('logoutBtn');
    const logoutModal = document.getElementById('logoutModal');
    const cancelLogout = document.getElementById('cancelLogout');
    const confirmLogout = document.getElementById('confirmLogout');
    
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            if (logoutModal) {
                logoutModal.classList.add('show');
            } else {
                if (confirm('Are you sure you want to log out?')) {
                    window.location.href = '/logout';
                }
            }
        });
    }

    if (cancelLogout && logoutModal) {
        cancelLogout.addEventListener('click', function() {
            logoutModal.classList.remove('show');
        });
    }

    if (confirmLogout) {
        confirmLogout.addEventListener('click', function() {
            window.location.href = '/logout';
        });
    }

    // --- 4. Light/Dark Theme Toggle ---
    const navbar = document.querySelector('.navbar');
    const navLinksList = document.querySelector('.nav-links');
    
    if (navbar && navLinksList) {
        // Create the switch inside nav-links
        const toggleLi = document.createElement('li');
        toggleLi.className = 'theme-toggle-wrapper';
        toggleLi.innerHTML = `
            <label class="theme-switch">
                <input type="checkbox" id="themeToggleCheckbox">
                <span class="theme-slider"></span>
            </label>
        `;
        navLinksList.appendChild(toggleLi);

        const themeToggleCheckbox = document.getElementById('themeToggleCheckbox');

        // Apply saved theme
        const savedTheme = localStorage.getItem('theme') || 'light';
        if (savedTheme === 'dark') {
            document.body.classList.add('dark-mode');
            themeToggleCheckbox.checked = true;
        }

        // Handle click
        themeToggleCheckbox.addEventListener('change', (e) => {
            if (e.target.checked) {
                document.body.classList.add('dark-mode');
                localStorage.setItem('theme', 'dark');
            } else {
                document.body.classList.remove('dark-mode');
                localStorage.setItem('theme', 'light');
            }
        });
    }

    // --- 5. Auto-hide flash messages Modal ---
    const messageModal = document.getElementById('messageModal');
    if (messageModal) {
        // 'Welcome back' notification stays for 1 second. All other notifications stay for 2 seconds.
        const modalText = messageModal.textContent || '';
        const delay = modalText.includes('Welcome back') ? 1000 : 2000;

        setTimeout(() => {
            messageModal.style.transition = 'opacity 0.6s ease';
            messageModal.style.opacity = '0';
            setTimeout(() => {
                messageModal.classList.remove('show');
                messageModal.style.opacity = ''; // reset style
            }, 600);
        }, delay);
    }
});