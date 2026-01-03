// Only declare GameEffects if it doesn't exist
if (typeof window.GameEffects === 'undefined') {
    // Инициализация всех визуальных и звуковых эффектов
    class GameEffects {
        static init() {
            console.log('🚀 Initializing game effects...');

            // Инициализируем системы эффектов
            this.initParticleSystem();
            this.initAudioSystem();
            this.initVisualEffects();
            this.initLoadingScreen();

            // Добавляем глобальные обработчики
            this.setupGlobalEffects();

            console.log('✅ Game effects initialized!');
        }

        static initParticleSystem() {
            if (!window.particleSystem && typeof ParticleSystem !== 'undefined') {
                // Check that canvas is not already created
                if (!document.getElementById('particle-canvas')) {
                    window.particleSystem = new ParticleSystem();
                }
            }
        }

        static initAudioSystem() {
            if (!window.audioManager && typeof window.EnhancedAudioManager !== 'undefined') {
                window.audioManager = new window.EnhancedAudioManager();
                window.audioManagerInstance = window.audioManager;
            }

            // Initialize sound on first click
            document.addEventListener('click', () => {
                if (window.audioManager && !window.audioInitialized) {
                    window.audioManager.playMusic();
                    window.audioInitialized = true;
                }
            }, { once: true });
        }

        static initVisualEffects() {
            if (!window.screenShaker && typeof ScreenShaker !== 'undefined') {
                window.screenShaker = new ScreenShaker();
            }

            if (!window.comboSystem && typeof ComboSystem !== 'undefined') {
                window.comboSystem = new ComboSystem();
            }

            if (!window.confettiEffects && typeof ConfettiEffects !== 'undefined') {
                window.confettiEffects = new ConfettiEffects();
            }

            if (!window.floatingText && typeof FloatingText !== 'undefined') {
                window.floatingText = FloatingText;
            }
        }

        static initLoadingScreen() {
            // Создаем экран загрузки если его нет
            if (!document.getElementById('loading-screen')) {
                const loadingScreen = document.createElement('div');
                loadingScreen.id = 'loading-screen';
                loadingScreen.className = 'loading-screen';
                loadingScreen.innerHTML = `
                    <div class="loading-spinner"></div>
                    <div class="loading-text">ЗАГРУЗКА ЭФФЕКТОВ...</div>
                    <div class="loading-progress">
                        <div class="loading-progress-bar" id="loading-progress"></div>
                    </div>
                `;
                document.body.appendChild(loadingScreen);

                // Симулируем загрузку
                let progress = 0;
                const interval = setInterval(() => {
                    progress += Math.random() * 20;
                    if (progress >= 100) {
                        progress = 100;
                        clearInterval(interval);

                        setTimeout(() => {
                            loadingScreen.style.opacity = '0';
                            setTimeout(() => {
                                loadingScreen.remove();
                                // Уведомляем о завершении загрузки
                                if (window.audioManager) {
                                    window.audioManager.playRandomSound('upgrade');
                                }
                            }, 500);
                        }, 500);
                    }

                    const progressBar = document.getElementById('loading-progress');
                    if (progressBar) {
                        progressBar.style.width = `${progress}%`;
                    }
                }, 100);
            }
        }

        static setupGlobalEffects() {
            // Добавляем глобальные эффекты для всех страниц

            // Эффект при наведении на кнопки
            document.querySelectorAll('button, .btn, .nav-link').forEach(btn => {
                btn.addEventListener('mouseenter', function() {
                    if (window.audioManager) {
                        window.audioManager.playSpatialSound(
                            this.getBoundingClientRect().left,
                            this.getBoundingClientRect().top
                        );
                    }

                    // Эффект свечения
                    this.classList.add('hover-effect');
                });

                btn.addEventListener('mouseleave', function() {
                    this.classList.remove('hover-effect');
                });
            });

            // Эффект при клике на ссылки
            document.querySelectorAll('a').forEach(link => {
                link.addEventListener('click', function(e) {
                    if (this.href && !this.href.includes('javascript:')) {
                        // Создаем эффект перехода
                        if (window.particleSystem) {
                            const rect = this.getBoundingClientRect();
                            const x = rect.left + rect.width / 2;
                            const y = rect.top + rect.height / 2;
                            window.particleSystem.createParticles(x, y, 5, '#00BCD4', 'link');
                        }

                        // Звук клика
                        if (window.audioManager) {
                            window.audioManager.playRandomSound('click');
                        }
                    }
                });
            });

            // Эффект для форм
            document.querySelectorAll('input, textarea, select').forEach(input => {
                input.addEventListener('focus', function() {
                    this.classList.add('focus-effect');

                    if (window.audioManager) {
                        window.audioManager.playRandomSound('click');
                    }
                });

                input.addEventListener('blur', function() {
                    this.classList.remove('focus-effect');
                });
            });

            // Плавная прокрутка
            document.querySelectorAll('a[href^="#"]').forEach(anchor => {
                anchor.addEventListener('click', function(e) {
                    e.preventDefault();
                    const targetId = this.getAttribute('href');
                    if (targetId === '#') return;

                    const targetElement = document.querySelector(targetId);
                    if (targetElement) {
                        // Эффект перед прокруткой
                        if (window.particleSystem) {
                            const rect = targetElement.getBoundingClientRect();
                            const x = rect.left + rect.width / 2;
                            const y = rect.top + rect.height / 2;
                            window.particleSystem.createParticles(x, y, 10, '#FF4081', 'scroll');
                        }

                        // Плавная прокрутка
                        targetElement.scrollIntoView({
                            behavior: 'smooth',
                            block: 'start'
                        });
                    }
                });
            });
        }

        // Статические методы для глобального использования
        static showNotification(message, type = 'info') {
            const notification = document.createElement('div');
            notification.className = `global-notification ${type}`;
            notification.innerHTML = `
                <i class="fas fa-${type === 'success' ? 'check-circle' :
                                type === 'error' ? 'exclamation-circle' :
                                type === 'warning' ? 'exclamation-triangle' : 'info-circle'}"></i>
                <span>${message}</span>
                <button class="btn-close-notification">&times;</button>
            `;

            document.body.appendChild(notification);

            // Автоматическое скрытие
            setTimeout(() => {
                notification.style.opacity = '0';
                notification.style.transform = 'translateY(-20px)';
                setTimeout(() => notification.remove(), 300);
            }, 3000);

            // Закрытие по клику
            notification.querySelector('.btn-close-notification').addEventListener('click', () => {
                notification.remove();
            });

            // Звук уведомления
            if (window.audioManager) {
                window.audioManager.playRandomSound('upgrade');
            }
        }

        static createExplosion(x, y, color = '#FF4081', count = 30) {
            if (window.particleSystem) {
                window.particleSystem.createParticles(x, y, count, color, 'explosion');
            }

            // Экран трясется
            if (window.screenShaker) {
                window.screenShaker.shake(5, 300);
            }

            // Звук взрыва
            if (window.audioManager) {
                window.audioManager.playRandomSound('achievement');
            }
        }

        static createSparkles(element, count = 20) {
            const rect = element.getBoundingClientRect();
            const x = rect.left + rect.width / 2;
            const y = rect.top + rect.height / 2;

            if (window.particleSystem) {
                for (let i = 0; i < count; i++) {
                    setTimeout(() => {
                        window.particleSystem.createParticles(x, y, 3, '#FFD700', 'sparkle');
                    }, i * 50);
                }
            }
        }
    }
    // Make GameEffects globally available
    window.GameEffects = GameEffects;
}

