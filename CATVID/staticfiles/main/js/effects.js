// Particle system for visual effects
class ParticleSystem {
    constructor() {
        this.particles = [];
        this.canvas = null;
        this.ctx = null;
        this.initCanvas();
    }

    initCanvas() {
        // Check if canvas already exists
        const existingCanvas = document.getElementById('particle-canvas');
        if (existingCanvas) {
            this.canvas = existingCanvas;
        } else {
            this.canvas = document.createElement('canvas');
            this.canvas.id = 'particle-canvas';
            this.canvas.style.cssText = `
                position: fixed;
                top: 0;
                left: 0;
                width: 100%;
                height: 100%;
                pointer-events: none;
                z-index: 9998;
            `;
            document.body.appendChild(this.canvas);
        }
        
        try {
            this.ctx = this.canvas.getContext('2d');
            if (!this.ctx) {
                console.warn('Canvas 2D context not available');
                return;
            }
        } catch (error) {
            console.error('Error getting canvas context:', error);
            return;
        }
        
        this.resizeCanvas();
        window.addEventListener('resize', () => this.resizeCanvas());
        this.animate();
    }

    resizeCanvas() {
        this.canvas.width = window.innerWidth;
        this.canvas.height = window.innerHeight;
    }

    createParticles(x, y, count, color, type = 'explosion') {
        for (let i = 0; i < count; i++) {
            this.particles.push({
                x,
                y,
                vx: (Math.random() - 0.5) * 10,
                vy: (Math.random() - 0.5) * 10 - 5,
                radius: Math.random() * 4 + 2,
                color: color || this.getRandomColor(),
                life: 1,
                decay: Math.random() * 0.02 + 0.01,
                type
            });
        }
    }

    createCoinParticles(x, y, amount) {
        for (let i = 0; i < Math.min(amount, 50); i++) {
            this.particles.push({
                x,
                y,
                vx: (Math.random() - 0.5) * 8,
                vy: (Math.random() - 0.5) * 8 - 3,
                radius: Math.random() * 3 + 1,
                color: '#FFD700',
                life: 1,
                decay: Math.random() * 0.015 + 0.005,
                type: 'coin',
                rotation: Math.random() * Math.PI * 2
            });
        }
    }

    createTextParticle(x, y, text, color = '#FFD700') {
        this.particles.push({
            x,
            y,
            vx: 0,
            vy: -2,
            text,
            color,
            life: 1,
            decay: 0.01,
            type: 'text',
            fontSize: 20
        });
    }

    getRandomColor() {
        const colors = [
            '#FF4081', '#00BCD4', '#4CAF50', '#FF9800',
            '#9C27B0', '#2196F3', '#FF5722', '#E91E63'
        ];
        return colors[Math.floor(Math.random() * colors.length)];
    }

    animate() {
        if (!this.ctx) return;
        
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);

        for (let i = this.particles.length - 1; i >= 0; i--) {
            const p = this.particles[i];

            p.x += p.vx;
            p.y += p.vy;
            p.vy += 0.1; // gravity
            p.life -= p.decay;

            if (p.type === 'coin') {
                p.rotation += 0.1;
            }

            if (p.life <= 0) {
                this.particles.splice(i, 1);
                continue;
            }

            this.ctx.globalAlpha = p.life;

            if (p.type === 'text') {
                this.ctx.fillStyle = p.color;
                this.ctx.font = `${p.fontSize}px 'Press Start 2P'`;
                this.ctx.fillText(p.text, p.x, p.y);
            } else {
                this.ctx.fillStyle = p.color;
                this.ctx.beginPath();

                if (p.type === 'coin') {
                    // Draw coin with rotation
                    this.ctx.save();
                    this.ctx.translate(p.x, p.y);
                    this.ctx.rotate(p.rotation);
                    this.ctx.fillRect(-p.radius, -p.radius, p.radius * 2, p.radius * 2);
                    this.ctx.restore();
                } else {
                    this.ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
                }

                this.ctx.fill();
            }
        }

        requestAnimationFrame(() => this.animate());
    }
}

// Screen shake effect
class ScreenShaker {
    constructor() {
        this.isShaking = false;
        this.intensity = 0;
        this.originalTransform = '';
    }

