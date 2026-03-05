/* ============================================================
   IGC SALAS — JavaScript Base
   Navbar scroll, toasts, notificações
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

    // ===== Navbar scroll shadow =====
    const navbar = document.getElementById('mainNav');
    if (navbar) {
        window.addEventListener('scroll', () => {
            navbar.classList.toggle('scrolled', window.scrollY > 20);
        });
    }

    // ===== Auto-fechar toasts =====
    document.querySelectorAll('.toast').forEach(el => {
        setTimeout(() => {
            const toast = bootstrap.Toast.getOrCreateInstance(el);
            toast.hide();
        }, 5000);
    });

    // ===== Carregar notificações no dropdown =====
    const notifList = document.getElementById('notif-list');
    if (notifList) {
        document.querySelector('[data-bs-toggle="dropdown"]')?.addEventListener('show.bs.dropdown', function (e) {
            if (!e.target.closest('.dropdown')?.querySelector('#notif-list')) return;
            fetch('/api/v1/notificacoes/recentes/')
                .then(r => r.json())
                .then(data => {
                    if (!data.resultados || data.resultados.length === 0) {
                        notifList.innerHTML = '<span class="text-muted small">Nenhuma notificação nova.</span>';
                        return;
                    }
                    notifList.innerHTML = data.resultados.map(n => `
                        <a href="/notificacoes/" class="d-flex gap-2 text-decoration-none text-dark px-1 py-1">
                            <div style="font-size:1.1rem">${n.icone || '🔔'}</div>
                            <div>
                                <div class="fw-medium" style="font-size:.82rem">${n.titulo}</div>
                                <div class="text-muted" style="font-size:.72rem">${n.tempo}</div>
                            </div>
                        </a>
                    `).join('<hr class="my-1">');
                })
                .catch(() => {
                    notifList.innerHTML = '<span class="text-muted small">Erro ao carregar.</span>';
                });
        });
    }

    // ===== Confirmação em botões de exclusão/ação destrutiva =====
    document.querySelectorAll('[data-confirm]').forEach(btn => {
        btn.addEventListener('click', function (e) {
            if (!confirm(this.dataset.confirm)) {
                e.preventDefault();
            }
        });
    });

    // ===== Highlight da linha da tabela ao clicar =====
    document.querySelectorAll('table.table-hover tbody tr[data-href]').forEach(row => {
        row.style.cursor = 'pointer';
        row.addEventListener('click', () => {
            window.location.href = row.dataset.href;
        });
    });

});
