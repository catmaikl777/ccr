// auto_clicker.js
document.addEventListener('DOMContentLoaded', function() {
    const playerId = document.getElementById('player-id').value;
    const csrfToken = window.csrfToken;

    // Переменные для управления автокликером
    let autoClickerInterval = null;
    let isAutoClickerActive = false;

    // Инициализация автокликера
    function initAutoClicker() {
        // Получаем информацию об автокликере
        fetch(`/player/${playerId}/auto_clicker_info/`)
            .then(response => response.json())
            .then(data => {
                if (data.has_auto_clicker && data.clicks_per_second > 0) {
                    startAutoClicker(data.clicks_per_second);
                }
            })
            .catch(error => console.error('Error loading auto clicker:', error));

        // Запускаем обновление каждые 10 секунд
        setInterval(updateAutoClicker, 10000);
    }

    // Запуск автокликера
    function startAutoClicker(clicksPerSecond) {
        if (isAutoClickerActive) return;

        console.log(`Starting auto clicker with ${clicksPerSecond} clicks/sec`);
        isAutoClickerActive = true;

        // Рассчитываем интервал (1000ms / кликов в секунду)
        const interval = Math.max(100, 1000 / clicksPerSecond);

        // Останавливаем предыдущий интервал
        if (autoClickerInterval) {
            clearInterval(autoClickerInterval);
        }

        // Запускаем новый интервал
        autoClickerInterval = setInterval(() => {
            processAutoClick();
        }, interval);

        // Показываем индикатор
        showAutoClickerIndicator(clicksPerSecond);
        showNotification(`Автокликер активирован! ${clicksPerSecond} кликов/сек`, 'success');
    }

    // Остановка автокликера
    function stopAutoClicker() {
        if (autoClickerInterval) {
            clearInterval(autoClickerInterval);
            autoClickerInterval = null;
        }
        isAutoClickerActive = false;

        // Скрываем индикатор
        hideAutoClickerIndicator();
    }

    // Обработка одного авто-клика
    function processAutoClick() {
        fetch('/auto_click/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                player_id: playerId
            })
        })
        .then(response => {
            if (!response.ok) {
                throw new Error('Network response was not ok');
            }
            return response.json();
        })
        .then(data => {
            if (data.success) {
                // Обновляем счет
                updateStats(data);

                // Показываем уведомление каждые 10 кликов
                if (data.auto_clicks > 0 && Math.random() < 0.1) {
                    showAutoClickNotification(data);
                }

                // Играем звук клика с малой вероятностью
                if (window.audioManager && Math.random() < 0.05) {
                    window.audioManager.playRandomSound('click');
                }
            }
        })
        .catch(error => {
            console.error('Auto click error:', error);
            // Не останавливаем автокликер при ошибке сети
        });
    }

    // Обновление статистики
    function updateStats(data) {
        // Обновляем монеты
        const coinsElement = document.getElementById('coins');
        if (coinsElement) {
            coinsElement.textContent = data.coins;
        }

        // Обновляем клики
        const clicksElement = document.getElementById('clicks');
        if (clicksElement) {
            clicksElement.textContent = data.clicks;
        }

        // Обновляем информацию о заработке
        const autoCoinsPerSecond = document.getElementById('auto-coins-per-second');
        if (autoCoinsPerSecond) {
            const clickPower = parseInt(document.getElementById('click-power').textContent) || 1;
            const autoClickPower = parseInt(document.getElementById('auto-clicker-power').textContent) || 0;
            autoCoinsPerSecond.textContent = autoClickPower * clickPower;
        }

        // Обновляем доступность улучшений
        checkUpgradeAvailability();
    }

    // Функция обновления автокликера (проверка новых уровней)
    function updateAutoClicker() {
        // Проверяем текущую мощность автокликера
        const autoClickerPowerElement = document.getElementById('auto-clicker-power');
        if (!autoClickerPowerElement) return;

        const currentPower = parseInt(autoClickerPowerElement.textContent) || 0;

        // Получаем обновленную информацию
        fetch(`/player/${playerId}/auto_clicker_info/`)
            .then(response => response.json())
            .then(data => {
                if (data.has_auto_clicker && data.clicks_per_second > 0) {
                    // Если мощность изменилась
                    if (data.clicks_per_second !== currentPower) {
                        console.log(`Auto clicker power changed: ${currentPower} -> ${data.clicks_per_second}`);

                        // Обновляем отображение
                        autoClickerPowerElement.textContent = data.clicks_per_second + '/сек';

                        // Перезапускаем автокликер с новой мощностью
                        stopAutoClicker();
                        startAutoClicker(data.clicks_per_second);
                    }
                } else if (isAutoClickerActive) {
                    // Если автокликер исчез
                    stopAutoClicker();
                }
            })
            .catch(error => console.error('Error updating auto clicker:', error));
    }

    // Вспомогательные функции

    function showAutoClickerIndicator(clicksPerSecond) {
        // Удаляем старый индикатор
        hideAutoClickerIndicator();

        // Создаем новый индикатор
        const indicator = document.createElement('div');
        indicator.id = 'auto-clicker-indicator';
        indicator.innerHTML = `
            <i class="fas fa-robot fa-spin"></i>
            <span>Автокликер: ${clicksPerSecond} клик/сек</span>
        `;

        // Добавляем в тело
        document.body.appendChild(indicator);

        // Анимация появления
        setTimeout(() => {
            indicator.style.opacity = '1';
        }, 10);
    }

    function hideAutoClickerIndicator() {
        const indicator = document.getElementById('auto-clicker-indicator');
        if (indicator) {
            indicator.style.opacity = '0';
            setTimeout(() => {
                if (indicator.parentNode) {
                    indicator.parentNode.removeChild(indicator);
                }
            }, 300);
        }
    }

    function showAutoClickNotification(data) {
        // Создаем временное уведомление
        const notification = document.createElement('div');
        notification.className = 'auto-click-notification';
        notification.innerHTML = `
            <i class="fas fa-robot"></i>
            <span>Автокликер: +${data.coins_earned} монет</span>
        `;

        document.body.appendChild(notification);

        // Показываем
        setTimeout(() => notification.classList.add('show'), 10);

        // Скрываем через 2 секунды
        setTimeout(() => {
            notification.classList.remove('show');
            setTimeout(() => {
                if (notification.parentNode) {
                    notification.parentNode.removeChild(notification);
                }
            }, 300);
        }, 2000);
    }

    function showNotification(message, type = 'info') {
        // Используем ту же функцию из clicker.js или создаем новую
        const notification = document.createElement('div');
        notification.className = `notification ${type}`;
        notification.innerHTML = `
            <i class="fas fa-${type === 'success' ? 'check-circle' : 'exclamation-circle'}"></i>
            <span>${message}</span>
        `;

        notification.style.cssText = `
            position: fixed;
            top: 100px;
            right: 20px;
            background: ${type === 'success' ? 'linear-gradient(135deg, #4caf50 0%, #388e3c 100%)' :
                         type === 'error' ? 'linear-gradient(135deg, #f44336 0%, #d32f2f 100%)' :
                         'linear-gradient(135deg, #2196f3 0%, #1976d2 100%)'};
            color: white;
            padding: 15px 20px;
            border-radius: 0;
            border: 2px solid #ffd700;
            font-family: 'Press Start 2P', cursive;
            font-size: 0.7rem;
            display: flex;
            align-items: center;
            gap: 10px;
            z-index: 1000;
            transform: translateX(150%);
            transition: transform 0.3s ease;
            box-shadow: 0 0 20px rgba(0,0,0,0.3);
        `;

        document.body.appendChild(notification);

        setTimeout(() => {
            notification.style.transform = 'translateX(0)';
        }, 10);

        setTimeout(() => {
            notification.style.transform = 'translateX(150%)';
            setTimeout(() => notification.remove(), 300);
        }, 3000);
    }

    // Глобальные функции для обновления доступности улучшений
    function checkUpgradeAvailability() {
        // Эта функция должна быть в clicker.js
        // Вызываем её если доступна глобально
        if (typeof window.checkUpgradeAvailability === 'function') {
            window.checkUpgradeAvailability();
        }
    }

    // Инициализация
    console.log('Auto clicker script loaded');
    console.log('Player ID for auto clicker:', playerId);

    // Запускаем автокликер через 1 секунду после загрузки
    setTimeout(() => {
        initAutoClicker();
    }, 1000);

    // Слушаем события обновления автокликера
    document.addEventListener('upgradePurchased', function(e) {
        if (e.detail && e.detail.upgrade_type === 'auto_clicker') {
            console.log('Auto clicker upgrade purchased, updating...');
            // Обновляем автокликер через 2 секунды после покупки
            setTimeout(updateAutoClicker, 2000);
        }
    });

    // Экспортируем функции для использования в других скриптах
    window.autoClicker = {
        start: startAutoClicker,
        stop: stopAutoClicker,
        update: updateAutoClicker
    };
});