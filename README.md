# IGC Salas — Sistema de Gestão de Salas e Laboratórios

## Instituto de Geociências (IGC) — UFMG

Sistema web completo para gestão de salas e laboratórios acadêmicos, desenvolvido com **Django + PostgreSQL + Docker**.

---

## 🚀 Início Rápido

```bash
git clone https://github.com/edmargasjunior/igc-salas.git
cd igc-salas
cp .env.example .env   # edite as variáveis conforme necessário
docker compose up -d
```

Acesse: **http://localhost**  
Admin: `admin` / `IGCAdmin@2025`

---

## 🏗️ Stack Tecnológica

| Camada | Tecnologia |
|---|---|
| Backend | Python 3.11, Django 4.2, Django REST Framework |
| Frontend | HTML5, CSS3, Bootstrap 5, JavaScript ES6+ |
| Banco de Dados | PostgreSQL 16 |
| Cache / Filas | Redis 7, Celery |
| Servidor Web | Nginx (reverse proxy), Gunicorn (WSGI) |
| Containerização | Docker, Docker Compose |

---

## 📁 Estrutura do Projeto

```
igc-salas/
├── backend/
│   ├── igc_salas/          # Configurações Django (settings, urls, wsgi)
│   ├── apps/
│   │   ├── core/           # Views públicas, busca, dashboard, middlewares
│   │   ├── accounts/       # Autenticação, perfis (Admin, Responsável, Professor)
│   │   ├── estrutura/      # Prédios, Andares, Salas, Equipamentos
│   │   ├── academico/      # Professores, Disciplinas, Turmas
│   │   ├── reservas/       # Sistema de reservas, conflitos, override, logs
│   │   ├── notificacoes/   # Notificações internas e e-mail
│   │   └── importacao/     # Importação de planejamento via CSV
│   ├── templates/          # Templates HTML organizados por módulo
│   ├── static/             # CSS, JS, imagens
│   ├── requirements.txt
│   ├── Dockerfile
│   └── entrypoint.sh
├── nginx/
│   ├── nginx.conf
│   └── conf.d/igc_salas.conf
├── docker/
│   └── postgres/init.sql
├── docker-compose.yml
├── .env                    # Variáveis de ambiente (não comitar em produção)
└── README.md
```

---

## 🔑 Perfis de Acesso

| Perfil | Permissões |
|---|---|
| **Administrador** | Acesso total, override de reservas, importação CSV, gestão de usuários |
| **Responsável pela Alocação** | Aprovar/rejeitar reservas, gestão de salas e turmas |
| **Professor** | Solicitar reservas, ver agenda própria |

---

## 🗓️ Funcionalidades

### Tela Pública (sem login)
- Busca em tempo real (autocomplete) por sala, laboratório, professor, turma, disciplina
- Agenda semanal de qualquer sala ou laboratório
- Agenda semanal de qualquer professor

### Sistema de Reservas
- Reservas pontuais e recorrentes (semanais/quinzenais)
- Detecção automática de conflitos de horário
- Fluxo de aprovação: Pendente → Aprovada / Rejeitada
- Override administrativo com log de auditoria
- Notificações automáticas (sistema + e-mail)

### Importação CSV
- Upload de planejamento semestral completo
- Validação de formato e campos
- Detecção prévia de conflitos
- Relatório detalhado antes da confirmação

### Dashboard Administrativo
- Métricas de ocupação por sala e professor
- Reservas pendentes de aprovação
- Agenda do dia
- Notificações em tempo real
- Gráficos com Chart.js

---

## 🔒 Segurança

- ORM Django (proteção contra SQL injection)
- CSRF protection em todos os formulários
- Hash seguro de senhas (PBKDF2 + SHA256)
- Rate limiting no Nginx (login e API)
- Logs de auditoria completos
- URLs limpas e mascaradas
- Headers de segurança (XSS, HSTS, CSP)
- Usuário não-root no container Docker

---

## 🌐 Endpoints da API

```
GET  /api/v1/health/                         Health check
GET  /api/v1/busca/?q=termo&tipo=sala        Busca global
GET  /api/v1/busca/agenda-sala/<slug>/       Agenda semanal da sala
GET  /api/v1/busca/agenda-professor/<slug>/  Agenda semanal do professor
```

---

## 🐳 Serviços Docker

| Serviço | Descrição | Porta |
|---|---|---|
| `nginx` | Reverse proxy | 80, 443 |
| `backend` | Django + Gunicorn | 8000 (interno) |
| `db` | PostgreSQL 16 | 5432 (interno) |
| `redis` | Cache + Broker | 6379 (interno) |
| `celery_worker` | Tarefas assíncronas | — |
| `celery_beat` | Tarefas agendadas | — |

---

## ⚙️ Variáveis de Ambiente (.env)

```env
SECRET_KEY=sua-chave-secreta
DEBUG=False
POSTGRES_DB=igc_salas_db
POSTGRES_USER=igc_admin
POSTGRES_PASSWORD=sua-senha-segura
EMAIL_HOST=smtp.gmail.com
EMAIL_HOST_USER=seu@email.com
EMAIL_HOST_PASSWORD=sua-senha-app
```

---

## 📜 URLs do Sistema

```
/                           Tela pública de busca
/entrar/                    Login
/dashboard/                 Painel principal
/reservas/                  Minhas reservas
/reservas/nova/             Nova reserva
/salas/<slug>/              Detalhe da sala
/professor/<slug>/          Agenda do professor
/turma/<slug>/              Detalhe da turma
/estrutura/salas/           Gestão de salas (admin)
/importacao/                Importação CSV (admin)
/igc-admin-portal/          Django Admin
```

---

## 👥 Desenvolvimento

Desenvolvido para o **Instituto de Geociências — UFMG**  
Arquitetura MVC com Django REST Framework  
Interface moderna estilo SaaS Dashboard  

---

**© 2025 IGC Salas — Instituto de Geociências**
