"""
Serviço de Reservas - Lógica de negócio central.
Controla conflitos, aprovações, overrides e recorrências.
"""
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
import logging

from .models import Reserva, LogReserva

logger = logging.getLogger('apps.reservas')


class ReservaService:
    """Serviço principal de gerenciamento de reservas."""

    def criar_reserva(self, dados, usuario, request=None):
        """
        Cria uma nova reserva com verificação de conflitos.
        Retorna a reserva criada ou lança ValidationError em caso de conflito.
        """
        with transaction.atomic():
            reserva = Reserva(
                sala=dados['sala'],
                solicitante=usuario,
                turma=dados.get('turma'),
                tipo=dados.get('tipo', Reserva.Tipo.PONTUAL),
                data_inicio=dados['data_inicio'],
                data_fim=dados.get('data_fim'),
                hora_inicio=dados['hora_inicio'],
                hora_fim=dados['hora_fim'],
                recorrencia=dados.get('recorrencia'),
                dia_semana=dados.get('dia_semana'),
                motivo=dados.get('motivo', ''),
                observacoes=dados.get('observacoes', ''),
            )
            reserva.clean()

            # Verificar conflitos
            conflitos = reserva.verificar_conflito()
            if conflitos.exists():
                conflito_info = []
                for c in conflitos:
                    conflito_info.append(
                        f"Reserva #{c.pk} de {c.solicitante} ({c.hora_inicio}-{c.hora_fim})"
                    )
                raise ValidationError({
                    'conflito': _('Conflito de horário detectado: ') + '; '.join(conflito_info)
                })

            reserva.save()

            # Auto-aprovar se o usuário for admin/responsável
            if usuario.pode_aprovar_reservas():
                reserva.aprovar(usuario)

            logger.info(f"Reserva #{reserva.pk} criada por {usuario}")
            return reserva

    def aprovar_reserva(self, reserva, aprovador, request=None):
        """Aprova uma reserva pendente."""
        if reserva.status != Reserva.Status.PENDENTE:
            raise ValidationError(_('Apenas reservas pendentes podem ser aprovadas.'))

        if not aprovador.pode_aprovar_reservas():
            raise ValidationError(_('Usuário sem permissão para aprovar reservas.'))

        # Verificar conflitos novamente antes de aprovar
        conflitos = reserva.verificar_conflito()
        conflitos_aprovados = conflitos.filter(status=Reserva.Status.APROVADA)
        if conflitos_aprovados.exists():
            raise ValidationError(_('Existem conflitos com reservas aprovadas para este horário.'))

        with transaction.atomic():
            reserva.aprovar(aprovador)
            LogReserva.objects.create(
                reserva=reserva,
                usuario=aprovador,
                acao=LogReserva.Acao.APROVADA,
                descricao=f"Reserva aprovada por {aprovador}",
                ip_address=self._get_ip(request)
            )

        return reserva

    def rejeitar_reserva(self, reserva, aprovador, motivo, request=None):
        """Rejeita uma reserva pendente com motivo."""
        if reserva.status != Reserva.Status.PENDENTE:
            raise ValidationError(_('Apenas reservas pendentes podem ser rejeitadas.'))

        if not aprovador.pode_aprovar_reservas():
            raise ValidationError(_('Usuário sem permissão para rejeitar reservas.'))

        with transaction.atomic():
            reserva.rejeitar(aprovador, motivo)
            LogReserva.objects.create(
                reserva=reserva,
                usuario=aprovador,
                acao=LogReserva.Acao.REJEITADA,
                descricao=f"Reserva rejeitada por {aprovador}. Motivo: {motivo}",
                ip_address=self._get_ip(request)
            )

        return reserva

    def override_reserva(self, reserva_existente, nova_reserva_dados, administrador, motivo, request=None):
        """
        Override administrativo: cancela reserva existente e cria nova.
        Apenas administradores podem executar esta operação.
        """
        if not administrador.pode_fazer_override():
            raise ValidationError(_('Apenas administradores podem realizar override de reservas.'))

        with transaction.atomic():
            # Registrar dados anteriores para audit log
            dados_anteriores = {
                'status': reserva_existente.status,
                'solicitante': str(reserva_existente.solicitante),
                'data': str(reserva_existente.data_inicio),
                'hora_inicio': str(reserva_existente.hora_inicio),
                'hora_fim': str(reserva_existente.hora_fim),
            }

            # Cancelar reserva existente
            reserva_existente.status = Reserva.Status.SUBSTITUIDA
            reserva_existente.motivo_override = motivo
            reserva_existente.save()

            # Log do override
            LogReserva.objects.create(
                reserva=reserva_existente,
                usuario=administrador,
                acao=LogReserva.Acao.OVERRIDE,
                descricao=f"Override realizado por {administrador}. Motivo: {motivo}",
                dados_anteriores=dados_anteriores,
                ip_address=self._get_ip(request)
            )

            # Criar nova reserva aprovada
            nova_reserva = Reserva(
                sala=nova_reserva_dados.get('sala', reserva_existente.sala),
                solicitante=administrador,
                turma=nova_reserva_dados.get('turma'),
                tipo=nova_reserva_dados.get('tipo', Reserva.Tipo.PONTUAL),
                data_inicio=nova_reserva_dados['data_inicio'],
                hora_inicio=nova_reserva_dados['hora_inicio'],
                hora_fim=nova_reserva_dados['hora_fim'],
                motivo=nova_reserva_dados.get('motivo', ''),
                status=Reserva.Status.APROVADA,
                aprovado_por=administrador,
                data_aprovacao=timezone.now(),
                motivo_override=f"Criada via override sobre reserva #{reserva_existente.pk}",
            )
            nova_reserva.save()
            reserva_existente.substituida_por = nova_reserva
            reserva_existente.save()

            logger.warning(
                f"OVERRIDE: Reserva #{reserva_existente.pk} substituída pela #{nova_reserva.pk} "
                f"por {administrador}. Motivo: {motivo}"
            )

        return nova_reserva

    def gerar_ocorrencias_recorrentes(self, reserva):
        """
        Gera lista de datas para uma reserva recorrente.
        Não salva no banco, apenas retorna as datas.
        """
        if reserva.tipo != Reserva.Tipo.RECORRENTE:
            return [reserva.data_inicio]

        datas = []
        data_atual = reserva.data_inicio
        delta = timedelta(weeks=1) if reserva.recorrencia == Reserva.Recorrencia.SEMANAL else timedelta(weeks=2)

        while data_atual <= reserva.data_fim:
            if reserva.dia_semana is not None:
                if data_atual.weekday() == reserva.dia_semana:
                    datas.append(data_atual)
            else:
                datas.append(data_atual)
            data_atual += delta

        return datas

    def _get_ip(self, request):
        if not request:
            return None
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR')
