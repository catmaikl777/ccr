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
        // Загружаем текущий скин из элемента на странице
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

        // Если есть текущий скин, анимируем переход
        if (this.currentSkin && animate) {
            this.animateSkinTransition(skinImage, skinName);
        } else {
            skinImage.src = `/static/main/skins/${skinName}`;
        }

        this.currentSkin = skinName;
        localStorage.setItem('currentSkin', skinName);

        // Воспроизводим звук смены скина
        this.playSkinChangeSound();

        // Создаем эффекты
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

        // Создаем частицы
        if (window.particleSystem) {
            window.particleSystem.createParticles(x, y, 50, '#FF4081', 'star');
        }

        // Экран трясется
        if (window.screenShaker) {
            window.screenShaker.shake(3, 200);
        }

        // Показываем текст
        if (window.floatingText) {
            window.floatingText.show('NEW SKIN!', x, y, '#FF4081');
        }
    }

    playSkinChangeSound() {
        // Используем наш аудио-менеджер
        if (window.audioManager) {
            window.audioManager.playSound('unlock', 0.5);
        } else {
            // Fallback звук
            const audio = new Audio('/static/main/sounds/click.mp3');
            audio.volume = 0.3;
            audio.play().catch(e => console.log('Audio play prevented:', e));
        }
    }

    playAmbientSound() {
        // Фоновые звуки для страницы скинов
        if (window.location.pathname.includes('/skins/')) {
            if (window.audioManager) {
                window.audioManager.playMusic();
            }
        }
    }

    unlockSkin(skinName) {
        this.unlockedSkins.add(skinName);
        localStorage.setItem('unlockedSkins', JSON.stringify([...this.unlockedSkins]));

        // Эффект разблокировки
        this.createUnlockEffects();

        // Звук разблокировки
        if (window.audioManager) {
            window.audioManager.playSound('achievement', 0.7);
        }
    }

    createUnlockEffects() {
        // Создаем эффект взрыва звезд по всему экрану
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
        // Обработчики для страницы скинов
        if (window.location.pathname.includes('/skins/')) {
            this.setupSkinsPageListeners();
        }

        // Обработчики для главной страницы
        this.setupMainPageListeners();
    }

    setupSkinsPageListeners() {
        document.addEventListener('click', (e) => {
            // Эффект при клике на карточку скина
            if (e.target.classList.contains('skin-card') ||
                e.target.closest('.skin-card')) {
                this.createRippleEffect(e);
            }
        });
    }

    setupMainPageListeners() {
        // Обработчики для кнопок покупки ящиков
        document.addEventListener('click', (e) => {
            if (e.target.classList.contains('buy-box-button')) {
                const boxId = e.target.dataset.boxId;
                const price = parseInt(e.target.dataset.price);
                this.handleBoxPurchase(boxId, price);
            }
        });
    }

    handleBoxPurchase(boxId, price) {
        // Эта функция будет вызвана из основного скрипта
        console.log('Box purchase handled by main script');
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

    // Метод для обновления скина из внешнего кода
    updateSkin(skinName) {
        this.changeSkin(skinName, true);
    }

    // Метод для получения текущего скина
    getCurrentSkin() {
        return this.currentSkin;
    }
}

// CSS для ripple эффекта
const rippleStyle = document.createElement('style');
rippleStyle.textContent = `
    @keyframes ripple {
        0% {
            width: 0;
            height: 0;
            opacity: 0.7;
        }
        100% {
            width: 200px;
            height: 200px;
            opacity: 0;
        }
    }

    .skin-card {
        position: relative;
        overflow: hidden;
    }

    .skin-ripple {
        position: absolute;
        border-radius: 50%;
        transform: translate(-50%, -50%);
        animation: ripple 0.6s linear;
        pointer-events: none;
        z-index: 1;
    }
`;
document.head.appendChild(rippleStyle);

// Инициализация при загрузке
document.addEventListener('DOMContentLoaded', function() {
    window.skinManager = new SkinManager();
    
    // Глобальная функция для обновления скина
    window.updateSkin = function(skinName) {
        if (window.skinManager) {
            window.skinManager.updateSkin(skinName);
        }
    };
});