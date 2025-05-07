// Advanced Level 89 Animations for Tryambakam Intelligence System

// Global variables
let particleCanvas, neuralNetworkCanvas;
let isInitialized = false;
let audioContext, audioBuffers = {};

// Initialize all animations
function initializeAnimations() {
    if (isInitialized) return;
    isInitialized = true;
    
    // Create particle background
    createParticleBackground();
    
    // Create neural network background
    createNeuralNetwork();
    
    // Add glitch effect to titles
    addGlitchEffect();
    
    // Add holographic effect to cards
    addHolographicEffect();
    
    // Add typing effect to AI responses
    addTypingEffect();
    
    // Add scan lines effect
    addScanLinesEffect();
    
    // Add pulse effect to buttons
    addButtonEffects();
    
    // Add 3D tilt effect to cards
    add3DTiltEffect();
    
    // Add audio feedback
    initializeAudioFeedback();
    
    // Add data visualization animations
    initializeDataVisualizations();
    
    // Add voice waveform animation
    createVoiceWaveform();
    
    // Add matrix code rain effect
    createMatrixEffect();
    
    // Add cybernetic interface elements
    createCyberneticInterface();
    
    // Add responsive animations
    window.addEventListener('resize', handleResize);
    
    // Add AI thinking animation
    createAIThinkingAnimation();
    
    // Add memory lane visualization
    createMemoryLaneVisualization();
    
    // Add expert knowledge graph
    createExpertKnowledgeGraph();
    
    // Add vision analysis overlay
    createVisionAnalysisOverlay();
}

