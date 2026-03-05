"""Views de autenticação completas incluindo recuperação de senha."""
from django.contrib.auth import login, logout, authenticate
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger('apps.accounts')


class LoginView(View):
    template_name = 'accounts/login.html'

    def get(self, request):
        if request.user.is_authenticated:
            return redirect('dashboard')
        return render(request, self.template_name)

    @method_decorator(csrf_protect)
    def post(self, request):
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not username or not password:
            messages.error(request, 'Informe usuário e senha.')
            return render(request, self.template_name)

        user = authenticate(request, username=username, password=password)
        if user is not None:
            if user.is_active:
                login(request, user)
                messages.success(request, f'Bem-vindo, {user.first_name or user.username}!')
                next_url = request.GET.get('next', '/dashboard/')
                return redirect(next_url)
            else:
                messages.error(request, 'Conta desativada. Entre em contato com a administração.')
        else:
            messages.error(request, 'Usuário ou senha incorretos.')
            logger.warning(f"Tentativa de login falha para usuário: {username}")

        return render(request, self.template_name, {'username': username})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'Você saiu do sistema com segurança.')
        return redirect('/')

    def get(self, request):
        logout(request)
        return redirect('/')


class RecuperarSenhaView(View):
    template_name = 'accounts/recuperar_senha.html'

    def get(self, request):
        return render(request, self.template_name)

    @method_decorator(csrf_protect)
    def post(self, request):
        email = request.POST.get('email', '').strip().lower()
        if not email:
            messages.error(request, 'Informe um e-mail válido.')
            return render(request, self.template_name)

        from .models import Usuario
        user = Usuario.objects.filter(email__iexact=email, is_active=True).first()

        # Por segurança, sempre mostrar mensagem de sucesso
        # mesmo se o e-mail não existir (evita enumeração de usuários)
        if user:
            try:
                # Em produção, usar django.contrib.auth.views.PasswordResetView
                # Esta é uma implementação simplificada
                send_mail(
                    subject='[IGC Salas] Recuperação de Senha',
                    message=(
                        f'Olá, {user.first_name or user.username}!\n\n'
                        f'Recebemos uma solicitação de recuperação de senha para sua conta no IGC Salas.\n\n'
                        f'Por favor, entre em contato com o administrador do sistema para redefinir sua senha.\n\n'
                        f'Se você não solicitou isso, ignore este e-mail.\n\n'
                        f'Equipe IGC Salas'
                    ),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[email],
                    fail_silently=True,
                )
                logger.info(f"E-mail de recuperação enviado para: {email}")
            except Exception as e:
                logger.error(f"Erro ao enviar e-mail de recuperação: {e}")

        return render(request, self.template_name, {'enviado': True, 'email': email})


class PerfilView(View):
    template_name = 'accounts/perfil.html'

    @method_decorator(login_required)
    def get(self, request):
        return render(request, self.template_name, {'usuario': request.user})

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name).strip()
        user.last_name = request.POST.get('last_name', user.last_name).strip()
        user.email = request.POST.get('email', user.email).strip()
        user.telefone = request.POST.get('telefone', user.telefone).strip()
        user.departamento = request.POST.get('departamento', user.departamento).strip()
        user.save()
        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('perfil')