    shake(intensity = 5, duration = 300) {
        if (this.isShaking) return;

        this.isShaking = true;
        this.intensity = intensity;
        this.originalTransform = document.body.style.transform;

        let startTime = Date.now();

        const shakeFrame = () => {
            if (!this.isShaking) return;

            const elapsed = Date.now() - startTime;
            const progress = Math.min(elapsed / duration, 1);

            if (progress >= 1) {
                this.stopShake();
                return;
            }

            const currentIntensity = this.intensity * (1 - progress);
            const x = (Math.random() - 0.5) * currentIntensity * 2;
            const y = (Math.random() - 0.5) * currentIntensity * 2;

            document.body.style.transform = `translate(${x}px, ${y}px)`;
            requestAnimationFrame(shakeFrame);
        };

        shakeFrame();

        setTimeout(() => this.stopShake(), duration);
    }

    stopShake() {
        this.isShaking = false;
        document.body.style.transform = this.originalTransform;
    }
}

// Floating text effect
class FloatingText {
    static show(text, x, y, color = '#FFD700') {
        const floatingText = document.createElement('div');
        floatingText.className = 'floating-text';
        floatingText.textContent = text;
        floatingText.style.cssText = `
            position: fixed;
            left: ${x}px;
            top: ${y}px;
            color: ${color};
            font-family: 'Press Start 2P', cursive;
            font-size: 14px;
            font-weight: bold;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            pointer-events: none;
            z-index: 9999;
            opacity: 1;
            transition: all 1s ease-out;
        `;

        document.body.appendChild(floatingText);

        setTimeout(() => {
            floatingText.style.transform = 'translateY(-50px)';
            floatingText.style.opacity = '0';
        }, 10);

        setTimeout(() => {
            floatingText.remove();
        }, 1000);
    }
}

// Combo system
class ComboSystem {
    constructor() {
        this.combo = 0;
        this.lastClickTime = 0;
        this.comboTimeout = 500; // ms
        this.maxCombo = 0;
        this.comboElement = null;
        this.initComboDisplay();
    }

    initComboDisplay() {
        this.comboElement = document.createElement('div');
        this.comboElement.id = 'combo-display';
        this.comboElement.style.cssText = `
            position: fixed;
            top: 20px;
            right: 20px;
            font-family: 'Press Start 2P', cursive;
            font-size: 1.5rem;
            color: #FFD700;
            text-shadow: 0 0 10px rgba(255, 215, 0, 0.5);
            z-index: 9999;
            opacity: 0;
            transition: opacity 0.3s;
        `;
        document.body.appendChild(this.comboElement);
    }

    addClick() {
        const now = Date.now();

        if (now - this.lastClickTime < this.comboTimeout) {
            this.combo++;
        } else {
            this.combo = 1;
        }

        this.lastClickTime = now;
        this.showCombo();

        if (this.combo > this.maxCombo) {
            this.maxCombo = this.combo;
        }

        this.resetComboTimer();
    }

    showCombo() {
        if (this.combo > 1) {
            this.comboElement.textContent = `${this.combo} COMBO!`;
            this.comboElement.style.opacity = '1';
            this.comboElement.style.color = this.getComboColor();

            // Add combo effects
            window.particleSystem?.createParticles(
                window.innerWidth - 100,
                50,
                Math.min(this.combo * 2, 20),
                this.getComboColor()
            );

            if (this.combo % 10 === 0) {
                window.screenShaker?.shake(3 + Math.floor(this.combo / 10));
            }
        }
    }

    getComboColor() {
        if (this.combo >= 50) return '#FF4081';
        if (this.combo >= 30) return '#9C27B0';
        if (this.combo >= 20) return '#2196F3';
        if (this.combo >= 10) return '#4CAF50';
        return '#FFD700';
    }

    resetComboTimer() {
        clearTimeout(this.comboTimer);
        this.comboTimer = setTimeout(() => {
            this.combo = 0;
            this.comboElement.style.opacity = '0';
        }, this.comboTimeout);
    }
}

// Initialize effects
document.addEventListener('DOMContentLoaded', function() {
    // Only initialize if not already initialized
    if (!window.particleSystem) {
        window.particleSystem = new ParticleSystem();
    }
    if (!window.screenShaker) {
        window.screenShaker = new ScreenShaker();
    }
    if (!window.comboSystem) {
        window.comboSystem = new ComboSystem();
    }
    if (!window.floatingText) {
        window.floatingText = FloatingText;
    }
});