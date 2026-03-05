"""API Views das Reservas."""
from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Reserva
from .serializers import ReservaSerializer
from .services import ReservaService


class ReservaViewSet(viewsets.ModelViewSet):
    serializer_class = ReservaSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.is_responsavel:
            return Reserva.objects.all().select_related('sala', 'solicitante', 'turma')
        return Reserva.objects.filter(solicitante=user).select_related('sala', 'turma')

    def perform_create(self, serializer):
        service = ReservaService()
        reserva = service.criar_reserva(
            serializer.validated_data, self.request.user, self.request
        )
        return reserva

    @action(detail=True, methods=['post'])
    def aprovar(self, request, pk=None):
        reserva = self.get_object()
        service = ReservaService()
        try:
            service.aprovar_reserva(reserva, request.user, request)
            return Response({'status': 'aprovada'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)

    @action(detail=True, methods=['post'])
    def rejeitar(self, request, pk=None):
        reserva = self.get_object()
        motivo = request.data.get('motivo', '')
        service = ReservaService()
        try:
            service.rejeitar_reserva(reserva, request.user, motivo, request)
            return Response({'status': 'rejeitada'})
        except Exception as e:
            return Response({'error': str(e)}, status=400)
