# IGC Salas
## Sistema de Gestão de Salas e Laboratórios
### Instituto de Geociências — UFMG

---

## 📋 Visão Geral

Sistema web institucional para gestão, reserva e acompanhamento de salas e laboratórios do Instituto de Geociências (IGC) da UFMG. Permite busca pública em tempo real e controle completo de reservas com fluxo de aprovação.

---

## 🏗️ Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Browser)                         │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/HTTPS :80/:443
┌──────────────────────────▼──────────────────────────────────────┐
│                    NGINX (Reverse Proxy)                          │
│     • Servir arquivos estáticos e mídia                          │
│     • Rate limiting (login: 5r/m, API: 30r/m)                   │
│     • Headers de segurança                                        │
└──────────────────────────┬──────────────────────────────────────┘
                           │ :8000
┌──────────────────────────▼──────────────────────────────────────┐
│               GUNICORN + DJANGO (WSGI)                            │
│     • 4 workers, 120s timeout                                    │
│     • Django 4.2 + DRF 3.15                                      │
│     • Autenticação JWT + Session                                  │
└─────────┬───────────────────────────┬───────────────────────────┘
          │                           │
┌─────────▼────────┐       ┌──────────▼──────────────┐
│  PostgreSQL 16   │       │     Redis 7              │
│  • ORM Django    │       │  • Cache de sessões      │
│  • Migrações     │       │  • Celery Broker         │
└──────────────────┘       └─────────────────────────┘
                                      │
                           ┌──────────▼──────────────┐
                           │   CELERY (Workers)       │
                           │  • Envio de e-mails      │
                           │  • Tarefas agendadas     │
                           └─────────────────────────┘
