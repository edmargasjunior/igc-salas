/**
 * IGC SALAS — JavaScript da Busca em Tempo Real
 * Motor de busca com autocomplete para tela pública
 */

const IGCBusca = (() => {
    const API_URL = '/api/v1/busca/';
    let tipoAtivo = 'todos';
    let debounceTimer = null;
    let currentAgendaSlug = null;

    // ============================================================
    // ELEMENTOS DOM
    // ============================================================
    const $input = document.getElementById('searchInput');
    const $results = document.getElementById('searchResults');
    const $content = document.getElementById('resultsContent');
    const $footer = document.getElementById('searchFooter');
    const $total = document.getElementById('totalResultados');
    const $icon = document.getElementById('searchIcon');
    const $spinner = document.getElementById('searchSpinner');
    const $panel = document.getElementById('resultPanel');
    const $panelContent = document.getElementById('panelContent');
    const $panelTitleText = document.getElementById('panelTitleText');
    const $filterTags = document.querySelectorAll('.filter-tag');

    // ============================================================
    // INICIALIZAÇÃO
    // ============================================================
    function init() {
        if (!$input) return;

        $input.addEventListener('input', onInput);
        $input.addEventListener('keydown', onKeydown);
        $input.addEventListener('focus', () => {
            if ($input.value.length >= 2) mostrarResultados();
        });

        // Fechar ao clicar fora
        document.addEventListener('click', (e) => {
            if (!e.target.closest('.search-container')) {
                fecharResultados();
            }
        });

        // Filtros de tipo
        $filterTags.forEach(btn => {
            btn.addEventListener('click', () => {
                $filterTags.forEach(b => b.classList.remove('active'));
                btn.classList.add('active');
                tipoAtivo = btn.dataset.tipo;
                if ($input.value.length >= 2) buscar($input.value);
            });
        });
    }

    // ============================================================
    // HANDLERS
    // ============================================================
    function onInput(e) {
        const q = e.target.value.trim();
        clearTimeout(debounceTimer);

        if (q.length < 2) {
            fecharResultados();
            return;
        }

        setLoading(true);
        debounceTimer = setTimeout(() => buscar(q), 280);
    }

    function onKeydown(e) {
        if (e.key === 'Escape') fecharResultados();
    }

    // ============================================================
    // BUSCA
    // ============================================================
    async function buscar(q) {
        try {
            const url = `${API_URL}?q=${encodeURIComponent(q)}&tipo=${tipoAtivo}`;
            const resp = await fetch(url, {
                headers: { 'Accept': 'application/json' }
            });

            if (!resp.ok) throw new Error('Erro na busca');

            const data = await resp.json();
            renderResultados(data);
        } catch (err) {
            renderErro();
        } finally {
            setLoading(false);
        }
    }

    // ============================================================
    // RENDERIZAÇÃO
    // ============================================================
    function renderResultados(data) {
        if (data.resultados.length === 0) {
            $content.innerHTML = `
                <div class="no-results">
                    <i class="bi bi-search" style="font-size:2rem;opacity:.3"></i>
                    <p class="mt-2 mb-0">Nenhum resultado para "<strong>${escapeHtml(data.query)}</strong>"</p>
                    <small>Tente outros termos ou use os filtros acima</small>
                </div>`;
            $footer.style.display = 'none';
        } else {
            $content.innerHTML = data.resultados.map(renderItem).join('');
            $total.textContent = `${data.total} resultado${data.total !== 1 ? 's' : ''} encontrado${data.total !== 1 ? 's' : ''}`;
            $footer.style.display = 'block';
        }

        mostrarResultados();
    }

    function renderItem(item) {
        const iconMap = {
            sala: 'door-open',
            laboratorio: 'flask',
            professor: 'person-workspace',
            turma: 'people',
            disciplina: 'book'
        };
        const icon = iconMap[item.tipo] || 'search';
        const tipo = item.subtipo || item.tipo;

        return `
            <div class="result-item" onclick="IGCBusca.selecionarItem(${JSON.stringify(item).replace(/"/g, '&quot;')})">
                <div class="result-icon ${tipo}">
                    <i class="bi bi-${icon}"></i>
                </div>
                <div class="flex-grow-1 overflow-hidden">
                    <p class="result-title text-truncate">${escapeHtml(item.titulo)}</p>
                    <p class="result-sub text-truncate">${escapeHtml(item.subtitulo || '')}</p>
                    ${item.professor ? `<p class="result-sub text-truncate text-muted" style="font-size:.7rem">${escapeHtml(item.professor)}</p>` : ''}
                </div>
                <span class="result-badge">${escapeHtml(item.badge || '')}</span>
            </div>`;
    }

    function renderErro() {
        $content.innerHTML = `
            <div class="no-results">
                <i class="bi bi-exclamation-triangle text-warning" style="font-size:2rem"></i>
                <p class="mt-2 mb-0">Erro ao buscar. Tente novamente.</p>
            </div>`;
        mostrarResultados();
    }

    // ============================================================
    // SELEÇÃO DE ITEM
    // ============================================================
    async function selecionarItem(item) {
        fecharResultados();
        $input.value = item.titulo;

        if (item.tipo === 'sala' || item.subtipo === 'laboratorio') {
            await carregarAgendaSala(item.slug, item.titulo);
        } else if (item.tipo === 'professor') {
            await carregarAgendaProfessor(item.slug, item.titulo);
        } else if (item.tipo === 'turma') {
            window.location.href = item.url;
        } else {
            window.location.href = item.url;
        }
    }

    // ============================================================
    // AGENDA DE SALA
    // ============================================================
    async function carregarAgendaSala(slug, nome) {
        mostrarPainel(`Agenda de ${nome}`);
        setLoadingPainel();

        try {
            const resp = await fetch(`/api/v1/busca/agenda-sala/${slug}/`);
            const data = await resp.json();
            renderAgendaSala(data);
        } catch (err) {
            $panelContent.innerHTML = '<p class="text-center py-4 text-muted">Erro ao carregar agenda.</p>';
        }
    }

    function renderAgendaSala(data) {
        const sala = data.sala;
        const agenda = data.agenda;
        const semana = data.semana;

        // Agrupar por dia da semana
        const diasMap = {};
        const diasNomes = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta', 'Sábado', 'Domingo'];
        agenda.forEach(r => {
            const key = r.data;
            if (!diasMap[key]) diasMap[key] = { data_br: r.data_br, dia: r.dia_semana, slots: [] };
            diasMap[key].slots.push(r);
        });

        const diasHtml = Object.values(diasMap).length > 0
            ? Object.entries(diasMap).map(([data, dia]) => `
                <div class="agenda-day">
                    <div class="agenda-day-header">${dia.dia_semana || dia.dia}<br><small>${dia.data_br}</small></div>
                    ${dia.slots.map(s => `
                        <div class="agenda-slot">
                            <strong>${s.hora_inicio}–${s.hora_fim}</strong><br>
                            <span class="text-truncate d-block" style="font-size:.72rem">${escapeHtml(s.disciplina)}</span>
                            <span class="text-muted" style="font-size:.7rem">${escapeHtml(s.professor)}</span>
                        </div>
                    `).join('')}
                </div>`).join('')
            : `<div class="p-4 text-center text-muted">
                <i class="bi bi-calendar-check fs-2 d-block mb-2 opacity-50"></i>
                Nenhuma reserva esta semana — sala disponível!
               </div>`;

        $panelContent.innerHTML = `
            <div class="p-3 border-bottom bg-light d-flex flex-wrap gap-3 align-items-center">
                <div>
                    <h6 class="mb-1 fw-bold">${escapeHtml(sala.nome)}</h6>
                    <small class="text-muted">
                        <i class="bi bi-building me-1"></i>${escapeHtml(sala.predio)} · ${escapeHtml(sala.andar)}
                        <span class="ms-2"><i class="bi bi-people me-1"></i>Capacidade: ${sala.capacidade}</span>
                    </small>
                </div>
                <span class="badge bg-primary ms-auto">${escapeHtml(sala.tipo)}</span>
            </div>
            <div class="p-3">
                <div class="d-flex align-items-center justify-content-between mb-3">
                    <small class="text-muted fw-semibold">
                        <i class="bi bi-calendar3 me-1"></i>
                        Semana ${semana.inicio} – ${semana.fim}
                        <span class="badge bg-success ms-2">${data.total_reservas} reserva${data.total_reservas !== 1 ? 's' : ''}</span>
                    </small>
                </div>
                <div class="agenda-grid">${diasHtml}</div>
            </div>`;
    }

    // ============================================================
    // AGENDA DE PROFESSOR
    // ============================================================
    async function carregarAgendaProfessor(slug, nome) {
        mostrarPainel(`Agenda de ${nome}`);
        setLoadingPainel();

        try {
            const resp = await fetch(`/api/v1/busca/agenda-professor/${slug}/`);
            const data = await resp.json();
            renderAgendaProfessor(data);
        } catch {
            $panelContent.innerHTML = '<p class="text-center py-4 text-muted">Erro ao carregar agenda.</p>';
        }
    }

    function renderAgendaProfessor(data) {
        const prof = data.professor;
        const agenda = data.agenda;
        const semana = data.semana;

        const linhas = agenda.length > 0
            ? agenda.map(r => `
                <tr>
                    <td>${r.data_br}</td>
                    <td class="fw-medium">${r.hora_inicio}–${r.hora_fim}</td>
                    <td>${escapeHtml(r.disciplina)}</td>
                    <td>${escapeHtml(r.sala)} <small class="text-muted">${escapeHtml(r.predio)}</small></td>
                </tr>`).join('')
            : `<tr><td colspan="4" class="text-center text-muted py-3">Nenhuma aula esta semana.</td></tr>`;

        $panelContent.innerHTML = `
            <div class="p-3 border-bottom bg-light d-flex flex-wrap gap-3 align-items-center">
                <div>
                    <h6 class="mb-1 fw-bold">${escapeHtml(prof.nome)}</h6>
                    <small class="text-muted">${escapeHtml(prof.titulacao)} · ${escapeHtml(prof.area || '')}</small>
                </div>
            </div>
            <div class="p-3">
                <small class="text-muted fw-semibold d-block mb-3">
                    <i class="bi bi-calendar3 me-1"></i>Semana ${semana.inicio} – ${semana.fim}
                </small>
                <div class="table-responsive">
                    <table class="table table-sm table-hover mb-0">
                        <thead class="table-light">
                            <tr><th>Data</th><th>Horário</th><th>Disciplina</th><th>Sala</th></tr>
                        </thead>
                        <tbody>${linhas}</tbody>
                    </table>
                </div>
            </div>`;
    }

    // ============================================================
    // HELPERS
    // ============================================================
    function mostrarPainel(titulo) {
        if ($panel) {
            $panel.style.display = 'block';
            $panelTitleText.textContent = titulo;
            $panel.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    }

    function setLoadingPainel() {
        if ($panelContent) {
            $panelContent.innerHTML = `
                <div class="text-center py-5">
                    <div class="spinner-border text-primary"></div>
                    <p class="text-muted mt-2 small">Carregando agenda...</p>
                </div>`;
        }
    }

    function mostrarResultados() {
        if ($results) $results.style.display = 'block';
    }

    function fecharResultados() {
        if ($results) $results.style.display = 'none';
    }

    function setLoading(loading) {
        if ($icon && $spinner) {
            $icon.classList.toggle('d-none', loading);
            $spinner.classList.toggle('d-none', !loading);
        }
    }

    function escapeHtml(str) {
        if (!str) return '';
        return String(str)
            .replace(/&/g, '&amp;')
            .replace(/</g, '&lt;')
            .replace(/>/g, '&gt;')
            .replace(/"/g, '&quot;');
    }

    // Busca rápida (chamada pelos botões de sugestão)
    function buscarRapido(termo) {
        $input.value = termo;
        $input.focus();
        setLoading(true);
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => buscar(termo), 100);
    }

    // Init
    document.addEventListener('DOMContentLoaded', init);

    return { selecionarItem, buscarRapido, fecharResultados };
})();

function buscarRapido(termo) { IGCBusca.buscarRapido(termo); }
function fecharPainel() {
    const p = document.getElementById('resultPanel');
    if (p) p.style.display = 'none';
}
