// main/static/main/js/init.js
// Главный инициализационный скрипт

(function() {
    'use strict';

    // Флаги инициализации
    let audioManagerReady = false;
    let gameEffectsReady = false;

    // Функция проверки готовности всех компонентов
    function checkReadiness() {
        if (audioManagerReady && gameEffectsReady) {
            console.log('✅ All game systems initialized successfully!');
            
            // Уведомляем о готовности системы
            document.dispatchEvent(new CustomEvent('gameSystemsReady'));
            
            // Запускаем финальную инициализацию
            finalizeInitialization();
        }
    }

    // Финальная инициализация
    function finalizeInitialization() {
        // Создаем глобальные функции для обратной совместимости
        if (window.audioManager) {
            window.playClickSound = function(isCritical) {
                if (isCritical) {
                    window.audioManager.playRandomSound('critical');
                } else {
                    window.audioManager.playRandomSound('click');
                }
            };

            window.playUpgradeSound = function() {
                window.audioManager.playRandomSound('upgrade');
            };

            window.playAchievementSound = function() {
                window.audioManager.playRandomSound('achievement');
            };

            window.playSkinChangeSound = function() {
                window.audioManager.playRandomSound('skin');
            };
        }

        // Инициализируем звуки для всех кнопок
        document.querySelectorAll('button, .btn, .nav-link').forEach(element => {
            if (!element.hasAttribute('data-sound-initialized')) {
                element.addEventListener('click', function() {
                    if (window.audioManager && !window.audioManager.isMuted) {
                        window.audioManager.playRandomSound('click');
                    }
                });
                element.setAttribute('data-sound-initialized', 'true');
            }
        });

        // Показываем уведомление о готовности
        if (window.showNotification) {
            setTimeout(() => {
                window.showNotification('Игровые системы загружены!', 'success');
            }, 1000);
        }
    }

    // Инициализация аудио менеджера
    function initAudioManager() {
        if (typeof EnhancedAudioManager !== 'undefined' && !window.audioManager) {
            try {
                window.audioManager = new EnhancedAudioManager();
                audioManagerReady = true;
                console.log('🔊 Audio Manager initialized');
                checkReadiness();
            } catch (error) {
                console.error('❌ Audio Manager initialization failed:', error);
                // Продолжаем без аудио
                audioManagerReady = true;
                checkReadiness();
            }
        } else if (window.audioManager) {
            audioManagerReady = true;
            checkReadiness();
        } else {
            // Повторяем попытку через 100ms
            setTimeout(initAudioManager, 100);
        }
    }

    // Инициализация игровых эффектов
    function initGameEffects() {
        if (typeof GameEffects !== 'undefined') {
            try {
                GameEffects.init();
                gameEffectsReady = true;
                console.log('✨ Game Effects initialized');
                checkReadiness();
            } catch (error) {
                console.error('❌ Game Effects initialization failed:', error);
                gameEffectsReady = true;
                checkReadiness();
            }
        } else {
            // Повторяем попытку через 100ms
            setTimeout(initGameEffects, 100);
        }
    }

    // Основная функция инициализации
    function initialize() {
        console.log('🚀 Starting game systems initialization...');
        
        // Инициализируем компоненты
        initAudioManager();
        initGameEffects();
        
        // Таймаут безопасности - если что-то не загрузилось за 5 секунд
        setTimeout(() => {
            if (!audioManagerReady || !gameEffectsReady) {
                console.warn('⚠️ Some systems failed to initialize within timeout');
                audioManagerReady = true;
                gameEffectsReady = true;
                checkReadiness();
            }
        }, 5000);
    }

    // Запускаем инициализацию
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initialize);
    } else {
        initialize();
    }

    // Экспортируем функции для отладки
    window.gameInit = {
        audioManagerReady: () => audioManagerReady,
        gameEffectsReady: () => gameEffectsReady,
        reinitialize: initialize
    };

})();