"""API de Notificações."""
from django.urls import path
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from .models import Notificacao

class NotificacaoListView(APIView):
    permission_classes = [IsAuthenticated]
    def get(self, request):
        notifs = Notificacao.objects.filter(
            destinatario=request.user
        ).order_by('-criado_em')[:20]
        data = [{'id': n.pk, 'titulo': n.titulo, 'mensagem': n.mensagem,
                 'lida': n.lida, 'tipo': n.tipo, 'criado_em': str(n.criado_em)} for n in notifs]
        return Response({'results': data, 'count': len(data)})

urlpatterns = [
    path('', NotificacaoListView.as_view(), name='api_notificacoes'),
]
