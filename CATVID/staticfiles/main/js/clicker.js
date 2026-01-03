if (!window.EnhancedClicker) {
    window.EnhancedClicker = class {
        constructor() {
            if (window.clickerInstance) {
                return window.clickerInstance;
            }
            window.clickerInstance = this;
        this.coins = 0;
        this.clickPower = 1;
        this.criticalChance = 0.1;
        this.criticalMultiplier = 2;
        this.clickButton = null;
        this.coinsElement = null;
        this.clicksElement = null;
        this.clickPowerElement = null;
        this.isAnimating = false;
        this.lastClickTime = 0;
        this.clickStreak = 0;
        this.maxStreak = 0;
        this.streakTimer = null;
        this.init();
    }

    init() {
        this.clickButton = document.getElementById('click-button');
        this.coinsElement = document.getElementById('coins');
        this.clicksElement = document.getElementById('clicks');
        this.clickPowerElement = document.getElementById('click-power');

        if (this.coinsElement) {
            this.coins = parseInt(this.coinsElement.textContent) || 0;
        }

        if (this.clickPowerElement) {
            this.clickPower = parseInt(this.clickPowerElement.textContent) || 1;
        }

        this.setupEventListeners();
        this.createFloatingCoins();
        this.setupAutoClicker();
        this.playClickerTheme();
    }

    setupEventListeners() {
        if (this.clickButton) {
            // Mouse events
            this.clickButton.addEventListener('click', (e) => this.handleClick(e));

            // Touch events for mobile
            this.clickButton.addEventListener('touchstart', (e) => {
                e.preventDefault();
                this.handleClick(e.touches[0]);
            }, { passive: false });

            // Mouse down/up for animation
            this.clickButton.addEventListener('mousedown', () => this.animateButtonPress(true));
            this.clickButton.addEventListener('mouseup', () => this.animateButtonPress(false));
            this.clickButton.addEventListener('mouseleave', () => this.animateButtonPress(false));

            // Touch events for press animation
            this.clickButton.addEventListener('touchstart', () => this.animateButtonPress(true));
            this.clickButton.addEventListener('touchend', () => this.animateButtonPress(false));
            this.clickButton.addEventListener('touchcancel', () => this.animateButtonPress(false));
        }

        // Keyboard support
        document.addEventListener('keydown', (e) => {
            if (e.code === 'Space' || e.code === 'Enter') {
                e.preventDefault();
                this.handleClick({ clientX: window.innerWidth / 2, clientY: window.innerHeight / 2 });
            }
        });
    }

    handleClick(event) {
        if (this.isAnimating) return;

        const rect = this.clickButton.getBoundingClientRect();
        const x = event.clientX || rect.left + rect.width / 2;
        const y = event.clientY || rect.top + rect.height / 2;

        // Calculate earnings
        const isCritical = Math.random() < this.criticalChance;
        const earnings = isCritical ?
            Math.floor(this.clickPower * this.criticalMultiplier) :
            this.clickPower;

        // Update coins
        this.addCoins(earnings);

        // Update clicks counter
        this.updateClicks();

        // Create visual effects
        this.createClickEffects(x, y, earnings, isCritical);

        // Play sounds
        this.playClickSound(isCritical);

        // Combo system
        if (window.comboSystem) {
            window.comboSystem.addClick();
        }

        // Streak system
        this.updateClickStreak();

        // Vibrate on mobile
        if (navigator.vibrate) {
            navigator.vibrate(50);
        }

        // Screen shake for critical hits
        if (isCritical && window.screenShaker) {
            window.screenShaker.shake(8, 100);
        }
    }

    createClickEffects(x, y, amount, isCritical) {
        // Create particles
        if (window.particleSystem) {
            const color = isCritical ? '#FF4081' : '#FFD700';
            window.particleSystem.createParticles(x, y, 15, color);
            window.particleSystem.createCoinParticles(x, y, Math.min(amount, 10));
        }

        // Floating text
        const text = isCritical ? `CRIT! +${amount}` : `+${amount}`;
        const color = isCritical ? '#FF4081' : '#4CAF50';
        window.floatingText?.show(text, x, y - 50, color);

        // Button animation
        this.animateButton();

        // Trail effect
        this.createClickTrail(x, y);
    }

    createClickTrail(x, y) {
        for (let i = 0; i < 3; i++) {
            setTimeout(() => {
                if (window.particleSystem) {
                    window.particleSystem.createParticles(
                        x + (Math.random() - 0.5) * 20,
                        y + (Math.random() - 0.5) * 20,
                        3,
                        '#00BCD4',
                        'trail'
                    );
                }
            }, i * 50);
        }
    }

    animateButton() {
        this.isAnimating = true;
        const button = this.clickButton;

        // Scale animation
        button.style.transform = 'scale(0.9)';

        // Glow effect
        button.style.boxShadow = '0 0 30px rgba(255, 215, 0, 0.7)';

        setTimeout(() => {
            button.style.transform = 'scale(1.05)';
            button.style.boxShadow = '0 0 50px rgba(255, 64, 129, 0.5)';
        }, 100);

        setTimeout(() => {
            button.style.transform = 'scale(1)';
            button.style.boxShadow = '';
            this.isAnimating = false;
        }, 200);
    }

    animateButtonPress(isPressed) {
        if (!this.clickButton) return;

        if (isPressed) {
            this.clickButton.style.transform = 'scale(0.85)';
            this.clickButton.style.filter = 'brightness(0.8)';
        } else {
            this.clickButton.style.transform = 'scale(1)';
            this.clickButton.style.filter = 'brightness(1)';
        }
    }

    addCoins(amount) {
        this.coins += amount;

        if (this.coinsElement) {
            // Animate number increase
            this.animateNumber(this.coinsElement, this.coins - amount, this.coins);
        }

        // Save to server
        this.saveProgress();
    }

    animateNumber(element, from, to) {
        const duration = 500;
        const start = performance.now();
        const step = (timestamp) => {
            const progress = Math.min((timestamp - start) / duration, 1);
            const current = Math.floor(from + (to - from) * progress);
            element.textContent = current.toLocaleString();

            // Color animation
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

            // Animation
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

            // Special effects for new streak records
            if (this.clickStreak % 10 === 0) {
                this.createStreakEffects();
            }
        }

        // Reset streak after 2 seconds
        clearTimeout(this.streakTimer);
        this.streakTimer = setTimeout(() => {
            this.clickStreak = 0;
        }, 2000);
    }

    createStreakEffects() {
        // Rainbow effect for high streaks
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
        // Используем наш аудио-менеджер
        if (window.audioManager) {
            if (isCritical) {
                window.audioManager.playSound('critical', 0);
            } else {
                window.audioManager.playRandomSound('click');
            }
        } else {
            console.warn('⚠️ Audio manager not available for click sound');
        }
    }

    playClickerTheme() {
        // Используем наш аудио-менеджер для фоновой музыки
        const startTheme = () => {
            if (window.audioManager) {
                window.audioManager.playMusic();
            } else {
                console.warn('⚠️ Audio manager not available for theme music');
            }
        };

        document.addEventListener('click', startTheme, { once: true });
        document.addEventListener('touchstart', startTheme, { once: true });
    }

    createFloatingCoins() {
        // Create floating coins in background
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

        // Add CSS animation
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

                // Visual feedback for auto clicks
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
        // Save to server via AJAX
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
    };
}

// Initialize when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    window.enhancedClicker = new EnhancedClicker();

    // Add CSS for effects
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
}