# 🏛️ IGC Salas — Sistema de Gestão de Salas e Laboratórios

**Instituto de Geociências — UFMG**

Sistema web completo para reserva, gestão e consulta de salas, laboratórios e equipamentos do IGC/UFMG. Desenvolvido com Django 4.2, PostgreSQL, Redis, Celery e Docker.

---

## ✅ Funcionalidades Implementadas

### 🌐 Área Pública (sem login)
- [x] **Busca em tempo real** com autocomplete (salas, laboratórios, professores, turmas, disciplinas)
- [x] **Filtros** por tipo (sala, laboratório, informática, auditório), prédio, andar
- [x] **Página de detalhe** de cada sala com agenda semanal ao vivo
- [x] **Página de professor** com agenda semanal e turmas ativas
- [x] **Página de turma** com próximas reservas aprovadas
- [x] **Página de disciplina** com turmas vinculadas
- [x] **Lista de salas** com filtros por tipo e prédio

### 🔐 Autenticação e Perfis
- [x] Login / Logout com session-based auth + CSRF protection
- [x] Recuperação de senha via e-mail
- [x] Perfis: **Administrador**, **Responsável pela Alocação**, **Professor**
- [x] Controle de permissões por perfil em todas as views
- [x] Edição de perfil pessoal

### 🏗️ CRUD — Estrutura Física
- [x] **Prédios**: listagem e cadastro
- [x] **Andares**: vinculados aos prédios
- [x] **Salas e Laboratórios**: CRUD completo (criar/editar/desativar)
  - Tipos: sala_aula, laboratório, auditório, sala_informática, sala_reunião, estúdio
  - Recursos: projetor, A/C, lousa digital, videoconferência, acessibilidade, computadores
- [x] **Equipamentos**: CRUD completo com patrimônio, modelo, fabricante, garantia, estado de conservação

### 📚 CRUD — Acadêmico
- [x] **Disciplinas**: código, nome, ementa, carga horária, créditos, modalidade
- [x] **Professores**: SIAPE, titulação, área de atuação, Lattes, criação de conta vinculada
- [x] **Turmas**: professor → disciplina → turma (ano/semestre), vagas, matriculados

### 📅 Sistema de Reservas
- [x] **Reservas pontuais** (data/hora específica)
- [x] **Reservas recorrentes** (semanal/quinzenal com data de fim)
- [x] **Detecção de conflitos** em tempo real antes de salvar
- [x] **Fluxo de aprovação**: pendente → aprovada → rejeitada/cancelada/substituída
- [x] **Auto-aprovação** para Responsáveis e Administradores
- [x] **Painel de reservas pendentes** para aprovadores
- [x] **Histórico completo** (audit log imutável) de cada reserva
- [x] **Override administrativo**: cancela reserva existente, cria nova, notifica professor

### 🔔 Notificações
- [x] **Notificações internas** (badge no menu, listagem)
- [x] **E-mail** para aprovação, rejeição, cancelamento e override (via Celery)
- [x] Notificações não lidas no context processor global

### 📊 Dashboard
- [x] **Métricas rápidas**: total salas, reservas hoje, semana, pendentes
- [x] **Minhas reservas** recentes
- [x] **Reservas de hoje** para responsáveis
- [x] **Pendentes** para aprovação (responsáveis/admin)
- [x] **Dashboard de ocupação** com gráficos Chart.js: ocupação por sala, por status, tendência 14 dias

### 📥 Importação CSV
- [x] Upload de arquivo CSV com planejamento semestral
- [x] Modo **validação** com pré-visualização do relatório (linhas válidas, erros, conflitos)
- [x] Modo **confirmação** de importação em lote
- [x] Histórico de importações
- [x] Modelo CSV de exemplo em `/docs/modelo_importacao.csv`

### 🔧 API REST
- [x] Endpoints com DRF + JWT auth
- [x] Busca global em tempo real (autocomplete)
- [x] CRUD de reservas via API
- [x] ViewSets para estrutura (prédios, salas, equipamentos) e acadêmico (professores, disciplinas, turmas)
- [x] Estatísticas do dashboard (ocupação, status, tendência, notificações)

---

## 🛠️ Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| Backend | Python 3.11, Django 4.2, DRF 3.15 |
| Banco de Dados | PostgreSQL 16 |
| Cache/Broker | Redis 7 |
| Tarefas Assíncronas | Celery 5.4 + django-celery-beat |
| Servidor WSGI | Gunicorn 23 |
| Proxy Reverso | Nginx Alpine |
| Frontend | Bootstrap 5.3, Chart.js, Bootstrap Icons |
| Containerização | Docker, Docker Compose |

---

## 🚀 Instalação e Deploy

### Pré-requisitos
- Docker >= 24.0
- Docker Compose >= 2.20
- 2 GB RAM mínimo

### 1. Clonar o repositório
```bash
git clone https://github.com/edmargasjunior/igc-salas.git
cd igc-salas
```

