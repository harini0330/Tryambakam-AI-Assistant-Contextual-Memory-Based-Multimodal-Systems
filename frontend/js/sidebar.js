document.addEventListener('DOMContentLoaded', function() {
    // Get the sidebar and toggle button
    const sidebar = document.querySelector('.sidebar');
    const toggleBtn = document.getElementById('sidebar-toggle');
    
    // Set active nav item based on current page
    const currentPath = window.location.pathname;
    const isHomePage = currentPath.endsWith('index.html') || currentPath.endsWith('/') || currentPath.endsWith('/frontend/');
    
    const navItems = document.querySelectorAll('.nav-menu a');
    
    navItems.forEach(item => {
        const href = item.getAttribute('href');
        
        // Handle home page special case
        if (isHomePage && item.id === 'nav-home') {
            item.classList.add('active');
        }
        // Handle other pages
        else if (!isHomePage) {
            const currentPage = currentPath.split('/').pop();
            if (href.endsWith(currentPage)) {
                item.classList.add('active');
            }
        }
    });
    
    // Toggle sidebar
    toggleBtn.addEventListener('click', function() {
        sidebar.classList.toggle('collapsed');
        
        // Save state to localStorage
        localStorage.setItem('sidebarCollapsed', sidebar.classList.contains('collapsed'));
    });
    
    // Check if sidebar was collapsed in previous session
    if (localStorage.getItem('sidebarCollapsed') === 'true') {
        sidebar.classList.add('collapsed');
    }
}); 