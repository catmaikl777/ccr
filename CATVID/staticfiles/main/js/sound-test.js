// Простой тест звуков
(function() {
    'use strict';
    
    console.log('🎵 Sound test script loaded');
    
    // Функция для тестирования звуков
    window.testSounds = function() {
        console.log('🎵 Testing sounds...');
        
        if (!window.audioManager) {
            console.warn('⚠️ Audio manager not found, creating...');
            if (typeof EnhancedAudioManager !== 'undefined') {
                window.audioManager = new EnhancedAudioManager();
            } else {
                console.error('❌ EnhancedAudioManager class not available');
                return;
            }
        }
        
        // Тестируем разные звуки
        setTimeout(() => {
            console.log('🎵 Testing click sound...');
            window.audioManager.playRandomSound('click');
        }, 500);
        
        setTimeout(() => {
            console.log('🎵 Testing critical sound...');
            window.audioManager.playSound('critical', 0);
        }, 1500);
        
        setTimeout(() => {
            console.log('🎵 Testing upgrade sound...');
            window.audioManager.playSound('upgrade', 0);
        }, 2500);
    };
    
    // Функция для проверки доступности файлов
    window.checkSoundFiles = function() {
        const sounds = [
            '/static/main/sounds/click.mp3',
            '/static/main/sounds/meow1.mp3',
            '/static/main/sounds/meow2.mp3',
            '/static/main/sounds/meow3.mp3',
            '/static/main/sounds/bg.mp3'
        ];
        
        console.log('🎵 Checking sound files...');
        
        sounds.forEach(soundUrl => {
            const audio = new Audio(soundUrl);
            audio.addEventListener('canplaythrough', () => {
                console.log('✅ Sound file loaded:', soundUrl);
            });
            audio.addEventListener('error', (e) => {
                console.error('❌ Sound file failed to load:', soundUrl, e);
            });
            audio.load();
        });
    };
    
    // Автоматически проверяем файлы при загрузке
    document.addEventListener('DOMContentLoaded', function() {
        console.log('🎵 DOM loaded, checking sound files...');
        window.checkSoundFiles();
        
        // Добавляем кнопку тестирования в консоль
        console.log('🎵 Use window.testSounds() to test audio');
        console.log('🎵 Use window.checkSoundFiles() to check file availability');
    });
    
})();