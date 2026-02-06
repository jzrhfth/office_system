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
});