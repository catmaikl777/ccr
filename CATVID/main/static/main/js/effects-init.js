// Simple initialization script to ensure proper loading order
(function() {
    'use strict';
    
    // Wait for DOM to be ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initializeEffects);
    } else {
        initializeEffects();
    }
    
    function initializeEffects() {
        console.log('🎮 Initializing game effects...');
        
        // Initialize audio manager
        if (typeof EnhancedAudioManager !== 'undefined' && !window.audioManager) {
            try {
                window.audioManager = new EnhancedAudioManager();
                console.log('✅ Audio manager initialized');
            } catch (error) {
                console.warn('⚠️ Audio manager failed to initialize:', error);
            }
        }
        
        // Initialize game effects
        if (typeof GameEffects !== 'undefined') {
            try {
                GameEffects.init();
                console.log('✅ Game effects initialized');
            } catch (error) {
                console.warn('⚠️ Game effects failed to initialize:', error);
            }
        }
        
        // Initialize confetti effects
        if (typeof ConfettiEffects !== 'undefined' && !window.confettiEffects) {
            try {
                window.confettiEffects = new ConfettiEffects();
                console.log('✅ Confetti effects initialized');
            } catch (error) {
                console.warn('⚠️ Confetti effects failed to initialize:', error);
            }
        }
        
        // Fix cursor issues
        fixCursorIssues();
        
        console.log('🚀 All effects initialized successfully!');
    }
    
    function fixCursorIssues() {
        // Ensure click button always has pointer cursor
        const clickButton = document.getElementById('click-button');
        if (clickButton) {
            clickButton.style.cursor = 'pointer';
            
            // Fix all children elements
            const children = clickButton.querySelectorAll('*');
            children.forEach(child => {
                child.style.cursor = 'pointer';
                child.style.pointerEvents = 'none';
            });
            
            console.log('✅ Cursor issues fixed');
        }
    }
    
    // Global error handler for missing dependencies
    window.addEventListener('error', function(e) {
        if (e.message.includes('is not defined')) {
            console.warn('⚠️ Missing dependency:', e.message);
        }
    });
    
})();