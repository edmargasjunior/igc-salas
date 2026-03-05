/* ============================================================
   IGC SALAS — JavaScript Dashboard
   Gráficos de ocupação, métricas em tempo real
   ============================================================ */

document.addEventListener('DOMContentLoaded', function () {

    // ===== Gráfico de Ocupação por Sala =====
    const ctxOcupacao = document.getElementById('chartOcupacao');
    if (ctxOcupacao) {
        fetch('/api/v1/reservas/stats/ocupacao/')
            .then(r => r.json())
            .then(data => {
                new Chart(ctxOcupacao, {
                    type: 'bar',
                    data: {
                        labels: data.labels || [],
                        datasets: [{
                            label: 'Reservas (30 dias)',
                            data: data.valores || [],
                            backgroundColor: 'rgba(30, 64, 175, 0.75)',
                            borderColor: '#1e40af',
                            borderWidth: 1,
                            borderRadius: 6,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: {
                            legend: { display: false },
                            tooltip: {
                                callbacks: {
                                    label: ctx => ` ${ctx.raw} reservas`
                                }
                            }
                        },
                        scales: {
                            y: {
                                beginAtZero: true,
                                ticks: { stepSize: 1 },
                                grid: { color: '#f1f5f9' }
                            },
                            x: { grid: { display: false } }
                        }
                    }
                });
            })
            .catch(() => {
                if (ctxOcupacao.parentElement) {
                    ctxOcupacao.parentElement.innerHTML = '<p class="text-muted text-center py-4 small">Dados não disponíveis</p>';
                }
            });
    }

    // ===== Gráfico de Reservas por Status (Donut) =====
    const ctxStatus = document.getElementById('chartStatus');
    if (ctxStatus) {
        fetch('/api/v1/reservas/stats/status/')
            .then(r => r.json())
            .then(data => {
                new Chart(ctxStatus, {
                    type: 'doughnut',
                    data: {
                        labels: data.labels || [],
                        datasets: [{
                            data: data.valores || [],
                            backgroundColor: [
                                '#10b981', '#f59e0b', '#ef4444',
                                '#64748b', '#8b5cf6', '#94a3b8'
                            ],
                            borderWidth: 2,
                            borderColor: '#ffffff',
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        cutout: '65%',
                        plugins: {
                            legend: {
                                position: 'bottom',
                                labels: { boxWidth: 12, font: { size: 11 } }
                            }
                        }
                    }
                });
            })
            .catch(() => {});
    }

    // ===== Gráfico de Reservas por Dia (Linha - últimos 14 dias) =====
    const ctxTendencia = document.getElementById('chartTendencia');
    if (ctxTendencia) {
        fetch('/api/v1/reservas/stats/tendencia/')
            .then(r => r.json())
            .then(data => {
                new Chart(ctxTendencia, {
                    type: 'line',
                    data: {
                        labels: data.labels || [],
                        datasets: [{
                            label: 'Reservas',
                            data: data.valores || [],
                            borderColor: '#1e40af',
                            backgroundColor: 'rgba(30,64,175,0.08)',
                            tension: 0.4,
                            fill: true,
                            pointBackgroundColor: '#1e40af',
                            pointRadius: 4,
                        }]
                    },
                    options: {
                        responsive: true,
                        maintainAspectRatio: false,
                        plugins: { legend: { display: false } },
                        scales: {
                            y: { beginAtZero: true, grid: { color: '#f1f5f9' } },
                            x: { grid: { display: false } }
                        }
                    }
                });
            })
            .catch(() => {});
    }

});
