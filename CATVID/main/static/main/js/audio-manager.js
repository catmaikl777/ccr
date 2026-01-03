// Simple Audio Manager using local files
if (typeof window.EnhancedAudioManager === 'undefined') {
    class EnhancedAudioManager {
        constructor() {
            if (window.audioManagerInstance) {
                return window.audioManagerInstance;
            }
            window.audioManagerInstance = this;
            this.sounds = {};
            this.musicVolume = 0.3;
            this.sfxVolume = 0.5;
            this.isMuted = false;
            this.init();
        }

        init() {
            this.loadSounds();
            this.setupEventListeners();
        }

        loadSounds() {
            // Используем локальные файлы
            const basePath = '/static/main/sounds/';
            
            // Основные звуки кликов
            this.sounds.click = [
                basePath + 'click.mp3',
                basePath + 'meow1.mp3',
                basePath + 'meow2.mp3'
            ];

            // Критические удары (используем те же звуки)
            this.sounds.critical = [
                basePath + 'meow3.mp3',
                basePath + 'click.mp3'
            ];

            // Улучшения
            this.sounds.upgrade = [
                basePath + 'meow1.mp3',
                basePath + 'meow2.mp3'
            ];

            // Достижения
            this.sounds.achievement = [
                basePath + 'meow3.mp3',
                basePath + 'click.mp3'
            ];

            // Скины
            this.sounds.skin = [
                basePath + 'meow1.mp3',
                basePath + 'meow2.mp3'
            ];

            // Фоновая музыка
            this.sounds.music = [
                basePath + 'bg.mp3'
            ];
        }

        async playSound(type, variant = 0) {
            if (this.isMuted || !this.sounds[type]) {
                console.log('Sound muted or type not found:', type);
                return null;
            }

            try {
                const soundUrl = this.sounds[type][variant % this.sounds[type].length];
                console.log('Playing sound:', soundUrl);
                
                const audio = new Audio(soundUrl);
                audio.volume = this.sfxVolume;
                audio.preload = 'auto';

                const playPromise = audio.play();
                if (playPromise !== undefined) {
                    await playPromise;
                    console.log('✅ Sound played successfully');
                }
                return audio;
            } catch (error) {
                console.warn('❌ Sound play failed:', error);
                return null;
            }
        }

        playRandomSound(type) {
            if (!this.sounds[type]) return;
            const variant = Math.floor(Math.random() * this.sounds[type].length);
            this.playSound(type, variant);
        }

        playMusic() {
            if (this.isMuted || this.currentMusic) {
                console.log('Music muted or already playing');
                return;
            }

            try {
                const musicUrl = this.sounds.music[0];
                console.log('Starting background music:', musicUrl);
                
                this.currentMusic = new Audio(musicUrl);
                this.currentMusic.loop = true;
                this.currentMusic.volume = this.musicVolume;
                this.currentMusic.preload = 'auto';

                this.currentMusic.play().then(() => {
                    console.log('✅ Background music started');
                }).catch(e => {
                    console.warn('❌ Music autoplay prevented:', e);
                });
            } catch (error) {
                console.error('❌ Music initialization failed:', error);
            }
        }

        stopMusic() {
            if (this.currentMusic) {
                this.currentMusic.pause();
                this.currentMusic.currentTime = 0;
                this.currentMusic = null;
            }
        }

        toggleMute() {
            this.isMuted = !this.isMuted;

            if (this.isMuted) {
                this.stopMusic();
            } else {
                this.playMusic();
            }

            return this.isMuted;
        }

        setVolume(type, volume) {
            if (type === 'music') {
                this.musicVolume = volume;
                if (this.currentMusic) {
                    this.currentMusic.volume = volume;
                }
            } else if (type === 'sfx') {
                this.sfxVolume = volume;
            }
        }

        // Простая функция для воспроизведения звука клика
        playClickSound() {
            this.playRandomSound('click');
        }

        setupEventListeners() {
            // Запуск звуков при первом взаимодействии
            const startAudio = () => {
                console.log('🎵 User interaction detected, starting audio...');
                this.playMusic();
                // Тестовый звук
                this.playRandomSound('click');
            };

            document.addEventListener('click', startAudio, { once: true });
            document.addEventListener('touchstart', startAudio, { once: true });
            
            console.log('🎵 Audio event listeners set up');
        }

        // Специальные звуковые эффекты
        playCoinSound(amount) {
            if (amount >= 1000) {
                this.playSound('achievement', 0);
            } else if (amount >= 100) {
                this.playSound('upgrade', 0);
            } else {
                this.playRandomSound('click');
            }
        }

        playLevelUpSound() {
            this.playSound('achievement', 0);
        }

        playUpgradeSound() {
            this.playSound('upgrade', 0);
        }
    }
    // Make EnhancedAudioManager globally available
    window.EnhancedAudioManager = EnhancedAudioManager;
    
    console.log('🎵 EnhancedAudioManager class defined');
}