### 2. Configurar variáveis de ambiente
```bash
cp .env.example .env
# Edite o .env e defina:
# - SECRET_KEY (chave segura para produção)
# - POSTGRES_PASSWORD (senha forte)
# - EMAIL_HOST_USER e EMAIL_HOST_PASSWORD (para notificações)
```

### 3. Subir os containers
```bash
docker compose up -d
```

Aguarde ~30 segundos para a inicialização completa. O sistema irá:
- Criar o banco de dados PostgreSQL
- Aplicar todas as migrações
- Coletar arquivos estáticos
- Criar o superusuário padrão `admin / IGCAdmin@2025`
- Carregar dados iniciais (prédios, salas, disciplinas de exemplo)

### 4. Acessar o sistema
| URL | Descrição |
|-----|-----------|
| `http://localhost` | Tela pública de busca |
| `http://localhost/entrar/` | Login |
| `http://localhost/dashboard/` | Dashboard (autenticado) |
| `http://localhost/salas/` | Lista de salas |
| `http://localhost/igc-admin-portal/` | Admin Django |
| `http://localhost/api/v1/` | API REST |

**Login padrão:**
- Usuário: `admin`
- Senha: `IGCAdmin@2025`

> ⚠️ **Importante:** Altere a senha do admin após o primeiro acesso!

---

## 📁 Estrutura do Projeto

```
igc-salas/
├── backend/
│   ├── apps/
│   │   ├── core/           # Views principais, busca global, dashboard
│   │   ├── accounts/       # Autenticação, perfis de usuário
│   │   ├── estrutura/      # Prédios, Andares, Salas, Equipamentos
│   │   ├── academico/      # Professores, Disciplinas, Turmas
│   │   ├── reservas/       # Sistema de reservas
│   │   ├── notificacoes/   # Notificações internas e e-mail
│   │   └── importacao/     # Importação CSV semestral
│   ├── igc_salas/
│   │   ├── settings/       # base.py, development.py, production.py
│   │   ├── urls.py         # URLs principais
│   │   ├── celery.py       # Configuração Celery
│   │   └── wsgi.py
│   ├── static/             # CSS, JS globais
│   ├── templates/          # Templates HTML
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
├── nginx/
│   ├── nginx.conf
│   └── conf.d/igc_salas.conf
├── docker/
│   └── postgres/init.sql
├── docs/
│   └── modelo_importacao.csv
├── docker-compose.yml
├── .env.example
└── README.md
```

---

## 🌐 Endpoints Principais

### Área Pública
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/` | Tela de busca pública |
| GET | `/salas/` | Lista de salas e laboratórios |
| GET | `/salas/<slug>/` | Detalhe de sala + agenda semanal |
| GET | `/professor/<slug>/` | Agenda do professor |
| GET | `/turma/<slug>/` | Turma + próximas reservas |

### Autenticação
| Método | URL | Descrição |
|--------|-----|-----------|
| GET/POST | `/entrar/` | Login |
| GET/POST | `/sair/` | Logout |
| GET/POST | `/recuperar-senha/` | Recuperação de senha |
| GET/POST | `/perfil/` | Editar perfil |

### Dashboard (autenticado)
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/dashboard/` | Painel principal |
| GET | `/dashboard/ocupacao/` | Gráficos de ocupação |

### Reservas (autenticado)
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/reservas/` | Minhas reservas |
| GET/POST | `/reservas/nova/` | Nova reserva |
| GET | `/reservas/pendentes/` | Reservas pendentes (aprovadores) |
| GET | `/reservas/<pk>/` | Detalhe da reserva |
| GET/POST | `/reservas/<pk>/aprovar/` | Aprovar reserva |
| GET/POST | `/reservas/<pk>/rejeitar/` | Rejeitar reserva |
| GET/POST | `/reservas/<pk>/override/` | Override administrativo |

### Estrutura (responsável/admin)
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/estrutura/salas/` | Lista admin de salas |
| GET/POST | `/estrutura/salas/nova/` | Criar sala |
| GET/POST | `/estrutura/salas/<pk>/editar/` | Editar sala |
| POST | `/estrutura/salas/<pk>/excluir/` | Desativar sala |
| GET | `/estrutura/predios/` | Lista de prédios |
| GET | `/estrutura/equipamentos/` | Lista de equipamentos |
| GET/POST | `/estrutura/equipamentos/novo/` | Cadastrar equipamento |

