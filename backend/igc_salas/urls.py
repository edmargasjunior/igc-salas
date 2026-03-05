"""
IGC SALAS - URLs Principais
URLs limpas e mascaradas para segurança
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

# Personalizar admin
admin.site.site_header = 'IGC Salas - Administração'
admin.site.site_title = 'IGC Salas'
admin.site.index_title = 'Painel Administrativo'

urlpatterns = [
    # Admin Django (URL mascarada por segurança)
    path('igc-admin-portal/', admin.site.urls),

    # ===== ÁREA PÚBLICA (sem autenticação) =====
    path('', include('apps.core.urls')),              # Tela inicial / busca
    path('salas/', include('apps.estrutura.urls')),    # /salas/laboratorio-geologia
    path('professor/', include('apps.academico.urls_professor')),  # /professor/joao-silva
    path('turma/', include('apps.academico.urls_turma')),          # /turma/geologia-2025

    # ===== AUTENTICAÇÃO =====
    path('', include('apps.accounts.urls')),           # /entrar, /sair, /recuperar-senha

    # ===== ÁREA AUTENTICADA =====
    path('dashboard/', include('apps.core.urls_dashboard')),
    path('reservas/', include('apps.reservas.urls')),  # /reservas/123
    path('academico/', include('apps.academico.urls')),
    path('estrutura/', include('apps.estrutura.urls_admin')),
    path('importacao/', include('apps.importacao.urls')),

    # ===== API REST =====
    path('api/v1/', include([
        path('', include('apps.core.api_urls')),
        path('auth/', include('apps.accounts.api_urls')),
        path('estrutura/', include('apps.estrutura.api_urls')),
        path('academico/', include('apps.academico.api_urls')),
        path('reservas/', include('apps.reservas.api_urls')),
        path('notificacoes/', include('apps.notificacoes.api_urls')),
        path('busca/', include('apps.core.api_busca_urls')),
    ])),
]

# Servir mídia em desenvolvimento
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
