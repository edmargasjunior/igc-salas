/**
 * IGC SALAS — JavaScript Base
 * Scripts globais compartilhados em todos os templates
 */

document.addEventListener('DOMContentLoaded', () => {

    // ===== NAVBAR SCROLL EFFECT =====
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 10);
        });
    }

    // ===== AUTO-DISMISS TOASTS =====
    document.querySelectorAll('.toast').forEach(el => {
        setTimeout(() => {
            const toast = bootstrap.Toast.getInstance(el);
            if (toast) toast.hide();
            else el.classList.remove('show');
        }, 5000);
    });

    // ===== CONFIRMAÇÕES DE AÇÕES DESTRUTIVAS =====
    document.querySelectorAll('[data-confirm]').forEach(el => {
        el.addEventListener('click', (e) => {
            const msg = el.dataset.confirm || 'Confirmar esta ação?';
            if (!confirm(msg)) e.preventDefault();
        });
    });

    // ===== CARREGAR NOTIFICAÇÕES NO DROPDOWN =====
    const notifList = document.getElementById('notif-list');
    if (notifList) {
        document.querySelector('[data-bs-toggle="dropdown"] .bi-bell')
            ?.closest('button')
            ?.addEventListener('click', carregarNotificacoes);
    }
});

async function carregarNotificacoes() {
    const list = document.getElementById('notif-list');
    if (!list || list.dataset.loaded) return;

    try {
        const resp = await fetch('/api/v1/notificacoes/?page_size=5', {
            headers: { 'X-Requested-With': 'XMLHttpRequest' }
        });
        if (!resp.ok) throw new Error();
        const data = await resp.json();
        const notifs = data.results || [];

        if (notifs.length === 0) {
            list.innerHTML = '<span>Nenhuma notificação não lida.</span>';
        } else {
            list.innerHTML = notifs.map(n => `
                <a href="#" class="dropdown-item py-2 px-3 border-bottom" style="white-space:normal">
                    <div class="fw-semibold small">${n.titulo}</div>
                    <div class="text-muted" style="font-size:.75rem">${n.mensagem.substring(0,80)}...</div>
                </a>`).join('');
        }
        list.dataset.loaded = '1';
    } catch {
        list.innerHTML = '<span>Erro ao carregar notificações.</span>';
    }
}
