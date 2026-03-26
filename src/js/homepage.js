document.addEventListener('DOMContentLoaded', async () => {
    // Pegar token da URL ou localStorage
    const urlParams = new URLSearchParams(window.location.search);
    let token = urlParams.get('token');
    
    if (token) {
        localStorage.setItem('auth_token', token);
        // Limpar URL
        window.history.replaceState({}, document.title, window.location.pathname);
    } else {
        token = localStorage.getItem('auth_token');
    }

    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // Carregar itens do backend
    try {
        const response = await fetch('http://localhost:8000/items/');
        const items = await response.json();
        renderItems(items);
    } catch (error) {
        console.error('Erro ao buscar itens:', error);
    }
});

function renderItems(items) {
    const gridContainer = document.querySelector('.grid-container');
    gridContainer.innerHTML = ''; // Limpar estático

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'item-card';

        // Definir a imagem baseando na categoria/nome (fallback genérico)
        let imgPath = "img/magical_sword.png";
        if (item.name.toLowerCase().includes('fortnite')) imgPath = "img/treasure_chest.png";
        if (item.name.toLowerCase().includes('roblox')) imgPath = "img/magical_sword.png";

        card.innerHTML = `
            <div class="item-image-container">
                <img src="${imgPath}" alt="${item.name}" class="item-image">
                <span class="item-rarity legendary">Destaque</span>
            </div>
            <div class="item-details">
                <h3 class="item-name">${item.name}</h3>
                <p class="item-description">${item.description}</p>
                <div class="item-meta">
                    <span class="item-qty">Qtd: ${item.stock?.length || 0} un.</span>
                    <span class="item-price">R$ ${item.price.toFixed(2).replace('.', ',')}</span>
                </div>
                <button class="buy-btn" onclick="window.location.href='details.html?id=${item.id}'">
                    <span>Ver Detalhes</span>
                </button>
            </div>
        `;
        gridContainer.appendChild(card);
    });
}