// Enhanced particle background with connection lines
function createParticleBackground() {
    particleCanvas = document.createElement('canvas');
    particleCanvas.id = 'particle-background';
    particleCanvas.style.position = 'fixed';
    particleCanvas.style.top = '0';
    particleCanvas.style.left = '0';
    particleCanvas.style.width = '100%';
    particleCanvas.style.height = '100%';
    particleCanvas.style.zIndex = '-1';
    particleCanvas.style.opacity = '0.4';
    document.body.appendChild(particleCanvas);

    const ctx = particleCanvas.getContext('2d');
    particleCanvas.width = window.innerWidth;
    particleCanvas.height = window.innerHeight;

    const particles = [];
    const particleCount = 150;
    const connectionDistance = 150;
    const mouseInfluence = 200;
    let mouseX = particleCanvas.width / 2;
    let mouseY = particleCanvas.height / 2;

    // Track mouse position
    document.addEventListener('mousemove', (e) => {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    // Create particles
    for (let i = 0; i < particleCount; i++) {
        particles.push({
            x: Math.random() * particleCanvas.width,
            y: Math.random() * particleCanvas.height,
            radius: Math.random() * 2 + 1,
            color: `rgba(${Math.floor(Math.random() * 100 + 155)}, ${Math.floor(Math.random() * 100 + 155)}, 255, ${Math.random() * 0.5 + 0.5})`,
            speedX: Math.random() * 0.5 - 0.25,
            speedY: Math.random() * 0.5 - 0.25,
            lastX: 0,
            lastY: 0
        });
    }

    function animate() {
        requestAnimationFrame(animate);
        ctx.clearRect(0, 0, particleCanvas.width, particleCanvas.height);

        // Draw connections first (behind particles)
        ctx.lineWidth = 0.5;
        for (let i = 0; i < particleCount; i++) {
            const p1 = particles[i];
            
            // Connect to nearby particles
            for (let j = i + 1; j < particleCount; j++) {
                const p2 = particles[j];
                const dx = p1.x - p2.x;
                const dy = p1.y - p2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < connectionDistance) {
                    // Calculate opacity based on distance
                    const opacity = 1 - (distance / connectionDistance);
                    
                    // Draw connection line
                    ctx.beginPath();
                    ctx.strokeStyle = `rgba(0, 204, 255, ${opacity * 0.2})`;
                    ctx.moveTo(p1.x, p1.y);
                    ctx.lineTo(p2.x, p2.y);
                    ctx.stroke();
                }
            }
            
            // Connect to mouse if nearby
            const dxMouse = p1.x - mouseX;
            const dyMouse = p1.y - mouseY;
            const distanceMouse = Math.sqrt(dxMouse * dxMouse + dyMouse * dyMouse);
            
            if (distanceMouse < connectionDistance * 1.5) {
                const opacity = 1 - (distanceMouse / (connectionDistance * 1.5));
                
                ctx.beginPath();
                ctx.strokeStyle = `rgba(0, 255, 204, ${opacity * 0.5})`;
                ctx.moveTo(p1.x, p1.y);
                ctx.lineTo(mouseX, mouseY);
                ctx.stroke();
            }
        }

        // Update and draw particles
        for (let i = 0; i < particleCount; i++) {
            const p = particles[i];
            
            // Save last position for trail effect
            p.lastX = p.x;
            p.lastY = p.y;
            
            // Update position
            p.x += p.speedX;
            p.y += p.speedY;
            
            // Mouse influence
            const dx = mouseX - p.x;
            const dy = mouseY - p.y;
            const distance = Math.sqrt(dx * dx + dy * dy);
            
            if (distance < mouseInfluence) {
                const force = (mouseInfluence - distance) / mouseInfluence;
                p.speedX -= dx * force * 0.02;
                p.speedY -= dy * force * 0.02;
            }
            
            // Boundary check with bounce
            if (p.x < 0 || p.x > particleCanvas.width) {
                p.speedX *= -1;
                p.x = p.x < 0 ? 0 : particleCanvas.width;
            }
            if (p.y < 0 || p.y > particleCanvas.height) {
                p.speedY *= -1;
                p.y = p.y < 0 ? 0 : particleCanvas.height;
            }
            
            // Speed limit
            const speed = Math.sqrt(p.speedX * p.speedX + p.speedY * p.speedY);
            if (speed > 2) {
                p.speedX = (p.speedX / speed) * 2;
                p.speedY = (p.speedY / speed) * 2;
            }
            
            // Draw particle
            ctx.beginPath();
            ctx.arc(p.x, p.y, p.radius, 0, Math.PI * 2);
            ctx.fillStyle = p.color;
            ctx.fill();
            
            // Draw trail
            ctx.beginPath();
            ctx.strokeStyle = p.color.replace(')', ', 0.3)').replace('rgba', 'rgba');
            ctx.moveTo(p.lastX, p.lastY);
            ctx.lineTo(p.x, p.y);
            ctx.stroke();
        }
    }

    animate();
}

// Create neural network background
function createNeuralNetwork() {
    neuralNetworkCanvas = document.createElement('canvas');
    neuralNetworkCanvas.id = 'neural-network';
    neuralNetworkCanvas.className = 'neural-network';
    document.body.appendChild(neuralNetworkCanvas);

    const ctx = neuralNetworkCanvas.getContext('2d');
    neuralNetworkCanvas.width = window.innerWidth;
    neuralNetworkCanvas.height = window.innerHeight;

    // Neural network parameters
    const layers = [5, 10, 8, 6, 4]; // Number of neurons per layer
    const neurons = [];
    const connections = [];
    const layerDistance = neuralNetworkCanvas.width / (layers.length + 1);
    const activationWaves = [];

    // Create neurons
    for (let l = 0; l < layers.length; l++) {
        const layerSize = layers[l];
        const x = layerDistance * (l + 1);
        const verticalSpacing = neuralNetworkCanvas.height / (layerSize + 1);
        
        for (let n = 0; n < layerSize; n++) {
            const y = verticalSpacing * (n + 1);
            neurons.push({
                x,
                y,
                layer: l,
                radius: 4,
                activation: 0,
                targetActivation: 0
            });
            
            // Create connections to previous layer
            if (l > 0) {
                const prevLayerStart = neurons.findIndex(neuron => neuron.layer === l - 1);
                const prevLayerSize = layers[l - 1];
                
                for (let p = 0; p < prevLayerSize; p++) {
                    const prevNeuronIndex = prevLayerStart + p;
                    const weight = Math.random() * 2 - 1; // Random weight between -1 and 1
                    
                    connections.push({
                        from: prevNeuronIndex,
                        to: neurons.length - 1,
                        weight
                    });
                }
            }
        }
    }

    // Function to trigger activation wave
    function triggerActivation() {
        // Randomly activate input neurons
        const inputLayerIndices = neurons
            .map((neuron, index) => neuron.layer === 0 ? index : -1)
            .filter(index => index !== -1);
        
        // Randomly select 1-3 input neurons to activate
        const numToActivate = Math.floor(Math.random() * 3) + 1;
        for (let i = 0; i < numToActivate; i++) {
            const randomIndex = inputLayerIndices[Math.floor(Math.random() * inputLayerIndices.length)];
            neurons[randomIndex].targetActivation = Math.random() * 0.5 + 0.5; // Random activation between 0.5 and 1
        }
        
        // Create activation wave
        activationWaves.push({
            progress: 0,
            speed: 0.01 + Math.random() * 0.02 // Random speed
        });
        
        // Schedule next activation
        setTimeout(triggerActivation, 2000 + Math.random() * 3000);
    }

    // Start activation waves
    triggerActivation();

    function animate() {
        requestAnimationFrame(animate);
        ctx.clearRect(0, 0, neuralNetworkCanvas.width, neuralNetworkCanvas.height);
        
        // Process activation waves
        for (let i = activationWaves.length - 1; i >= 0; i--) {
            const wave = activationWaves[i];
            wave.progress += wave.speed;
            
            if (wave.progress >= 1) {
                activationWaves.splice(i, 1);
                continue;
            }
            
            // Determine which layer should be activated based on wave progress
            const activeLayerIndex = Math.floor(wave.progress * layers.length);
            
            // Propagate activations through the network
            if (activeLayerIndex > 0) {
                const currentLayerNeurons = neurons.filter(n => n.layer === activeLayerIndex);
                const prevLayerNeurons = neurons.filter(n => n.layer === activeLayerIndex - 1);
                
                // For each neuron in current layer, compute activation from previous layer
                for (const neuron of currentLayerNeurons) {
                    const neuronIndex = neurons.indexOf(neuron);
                    const incomingConnections = connections.filter(c => c.to === neuronIndex);
                    
                    let activation = 0;
                    for (const conn of incomingConnections) {
                        activation += neurons[conn.from].activation * conn.weight;
                    }
                    
                    // Apply sigmoid-like activation function
                    neuron.targetActivation = 1 / (1 + Math.exp(-activation * 2));
                }
            }
        }
        
        // Update neuron activations (smooth transition)
        for (const neuron of neurons) {
            neuron.activation += (neuron.targetActivation - neuron.activation) * 0.1;
        }
        
        // Draw connections
        for (const conn of connections) {
            const from = neurons[conn.from];
            const to = neurons[conn.to];
            const activation = from.activation;
            
            // Only draw active connections
            if (activation > 0.1) {
                const gradient = ctx.createLinearGradient(from.x, from.y, to.x, to.y);
                gradient.addColorStop(0, `rgba(0, 204, 255, ${activation * 0.7})`);
                gradient.addColorStop(1, `rgba(0, 255, 204, ${to.activation * 0.7})`);
                
                ctx.beginPath();
                ctx.strokeStyle = gradient;
                ctx.lineWidth = activation * 2;
                ctx.moveTo(from.x, from.y);
                ctx.lineTo(to.x, to.y);
                ctx.stroke();
            }
        }
        
        // Draw neurons
        for (const neuron of neurons) {
            const activation = neuron.activation;
            
            // Draw glow
            if (activation > 0.1) {
                ctx.beginPath();
                const gradient = ctx.createRadialGradient(
                    neuron.x, neuron.y, 0,
                    neuron.x, neuron.y, neuron.radius * 4
                );
                gradient.addColorStop(0, `rgba(0, 204, 255, ${activation * 0.8})`);
                gradient.addColorStop(1, 'rgba(0, 204, 255, 0)');
                ctx.fillStyle = gradient;
                ctx.arc(neuron.x, neuron.y, neuron.radius * 4, 0, Math.PI * 2);
                ctx.fill();
            }
            
            // Draw neuron
            ctx.beginPath();
            ctx.fillStyle = `rgba(255, 255, 255, ${0.3 + activation * 0.7})`;
            ctx.arc(neuron.x, neuron.y, neuron.radius, 0, Math.PI * 2);
            ctx.fill();
        }
    }

    animate();
}

// Add glitch effect to titles
function addGlitchEffect() {
    const titles = document.querySelectorAll('h1, h2, h3');
    
    titles.forEach(title => {
        // Store original text
        const originalText = title.textContent;
        title.setAttribute('data-text', originalText);
        
        // Create glitch animation
        title.addEventListener('mouseover', () => {
            if (title.classList.contains('glitching')) return;
            
            title.classList.add('glitching');
            
            let glitchInterval = setInterval(() => {
                // Create glitched text
                let glitchedText = '';
                const glitchChars = '!<>-_\\/[]{}—=+*^?#________';
                
                for (let i = 0; i < originalText.length; i++) {
                    // 10% chance to replace with glitch character
                    if (Math.random() < 0.1) {
                        glitchedText += glitchChars.charAt(Math.floor(Math.random() * glitchChars.length));
                    } else {
                        glitchedText += originalText.charAt(i);
                    }
                }
                
                title.textContent = glitchedText;
            }, 100);
            
            // Stop glitching after a short time
            setTimeout(() => {
                clearInterval(glitchInterval);
                title.textContent = originalText;
                title.classList.remove('glitching');
            }, 1000);
        });
    });
}

// Add holographic effect to cards
function addHolographicEffect() {
    const cards = document.querySelectorAll('.expert-card, .mode-card, .feature-card, .status-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left; // x position within the card
            const y = e.clientY - rect.top; // y position within the card
            
            // Calculate rotation based on mouse position
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            // Apply 3D rotation
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale3d(1.05, 1.05, 1.05)`;
            
            // Add holographic highlight
            const percentX = x / rect.width * 100;
            const percentY = y / rect.height * 100;
            card.style.background = `
                linear-gradient(135deg, rgba(30, 33, 48, 0.8) 0%, rgba(20, 23, 38, 0.8) 100%),
                radial-gradient(circle at ${percentX}% ${percentY}%, rgba(0, 204, 255, 0.3) 0%, rgba(0, 204, 255, 0) 50%)
            `;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = '';
            card.style.background = '';
        });
    });
}

// Add typing effect to AI responses
function addTypingEffect() {
    // Find AI message elements that don't have the typing effect yet
    const aiMessages = document.querySelectorAll('div[data-testid="stChatMessage"]:not([data-is-user="true"]):not(.typing-effect-applied)');
    
    aiMessages.forEach(message => {
        // Mark as processed
        message.classList.add('typing-effect-applied');
        
        // Get the message content
        const contentElement = message.querySelector('p');
        if (!contentElement) return;
        
        const originalContent = contentElement.textContent;
        contentElement.textContent = '';
        
        // Apply typing effect
        typeWriter(contentElement, originalContent, 10);
    });
    
    // Check for new messages periodically
    setTimeout(addTypingEffect, 1000);
}

// Add scan lines effect
function addScanLinesEffect() {
    const scanLines = document.createElement('div');
    scanLines.className = 'scan-lines';
    scanLines.style.position = 'fixed';
    scanLines.style.top = '0';
    scanLines.style.left = '0';
    scanLines.style.width = '100%';
    scanLines.style.height = '100%';
    scanLines.style.backgroundImage = 'linear-gradient(transparent 50%, rgba(0, 0, 0, 0.05) 50%)';
    scanLines.style.backgroundSize = '100% 4px';
    scanLines.style.pointerEvents = 'none';
    scanLines.style.zIndex = '9999';
    scanLines.style.opacity = '0.2';
    document.body.appendChild(scanLines);
}

// Add pulse effect to buttons
function addButtonEffects() {
    const buttons = document.querySelectorAll('.stButton > button');
    
    buttons.forEach(button => {
        button.addEventListener('click', () => {
            // Play button sound
            playSound('button');
            
            // Add ripple effect
            const ripple = document.createElement('span');
            ripple.className = 'button-ripple';
            button.appendChild(ripple);
            
            const rect = button.getBoundingClientRect();
            ripple.style.width = ripple.style.height = `${Math.max(rect.width, rect.height) * 2}px`;
            ripple.style.left = `${-rect.width / 2}px`;
            ripple.style.top = `${-rect.height / 2}px`;
            
            setTimeout(() => {
                ripple.remove();
            }, 600);
        });
    });
}

// Add 3D tilt effect to cards
function add3DTiltEffect() {
    const cards = document.querySelectorAll('.expert-card, .mode-card, .feature-card, .status-card');
    
    cards.forEach(card => {
        card.addEventListener('mousemove', (e) => {
            const rect = card.getBoundingClientRect();
            const x = e.clientX - rect.left;
            const y = e.clientY - rect.top;
            
            const centerX = rect.width / 2;
            const centerY = rect.height / 2;
            
            const rotateX = (y - centerY) / 10;
            const rotateY = (centerX - x) / 10;
            
            card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg)`;
        });
        
        card.addEventListener('mouseleave', () => {
            card.style.transform = 'perspective(1000px) rotateX(0) rotateY(0)';
        });
    });
}

