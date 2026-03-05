"""Serializers das Reservas."""
from rest_framework import serializers
from .models import Reserva, LogReserva


class ReservaSerializer(serializers.ModelSerializer):
    sala_nome = serializers.CharField(source='sala.nome', read_only=True)
    solicitante_nome = serializers.CharField(source='solicitante.get_full_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)

    class Meta:
        model = Reserva
        fields = [
            'id', 'sala', 'sala_nome', 'solicitante', 'solicitante_nome',
            'turma', 'tipo', 'tipo_display', 'data_inicio', 'data_fim',
            'hora_inicio', 'hora_fim', 'status', 'status_display',
            'motivo', 'observacoes', 'criado_em'
        ]
        read_only_fields = ['solicitante', 'status', 'criado_em']


class LogReservaSerializer(serializers.ModelSerializer):
    class Meta:
        model = LogReserva
        fields = ['id', 'acao', 'descricao', 'usuario', 'criado_em']
