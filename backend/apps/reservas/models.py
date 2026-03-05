"""
App: reservas
Sistema de reservas de salas com controle de conflitos, aprovações e overrides.
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.db import transaction
import logging

logger = logging.getLogger('apps.reservas')


class Reserva(models.Model):
    """
    Reserva de sala/laboratório.
    Suporta reservas pontuais e recorrentes.
    Controle completo de status e histórico de aprovações.
    """

    class Status(models.TextChoices):
        PENDENTE = 'pendente', _('Pendente')
        APROVADA = 'aprovada', _('Aprovada')
        REJEITADA = 'rejeitada', _('Rejeitada')
        CANCELADA = 'cancelada', _('Cancelada')
        SUBSTITUIDA = 'substituida', _('Substituída')
        EXPIRADA = 'expirada', _('Expirada')

    class Tipo(models.TextChoices):
        PONTUAL = 'pontual', _('Reserva Pontual')
        RECORRENTE = 'recorrente', _('Reserva Recorrente (Semestral)')

    class Recorrencia(models.TextChoices):
        SEMANAL = 'semanal', _('Semanal')
        QUINZENAL = 'quinzenal', _('Quinzenal')

    # Relacionamentos principais
    sala = models.ForeignKey(
        'estrutura.Sala',
        on_delete=models.CASCADE,
        related_name='reservas',
        verbose_name=_('Sala')
    )
    solicitante = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.CASCADE,
        related_name='reservas_solicitadas',
        verbose_name=_('Solicitante')
    )
    turma = models.ForeignKey(
        'academico.Turma',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reservas',
        verbose_name=_('Turma')
    )

    # Temporalidade
    tipo = models.CharField(
        max_length=15,
        choices=Tipo.choices,
        default=Tipo.PONTUAL,
        verbose_name=_('Tipo de Reserva')
    )
    data_inicio = models.DateField(verbose_name=_('Data de Início'))
    data_fim = models.DateField(
        null=True, blank=True,
        verbose_name=_('Data de Fim (recorrência)')
    )
    hora_inicio = models.TimeField(verbose_name=_('Hora de Início'))
    hora_fim = models.TimeField(verbose_name=_('Hora de Fim'))

    # Recorrência
    recorrencia = models.CharField(
        max_length=15,
        choices=Recorrencia.choices,
        null=True, blank=True,
        verbose_name=_('Tipo de Recorrência')
    )
    dia_semana = models.IntegerField(
        null=True, blank=True,
        choices=[(0, 'Segunda'), (1, 'Terça'), (2, 'Quarta'),
                 (3, 'Quinta'), (4, 'Sexta'), (5, 'Sábado')],
        verbose_name=_('Dia da Semana')
    )

    # Status e fluxo
    status = models.CharField(
        max_length=15,
        choices=Status.choices,
        default=Status.PENDENTE,
        verbose_name=_('Status')
    )
    motivo = models.TextField(blank=True, verbose_name=_('Motivo / Descrição'))
    observacoes = models.TextField(blank=True, verbose_name=_('Observações'))

    # Aprovação/Rejeição
    aprovado_por = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='reservas_aprovadas',
        verbose_name=_('Aprovado/Rejeitado por')
    )
    data_aprovacao = models.DateTimeField(null=True, blank=True, verbose_name=_('Data de Aprovação'))
    motivo_rejeicao = models.TextField(blank=True, verbose_name=_('Motivo de Rejeição'))

    # Override (substituição)
    substituida_por = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True, blank=True,
        related_name='substituiu',
        verbose_name=_('Substituída pela Reserva')
    )
    motivo_override = models.TextField(blank=True, verbose_name=_('Motivo do Override'))

    # Controle
    criado_em = models.DateTimeField(auto_now_add=True)
    atualizado_em = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Reserva')
        verbose_name_plural = _('Reservas')
        ordering = ['data_inicio', 'hora_inicio']
        indexes = [
            models.Index(fields=['sala', 'data_inicio', 'status']),
            models.Index(fields=['solicitante', 'status']),
            models.Index(fields=['data_inicio', 'hora_inicio']),
        ]

    def __str__(self):
        return f"Reserva #{self.pk} - {self.sala} em {self.data_inicio} {self.hora_inicio}"

    def clean(self):
        """Validação de negócio no modelo."""
        super().clean()

        if self.hora_inicio and self.hora_fim:
            if self.hora_fim <= self.hora_inicio:
                raise ValidationError({
                    'hora_fim': _('O horário de fim deve ser posterior ao horário de início.')
                })

        if self.tipo == self.Tipo.RECORRENTE:
            if not self.data_fim:
                raise ValidationError({
                    'data_fim': _('Para reservas recorrentes, informe a data de fim.')
                })
            if self.data_fim and self.data_inicio and self.data_fim < self.data_inicio:
                raise ValidationError({
                    'data_fim': _('A data de fim deve ser posterior à data de início.')
                })

    def verificar_conflito(self, excluir_id=None):
        """
        Verifica conflitos de horário com outras reservas aprovadas.
        Retorna queryset de conflitos ou None.
        """
        from django.db.models import Q

        qs = Reserva.objects.filter(
            sala=self.sala,
            status__in=[self.Status.APROVADA, self.Status.PENDENTE],
            data_inicio=self.data_inicio,
        ).filter(
            # Sobreposição de horários
            Q(hora_inicio__lt=self.hora_fim) & Q(hora_fim__gt=self.hora_inicio)
        )

        if excluir_id:
            qs = qs.exclude(pk=excluir_id)

        if self.pk:
            qs = qs.exclude(pk=self.pk)

        return qs

    def aprovar(self, usuario):
        """Aprova a reserva."""
        self.status = self.Status.APROVADA
        self.aprovado_por = usuario
        self.data_aprovacao = timezone.now()
        self.save()
        logger.info(f"Reserva #{self.pk} aprovada por {usuario}")
        return self

    def rejeitar(self, usuario, motivo=''):
        """Rejeita a reserva."""
        self.status = self.Status.REJEITADA
        self.aprovado_por = usuario
        self.data_aprovacao = timezone.now()
        self.motivo_rejeicao = motivo
        self.save()
        logger.info(f"Reserva #{self.pk} rejeitada por {usuario}: {motivo}")
        return self

    def cancelar(self, motivo=''):
        """Cancela a reserva."""
        self.status = self.Status.CANCELADA
        if motivo:
            self.observacoes = motivo
        self.save()
        logger.info(f"Reserva #{self.pk} cancelada: {motivo}")
        return self

    @property
    def esta_ativa(self):
        return self.status in [self.Status.APROVADA, self.Status.PENDENTE]

    @property
    def duracao_minutos(self):
        if self.hora_inicio and self.hora_fim:
            from datetime import datetime, date
            inicio = datetime.combine(date.today(), self.hora_inicio)
            fim = datetime.combine(date.today(), self.hora_fim)
            return int((fim - inicio).total_seconds() / 60)
        return 0

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('reserva_detalhe', kwargs={'pk': self.pk})


class LogReserva(models.Model):
    """
    Audit log de todas as ações realizadas em reservas.
    Imutável após criação.
    """

    class Acao(models.TextChoices):
        CRIADA = 'criada', _('Reserva Criada')
        APROVADA = 'aprovada', _('Reserva Aprovada')
        REJEITADA = 'rejeitada', _('Reserva Rejeitada')
        CANCELADA = 'cancelada', _('Reserva Cancelada')
        OVERRIDE = 'override', _('Override Administrativo')
        SUBSTITUIDA = 'substituida', _('Reserva Substituída')
        EDITADA = 'editada', _('Reserva Editada')

    reserva = models.ForeignKey(
        Reserva,
        on_delete=models.CASCADE,
        related_name='logs',
        verbose_name=_('Reserva')
    )
    usuario = models.ForeignKey(
        'accounts.Usuario',
        on_delete=models.SET_NULL,
        null=True,
        verbose_name=_('Usuário')
    )
    acao = models.CharField(
        max_length=15,
        choices=Acao.choices,
        verbose_name=_('Ação')
    )
    descricao = models.TextField(verbose_name=_('Descrição'))
    dados_anteriores = models.JSONField(
        null=True, blank=True,
        verbose_name=_('Dados Anteriores')
    )
    ip_address = models.GenericIPAddressField(
        null=True, blank=True,
        verbose_name=_('IP do Usuário')
    )
    criado_em = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _('Log de Reserva')
        verbose_name_plural = _('Logs de Reservas')
        ordering = ['-criado_em']

    def __str__(self):
        return f"[{self.criado_em.strftime('%d/%m/%Y %H:%M')}] {self.acao} - Reserva #{self.reserva_id}"
