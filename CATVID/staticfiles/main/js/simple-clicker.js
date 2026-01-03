// Simple clicker functionality
(function() {
    'use strict';
    
    function initClicker() {
        const clickButton = document.getElementById('click-button');
        if (!clickButton) return;
        
        // Fix cursor
        clickButton.style.cursor = 'pointer';
        const children = clickButton.querySelectorAll('*');
        children.forEach(child => {
            child.style.cursor = 'pointer';
            child.style.pointerEvents = 'none';
        });
        
        // Add click handler
        clickButton.addEventListener('click', function(e) {
            e.preventDefault();
            
            // Visual feedback
            this.style.transform = 'scale(0.95)';
            setTimeout(() => {
                this.style.transform = 'scale(1)';
            }, 100);
            
            console.log('Click registered!');
            
            // Try to call existing click handler if available
            if (window.handleClick) {
                window.handleClick();
            }
        });
        
        console.log('✅ Clicker initialized');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initClicker);
    } else {
        initClicker();
    }
})();