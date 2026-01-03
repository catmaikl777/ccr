// Simple audio initialization
(function() {
    'use strict';
    
    console.log('🎵 Audio init script loaded');
    
    function initAudio(event) {
        console.log('🎵 User clicked, initializing audio...');
        
        if (typeof EnhancedAudioManager !== 'undefined' && !window.audioManager) {
            try {
                window.audioManager = new EnhancedAudioManager();
                console.log('✅ Audio manager created successfully');
                
                // Тестовый звук сразу после создания
                setTimeout(() => {
                    if (window.audioManager) {
                        console.log('🎵 Playing test click sound...');
                        window.audioManager.playRandomSound('click');
                    }
                }, 100);
                
            } catch (error) {
                console.error('❌ Audio manager creation failed:', error);
            }
        } else if (window.audioManager) {
            console.log('🎵 Audio manager already exists, playing test sound...');
            window.audioManager.playRandomSound('click');
        } else {
            console.warn('⚠️ EnhancedAudioManager not available');
        }
    }
    
    // Инициализация аудио при первом клике
    document.addEventListener('click', initAudio, { once: true });
    document.addEventListener('touchstart', initAudio, { once: true });
    
    // Также пробуем инициализировать при загрузке DOM
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🎵 DOM loaded, checking audio manager...');
        
        // Проверяем доступность аудио-менеджера
        if (typeof EnhancedAudioManager !== 'undefined') {
            console.log('✅ EnhancedAudioManager is available');
        } else {
            console.warn('⚠️ EnhancedAudioManager not loaded yet');
        }
    });
    
})();