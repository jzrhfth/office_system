document.addEventListener('DOMContentLoaded', function() {
    // Get current page filename from URL
    const currentPage = window.location.pathname.split("/").pop();
    
    const navItems = document.querySelectorAll('.sidebar .nav-item');
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.querySelector('.mobile-nav-toggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    // Function to open a submenu
    function openSubmenu(submenu) {
        if (submenu) {
            submenu.style.maxHeight = submenu.scrollHeight + "px";
        }
    }

    // Function to close a submenu
    function closeSubmenu(submenu) {
        if (submenu) {
            submenu.style.maxHeight = '0';
        }
    }

    // Set active state for the current page
    navItems.forEach(item => {
        const pages = item.getAttribute('data-page');
        if (pages && pages.split(' ').includes(currentPage)) {
            item.classList.add('active');
            // If the active item is in a submenu, also open the submenu
            if (item.closest('.submenu')) {
                const parentLi = item.closest('.has-submenu');
                if (parentLi) {
                    parentLi.classList.add('active');
                    openSubmenu(parentLi.querySelector('.submenu'));
                }
            } else if (item.classList.contains('has-submenu')) {
                openSubmenu(item.querySelector('.submenu'));
            }
        }
    });

    // Dropdown functionality
    const submenuLinks = document.querySelectorAll('.sidebar .nav-item.has-submenu > a');
    submenuLinks.forEach(link => {
        link.addEventListener('click', function(event) {
            event.preventDefault();
            const parentLi = this.closest('.has-submenu');
            parentLi.classList.toggle('active');
            
            // Ensure smooth transition by explicitly setting height
            const submenu = parentLi.querySelector('.submenu');
            if (parentLi.classList.contains('active')) {
                openSubmenu(submenu);
            } else {
                closeSubmenu(submenu);
            }
        });
    });

    // Sidebar toggle for mobile
    if (sidebarToggle) {
        sidebarToggle.addEventListener('click', function() {
            sidebar.classList.add('open');
            sidebarOverlay.classList.remove('d-none');
        });
    }

    // Close sidebar when overlay is clicked
    if (sidebarOverlay) {
        sidebarOverlay.addEventListener('click', function() {
            sidebar.classList.remove('open');
            this.classList.add('d-none');
        });
    }

    // Login Page Functionality
    const loginForm = document.getElementById('loginForm');
    const togglePassword = document.getElementById('togglePassword');
    const passwordInput = document.getElementById('password');

    // Form Validation
    if (loginForm) {
        loginForm.addEventListener('submit', (e) => {
            const username = document.getElementById('username').value.trim();
            const password = passwordInput.value.trim();

            if (!username || !password) {
                e.preventDefault();
                alert('Please enter both username and password.');
            }
        });
    }

    // Show/Hide Password Toggle
    if (togglePassword && passwordInput) {
        togglePassword.addEventListener('change', function() {
            passwordInput.type = this.checked ? 'text' : 'password';
        });
    }

    // Login Input Focus Effects
    const loginInputs = document.querySelectorAll('.login-card-container input[type="text"], .login-card-container input[type="password"]');
    loginInputs.forEach(input => {
        input.addEventListener('focus', function() {
            this.parentElement.style.transform = 'scale(1.02)';
        });

        input.addEventListener('blur', function() {
            this.parentElement.style.transform = 'scale(1)';
        });
    });

    // --- Notification Panel Logic ---
    const badge = document.getElementById('notificationBadge');
    
    if (badge) {
        function updateNotificationCount() {
            fetch('/api/pending_count')
                .then(response => response.json())
                .then(data => {
                    if (data.count > 0) {
                        badge.textContent = data.count > 99 ? '99+' : data.count;
                        badge.style.display = 'flex';
                    } else {
                        badge.style.display = 'none';
                    }
                })
                .catch(err => console.error('Error fetching notifications:', err));
        }

        updateNotificationCount();
        setInterval(updateNotificationCount, 15000);

        const notificationBtn = document.getElementById('notificationBtn');
        const notificationsPanel = document.getElementById('notificationsPanel');
        const notificationsList = document.getElementById('notificationsList');

        if (notificationBtn && notificationsPanel && notificationsList) {
            notificationBtn.addEventListener('click', function(event) {
                event.stopPropagation();
                const isActive = notificationsPanel.classList.toggle('active');
                if (isActive) {
                    loadNotifications();
                }
            });

            function loadNotifications() {
                notificationsList.innerHTML = '<p class="no-notifications">Loading...</p>';
                fetch('/api/notifications')
                    .then(response => response.json())
                    .then(data => {
                        renderNotifications(data);
                        setupTabs();
                        updateNotificationCount(); // Re-check count after viewing
                    })
                    .catch(err => {
                        console.error('Error fetching notifications:', err);
                        notificationsList.innerHTML = '<p class="no-notifications">Could not load notifications.</p>';
                    });
            }

            function renderNotifications(notifications) {
                if (!notifications || notifications.length === 0) {
                    notificationsList.innerHTML = '<p class="no-notifications">You are all caught up!</p>';
                    return;
                }

                notificationsList.innerHTML = '';
                notifications.forEach(notif => {
                    const item = document.createElement('a');
                    item.href = notif.url;
                    item.className = 'notification-item';
                    if (notif.unread) {
                        item.classList.add('unread');
                    }
                    item.dataset.unread = notif.unread;

                    const avatarIcon = notif.unread ? 'fa-file-invoice' : 'fa-check';

                    item.innerHTML = `
                        <div class="avatar"><i class="fas ${avatarIcon}"></i></div>
                        <div class="notification-content">
                            <div class="notification-text">${notif.text}</div>
                            <div class="notification-time">${notif.time}</div>
                        </div>
                        ${notif.unread ? '<div class="unread-indicator"></div>' : ''}
                    `;
                    notificationsList.appendChild(item);
                });
            }

            function setupTabs() {
                const tabs = notificationsPanel.querySelectorAll('.tab');
                tabs.forEach(tab => {
                    tab.addEventListener('click', (e) => {
                        e.stopPropagation();
                        tabs.forEach(t => t.classList.remove('active'));
                        tab.classList.add('active');
                        const tabType = tab.dataset.tab;
                        const allItems = notificationsList.querySelectorAll('.notification-item');
                        allItems.forEach(item => {
                            item.style.display = (tabType === 'unread' && item.dataset.unread !== 'true') ? 'none' : 'flex';
                        });
                    });
                });
            }

            document.addEventListener('click', function(event) {
                if (!notificationsPanel.contains(event.target) && !notificationBtn.contains(event.target)) {
                    notificationsPanel.classList.remove('active');
                }
            });
        }
    }

    // --- Change Password Validation ---
    const changePasswordForm = document.getElementById('changePasswordForm');
    if (changePasswordForm) {
        changePasswordForm.addEventListener('submit', function(e) {
            const newPass = document.querySelector('input[name="new_password"]').value;
            const confirmPass = document.querySelector('input[name="confirm_password"]').value;

            if (newPass !== confirmPass) {
                e.preventDefault();
                alert('New passwords do not match!');
            }
        });
    }

    // --- Auto-dismiss Flash Messages ---
    const alerts = document.querySelectorAll('.alert');
    if (alerts.length > 0) {
        setTimeout(() => {
            alerts.forEach(alert => {
                alert.style.transition = 'opacity 0.5s ease';
                alert.style.opacity = '0';
                setTimeout(() => alert.remove(), 500);
            });
        }, 4000);
    }

    // --- Profile Form Validation ---
    const profileForm = document.querySelector('.profile-form');
    if (profileForm) {
        profileForm.addEventListener('submit', function(e) {
            const firstName = this.querySelector('input[name="first_name"]').value.trim();
            const lastName = this.querySelector('input[name="last_name"]').value.trim();
            
            if (!firstName || !lastName) {
                e.preventDefault();
                alert('First Name and Last Name are required.');
            }
        });
    }
});