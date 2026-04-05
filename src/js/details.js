document.addEventListener('DOMContentLoaded', async () => {
    const urlParams = new URLSearchParams(window.location.search);
    const itemId = urlParams.get('id');
    const token = localStorage.getItem('auth_token');

    if (!itemId) {
        window.location.href = 'homepage.html';
        return;
    }

    // Fetch Item Data
    try {
        const response = await fetch(`http://localhost:8000/items/${itemId}`);
        const item = await response.json();

        if (item.error) {
            alert('Item não encontrado');
            window.location.href = 'homepage.html';
            return;
        }

        updateUI(item);
    } catch (error) {
        console.error('Erro ao buscar detalhes do item:', error);
    }

    // Carregar informações do usuário
    if (token) {
        try {
            const userRes = await fetch('http://localhost:8000/user/me', {
                headers: { 'Authorization': `Bearer ${token}` }
            });
            if (userRes.ok) {
                const user = await userRes.json();
                updateNavbar(user);
            }
        } catch (error) {
            console.error('Erro ao buscar usuário:', error);
        }
    }

    // Modal elements
    const modal = document.getElementById('pix-modal');
    const closeBtn = document.querySelector('.close-modal');
    const buyBtn = document.querySelector('.buy-button');

    closeBtn.onclick = () => modal.style.display = 'none';
    window.onclick = (e) => { if (e.target == modal) modal.style.display = 'none'; };

    // Buy Action
    buyBtn.onclick = async () => {
        if (!token) {
            alert('Você precisa estar logado para comprar!');
            window.location.href = 'index.html';
            return;
        }

        buyBtn.disabled = true;
        buyBtn.innerText = 'Processando...';

        try {
            const response = await fetch(`http://localhost:8000/buy/${itemId}`, {
                method: 'POST',
                headers: {
                    'Authorization': `Bearer ${token}`
                }
            });

            const data = await response.json();

            if (data.pix_qr) {
                document.getElementById('qr-code-img').src = `data:image/png;base64,${data.pix_code}`;
                document.getElementById('pix-code-input').value = data.pix_qr;
                modal.style.display = 'block';
            } else {
                alert('Erro ao gerar PIX: ' + (data.detail || 'Erro desconhecido'));
            }
        } catch (error) {
            console.error('Erro na compra:', error);
            alert('Erro na conexão com o servidor.');
        } finally {
            buyBtn.disabled = false;
            buyBtn.innerText = 'Comprar Agora';
        }
    };

    // Copy PIX Button
    document.getElementById('copy-pix-btn').onclick = () => {
        const input = document.getElementById('pix-code-input');
        input.select();
        document.execCommand('copy');
        alert('Código PIX copiado!');
    };
});

function updateUI(item) {
    document.querySelector('.item-title').innerText = item.name;
    document.querySelector('.item-id').innerText = `ID do Item: #SBX-${item.id}`;
    document.querySelector('.price').innerText = `R$ ${item.price.toFixed(2).replace('.', ',')}`;
    document.querySelector('.stock').innerText = `Em estoque: ${item.stock_count || 0} un.`;
    document.querySelector('.description-section p').innerText = item.description;

    // Define image
    let imgPath = "img/magical_sword.png";
    if (item.name.toLowerCase().includes('fortnite')) imgPath = "img/treasure_chest.png";
    if (item.name.toLowerCase().includes('roblox')) imgPath = "img/magical_sword.png";
    
    document.querySelector('.main-image').src = imgPath;
    document.querySelector('.main-image').alt = item.name;
    
    // Update max quantity based on stock
    const qtyInput = document.querySelector('.qty-input');
    if (item.stock_count && item.stock_count > 0) {
        qtyInput.max = item.stock_count;
    } else {
        qtyInput.value = 0;
        const buyBtn = document.querySelector('.buy-button');
        buyBtn.disabled = true;
        buyBtn.innerText = 'Sem Estoque';
    }
}

function updateNavbar(user) {
    const userNameElement = document.getElementById('user-name');
    const userAvatarElement = document.getElementById('user-avatar');
    const roleLinks = document.getElementById('role-links');

    if (userNameElement) userNameElement.innerText = user.name || user.username || "Usuário";
    
    if (userAvatarElement && user.avatar && user.discord_id) {
        userAvatarElement.src = `https://cdn.discordapp.com/avatars/${user.discord_id}/${user.avatar}.png`;
        userAvatarElement.style.borderRadius = "50%";
    }

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
        userProfile.onclick = () => {
            if (confirm('Deseja sair?')) {
                localStorage.removeItem('auth_token');
                window.location.href = 'index.html';
            }
        };
    }
}