// Initialize audio feedback
function initializeAudioFeedback() {
    try {
        audioContext = new (window.AudioContext || window.webkitAudioContext)();
        
        // Load sound effects
        loadSound('typing', 'https://assets.mixkit.co/sfx/preview/mixkit-keyboard-key-hit-1594.mp3');
        loadSound('complete', 'https://assets.mixkit.co/sfx/preview/mixkit-software-interface-start-2574.mp3');
        loadSound('button', 'https://assets.mixkit.co/sfx/preview/mixkit-modern-technology-select-2-2566.mp3');
        loadSound('error', 'https://assets.mixkit.co/sfx/preview/mixkit-software-interface-remove-2576.mp3');
        loadSound('success', 'https://assets.mixkit.co/sfx/preview/mixkit-software-interface-back-2575.mp3');
    } catch (e) {
        console.error('Web Audio API not supported');
    }
}

// Load a sound file
function loadSound(name, url) {
    fetch(url)
        .then(response => response.arrayBuffer())
        .then(arrayBuffer => audioContext.decodeAudioData(arrayBuffer))
        .then(audioBuffer => {
            audioBuffers[name] = audioBuffer;
        })
        .catch(error => console.error('Error loading sound:', error));
}

// Play a sound
function playSound(name) {
    if (!audioContext || !audioBuffers[name]) return;
    
    const source = audioContext.createBufferSource();
    source.buffer = audioBuffers[name];
    source.connect(audioContext.destination);
    source.start(0);
}

