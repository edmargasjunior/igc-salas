"""
App: academico
Modelos acadêmicos: Professores, Disciplinas, Turmas
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from apps.accounts.models import Usuario


class Professor(models.Model):
    """
    Perfil de professor vinculado ao usuário do sistema.
    Um professor pode ministrar várias disciplinas e turmas.
    """

    class Titulacao(models.TextChoices):
        GRADUADO = 'graduado', _('Graduado')
        ESPECIALISTA = 'especialista', _('Especialista')
        MESTRE = 'mestre', _('Mestre')
        DOUTOR = 'doutor', _('Doutor')
        POS_DOUTOR = 'pos_doutor', _('Pós-Doutor')

    usuario = models.OneToOneField(
        Usuario,
        on_delete=models.CASCADE,
        related_name='professor',
        verbose_name=_('Usuário')
    )
    siape = models.CharField(
        max_length=20, unique=True,
        verbose_name=_('SIAPE')
    )
    titulacao = models.CharField(
        max_length=20,
        choices=Titulacao.choices,
        default=Titulacao.DOUTOR,
        verbose_name=_('Titulação')
    )
    area_atuacao = models.CharField(
        max_length=100, blank=True,
        verbose_name=_('Área de Atuação')
    )
    lattes = models.URLField(blank=True, verbose_name=_('Link Lattes'))
    slug = models.SlugField(max_length=120, unique=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Professor')
        verbose_name_plural = _('Professores')
        ordering = ['usuario__first_name', 'usuario__last_name']

    def __str__(self):
        return f"Prof. {self.usuario.nome_completo}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(self.usuario.nome_completo)
            slug = base
            contador = 1
            while Professor.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def nome(self):
        return self.usuario.nome_completo

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('professor_detalhe', kwargs={'slug': self.slug})


class Disciplina(models.Model):
    """Disciplina acadêmica ministrada no IGC."""

    class Modalidade(models.TextChoices):
        PRESENCIAL = 'presencial', _('Presencial')
        EAD = 'ead', _('EAD')
        HIBRIDO = 'hibrido', _('Híbrido')

    codigo = models.CharField(
        max_length=20, unique=True,
        verbose_name=_('Código')
    )
    nome = models.CharField(max_length=150, verbose_name=_('Nome'))
    ementa = models.TextField(blank=True, verbose_name=_('Ementa'))
    carga_horaria = models.IntegerField(
        default=60,
        verbose_name=_('Carga Horária (horas)')
    )
    creditos = models.IntegerField(default=4, verbose_name=_('Créditos'))
    modalidade = models.CharField(
        max_length=15,
        choices=Modalidade.choices,
        default=Modalidade.PRESENCIAL
    )
    departamento = models.CharField(
        max_length=100, blank=True,
        verbose_name=_('Departamento')
    )
    slug = models.SlugField(max_length=170, unique=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Disciplina')
        verbose_name_plural = _('Disciplinas')
        ordering = ['nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.codigo}-{self.nome}")
        super().save(*args, **kwargs)


class Turma(models.Model):
    """
    Turma: vincula disciplina, professor e semestre.
    Uma turma pode ter múltiplos horários semanais regulares.
    """

    class Semestre(models.TextChoices):
        PRIMEIRO = '1', _('1º Semestre')
        SEGUNDO = '2', _('2º Semestre')

    class DiaSemana(models.IntegerChoices):
        SEGUNDA = 0, _('Segunda-feira')
        TERCA = 1, _('Terça-feira')
        QUARTA = 2, _('Quarta-feira')
        QUINTA = 3, _('Quinta-feira')
        SEXTA = 4, _('Sexta-feira')
        SABADO = 5, _('Sábado')

    disciplina = models.ForeignKey(
        Disciplina, on_delete=models.CASCADE,
        related_name='turmas',
        verbose_name=_('Disciplina')
    )
    professor = models.ForeignKey(
        Professor, on_delete=models.SET_NULL,
        null=True, related_name='turmas',
        verbose_name=_('Professor')
    )
    codigo = models.CharField(max_length=20, verbose_name=_('Código da Turma'))
    ano = models.IntegerField(verbose_name=_('Ano'))
    semestre = models.CharField(
        max_length=1,
        choices=Semestre.choices,
        default=Semestre.PRIMEIRO,
        verbose_name=_('Semestre')
    )
    vagas = models.IntegerField(default=40, verbose_name=_('Vagas'))
    matriculados = models.IntegerField(default=0, verbose_name=_('Matriculados'))
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    ativo = models.BooleanField(default=True)
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Turma')
        verbose_name_plural = _('Turmas')
        ordering = ['-ano', '-semestre', 'disciplina__nome']
        unique_together = [('disciplina', 'codigo', 'ano', 'semestre')]

    def __str__(self):
        return f"{self.disciplina.codigo}-{self.codigo} ({self.ano}.{self.semestre})"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.disciplina.codigo}-{self.codigo}-{self.ano}-{self.semestre}")
            slug = base
            contador = 1
            while Turma.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('turma_detalhe', kwargs={'slug': self.slug})

    @property
    def periodo(self):
        return f"{self.ano}.{self.semestre}"
