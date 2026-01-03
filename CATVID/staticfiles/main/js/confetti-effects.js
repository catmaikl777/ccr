// Confetti эффекты для особых событий
class ConfettiEffects {
    constructor() {
        this.confetti = null;
        // Отложенная инициализация
        this.initCanvas();
    }

    initCanvas() {
        // Создаем canvas для конфетти если его нет
        let canvas = document.getElementById('confetti-canvas');
        if (!canvas) {
            canvas = document.createElement('canvas');
            canvas.id = 'confetti-canvas';
            canvas.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 99997;
                display: none;
            `;
            document.body.appendChild(canvas);
        }

        // Проверяем наличие библиотеки и canvas
        setTimeout(() => {
            if (typeof ConfettiGenerator !== 'undefined' && canvas) {
                this.confetti = new ConfettiGenerator({
                    target: 'confetti-canvas',
                    max: 80,
                    size: 1,
                    animate: true,
                    props: ['circle', 'square', 'triangle', 'line'],
                    colors: [[255, 64, 129], [0, 188, 212], [255, 215, 0], [76, 175, 80]],
                    clock: 25
                });
            } else {
                console.warn('ConfettiGenerator not loaded or canvas not found');
            }
        }, 100);
    }

    launchConfetti(duration = 3000) {
        this.confetti.render();

        setTimeout(() => {
            this.confetti.clear();
        }, duration);
    }

    launchRainbowConfetti() {
        // Особый эффект радужного конфетти
        for (let i = 0; i < 5; i++) {
            setTimeout(() => {
                this.launchConfetti(1000);
            }, i * 200);
        }
    }

    launchDirectionalConfetti(x, y, direction = 'up') {
        // Направленный конфетти эффект
        const particles = [];
        const particleCount = 50;

        for (let i = 0; i < particleCount; i++) {
            const particle = document.createElement('div');
            particle.className = 'confetti-particle';
            particle.style.cssText = `
                position: fixed;
                left: ${x}px;
                top: ${y}px;
                width: 10px;
                height: 10px;
                background: ${this.getRandomColor()};
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
                opacity: 0;
            `;

            document.body.appendChild(particle);
            particles.push(particle);

            // Анимация
            const angle = direction === 'up' ? -Math.PI/2 : Math.PI/2;
            const speed = 2 + Math.random() * 3;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;

            this.animateParticle(particle, vx, vy);
        }

        setTimeout(() => {
            particles.forEach(p => p.remove());
        }, 2000);
    }

    animateParticle(particle, vx, vy) {
        let x = parseFloat(particle.style.left);
        let y = parseFloat(particle.style.top);
        let opacity = 1;
        let rotation = 0;

        const animate = () => {
            x += vx;
            y += vy;
            vy += 0.05; // гравитация
            opacity -= 0.01;
            rotation += 5;

            particle.style.left = `${x}px`;
            particle.style.top = `${y}px`;
            particle.style.opacity = opacity;
            particle.style.transform = `rotate(${rotation}deg)`;

            if (opacity > 0) {
                requestAnimationFrame(animate);
            }
        };

        animate();
    }

    getRandomColor() {
        const colors = [
            '#FF4081', '#00BCD4', '#FFD700', '#4CAF50',
            '#9C27B0', '#2196F3', '#FF9800', '#E91E63'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    // Эффект взрыва
    createExplosion(x, y, color = '#FF4081') {
        for (let i = 0; i < 30; i++) {
            const particle = document.createElement('div');
            particle.className = 'explosion-particle';
            particle.style.cssText = `
                position: fixed;
                left: ${x}px;
                top: ${y}px;
                width: 8px;
                height: 8px;
                background: ${color};
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
                opacity: 0;
            `;

            document.body.appendChild(particle);

            // Анимация взрыва
            const angle = Math.random() * Math.PI * 2;
            const speed = 3 + Math.random() * 4;
            const vx = Math.cos(angle) * speed;
            const vy = Math.sin(angle) * speed;

            this.animateExplosion(particle, vx, vy);
        }
    }

    animateExplosion(particle, vx, vy) {
        let x = parseFloat(particle.style.left);
        let y = parseFloat(particle.style.top);
        let opacity = 1;
        let size = 8;

        const animate = () => {
            x += vx;
            y += vy;
            vx *= 0.98;
            vy *= 0.98;
            opacity -= 0.02;
            size *= 0.95;

            particle.style.left = `${x}px`;
            particle.style.top = `${y}px`;
            particle.style.opacity = opacity;
            particle.style.width = `${size}px`;
            particle.style.height = `${size}px`;

            if (opacity > 0) {
                requestAnimationFrame(animate);
            } else {
                particle.remove();
            }
        };

        animate();
    }

    // Эффект дождя монет
    createCoinRain(count = 20) {
        for (let i = 0; i < count; i++) {
            setTimeout(() => {
                const coin = document.createElement('div');
                coin.className = 'coin-rain';
                coin.textContent = '💰';
                coin.style.cssText = `
                    position: fixed;
                    left: ${Math.random() * window.innerWidth}px;
                    top: -50px;
                    font-size: ${20 + Math.random() * 20}px;
                    pointer-events: none;
                    z-index: 9998;
                `;

                document.body.appendChild(coin);

                setTimeout(() => {
                    coin.remove();
                }, 3000);
            }, i * 100);
        }
    }

    // Эффект уровня
    showLevelUp() {
        const levelUp = document.getElementById('level-up');
        if (!levelUp) return;

        levelUp.style.display = 'block';
        levelUp.textContent = 'LEVEL UP!';

        // Запускаем конфетти
        this.launchConfetti(5000);

        // Воспроизводим звук
        if (window.audioManager) {
            window.audioManager.playLevelUpSound();
        }

        setTimeout(() => {
            levelUp.style.display = 'none';
        }, 2000);
    }

    // Эффект комбо
    showCombo(combo) {
        if (combo < 5) return;

        const comboText = document.createElement('div');
        comboText.className = 'combo-effect';
        comboText.textContent = `${combo} COMBO!`;
        comboText.style.cssText = `
            position: fixed;
            top: 50%;
            left: 50%;
            transform: translate(-50%, -50%);
            font-family: 'Press Start 2P', cursive;
            font-size: ${2 + combo * 0.1}rem;
            color: ${this.getComboColor(combo)};
            text-shadow: 0 0 20px currentColor;
            z-index: 10000;
            opacity: 0;
            animation: combo-pop 1s ease-out;
            pointer-events: none;
        `;

        document.body.appendChild(comboText);

        // Специальные эффекты для высоких комбо
        if (combo >= 50) {
            this.launchRainbowConfetti();
            window.screenShaker?.shake(10, 500);
        } else if (combo >= 30) {
            this.launchConfetti(2000);
            window.screenShaker?.shake(7, 300);
        } else if (combo >= 20) {
            window.screenShaker?.shake(5, 200);
        } else if (combo >= 10) {
            this.createCoinRain(10);
        }

        // Звук комбо
        if (window.audioManager) {
            window.audioManager.playComboSound(combo);
        }

        setTimeout(() => {
            comboText.remove();
        }, 1000);
    }

    getComboColor(combo) {
        if (combo >= 50) return '#FF4081';
        if (combo >= 30) return '#9C27B0';
        if (combo >= 20) return '#2196F3';
        if (combo >= 10) return '#4CAF50';
        return '#FFD700';
    }

    // CSS для анимаций
    static addStyles() {
        const style = document.createElement('style');
        style.textContent = `
            @keyframes combo-pop {
                0% {
                    opacity: 0;
                    transform: translate(-50%, -50%) scale(0.5);
                }
                50% {
                    opacity: 1;
                    transform: translate(-50%, -50%) scale(1.2);
                }
                100% {
                    opacity: 0;
                    transform: translate(-50%, -50%) scale(1);
                }
            }

            .confetti-particle {
                position: fixed;
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
            }

            .explosion-particle {
                position: fixed;
                border-radius: 50%;
                pointer-events: none;
                z-index: 9999;
            }

            .coin-rain {
                position: fixed;
                pointer-events: none;
                z-index: 9998;
                animation: coin-fall 3s linear forwards;
            }

            @keyframes coin-fall {
                0% {
                    opacity: 1;
                    transform: translateY(0) rotate(0deg);
                }
                100% {
                    opacity: 0;
                    transform: translateY(100vh) rotate(360deg);
                }
            }
        `;
        document.head.appendChild(style);
    }
}

// Make ConfettiEffects globally available
window.ConfettiEffects = ConfettiEffects;