```

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia | Versão |
|---|---|---|
| Backend | Python + Django | 3.11 / 4.2 |
| API REST | Django REST Framework | 3.15 |
| Frontend | HTML5 + Bootstrap 5 + JS | 5.3 |
| Banco de Dados | PostgreSQL | 16 |
| Cache/Broker | Redis | 7 |
| Task Queue | Celery + Beat | 5.4 |
| Web Server | Gunicorn | 23.0 |
| Proxy | Nginx | Alpine |
| Container | Docker + Compose | latest |

---

## ⚙️ Requisitos

- Docker Engine ≥ 24.0
- Docker Compose ≥ 2.20
- 2GB RAM mínimo
- 5GB de espaço em disco

---

## 🚀 Instalação e Execução

### 1. Clonar o repositório
```bash
git clone https://github.com/seu-usuario/igc-salas.git
cd igc-salas
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Editar .env com suas configurações
nano .env
```

### 3. Subir o sistema
```bash
docker compose up -d
```

### 4. Aguardar inicialização (≈ 30-60 segundos)
```bash
docker compose logs -f backend
# Aguardar mensagem: "Sistema IGC Salas pronto!"
```

### 5. Acessar o sistema
| URL | Descrição |
|---|---|
| http://localhost/ | Tela pública de busca |
| http://localhost/entrar/ | Login |
| http://localhost/dashboard/ | Dashboard |
| http://localhost/igc-admin-portal/ | Admin Django |
| http://localhost/api/v1/ | API REST |

### Credenciais padrão (alterar após primeiro acesso)
```
Usuário: admin
Senha:   IGCAdmin@2025
```

---

## 🗂️ Estrutura do Projeto

```
igc-salas/
│
├── backend/                          # Aplicação Django
│   ├── igc_salas/                    # Projeto principal
│   │   ├── settings/
│   │   │   ├── base.py               # Configurações base
│   │   │   ├── development.py        # Desenvolvimento
│   │   │   └── production.py         # Produção
│   │   ├── urls.py                   # URLs principais
│   │   ├── wsgi.py                   # WSGI entry point
│   │   └── celery.py                 # Config Celery
│   │
│   ├── apps/
│   │   ├── core/                     # Núcleo: views públicas, busca, dashboard
│   │   │   ├── api_busca.py          # API de busca em tempo real
│   │   │   ├── middleware.py         # Audit log, request logging
│   │   │   └── context_processors.py
│   │   │
│   │   ├── accounts/                 # Usuários e autenticação
│   │   │   ├── models.py             # Usuario (AbstractUser)
│   │   │   └── views.py              # Login, Logout, Perfil
│   │   │
│   │   ├── estrutura/                # Estrutura física
│   │   │   └── models.py             # Predio, Andar, Sala, Equipamento
│   │   │
│   │   ├── academico/                # Módulo acadêmico
│   │   │   └── models.py             # Professor, Disciplina, Turma
│   │   │
│   │   ├── reservas/                 # Sistema de reservas
│   │   │   ├── models.py             # Reserva, LogReserva
│   │   │   ├── services.py           # Lógica de negócio
│   │   │   ├── views.py              # Views do sistema
│   │   │   └── signals.py            # Automação de notificações
│   │   │
│   │   ├── notificacoes/             # Notificações internas e e-mail
│   │   │   ├── models.py             # Notificacao
│   │   │   ├── services.py           # NotificacaoService
│   │   │   └── tasks.py              # Tasks Celery
│   │   │
│   │   └── importacao/               # Importação de CSV
│   │       ├── models.py             # ImportacaoCSV
│   │       └── processador.py        # CSVImportador
│   │
│   ├── templates/                    # Templates HTML
│   ├── static/                       # CSS, JS, imagens
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
│
├── nginx/
│   ├── nginx.conf                    # Configuração principal
│   └── conf.d/igc_salas.conf         # Virtual host
│
├── docker/
│   └── postgres/init.sql             # Inicialização do BD
│
├── docs/
│   └── modelo_importacao.csv         # Modelo CSV para importação
│
├── docker-compose.yml
├── .env                              # Variáveis de ambiente
└── README.md
```

---

## 🔐 Perfis de Acesso

| Perfil | Permissões |
|---|---|
| **Administrador** | Acesso total: override, importação, aprovação, CRUD completo |
| **Responsável** | Aprovação/rejeição de reservas, importação CSV, visualização total |
| **Professor** | Criar/cancelar próprias reservas, visualizar agenda |
| **Público** | Busca pública de salas, professores, turmas (sem login) |

---

## 🔌 API REST — Endpoints Principais

### Autenticação
```
POST   /api/v1/auth/token/           # Obter token JWT
POST   /api/v1/auth/token/refresh/   # Renovar token
```

### Busca (pública)
```
GET    /api/v1/busca/?q=termo&tipo=todos|sala|professor|turma
GET    /api/v1/busca/agenda-sala/<slug>/
GET    /api/v1/busca/agenda-professor/<slug>/
```

### Reservas
```
GET    /api/v1/reservas/             # Listar reservas
POST   /api/v1/reservas/             # Criar reserva
GET    /api/v1/reservas/<id>/        # Detalhe
POST   /api/v1/reservas/<id>/aprovar/
POST   /api/v1/reservas/<id>/rejeitar/
```

### Sistema
```
GET    /api/v1/health/               # Health check
GET    /api/v1/notificacoes/         # Notificações do usuário
```

---

## 📊 Modelo de Dados

```
Predio (1) ──── (N) Andar (1) ──── (N) Sala (1) ──── (N) Equipamento
                                        │
                                        └─── (N) Reserva (N) ──── (1) Usuario
                                                    │
                                                    ├─── (1) Turma ──── (1) Disciplina
                                                    │         └──────── (1) Professor ──── (1) Usuario
                                                    └─── (N) LogReserva
                                                              │
                                                              └─── (N) Notificacao ──── (1) Usuario
```

---

## 🔄 Fluxo de Reservas

```
Professor solicita reserva
        │
        ▼
[PENDENTE] ──── Sistema verifica conflito
        │           │
        │      Conflito detectado? ──── SIM ──── Erro retornado
        │           │
        │          NÃO
        │           │
        │      Solicitante é admin? ──── SIM ──── [APROVADA automaticamente]
        │           │
        │          NÃO
        ▼           ▼
