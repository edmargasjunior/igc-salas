"""
App: estrutura
Modelos da estrutura física do IGC
Prédios → Andares → Salas/Laboratórios → Equipamentos
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils.text import slugify
from django.core.validators import MinValueValidator


class Predio(models.Model):
    """Representa um prédio do campus."""
    nome = models.CharField(max_length=100, verbose_name=_('Nome'))
    codigo = models.CharField(max_length=10, unique=True, verbose_name=_('Código'))
    descricao = models.TextField(blank=True, verbose_name=_('Descrição'))
    endereco = models.CharField(max_length=200, blank=True, verbose_name=_('Endereço'))
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    ativo = models.BooleanField(default=True, verbose_name=_('Ativo'))
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Prédio')
        verbose_name_plural = _('Prédios')
        ordering = ['nome']

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.nome)
        super().save(*args, **kwargs)


class Andar(models.Model):
    """Representa um andar dentro de um prédio."""
    predio = models.ForeignKey(
        Predio, on_delete=models.CASCADE,
        related_name='andares',
        verbose_name=_('Prédio')
    )
    numero = models.IntegerField(verbose_name=_('Número do Andar'))
    nome = models.CharField(max_length=50, blank=True, verbose_name=_('Nome'))
    descricao = models.TextField(blank=True, verbose_name=_('Descrição'))
    ativo = models.BooleanField(default=True)

    class Meta:
        verbose_name = _('Andar')
        verbose_name_plural = _('Andares')
        ordering = ['predio', 'numero']
        unique_together = [('predio', 'numero')]

    def __str__(self):
        if self.numero == 0:
            return f"Térreo - {self.predio.codigo}"
        return f"{self.numero}º Andar - {self.predio.codigo}"

    @property
    def nome_display(self):
        if self.nome:
            return self.nome
        return str(self)


class Sala(models.Model):
    """
    Representa uma sala ou laboratório.
    Esta é a entidade central do sistema.
    """

    class Tipo(models.TextChoices):
        SALA_AULA = 'sala_aula', _('Sala de Aula')
        LABORATORIO = 'laboratorio', _('Laboratório')
        SALA_REUNIAO = 'sala_reuniao', _('Sala de Reunião')
        AUDITORIO = 'auditorio', _('Auditório')
        ANFITEATRO = 'anfiteatro', _('Anfiteatro')
        SALA_INFORMATICA = 'sala_informatica', _('Sala de Informática')
        SALA_PESQUISA = 'sala_pesquisa', _('Sala de Pesquisa')
        OUTRO = 'outro', _('Outro')

    class Status(models.TextChoices):
        DISPONIVEL = 'disponivel', _('Disponível')
        OCUPADA = 'ocupada', _('Ocupada')
        MANUTENCAO = 'manutencao', _('Em Manutenção')
        INTERDITADA = 'interditada', _('Interditada')

    # Localização
    andar = models.ForeignKey(
        Andar, on_delete=models.CASCADE,
        related_name='salas',
        verbose_name=_('Andar')
    )

    # Identificação
    codigo = models.CharField(max_length=20, verbose_name=_('Código'))
    nome = models.CharField(max_length=100, verbose_name=_('Nome'))
    slug = models.SlugField(max_length=150, unique=True, blank=True)

    # Características
    tipo = models.CharField(
        max_length=20,
        choices=Tipo.choices,
        default=Tipo.SALA_AULA,
        verbose_name=_('Tipo')
    )
    capacidade = models.IntegerField(
        default=30,
        validators=[MinValueValidator(1)],
        verbose_name=_('Capacidade (pessoas)')
    )
    area_m2 = models.DecimalField(
        max_digits=8, decimal_places=2,
        null=True, blank=True,
        verbose_name=_('Área (m²)')
    )

    # Recursos disponíveis
    tem_projetor = models.BooleanField(default=False, verbose_name=_('Projetor'))
    tem_ar_condicionado = models.BooleanField(default=False, verbose_name=_('Ar Condicionado'))
    tem_lousa_digital = models.BooleanField(default=False, verbose_name=_('Lousa Digital'))
    tem_videoconferencia = models.BooleanField(default=False, verbose_name=_('Videoconferência'))
    tem_acessibilidade = models.BooleanField(default=False, verbose_name=_('Acessibilidade'))
    tem_computadores = models.BooleanField(default=False, verbose_name=_('Computadores'))
    qtd_computadores = models.IntegerField(default=0, verbose_name=_('Qtd. Computadores'))
    observacoes_recursos = models.TextField(blank=True, verbose_name=_('Observações sobre Recursos'))

    # Status e controle
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.DISPONIVEL,
        verbose_name=_('Status')
    )
    descricao = models.TextField(blank=True, verbose_name=_('Descrição'))
    foto = models.ImageField(upload_to='salas/fotos/', blank=True, null=True, verbose_name=_('Foto'))
    ativo = models.BooleanField(default=True, verbose_name=_('Ativo'))
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Sala')
        verbose_name_plural = _('Salas')
        ordering = ['andar__predio__codigo', 'andar__numero', 'codigo']
        unique_together = [('andar', 'codigo')]

    def __str__(self):
        return f"{self.codigo} - {self.nome}"

    def save(self, *args, **kwargs):
        if not self.slug:
            base = slugify(f"{self.andar.predio.codigo}-{self.nome}")
            slug = base
            contador = 1
            while Sala.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base}-{contador}"
                contador += 1
            self.slug = slug
        super().save(*args, **kwargs)

    @property
    def nome_completo(self):
        return f"{self.andar.predio.codigo} - {str(self.andar)} - {self.nome}"

    @property
    def is_laboratorio(self):
        return self.tipo == self.Tipo.LABORATORIO

    @property
    def predio(self):
        return self.andar.predio

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('sala_detalhe', kwargs={'slug': self.slug})


class Equipamento(models.Model):
    """
    Equipamentos pertencentes a uma sala.
    Controle de patrimônio, garantia e estado de conservação.
    """

    class Estado(models.TextChoices):
        OTIMO = 'otimo', _('Ótimo')
        BOM = 'bom', _('Bom')
        REGULAR = 'regular', _('Regular')
        RUIM = 'ruim', _('Ruim')
        INOPERANTE = 'inoperante', _('Inoperante')

    sala = models.ForeignKey(
        Sala, on_delete=models.CASCADE,
        related_name='equipamentos',
        verbose_name=_('Sala')
    )
    nome = models.CharField(max_length=100, verbose_name=_('Nome'))
    patrimonio = models.CharField(
        max_length=50,
        unique=True,
        verbose_name=_('Número de Patrimônio')
    )
    modelo = models.CharField(max_length=100, blank=True, verbose_name=_('Modelo'))
    fabricante = models.CharField(max_length=100, blank=True, verbose_name=_('Fabricante'))
    numero_serie = models.CharField(max_length=100, blank=True, verbose_name=_('Número de Série'))
    descricao = models.TextField(blank=True, verbose_name=_('Descrição'))
    quantidade = models.IntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        verbose_name=_('Quantidade')
    )
    data_aquisicao = models.DateField(null=True, blank=True, verbose_name=_('Data de Aquisição'))
    data_garantia = models.DateField(null=True, blank=True, verbose_name=_('Data de Fim de Garantia'))
    valor_aquisicao = models.DecimalField(
        max_digits=12, decimal_places=2,
        null=True, blank=True,
        verbose_name=_('Valor de Aquisição (R$)')
    )
    estado_conservacao = models.CharField(
        max_length=20,
        choices=Estado.choices,
        default=Estado.BOM,
        verbose_name=_('Estado de Conservação')
    )
    observacoes = models.TextField(blank=True, verbose_name=_('Observações'))
    ativo = models.BooleanField(default=True, verbose_name=_('Ativo'))
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Equipamento')
        verbose_name_plural = _('Equipamentos')
        ordering = ['sala', 'nome']

    def __str__(self):
        return f"{self.patrimonio} - {self.nome} ({self.sala.codigo})"

    @property
    def garantia_vigente(self):
        if not self.data_garantia:
            return False
        from django.utils import timezone
        return self.data_garantia >= timezone.now().date()
