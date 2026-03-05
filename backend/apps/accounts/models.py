"""
App: accounts
Modelos de autenticação e perfis de usuário
"""
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify


class Usuario(AbstractUser):
    """
    Modelo de usuário customizado com perfis de acesso.
    Estende AbstractUser para adicionar campos específicos do IGC.
    """

    class Perfil(models.TextChoices):
        ADMINISTRADOR = 'administrador', _('Administrador')
        RESPONSAVEL = 'responsavel', _('Responsável pela Alocação')
        PROFESSOR = 'professor', _('Professor')

    # Campos extras
    perfil = models.CharField(
        max_length=20,
        choices=Perfil.choices,
        default=Perfil.PROFESSOR,
        verbose_name=_('Perfil')
    )
    matricula = models.CharField(
        max_length=20,
        blank=True,
        unique=True,
        null=True,
        verbose_name=_('Matrícula')
    )
    departamento = models.CharField(
        max_length=100,
        blank=True,
        verbose_name=_('Departamento')
    )
    telefone = models.CharField(
        max_length=20,
        blank=True,
        verbose_name=_('Telefone')
    )
    foto = models.ImageField(
        upload_to='usuarios/fotos/',
        blank=True,
        null=True,
        verbose_name=_('Foto')
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        verbose_name=_('Slug URL')
    )
    ativo = models.BooleanField(default=True, verbose_name=_('Ativo'))
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Usuário')
        verbose_name_plural = _('Usuários')
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.get_full_name() or self.username)
            slug = base_slug
            contador = 1
            while Usuario.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def nome_completo(self):
        return self.get_full_name() or self.username

    @property
    def is_admin(self):
        return self.perfil == self.Perfil.ADMINISTRADOR or self.is_superuser

    @property
    def is_responsavel(self):
        return self.perfil in [self.Perfil.ADMINISTRADOR, self.Perfil.RESPONSAVEL]

    @property
    def is_professor(self):
        return self.perfil == self.Perfil.PROFESSOR

    def pode_aprovar_reservas(self):
        return self.is_responsavel

    def pode_fazer_override(self):
        return self.is_admin
