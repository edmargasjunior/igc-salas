"""Views de autenticação."""
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import PasswordResetForm
from django.shortcuts import render, redirect
from django.contrib import messages
from django.views import View
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect
from django.contrib.auth.decorators import login_required


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

        return render(request, self.template_name, {'username': username})


class LogoutView(View):
    def post(self, request):
        logout(request)
        messages.info(request, 'Você saiu do sistema com segurança.')
        return redirect('/')

    def get(self, request):
        logout(request)
        return redirect('/')


class PerfilView(View):
    template_name = 'accounts/perfil.html'

    @method_decorator(login_required)
    def get(self, request):
        return render(request, self.template_name, {'usuario': request.user})

    @method_decorator(login_required)
    def post(self, request):
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.email = request.POST.get('email', user.email)
        user.telefone = request.POST.get('telefone', user.telefone)
        user.save()
        messages.success(request, 'Perfil atualizado com sucesso.')
        return redirect('perfil')
