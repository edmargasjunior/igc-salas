"""API views para stats do dashboard e notificações."""
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta, date
from django.db.models import Count, Q


class ReservasStatsOcupacaoAPIView(APIView):
    """Dados para gráfico de ocupação por sala."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.reservas.models import Reserva
        from apps.estrutura.models import Sala

        inicio = date.today() - timedelta(days=30)
        salas = Sala.objects.filter(ativo=True).annotate(
            total=Count('reservas', filter=Q(
                reservas__status=Reserva.Status.APROVADA,
                reservas__data_inicio__gte=inicio
            ))
        ).order_by('-total')[:12]

        return Response({
            'labels': [s.nome[:20] for s in salas],
            'valores': [s.total for s in salas],
        })


class ReservasStatsStatusAPIView(APIView):
    """Dados para gráfico de reservas por status."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.reservas.models import Reserva
        inicio = date.today() - timedelta(days=30)
        stats = Reserva.objects.filter(
            criado_em__date__gte=inicio
        ).values('status').annotate(total=Count('id')).order_by()

        labels_map = {
            'aprovada': 'Aprovadas', 'pendente': 'Pendentes',
            'rejeitada': 'Rejeitadas', 'cancelada': 'Canceladas',
            'substituida': 'Substituídas', 'expirada': 'Expiradas',
        }
        labels = [labels_map.get(s['status'], s['status']) for s in stats]
        valores = [s['total'] for s in stats]
        return Response({'labels': labels, 'valores': valores})


class ReservasStatsTendenciaAPIView(APIView):
    """Dados para gráfico de tendência dos últimos 14 dias."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.reservas.models import Reserva
        hoje = date.today()
        labels, valores = [], []
        for i in range(13, -1, -1):
            dia = hoje - timedelta(days=i)
            total = Reserva.objects.filter(
                data_inicio=dia,
                status=Reserva.Status.APROVADA
            ).count()
            labels.append(dia.strftime('%d/%m'))
            valores.append(total)
        return Response({'labels': labels, 'valores': valores})


class NotificacoesRecentesAPIView(APIView):
    """API para carregar notificações recentes no dropdown."""
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from apps.notificacoes.models import Notificacao
        notifs = Notificacao.objects.filter(
            destinatario=request.user, lida=False
        ).order_by('-criado_em')[:5]

        iconemap = {
            'reserva_aprovada': '✅',
            'reserva_rejeitada': '❌',
            'reserva_override': '⚠️',
            'reserva_cancelada': '🚫',
            'sistema': '📢',
        }

        resultado = [{
            'id': n.pk,
            'titulo': n.titulo,
            'mensagem': n.mensagem[:80],
            'tempo': n.criado_em.strftime('%d/%m %H:%M'),
            'icone': iconemap.get(n.tipo, '🔔'),
            'lida': n.lida,
        } for n in notifs]

        return Response({'resultados': resultado, 'total': len(resultado)})

    def post(self, request):
        """Marcar notificação como lida."""
        from apps.notificacoes.models import Notificacao
        notif_id = request.data.get('id')
        if notif_id:
            Notificacao.objects.filter(pk=notif_id, destinatario=request.user).update(
                lida=True, lida_em=timezone.now()
            )
        return Response({'ok': True})
