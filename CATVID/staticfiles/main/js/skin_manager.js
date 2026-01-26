class SkinManager {
    constructor() {
        this.currentSkin = null;
        this.unlockedSkins = new Set();
        this.init();
    }

    init() {
        this.loadCurrentSkin();
        this.setupEventListeners();
        this.playAmbientSound();
    }

    loadCurrentSkin() {
        const skinImage = document.getElementById('skin-image');
        if (skinImage) {
            const src = skinImage.src;
            const skinName = src.split('/').pop();
            this.currentSkin = skinName;
        }
    }

    changeSkin(skinName, animate = true) {
        const skinImage = document.getElementById('skin-image');
        if (!skinImage) return;

        if (this.currentSkin && animate) {
            this.animateSkinTransition(skinImage, skinName);
        } else {
            skinImage.src = `/static/main/skins/${skinName}`;
        }

        this.currentSkin = skinName;
        localStorage.setItem('currentSkin', skinName);
        this.playSkinChangeSound();

        if (animate) {
            this.createSkinChangeEffects();
        }
    }

    animateSkinTransition(imgElement, newSkin) {
        imgElement.style.transition = 'all 0.5s cubic-bezier(0.68, -0.55, 0.27, 1.55)';
        imgElement.style.transform = 'scale(0.8) rotate(-180deg)';
        imgElement.style.opacity = '0.5';

        setTimeout(() => {
            imgElement.src = `/static/main/skins/${newSkin}`;
            imgElement.style.transform = 'scale(1.2) rotate(180deg)';
            imgElement.style.opacity = '1';

            setTimeout(() => {
                imgElement.style.transform = 'scale(1) rotate(0deg)';
                setTimeout(() => {
                    imgElement.style.transition = '';
                }, 500);
            }, 300);
        }, 300);
    }

    createSkinChangeEffects() {
        const button = document.querySelector('.click-button');
        if (!button) return;

        const rect = button.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;

        if (window.particleSystem) {
            window.particleSystem.createParticles(x, y, 50, '#FF4081', 'star');
        }
        if (window.screenShaker) {
            window.screenShaker.shake(3, 200);
        }
        if (window.floatingText) {
            window.floatingText.show('NEW SKIN!', x, y, '#FF4081');
        }
    }

    playSkinChangeSound() {
        if (window.audioManager) {
            window.audioManager.playSound('unlock', 0.5);
        } else {
            const audio = new Audio('/static/main/sounds/click.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => console.log('Audio play prevented:', e));
        }
    }

    playAmbientSound() {
        if (window.location.pathname.includes('/skins/')) {
            if (window.audioManager) {
                window.audioManager.playMusic();
            }
        }
    }

    unlockSkin(skinName) {
        this.unlockedSkins.add(skinName);
        localStorage.setItem('unlockedSkins', JSON.stringify([...this.unlockedSkins]));
        this.createUnlockEffects();

        if (window.audioManager) {
            window.audioManager.playSound('achievement', 0.7);
        }
    }

    createUnlockEffects() {
        for (let i = 0; i < 20; i++) {
            setTimeout(() => {
                const x = Math.random() * window.innerWidth;
                const y = Math.random() * window.innerHeight;

                if (window.particleSystem) {
                    window.particleSystem.createParticles(x, y, 10, '#4CAF50', 'star');
                }
            }, i * 100);
        }
    }

    setupEventListeners() {
        if (window.location.pathname.includes('/skins/')) {
            this.setupSkinsPageListeners();
        }
        this.setupMainPageListeners();
    }

    setupSkinsPageListeners() {
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('skin-card') ||
                e.target.closest('.skin-card')) {
                this.createRippleEffect(e);
            }
        });
    }

    setupMainPageListeners() {
        document.addEventListener('click', (e) => {
            const buyButton = e.target.closest('.buy-box-button');
            if (buyButton) {
                e.preventDefault();
                const boxId = buyButton.dataset.boxId;
                const price = parseInt(buyButton.dataset.price);
                this.handleBoxPurchase(boxId, price, buyButton);
            }
        });
    }

    // ✅ ИСПРАВЛЕННЫЙ МЕТОД - не удаляем бокс из DOM
    async handleBoxPurchase(boxId, price, button) {
        // Блокируем кнопку на время запроса
        button.disabled = true;
        button.classList.add('loading');
        const originalText = button.textContent;
        button.textContent = 'Покупка...';

        try {
            const response = await fetch(`/buy_box/`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': this.getCSRFToken()
                },
                body: JSON.stringify({
                    box_id: boxId
                })
            });

            const data = await response.json();

            if (data.success) {
                // ✅ Показываем эффект успешной покупки
                this.showPurchaseSuccess(button, data);

                // ✅ Обновляем баланс на странице
                this.updateBalance(data.new_balance);

                // ✅ НЕ удаляем бокс - его можно купить снова!
                // Просто показываем анимацию
                this.animateBoxPurchase(button);

                // Если получен скин - показываем его
                if (data.skin) {
                    this.showSkinReward(data.skin);
                }
            } else {
                // Показываем ошибку
                this.showPurchaseError(button, data.message || 'Недостаточно монет');
            }
        } catch (error) {
            console.error('Purchase error:', error);
            this.showPurchaseError(button, 'Ошибка сети');
        } finally {
            // Разблокируем кнопку
            button.disabled = false;
            button.classList.remove('loading');
            button.textContent = originalText;
        }
    }

    // ✅ Анимация покупки БЕЗ удаления элемента
    animateBoxPurchase(button) {
        const boxCard = button.closest('.box-card');
        if (!boxCard) return;

        // Анимация "встряхивания" бокса
        boxCard.style.animation = 'boxShake 0.5s ease-in-out';

        // Эффект свечения
        boxCard.style.boxShadow = '0 0 30px rgba(255, 215, 0, 0.8)';

        setTimeout(() => {
            boxCard.style.animation = '';
            boxCard.style.boxShadow = '';
        }, 500);

        // Частицы
        const rect = boxCard.getBoundingClientRect();
        const x = rect.left + rect.width / 2;
        const y = rect.top + rect.height / 2;

        if (window.particleSystem) {
            window.particleSystem.createParticles(x, y, 30, '#FFD700', 'star');
        }
    }

    showPurchaseSuccess(button, data) {
        const boxCard = button.closest('.box-card');
        if (!boxCard) return;

        // Показываем уведомление
        const notification = document.createElement('div');
        notification.className = 'purchase-notification success';
        notification.innerHTML = `
            <span class="notification-icon">🎉</span>
            <span class="notification-text">Куплено!</span>
        `;

        boxCard.appendChild(notification);

        setTimeout(() => {
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }

    showPurchaseError(button, message) {
        const boxCard = button.closest('.box-card');
        if (!boxCard) return;

        // Анимация ошибки
        boxCard.style.animation = 'errorShake 0.3s ease-in-out';

        const notification = document.createElement('div');
        notification.className = 'purchase-notification error';
        notification.innerHTML = `
            <span class="notification-icon">❌</span>
            <span class="notification-text">${message}</span>
        `;

        boxCard.appendChild(notification);

        setTimeout(() => {
            boxCard.style.animation = '';
            notification.classList.add('fade-out');
            setTimeout(() => notification.remove(), 300);
        }, 2000);
    }

    updateBalance(newBalance) {
        // Обновляем отображение баланса на странице
        const balanceElements = document.querySelectorAll('.user-coins, .balance-amount, #coin-count');
        balanceElements.forEach(el => {
            const oldValue = parseInt(el.textContent) || 0;
            this.animateNumber(el, oldValue, newBalance);
        });
    }

    animateNumber(element, from, to) {
        const duration = 500;
        const startTime = performance.now();

        const animate = (currentTime) => {
            const elapsed = currentTime - startTime;
            const progress = Math.min(elapsed / duration, 1);

            const easeOut = 1 - Math.pow(1 - progress, 3);
            const current = Math.round(from + (to - from) * easeOut);

            element.textContent = current.toLocaleString();

            if (progress < 1) {
                requestAnimationFrame(animate);
            }
        };

        requestAnimationFrame(animate);
    }

    showSkinReward(skin) {
        // Показываем модальное окно с полученным скином
        const modal = document.createElement('div');
        modal.className = 'skin-reward-modal';
        modal.innerHTML = `
            <div class="skin-reward-content">
                <h2>🎉 Вы получили скин!</h2>
                <div class="skin-reward-image">
                    <img src="/static/main/skins/${skin.image}" alt="${skin.name}">
                </div>
                <p class="skin-reward-name">${skin.name}</p>
                <p class="skin-reward-rarity rarity-${skin.rarity}">${skin.rarity}</p>
                <button class="close-reward-btn">Отлично!</button>
            </div>
        `;

        document.body.appendChild(modal);

        // Эффекты при открытии
        setTimeout(() => modal.classList.add('visible'), 10);

        this.createUnlockEffects();

        // Закрытие
        modal.querySelector('.close-reward-btn').addEventListener('click', () => {
            modal.classList.remove('visible');
            setTimeout(() => modal.remove(), 300);
        });
    }

    getCSRFToken() {
        const cookie = document.cookie.split(';').find(c => c.trim().startsWith('csrftoken='));
        return cookie ? cookie.split('=')[1] : '';
    }

    createRippleEffect(event) {
        const skinCard = event.target.closest('.skin-card');
        if (!skinCard) return;

        const ripple = document.createElement('div');
        ripple.className = 'skin-ripple';

        const rect = skinCard.getBoundingClientRect();
        const x = event.clientX - rect.left;
        const y = event.clientY - rect.top;

        ripple.style.cssText = `
            position: absolute;
            width: 0;
            height: 0;
            left: ${x}px;
            top: ${y}px;
            background: radial-gradient(circle, rgba(255,64,129,0.3) 0%, rgba(255,64,129,0) 70%);
            border-radius: 50%;
            transform: translate(-50%, -50%);
            animation: ripple 0.6s linear;
            pointer-events: none;
            z-index: 1;
        `;

        skinCard.style.position = 'relative';
        skinCard.appendChild(ripple);
        setTimeout(() => ripple.remove(), 600);
    }

    updateSkin(skinName) {
        this.changeSkin(skinName, true);
    }

    getCurrentSkin() {
        return this.currentSkin;
    }
}

// CSS стили
const styles = document.createElement('style');
styles.textContent = `
    @keyframes ripple {
        0% { width: 0; height: 0; opacity: 0.7; }
        100% { width: 200px; height: 200px; opacity: 0; }
    }

    @keyframes boxShake {
        0%, 100% { transform: translateX(0) rotate(0deg); }
        20% { transform: translateX(-5px) rotate(-2deg); }
        40% { transform: translateX(5px) rotate(2deg); }
        60% { transform: translateX(-5px) rotate(-1deg); }
        80% { transform: translateX(5px) rotate(1deg); }
    }

    @keyframes errorShake {
        0%, 100% { transform: translateX(0); }
        25% { transform: translateX(-10px); }
        75% { transform: translateX(10px); }
    }

    .skin-card, .box-card {
        position: relative;
        overflow: hidden;
    }

    .buy-box-button.loading {
        opacity: 0.7;
        cursor: wait;
    }

    .purchase-notification {
        position: absolute;
        top: 50%;
        left: 50%;
        transform: translate(-50%, -50%);
        padding: 10px 20px;
        border-radius: 10px;
        font-weight: bold;
        z-index: 100;
        animation: popIn 0.3s ease-out;
    }

    .purchase-notification.success {
        background: rgba(76, 175, 80, 0.9);
        color: white;
    }

    .purchase-notification.error {
        background: rgba(244, 67, 54, 0.9);
        color: white;
    }

    .purchase-notification.fade-out {
        opacity: 0;
        transition: opacity 0.3s;
    }

    @keyframes popIn {
        0% { transform: translate(-50%, -50%) scale(0); }
        50% { transform: translate(-50%, -50%) scale(1.2); }
        100% { transform: translate(-50%, -50%) scale(1); }
    }

    .skin-reward-modal {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.8);
        display: flex;
        align-items: center;
        justify-content: center;
        z-index: 10000;
        opacity: 0;
        transition: opacity 0.3s;
    }

    .skin-reward-modal.visible {
        opacity: 1;
    }

    .skin-reward-content {
        background: linear-gradient(135deg, #1a1a2e, #16213e);
        padding: 40px;
        border-radius: 20px;
        text-align: center;
        border: 2px solid #FFD700;
        animation: modalPop 0.5s ease-out;
    }

    @keyframes modalPop {
        0% { transform: scale(0) rotate(-10deg); }
        100% { transform: scale(1) rotate(0deg); }
    }

    .skin-reward-image img {
        width: 150px;
        height: 150px;
        object-fit: contain;
        animation: float 2s ease-in-out infinite;
    }

    @keyframes float {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    .close-reward-btn {
        margin-top: 20px;
        padding: 12px 30px;
        background: linear-gradient(135deg, #FFD700, #FFA500);
        border: none;
        border-radius: 25px;
        color: #1a1a2e;
        font-weight: bold;
        cursor: pointer;
        transition: transform 0.2s;
    }

    .close-reward-btn:hover {
        transform: scale(1.05);
    }
`;
document.head.appendChild(styles);

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    window.skinManager = new SkinManager();

    window.updateSkin = function(skinName) {
        if (window.skinManager) {
            window.skinManager.updateSkin(skinName);
        }
    };
});