[PENDENTE] ──── Admin/Responsável avalia
        │
        ├──── Aprovar ──── [APROVADA] ──── Notificação e-mail
        │
        ├──── Rejeitar + Motivo ──── [REJEITADA] ──── Notificação e-mail
        │
        └──── Override ──── [SUBSTITUIDA] ──── [NOVA APROVADA] ──── Notificação urgente
```

---

## 📁 Importação CSV

Formato do arquivo:
```csv
sala_codigo,data,hora_inicio,hora_fim,disciplina_codigo,professor_siape,turma_codigo
IGC-101,2025-03-03,08:00,09:40,GEO001,1234567,T01
LAB-GEO-1,2025-03-05,14:00,17:50,GEO002,2345678,T02
```

Processo:
1. Upload do arquivo em `/importacao/`
2. Sistema valida formato e detecta conflitos
3. Relatório pré-visualização sem confirmar
4. Confirmação cria todas as reservas aprovadas

---

## 🔒 Segurança Implementada

- ✅ ORM Django — proteção contra SQL Injection
- ✅ CSRF Protection em todos os formulários
- ✅ Senhas com hash PBKDF2 (padrão Django)
- ✅ Rate limiting no Nginx (login: 5r/min, API: 30r/min)
- ✅ Headers de segurança (XSS, X-Frame, CSP)
- ✅ Logs de auditoria para todas as ações POST/PUT/DELETE
- ✅ URLs mascaradas (sem expor estrutura interna)
- ✅ Usuário não-root no Docker
- ✅ Separação de ambientes (dev/prod)
- ✅ JWT com expiração de 8h

---

## 🐳 Comandos Docker Úteis

```bash
# Subir serviços
docker compose up -d

# Ver logs
docker compose logs -f backend
docker compose logs -f nginx

# Parar serviços
docker compose down

# Reconstruir após mudanças no código
docker compose up -d --build

# Acessar shell Django
docker compose exec backend python manage.py shell

# Criar migrações
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate

# Criar superusuário adicional
docker compose exec backend python manage.py createsuperuser

# Backup do banco
docker compose exec db pg_dump -U igc_admin igc_salas_db > backup.sql

# Restaurar banco
docker compose exec -T db psql -U igc_admin igc_salas_db < backup.sql
```

---

## 🖥️ Telas do Sistema

| Tela | URL | Acesso |
|---|---|---|
| Busca Pública | `/` | Público |
| Login | `/entrar/` | Público |
| Dashboard | `/dashboard/` | Autenticado |
| Nova Reserva | `/reservas/nova/` | Autenticado |
| Minhas Reservas | `/reservas/` | Autenticado |
| Pendentes | `/reservas/pendentes/` | Responsável+ |
| Importar CSV | `/importacao/` | Responsável+ |
| Admin Django | `/igc-admin-portal/` | Superusuário |

---

## 🚧 Próximas Implementações (Roadmap)

- [ ] Dashboard de ocupação com gráficos Chart.js
- [ ] Calendário visual de reservas (FullCalendar.js)
- [ ] Exportação de relatórios em PDF/Excel
- [ ] Notificações push (WebSocket)
- [ ] App mobile (PWA)
- [ ] Integração com SIGAA/sistemas universitários
- [ ] QR Code para salas
- [ ] Controle de chaves (check-in/check-out)

---

## 🐛 Solução de Problemas

**Banco não sobe:**
```bash
docker compose logs db
docker compose restart db
```

**Backend com erro:**
```bash
docker compose logs backend
docker compose exec backend python manage.py check
```

**Permissão negada no entrypoint:**
```bash
chmod +x backend/entrypoint.sh
docker compose up -d --build
```

**Porta 80 em uso:**
```bash
sudo lsof -i :80
sudo systemctl stop apache2  # se Apache estiver rodando
```

---

## 📄 Licença

Sistema desenvolvido para uso interno do Instituto de Geociências — UFMG.
Todos os direitos reservados.

---

*Última atualização: Março 2025*
