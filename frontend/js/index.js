document.addEventListener('DOMContentLoaded', function() {
    // Add mouse follow effect to the neural network nodes
    const nodes = document.querySelectorAll('.node');
    const container = document.querySelector('.animated-background');
    
    container.addEventListener('mousemove', function(e) {
        const x = e.clientX;
        const y = e.clientY;
        
        nodes.forEach((node, index) => {
            // Calculate distance from mouse to node
            const rect = node.getBoundingClientRect();
            const nodeX = rect.left + rect.width / 2;
            const nodeY = rect.top + rect.height / 2;
            
            const distX = x - nodeX;
            const distY = y - nodeY;
            const distance = Math.sqrt(distX * distX + distY * distY);
            
            // Move nodes slightly towards mouse when close
            if (distance < 200) {
                const moveX = distX * 0.05;
                const moveY = distY * 0.05;
                
                node.style.transform = `translate(${moveX}px, ${moveY}px) scale(${1 + (200 - distance) / 1000})`;
                node.style.boxShadow = `0 0 ${10 + (200 - distance) / 10}px var(--primary-color), 0 0 ${20 + (200 - distance) / 5}px var(--primary-color)`;
            } else {
                node.style.transform = '';
                node.style.boxShadow = '';
            }
        });
    });
    
    // Add parallax effect to feature cards
    const cards = document.querySelectorAll('.feature-card');
    
    window.addEventListener('mousemove', function(e) {
        const x = e.clientX / window.innerWidth;
        const y = e.clientY / window.innerHeight;
        
        cards.forEach(card => {
            const rect = card.getBoundingClientRect();
            const cardX = rect.left + rect.width / 2;
            const cardY = rect.top + rect.height / 2;
            
            // Calculate distance from mouse to card center (normalized)
            const distX = (e.clientX - cardX) / window.innerWidth;
            const distY = (e.clientY - cardY) / window.innerHeight;
            
            // Apply subtle rotation based on mouse position
            card.style.transform = `perspective(1000px) rotateY(${distX * 5}deg) rotateX(${-distY * 5}deg) translateY(-5px)`;
        });
    });
    
    // Reset card position when mouse leaves
    window.addEventListener('mouseleave', function() {
        cards.forEach(card => {
            card.style.transform = 'translateY(0)';
        });
    });
    
    // Create dynamic connections between nodes
    function createConnections() {
        const connections = document.querySelectorAll('.connection');
        connections.forEach(conn => conn.remove());
        
        const nodePositions = [];
        nodes.forEach(node => {
            const rect = node.getBoundingClientRect();
            nodePositions.push({
                x: rect.left + rect.width / 2,
                y: rect.top + rect.height / 2,
                element: node
            });
        });
        
        // Create connections between nearby nodes
        for (let i = 0; i < nodePositions.length; i++) {
            for (let j = i + 1; j < nodePositions.length; j++) {
                const node1 = nodePositions[i];
                const node2 = nodePositions[j];
                
                const dx = node1.x - node2.x;
                const dy = node1.y - node2.y;
                const distance = Math.sqrt(dx * dx + dy * dy);
                
                if (distance < 300) { // Only connect nearby nodes
                    const opacity = 1 - distance / 300;
                    
                    const connection = document.createElement('div');
                    connection.classList.add('connection');
                    
                    const length = Math.sqrt(dx * dx + dy * dy);
                    const angle = Math.atan2(dy, dx) * 180 / Math.PI;
                    
                    connection.style.width = `${length}px`;
                    connection.style.left = `${node2.x}px`;
                    connection.style.top = `${node2.y}px`;
                    connection.style.transform = `rotate(${angle}deg)`;
                    connection.style.opacity = opacity * 0.5;
                    
                    document.querySelector('.neural-network').appendChild(connection);
                }
            }
        }
    }
    
    // Create connections initially and on window resize
    createConnections();
    window.addEventListener('resize', createConnections);
    
    // Add CSS for connections
    const style = document.createElement('style');
    style.textContent = `
        .connection {
            position: absolute;
            height: 1px;
            background: linear-gradient(to right, var(--primary-color), transparent);
            transform-origin: left center;
            pointer-events: none;
            z-index: 1;
        }
    `;
    document.head.appendChild(style);
}); 