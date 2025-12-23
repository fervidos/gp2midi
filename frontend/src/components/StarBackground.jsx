import React, { useEffect, useRef } from 'react';

const StarBackground = () => {
    const canvasRef = useRef(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        let animationFrameId;

        // Configuration
        const STAR_COUNT = 800; // Unused but good for reference, loop below uses LAYERS
        const LAYERS = [
            { speed: 0.05, size: 0.5, count: 400 }, // Background (Slow, Small)
            { speed: 0.1, size: 1.0, count: 300 },  // Midground
            { speed: 0.3, size: 2.0, count: 100 }   // Foreground (Fast, Big)
        ];

        let stars = [];
        let shootingStars = [];
        let width = 0;
        let height = 0;

        // Mouse Parallax State
        let mouseX = 0;
        let mouseY = 0;
        let targetX = 0;
        let targetY = 0;
        let windowHalfX = 0;
        let windowHalfY = 0;

        // Helper: Random Range
        const random = (min, max) => Math.random() * (max - min) + min;

        // Class: Star
        class Star {
            constructor(layerSettings) {
                this.x = random(0, width);
                this.y = random(0, height);
                this.size = random(layerSettings.size * 0.8, layerSettings.size * 1.2);
                this.speed = layerSettings.speed * random(0.8, 1.2);
                this.parallaxFactor = layerSettings.speed * 400; // Sensitivity factor
                this.opacity = random(0.3, 1.0);
                this.baseOpacity = this.opacity;
                this.twinkleSpeed = random(0.005, 0.02);
                this.twinkleDir = 1;
            }

            update() {
                // Natural Drift (Vertical)
                this.y -= this.speed * 0.5; // Natural rise

                // Wrap around (Natural drift only)
                if (this.y < -10) this.y = height + 10;

                // Twinkle
                this.opacity += this.twinkleSpeed * this.twinkleDir;
                if (this.opacity > 1 || this.opacity < this.baseOpacity * 0.5) {
                    this.twinkleDir *= -1;
                }
            }

            draw(offsetX, offsetY) {
                // Apply Parallax Offset with wrapping
                let drawX = (this.x + (offsetX * this.speed * 50)) % width;
                let drawY = (this.y + (offsetY * this.speed * 50)) % height;

                if (drawX < 0) drawX += width;
                if (drawY < 0) drawY += height;

                ctx.fillStyle = `rgba(255, 255, 255, ${this.opacity})`;
                ctx.beginPath();
                ctx.arc(drawX, drawY, this.size, 0, Math.PI * 2);
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
                // Shooting stars ignored by parallax for effect
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

                ctx.fillStyle = `rgba(255, 255, 255, ${this.life})`;
                ctx.beginPath();
                ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
                ctx.fill();

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
            windowHalfX = width / 2;
            windowHalfY = height / 2;
            canvas.width = width;
            canvas.height = height;
        };

        const onMouseMove = (e) => {
            // Logic: Mouse moves right -> looks left -> stars move right
            // Start from center
            mouseX = (e.clientX - windowHalfX) / width; // -0.5 to 0.5
            mouseY = (e.clientY - windowHalfY) / height;
        };

        // Loop
        const animate = () => {
            ctx.clearRect(0, 0, width, height);

            // Smooth camera movement (Lerp)
            // We want range of maybe -200px to 200px magnitude?
            // targetX is the offset factor
            targetX += (mouseX - targetX) * 0.05;
            targetY += (mouseY - targetY) * 0.05;

            // Draw Stars
            stars.forEach(star => {
                star.update(); // Natural drift
                star.draw(targetX, targetY); // Parallax offset
            });

            // Manage Shooting Stars
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
        window.addEventListener('mousemove', onMouseMove);
        init();
        animate();

        return () => {
            window.removeEventListener('resize', resize);
            window.removeEventListener('mousemove', onMouseMove);
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
                // No pointerEvents: none, so mouse works? 
                // No, mouse works on window. 
                // We want clicks to pass through to elements below?
                // Wait, zIndex is -1. So elements are ABOVE it. 
                // Elements need to capture clicks.
                pointerEvents: 'none',
                background: 'radial-gradient(ellipse at bottom, #1B2735 0%, #090A0F 100%)'
            }}
        />
    );
};

export default StarBackground;