### Acadêmico (autenticado)
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/academico/professores/` | Lista de professores |
| GET/POST | `/academico/professores/novo/` | Cadastrar professor |
| GET | `/academico/turmas/` | Lista de turmas |
| GET/POST | `/academico/turmas/nova/` | Criar turma |
| GET | `/academico/disciplinas/<slug>/` | Detalhe disciplina |

### Importação CSV
| Método | URL | Descrição |
|--------|-----|-----------|
| GET/POST | `/importacao/` | Interface de importação CSV |

### API REST
| Método | URL | Descrição |
|--------|-----|-----------|
| GET | `/api/v1/health/` | Health check |
| GET | `/api/v1/busca/?q=termo` | Busca global autocomplete |
| GET | `/api/v1/busca/agenda-sala/<id>/` | Agenda semanal da sala |
| GET | `/api/v1/busca/agenda-professor/<id>/` | Agenda do professor |
| * | `/api/v1/estrutura/predios/` | CRUD prédios |
| * | `/api/v1/estrutura/salas/` | CRUD salas |
| * | `/api/v1/estrutura/equipamentos/` | CRUD equipamentos |
| * | `/api/v1/academico/professores/` | CRUD professores |
| * | `/api/v1/academico/disciplinas/` | CRUD disciplinas |
| * | `/api/v1/academico/turmas/` | CRUD turmas |
| * | `/api/v1/reservas/` | CRUD reservas |
| GET | `/api/v1/reservas/stats/ocupacao/` | Stats ocupação por sala |
| GET | `/api/v1/reservas/stats/status/` | Stats por status |
| GET | `/api/v1/reservas/stats/tendencia/` | Tendência 14 dias |
| GET | `/api/v1/notificacoes/recentes/` | Notificações recentes |
| POST | `/api/v1/auth/token/` | Obter JWT token |
| POST | `/api/v1/auth/token/refresh/` | Renovar JWT token |

---

## 📋 Formato do CSV de Importação

```csv
codigo_sala,data,hora_inicio,hora_fim,disciplina_codigo,turma_codigo,motivo,recorrente,data_fim,professor_siape
LAB-GEO-01,14/03/2025,08:00,09:40,IGC001,T1,Aula regular semestral,sim,04/07/2025,1234567
SALA-101,17/03/2025,14:00,15:40,IGC003,T3,Aula regular,sim,04/07/2025,1234569
AUD-01,20/03/2025,09:00,11:00,IGC004,T1,Seminário especial,nao,,1234567
```

Exemplo completo em: `/docs/modelo_importacao.csv`

---

## 🔒 Segurança

- Proteção CSRF em todos os formulários POST
- Hash de senha bcrypt (Django AbstractUser)
- Rate limiting configurado no Nginx
- Headers de segurança: X-Frame-Options, X-Content-Type-Options, HSTS
- ORM do Django em todas as queries (sem SQL raw)
- URLs mascaradas (sem IDs expostos nas públicas)
- Audit log imutável para todas as ações em reservas
- Usuário não-root no container Docker
- Secrets via variáveis de ambiente (nunca em código)

---

## 🐳 Comandos Úteis

```bash
# Ver logs do sistema
docker compose logs -f backend

# Criar migrations
docker compose exec backend python manage.py makemigrations

# Aplicar migrations
docker compose exec backend python manage.py migrate

# Criar superusuário
docker compose exec backend python manage.py createsuperuser

# Backup do banco
docker compose exec db pg_dump -U igc_admin igc_salas_db > backup.sql

# Restaurar backup
docker compose exec -T db psql -U igc_admin igc_salas_db < backup.sql

# Reiniciar serviços
docker compose restart backend

# Parar tudo
docker compose down

# Parar e remover volumes (CUIDADO: apaga o banco!)
docker compose down -v
```

---

## 📧 Configuração de E-mail

Para habilitar notificações por e-mail em produção, configure no `.env`:

```env
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=seu-email@gmail.com
EMAIL_HOST_PASSWORD=sua-senha-de-app  # Use App Password do Google
DEFAULT_FROM_EMAIL=IGC Salas <seu-email@gmail.com>
```

---

## 🗄️ Modelos de Dados Principais

```
Predio ──< Andar ──< Sala ──< Equipamento
                       |
                       └──< Reserva >── LogReserva
                                  \
Professor ──< Turma ──────────────'
     |          |
     └─── Disciplina
```

---

## 📅 Status do Projeto

| Módulo | Status |
|--------|--------|
| Infraestrutura Docker | ✅ Completo |
| Autenticação | ✅ Completo |
| Estrutura Física (CRUD) | ✅ Completo |
| Acadêmico (CRUD) | ✅ Completo |
| Sistema de Reservas | ✅ Completo |
| Override Administrativo | ✅ Completo |
| Notificações (sistema + e-mail) | ✅ Completo |
| Dashboard + Gráficos | ✅ Completo |
| Importação CSV | ✅ Completo |
| API REST | ✅ Completo |
| Busca Pública em Tempo Real | ✅ Completo |
| Audit Log | ✅ Completo |

---

## 👤 Usuários Padrão

| Usuário | Senha | Perfil |
|---------|-------|--------|
| admin | IGCAdmin@2025 | Administrador |

> ⚠️ Altere as senhas imediatamente após o primeiro acesso em produção!

---

## 📝 Licença

Projeto desenvolvido para o Instituto de Geociências — UFMG.
