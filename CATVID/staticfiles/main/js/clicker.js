class EnhancedClicker {
    constructor() {
        this.coins = 0;
        this.clickPower = 1;
        this.autoClickerPower = 0;
        this.clickStreak = 0;
        this.maxStreak = 0;
        this.lastClickTime = 0;
        this.streakTimer = null;
        
        this.clickButton = document.querySelector('.click-button') || document.getElementById('click-button');
        this.coinsElement = document.querySelector('#coins');
        this.clicksElement = document.querySelector('#clicks');
        
        this.init();
    }
    
    init() {
        if (this.clickButton) {
            this.clickButton.addEventListener('click', (e) => this.handleClick(e));
        }
        
        this.createFloatingCoins();
        this.setupAutoClicker();
        this.playClickerTheme();
    }
    
    handleClick(e) {
        const isCritical = Math.random() < 0.1;
        const coins = isCritical ? this.clickPower * 2 : this.clickPower;
        
        this.addCoins(coins);
        this.updateClicks();
        this.updateClickStreak();
        this.playClickSound(isCritical);
        
        this.createClickEffect(e);
        
        if (this.clickButton) {
            this.clickButton.style.transform = 'scale(0.95)';
            this.clickButton.style.filter = 'brightness(1.2)';
            
            setTimeout(() => {
                this.clickButton.style.transform = 'scale(1)';
                this.clickButton.style.filter = 'brightness(1)';
            }, 100);
        }
    }
    
    createClickEffect(e) {
        if (window.particleSystem) {
            window.particleSystem.createParticles(
                e.clientX,
                e.clientY,
                5,
                '#FFD700'
            );
        }
    }

    addCoins(amount) {
        this.coins += amount;

        if (this.coinsElement) {
            this.animateNumber(this.coinsElement, this.coins - amount, this.coins);
        }

        this.saveProgress();
    }

    animateNumber(element, from, to) {
        const duration = 500;
        const start = performance.now();
        const step = (timestamp) => {
            const progress = Math.min((timestamp - start) / duration, 1);
            const current = Math.floor(from + (to - from) * progress);
            element.textContent = current.toLocaleString();

            if (progress < 1) {
                element.style.color = '#4CAF50';
                element.style.transform = 'scale(1.1)';
            } else {
                element.style.color = '';
                element.style.transform = '';
            }

            if (progress < 1) {
                requestAnimationFrame(step);
            }
        };
        requestAnimationFrame(step);
    }

    updateClicks() {
        if (this.clicksElement) {
            const current = parseInt(this.clicksElement.textContent) || 0;
            this.clicksElement.textContent = current + 1;

            this.clicksElement.style.color = '#2196F3';
            this.clicksElement.style.transform = 'scale(1.1)';

            setTimeout(() => {
                this.clicksElement.style.color = '';
                this.clicksElement.style.transform = '';
            }, 200);
        }
    }

    updateClickStreak() {
        const now = Date.now();

        if (now - this.lastClickTime < 1000) {
            this.clickStreak++;
        } else {
            this.clickStreak = 1;
        }

        this.lastClickTime = now;

        if (this.clickStreak > this.maxStreak) {
            this.maxStreak = this.clickStreak;

            if (this.clickStreak % 10 === 0) {
                this.createStreakEffects();
            }
        }

        clearTimeout(this.streakTimer);
        this.streakTimer = setTimeout(() => {
            this.clickStreak = 0;
        }, 2000);
    }

    createStreakEffects() {
        const button = this.clickButton;
        if (!button) return;

        const colors = ['#FF4081', '#FF9800', '#FFD700', '#4CAF50', '#2196F3', '#9C27B0'];
        let index = 0;

        const interval = setInterval(() => {
            button.style.borderColor = colors[index];
            button.style.boxShadow = `0 0 40px ${colors[index]}80`;
            index = (index + 1) % colors.length;
        }, 100);

        setTimeout(() => {
            clearInterval(interval);
            button.style.borderColor = '';
            button.style.boxShadow = '';
        }, 1000);
    }

    playClickSound(isCritical) {
        if (window.audioManager) {
            if (isCritical) {
                window.audioManager.playSound('critical', 0);
            } else {
                window.audioManager.playRandomSound('click');
            }
        }
    }

    playClickerTheme() {
        const startTheme = () => {
            if (window.audioManager) {
                window.audioManager.playMusic();
            }
        };

        document.addEventListener('click', startTheme, { once: true });
        document.addEventListener('touchstart', startTheme, { once: true });
    }

    createFloatingCoins() {
        const coinContainer = document.createElement('div');
        coinContainer.id = 'floating-coins';
        coinContainer.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            pointer-events: none;
            z-index: 9990;
            overflow: hidden;
        `;
        document.body.appendChild(coinContainer);

        for (let i = 0; i < 15; i++) {
            this.createFloatingCoin(coinContainer);
        }
    }

    createFloatingCoin(container) {
        const coin = document.createElement('div');
        coin.className = 'floating-coin';
        coin.innerHTML = '💰';

        const size = Math.random() * 30 + 20;
        const duration = Math.random() * 10 + 10;
        const delay = Math.random() * 5;

        coin.style.cssText = `
            position: absolute;
            font-size: ${size}px;
            opacity: ${Math.random() * 0.3 + 0.1};
            left: ${Math.random() * 100}%;
            animation: float ${duration}s linear ${delay}s infinite;
        `;

        container.appendChild(coin);

        if (!document.getElementById('float-animation')) {
            const style = document.createElement('style');
            style.id = 'float-animation';
            style.textContent = `
                @keyframes float {
                    0% {
                        transform: translateY(100vh) rotate(0deg);
                        opacity: 0;
                    }
                    10% {
                        opacity: 0.3;
                    }
                    90% {
                        opacity: 0.3;
                    }
                    100% {
                        transform: translateY(-100px) rotate(360deg);
                        opacity: 0;
                    }
                }
            `;
            document.head.appendChild(style);
        }
    }

    setupAutoClicker() {
        setInterval(() => {
            if (this.autoClickerPower > 0) {
                this.addCoins(this.autoClickerPower);

                const rect = this.clickButton?.getBoundingClientRect();
                if (rect && window.particleSystem) {
                    window.particleSystem.createParticles(
                        rect.left + rect.width / 2,
                        rect.top + rect.height / 2,
                        3,
                        '#2196F3',
                        'auto'
                    );
                }
            }
        }, 1000);
    }

    saveProgress() {
        const csrfToken = document.querySelector('[name=csrfmiddlewaretoken]')?.value;
        if (!csrfToken) return;

        fetch('/update_coins/', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                coins: this.coins,
                click_power: this.clickPower
            })
        }).catch(e => console.error('Save error:', e));
    }
}

document.addEventListener('DOMContentLoaded', function() {
    // Проверяем, не инициализирован ли уже кликер в основном файле
    if (!window.gameClickerInitialized) {
        window.enhancedClicker = new EnhancedClicker();
        window.gameClickerInitialized = true;
    }

    const style = document.createElement('style');
    style.textContent = `
        .click-button {
            transition: all 0.2s cubic-bezier(0.68, -0.55, 0.27, 1.55);
            position: relative;
            overflow: hidden;
        }

        .click-button::after {
            content: '';
            position: absolute;
            top: 50%;
            left: 50%;
            width: 0;
            height: 0;
            border-radius: 50%;
            background: radial-gradient(circle, rgba(255,215,0,0.4) 0%, transparent 70%);
            transform: translate(-50%, -50%);
            transition: width 0.3s, height 0.3s;
        }

        .click-button:active::after {
            width: 200px;
            height: 200px;
        }

        .stat-card {
            transition: all 0.3s;
            position: relative;
            overflow: hidden;
        }

        .stat-card:hover {
            transform: translateY(-5px);
            box-shadow: 0 10px 30px rgba(0, 188, 212, 0.3);
        }

        .stat-card::before {
            content: '';
            position: absolute;
            top: 0;
            left: -100%;
            width: 100%;
            height: 100%;
            background: linear-gradient(90deg, transparent, rgba(255,255,255,0.1), transparent);
            transition: left 0.5s;
        }

        .stat-card:hover::before {
            left: 100%;
        }

        .floating-coin {
            pointer-events: none;
            user-select: none;
        }
    `;
    document.head.appendChild(style);
});