// Handle window resize
function handleResize() {
    if (particleCanvas) {
        particleCanvas.width = window.innerWidth;
        particleCanvas.height = window.innerHeight;
    }
    
    if (neuralNetworkCanvas) {
        neuralNetworkCanvas.width = window.innerWidth;
        neuralNetworkCanvas.height = window.innerHeight;
    }
}

// Initialize data visualizations
function initializeDataVisualizations() {
    // This will be implemented when specific data visualizations are needed
    console.log('Data visualizations initialized');
}

// Create AI thinking animation
function createAIThinkingAnimation() {
    // Create container for the thinking animation
    const thinkingContainer = document.createElement('div');
    thinkingContainer.className = 'ai-thinking-container';
    thinkingContainer.style.display = 'none';
    thinkingContainer.style.position = 'fixed';
    thinkingContainer.style.top = '50%';
    thinkingContainer.style.left = '50%';
    thinkingContainer.style.transform = 'translate(-50%, -50%)';
    thinkingContainer.style.width = '200px';
    thinkingContainer.style.height = '200px';
    thinkingContainer.style.zIndex = '9996';
    document.body.appendChild(thinkingContainer);
    
    // Create brain animation
    const brainSvg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
    brainSvg.setAttribute('width', '200');
    brainSvg.setAttribute('height', '200');
    brainSvg.setAttribute('viewBox', '0 0 100 100');
    thinkingContainer.appendChild(brainSvg);
    
    // Create brain paths
    const paths = [
        'M50,10 C70,10 85,25 85,45 C85,65 70,80 50,80 C30,80 15,65 15,45 C15,25 30,10 50,10 Z',
        'M50,20 C65,20 75,30 75,45 C75,60 65,70 50,70 C35,70 25,60 25,45 C25,30 35,20 50,20 Z',
        'M30,40 C35,35 45,35 50,40 C55,45 55,55 50,60 C45,65 35,65 30,60 C25,55 25,45 30,40 Z',
        'M50,40 C55,35 65,35 70,40 C75,45 75,55 70,60 C65,65 55,65 50,60 C45,55 45,45 50,40 Z',
        'M40,30 C45,25 55,25 60,30 C65,35 65,45 60,50 C55,55 45,55 40,50 C35,45 35,35 40,30 Z'
    ];
    
    // Add paths to SVG
    paths.forEach((pathData, index) => {
        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        path.setAttribute('d', pathData);
        path.setAttribute('fill', 'none');
        path.setAttribute('stroke', '#00ccff');
        path.setAttribute('stroke-width', '2');
        path.setAttribute('stroke-dasharray', '100');
        path.setAttribute('stroke-dashoffset', '100');
        
        // Add animation
        const animate = document.createElementNS('http://www.w3.org/2000/svg', 'animate');
        animate.setAttribute('attributeName', 'stroke-dashoffset');
        animate.setAttribute('from', '100');
        animate.setAttribute('to', '0');
        animate.setAttribute('dur', '2s');
        animate.setAttribute('begin', `${index * 0.2}s`);
        animate.setAttribute('repeatCount', 'indefinite');
        
        path.appendChild(animate);
        brainSvg.appendChild(path);
    });
    
    // Add pulsing circles
    for (let i = 0; i < 5; i++) {
        const circle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        circle.setAttribute('cx', '50');
        circle.setAttribute('cy', '50');
        circle.setAttribute('r', '40');
        circle.setAttribute('fill', 'none');
        circle.setAttribute('stroke', '#00ccff');
        circle.setAttribute('stroke-width', '1');
        circle.setAttribute('opacity', '0');
        
        // Add animation
        const animate = document.createElementNS('http://www.w3.org/2000/svg', 'animate');
        animate.setAttribute('attributeName', 'r');
        animate.setAttribute('from', '20');
        animate.setAttribute('to', '50');
        animate.setAttribute('dur', '3s');
        animate.setAttribute('begin', `${i * 0.6}s`);
        animate.setAttribute('repeatCount', 'indefinite');
        
        const animateOpacity = document.createElementNS('http://www.w3.org/2000/svg', 'animate');
        animateOpacity.setAttribute('attributeName', 'opacity');
        animateOpacity.setAttribute('from', '0.6');
        animateOpacity.setAttribute('to', '0');
        animateOpacity.setAttribute('dur', '3s');
        animateOpacity.setAttribute('begin', `${i * 0.6}s`);
        animateOpacity.setAttribute('repeatCount', 'indefinite');
        
        circle.appendChild(animate);
        circle.appendChild(animateOpacity);
        brainSvg.appendChild(circle);
    }
    
    // Add text
    const text = document.createElement('div');
    text.textContent = 'AI Thinking...';
    text.style.textAlign = 'center';
    text.style.marginTop = '10px';
    text.style.color = '#00ccff';
    text.style.fontFamily = 'Orbitron, sans-serif';
    text.style.fontSize = '16px';
    text.style.textShadow = '0 0 10px rgba(0, 204, 255, 0.5)';
    thinkingContainer.appendChild(text);
    
    // Expose function to show/hide thinking animation
    window.showAIThinking = function(show) {
        thinkingContainer.style.display = show ? 'block' : 'none';
    };
}

// Initialize animations when the page loads
window.addEventListener('DOMContentLoaded', () => {
    initializeAnimations();
});