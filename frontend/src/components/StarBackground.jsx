import React, { useEffect, useRef } from 'react';

const StarBackground = () => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let animationFrameId;

        // Configuration
        const STAR_COUNT = 800;
        const LAYERS = [
            { speed: 0.05, size: 0.5, count: 400 }, // Background (Slow, Small)
            { speed: 0.1, size: 1.0, count: 300 },  // Midground
            { speed: 0.3, size: 2.0, count: 100 }   // Foreground (Fast, Big)
        ];

        let stars = [];
        let shootingStars = [];
        let width = 0;
        let height = 0;

        // Helper: Random Range
        const random = (min, max) => Math.random() * (max - min) + min;

        // Class: Star
        class Star {
            constructor(layerSettings) {
                this.x = random(0, width);
                this.y = random(0, height);
                this.size = random(layerSettings.size * 0.8, layerSettings.size * 1.2);
                this.speed = layerSettings.speed * random(0.8, 1.2);
                this.opacity = random(0.3, 1.0);
                this.baseOpacity = this.opacity;
                this.twinkleSpeed = random(0.005, 0.02);
                this.twinkleDir = 1;
            }

            update() {
                // Movement (Deep Space Drift - vertical mostly)
                this.y -= this.speed; // Move up

                // Wrap around
                if (this.y < 0) {
                    this.y = height;
                    this.x = random(0, width);
                }

                // Twinkle
                this.opacity += this.twinkleSpeed * this.twinkleDir;
                if (this.opacity > 1 || this.opacity < this.baseOpacity * 0.5) {
                    this.twinkleDir *= -1;
                }
            }

            draw() {
                ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();
            }
        }

        // Class: ShootingStar
        class ShootingStar {
            constructor() {
                this.reset();
            }

            reset() {
                this.x = random(0, width);
                this.y = random(0, height / 2); // Start in top half
                this.length = 0;
                this.maxLength = random(100, 300);
                this.speed = random(5, 10);
                this.size = random(1, 2);
                this.angle = random(30, 60) * (Math.PI / 180); // Degrees to Radians
                this.life = random(0.5, 1.0); // Opacity/Life
                this.active = true;
            }

            update() {
                if (!this.active) return;

                this.x -= Math.cos(this.angle) * this.speed;
                this.y += Math.sin(this.angle) * this.speed;
                this.length += this.speed;
                this.life -= 0.01;

                if (this.life <= 0 || this.x < 0 || this.y > height) {
                    this.active = false;
                }
            }

            draw() {
                if (!this.active) return;

                const tailX = this.x + Math.cos(this.angle) * Math.min(this.length, this.maxLength);
                const tailY = this.y - Math.sin(this.angle) * Math.min(this.length, this.maxLength);

                const gradient = ctx.createLinearGradient(this.x, this.y, tailX, tailY);
                gradient.addColorStop(0, `rgba(255, 255, 255, ${this.life})`);
                gradient.addColorStop(1, `rgba(255, 255, 255, 0)`);

                ctx.strokeStyle = gradient;
                ctx.lineWidth = this.size;
                ctx.beginPath();
                ctx.moveTo(this.x, this.y);
                ctx.lineTo(tailX, tailY);
                ctx.stroke();

                // Head
                ctx.fillStyle = `rgba(255, 255, 255, ${this.life})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();

                // Glow
                ctx.shadowBlur = 10;
                ctx.shadowColor = "white";
                ctx.stroke();
                ctx.shadowBlur = 0;
            }
        }

        // Initialize
        const init = () => {
            resize();
            stars = [];
            LAYERS.forEach(layer => {
                for (let i = 0; i < layer.count; i++) {
                    stars.push(new Star(layer));
                }
            });
        };

        const resize = () => {
            width = window.innerWidth;
            height = window.innerHeight;
            canvas.width = width;
            canvas.height = height;
        };

        // Loop
        const animate = () => {
            // Clear with semi-transparent black for trails? No, crisp stars here.
            ctx.clearRect(0, 0, width, height);

            // Draw Stars
            stars.forEach(star => {
                star.update();
                star.draw();
            });

            // Manage Shooting Stars
            // Spawn chance
            if (Math.random() < 0.005 && shootingStars.length < 3) {
                shootingStars.push(new ShootingStar());
            }

            shootingStars = shootingStars.filter(s => s.active);
            shootingStars.forEach(s => {
                s.update();
                s.draw();
            });

            animationFrameId = requestAnimationFrame(animate);
        };

        window.addEventListener('resize', resize);
        init();
        animate();

        return () => {
            window.removeEventListener('resize', resize);
            cancelAnimationFrame(animationFrameId);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            style={{
                position: 'fixed',
                top: 0,
                left: 0,
                width: '100%',
                height: '100%',
                zIndex: -1,
                pointerEvents: 'none',
                background: 'radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%)' // Deep Space Background
            }}
        />
    );
};

export default StarBackground;
