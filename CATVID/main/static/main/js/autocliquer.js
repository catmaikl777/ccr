let autoClickerActive = false;
let autoClickerInterval = null;
let autoClickerLevel = 0;
let autoClickerPower = 1;

function startAutoClicker() {
    if (autoClickerActive) return;

    const clickButton = document.getElementById('click-button');
    const playerId = document.getElementById('player-id').value;

    if (!clickButton || !playerId) return;

    autoClickerActive = true;
    autoClickerInterval = setInterval(() => {
        // Симулируем клик
        if (typeof handleClick === 'function') {
            const event = new Event('click');
            clickButton.dispatchEvent(event);
        }
    }, 1000); // Кликаем каждую секунду
}

// Функция для обновления уровня автокликера
function updateAutoClicker(level, power) {
    autoClickerLevel = level;
    autoClickerPower = power;

    // Если уровень больше 0, запускаем автокликер
    if (level > 0 && !autoClickerActive) {
        startAutoClicker();
    }
}