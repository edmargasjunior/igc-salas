#!/bin/bash
set -e

echo "============================================"
echo " IGC SALAS - Iniciando Sistema"
echo " Instituto de Geociências"
echo "============================================"

# Aguardar banco de dados
echo "[*] Aguardando banco de dados PostgreSQL..."
while ! nc -z ${POSTGRES_HOST:-db} ${POSTGRES_PORT:-5432}; do
    echo "    ... aguardando conexão com o banco"
    sleep 2
done
echo "[OK] Banco de dados disponível!"

# Aguardar Redis
echo "[*] Aguardando Redis..."
while ! nc -z ${REDIS_HOST:-redis} 6379; do
    echo "    ... aguardando conexão com Redis"
    sleep 2
done
echo "[OK] Redis disponível!"

# Aplicar migrações
echo "[*] Aplicando migrações do banco de dados..."
python manage.py migrate --noinput

# Coletar arquivos estáticos
echo "[*] Coletando arquivos estáticos..."
python manage.py collectstatic --noinput

# Criar superusuário padrão se não existir
echo "[*] Verificando superusuário..."
python manage.py shell << 'EOF'
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@igc.ufmg.br',
        password='IGCAdmin@2025',
        first_name='Administrador',
        last_name='IGC'
    )
    print('[OK] Superusuário admin criado: admin / IGCAdmin@2025')
else:
    print('[OK] Superusuário já existe')
EOF

# Carregar dados iniciais
echo "[*] Carregando dados iniciais..."
python manage.py loaddata initial_data 2>/dev/null || echo "[INFO] Sem dados iniciais para carregar"

echo ""
echo "============================================"
echo " Sistema IGC Salas pronto!"
echo " Acesse: http://localhost"
echo " Admin:  http://localhost/admin"
echo " Login:  admin / IGCAdmin@2025"
echo "============================================"
echo ""

exec "$@"
