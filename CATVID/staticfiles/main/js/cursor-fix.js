// Dynamic cursor fix script
(function() {
    'use strict';
    
    let isFixed = false;
    
    function fixCursorIssues() {
        if (isFixed) return;
        
        const clickButton = document.getElementById('click-button');
        if (clickButton) {
            // Force pointer cursor on everything
            clickButton.style.setProperty('cursor', 'pointer', 'important');
            
            // Fix all elements inside
            const allElements = clickButton.querySelectorAll('*');
            allElements.forEach(el => {
                el.style.setProperty('cursor', 'pointer', 'important');
                el.style.setProperty('pointer-events', 'none', 'important');
            });
            
            isFixed = true;
            console.log('✅ Click button cursor fixed');
        }
    }
    
    // Run once when ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', fixCursorIssues);
    } else {
        fixCursorIssues();
    }
    
    // Run once more after delay
    setTimeout(fixCursorIssues, 1000);
    
})();