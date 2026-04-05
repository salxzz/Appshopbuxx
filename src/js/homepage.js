document.addEventListener('DOMContentLoaded', async () => {
    // Definir base da API (Tenta localhost primeiro, senao usa IP atual para acesso externo)
    const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : `${window.location.protocol}//${window.location.hostname}:8000`;
    console.log("🚀 Shopbuxx Iniciado na API:", API_BASE);

    // Pegar token da URL (OAuth) ou localStorage
    const urlParams = new URLSearchParams(window.location.search);
    let token = urlParams.get('token');
    
    if (token) {
        localStorage.setItem('auth_token', token);
        window.history.replaceState({}, document.title, window.location.pathname);
    } else {
        token = localStorage.getItem('auth_token');
    }

    if (!token) {
        window.location.href = 'index.html';
        return;
    }

    // 1. Carregar informações do perfil
    try {
        const userRes = await fetch(`${API_BASE}/user/me`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        if (userRes.ok) {
            const user = await userRes.json();
            updateNavbar(user);
        } else if (userRes.status === 401) {
            localStorage.removeItem('auth_token');
            window.location.href = 'index.html';
            return;
        }
    } catch (error) {
        console.error('❌ Erro ao buscar usuário:', error);
    }

    // 2. Listener do botão de Inventário (Navbar)
    const invBtn = document.getElementById('inventory-toggle');
    if (invBtn) {
        invBtn.addEventListener('click', async (e) => {
            e.preventDefault();
            const mainTitle = document.querySelector('.hero h1');
            if (mainTitle.innerText === 'Seu Inventário') {
                mainTitle.innerText = 'Itens em Destaque';
                invBtn.innerText = 'Inventário';
                const response = await fetch(`${API_BASE}/items/`);
                renderItems(await response.json());
            } else {
                mainTitle.innerText = 'Seu Inventário';
                invBtn.innerText = 'Voltar à Loja';
                loadInventory(token, API_BASE);
            }
        });
    }

    // 3. Carregar vitrine de itens
    try {
        const response = await fetch(`${API_BASE}/items/`);
        const items = await response.json();
        renderItems(items);
    } catch (error) {
        console.error('❌ Erro ao buscar itens da loja:', error);
    }

    // 4. listeners do Modal
    const closeBtn = document.getElementById('close-profile');
    if (closeBtn) {
        closeBtn.onclick = () => {
            document.getElementById('profile-modal').style.display = 'none';
        };
    }

    window.onclick = (e) => {
        const modal = document.getElementById('profile-modal');
        if (e.target == modal) modal.style.display = 'none';
    };
});

// --- VARIÁVEIS E FUNÇÕES GLOBAIS ---
let currentUserData = null;

function updateNavbar(user) {
    currentUserData = user; 
    const userNameElement = document.getElementById('user-name');
    const userAvatarElement = document.getElementById('user-avatar');
    const roleLinks = document.getElementById('role-links');

    if (userNameElement) userNameElement.innerText = user.name || user.username || "Usuário";
    
    if (userAvatarElement && user.avatar && user.discord_id) {
        userAvatarElement.src = `https://cdn.discordapp.com/avatars/${user.discord_id}/${user.avatar}.png`;
        userAvatarElement.style.borderRadius = "50%";
    }

    // Gerenciar links de cargo
    if (roleLinks) {
        roleLinks.innerHTML = '';
        if (user.role === 'admin') {
            roleLinks.innerHTML += '<a href="admin.html" class="nav-item-special">Painel Admin</a>';
            roleLinks.innerHTML += '<a href="seller.html" class="nav-item-special">Vendedor</a>';
        } else if (user.role === 'seller') {
            roleLinks.innerHTML += '<a href="seller.html" class="nav-item-special">Painel Vendedor</a>';
        }
    }

    const userProfile = document.querySelector('.user-profile');
    if (userProfile) {
        userProfile.onclick = openProfileModal;
    }
}

function openProfileModal() {
    if (!currentUserData) {
        alert("Carregando perfil...");
        return;
    }
    const modal = document.getElementById('profile-modal');
    if (!modal) return;
    
    document.getElementById('modal-name').innerText = currentUserData.name || currentUserData.username || "Usuário";
    document.getElementById('modal-role').innerText = currentUserData.role === 'admin' ? 'DIRETORIA (ADMIN)' : 'CLIENTE VIP';
    
    if (currentUserData.avatar && currentUserData.discord_id) {
        const avatarUrl = `https://cdn.discordapp.com/avatars/${currentUserData.discord_id}/${currentUserData.avatar}.png`;
        document.getElementById('modal-avatar').src = avatarUrl;
    }
    
    modal.style.display = 'block';
    fetchInventory();
}

function showTab(tabName) {
    document.querySelectorAll('.tab-content').forEach(t => t.style.display = 'none');
    document.querySelectorAll('.profile-sidebar .nav-btn').forEach(b => b.classList.remove('active'));
    
    const target = document.getElementById(`tab-${tabName}`);
    if (target) target.style.display = 'block';
    if (event) event.currentTarget.classList.add('active');
}

async function fetchInventory() {
    const API_BASE = window.location.hostname === 'localhost' ? 'http://localhost:8000' : `${window.location.protocol}//${window.location.hostname}:8000`;
    const list = document.getElementById('user-inventory-list');
    try {
        const res = await fetch(`${API_BASE}/user/inventory`, {
            headers: { 'Authorization': `Bearer ${localStorage.getItem('auth_token')}` }
        });
        const items = await res.json();
        list.innerHTML = items.length ? '' : '<p>Seu inventário está vazio.</p>';
        
        items.forEach(item => {
            const div = document.createElement('div');
            div.className = 'inventory-item';
            div.innerHTML = `
                <div style="flex:1;">
                    <strong>${item.item_name}</strong><br>
                    <small style="color:#666;">ID: #${item.id.substring(0,8)}</small>
                </div>
                <div style="background:#111; padding:8px; border-radius:6px; min-width:150px; text-align:center;">
                    <code style="color:var(--primary); font-size:11px;">${item.delivered_data || 'Processando...'}</code>
                </div>
            `;
            list.appendChild(div);
        });
    } catch (err) { console.error("Erro no inventário:", err); }
}

async function loadInventory(token, API_BASE) {
    try {
        const res = await fetch(`${API_BASE}/user/inventory`, {
            headers: { 'Authorization': `Bearer ${token}` }
        });
        const inventory = await res.json();
        renderInventory(inventory);
    } catch (error) { console.error(error); }
}

function renderInventory(items) {
    const gridContainer = document.querySelector('.grid-container');
    gridContainer.innerHTML = '';
    if (items.length === 0) {
        gridContainer.innerHTML = '<p style="grid-column: 1/-1; text-align: center; color: #fff;">Você ainda não possui compras.</p>';
        return;
    }
    items.forEach(order => {
        const card = document.createElement('div');
        card.className = 'item-card';
        card.innerHTML = `
            <div class="item-details">
                <h3 class="item-name">${order.item_name}</h3>
                <p class="item-description">Pedido: #${order.id.substring(0,8)}</p>
                <div class="item-meta">
                    <span class="item-price">R$ ${order.price}</span>
                </div>
                <button class="buy-btn" style="background:#27ae60; color:white; border:none;">
                    <span>Entregue</span>
                </button>
            </div>
        `;
        gridContainer.appendChild(card);
    });
}

function renderItems(items) {
    const gridContainer = document.querySelector('.grid-container');
    gridContainer.innerHTML = ''; 

    items.forEach(item => {
        const card = document.createElement('div');
        card.className = 'item-card';

        let rarityClass = 'legendary';
        let rarityText = 'Destaque';
        if (item.price < 20) { rarityClass = 'common'; rarityText = 'Comum'; }
        else if (item.price < 50) { rarityClass = 'epic'; rarityText = 'Épico'; }

        let imgPath = "img/magical_sword.png";
        if (item.name.toLowerCase().includes('fortnite')) imgPath = "img/treasure_chest.png";

        card.innerHTML = `
            <div class="item-image-container">
                <img src="${imgPath}" alt="${item.name}" class="item-image">
                <span class="item-rarity ${rarityClass}">${rarityText}</span>
            </div>
            <div class="item-details">
                <h3 class="item-name">${item.name}</h3>
                <p class="item-description">${item.description}</p>
                <div class="item-meta">
                    <span class="item-qty">Qtd: ${item.stock_count || 0} un.</span>
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

function logout() {
    if (confirm('Deseja realmente sair?')) {
        localStorage.removeItem('auth_token');
        window.location.href = 'index.html';
    }
}
