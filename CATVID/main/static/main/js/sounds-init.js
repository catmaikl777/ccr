// main/static/main/js/sounds-init.js
document.addEventListener('DOMContentLoaded', function() {
    console.log('Sounds init script loaded');

    // Ожидаем готовности системы
    document.addEventListener('gameSystemsReady', function() {
        const audioManager = window.audioManager;

        // Автоматически запускаем музыку на всех страницах после загрузки
        setTimeout(() => {
            if (audioManager && !audioManager.isMuted && !audioManager.currentMusic) {
                audioManager.playMusic();
            }
        }, 1000);

        console.log('Sounds initialized for all pages');
    });

    // Запасная инициализация если событие не пришло
    setTimeout(() => {
        if (window.audioManager && !window.audioManager.currentMusic) {
            const audioManager = window.audioManager;
            if (!audioManager.isMuted) {
                audioManager.playMusic();
            }
        }
    }, 3000);
});