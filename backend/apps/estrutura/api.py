"""API serializers e viewsets para estrutura física."""
from rest_framework import serializers, viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Predio, Andar, Sala, Equipamento


class PredioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Predio
        fields = ['id', 'nome', 'codigo', 'descricao', 'endereco', 'slug']


class AndarSerializer(serializers.ModelSerializer):
    predio_nome = serializers.CharField(source='predio.nome', read_only=True)

    class Meta:
        model = Andar
        fields = ['id', 'predio', 'predio_nome', 'numero', 'nome']


class SalaSerializer(serializers.ModelSerializer):
    predio_nome = serializers.CharField(source='andar.predio.nome', read_only=True)
    predio_codigo = serializers.CharField(source='andar.predio.codigo', read_only=True)
    andar_display = serializers.CharField(source='andar.nome_display', read_only=True)
    tipo_display = serializers.CharField(source='get_tipo_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Sala
        fields = [
            'id', 'codigo', 'nome', 'slug', 'tipo', 'tipo_display',
            'capacidade', 'area_m2', 'status', 'status_display',
            'tem_projetor', 'tem_ar_condicionado', 'tem_lousa_digital',
            'tem_videoconferencia', 'tem_acessibilidade', 'tem_computadores',
            'qtd_computadores', 'predio_nome', 'predio_codigo', 'andar_display',
        ]


class EquipamentoSerializer(serializers.ModelSerializer):
    sala_nome = serializers.CharField(source='sala.nome', read_only=True)
    sala_codigo = serializers.CharField(source='sala.codigo', read_only=True)
    estado_display = serializers.CharField(source='get_estado_conservacao_display', read_only=True)
    garantia_vigente = serializers.BooleanField(read_only=True)

    class Meta:
        model = Equipamento
        fields = [
            'id', 'nome', 'patrimonio', 'modelo', 'fabricante', 'numero_serie',
            'quantidade', 'data_aquisicao', 'data_garantia', 'valor_aquisicao',
            'estado_conservacao', 'estado_display', 'garantia_vigente',
            'sala', 'sala_nome', 'sala_codigo', 'observacoes',
        ]


class PredioViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Predio.objects.filter(ativo=True)
    serializer_class = PredioSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter]
    search_fields = ['nome', 'codigo']
    lookup_field = 'slug'


class SalaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Sala.objects.filter(ativo=True).select_related('andar__predio')
    serializer_class = SalaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend, filters.OrderingFilter]
    search_fields = ['nome', 'codigo', 'andar__predio__nome']
    filterset_fields = ['tipo', 'status', 'andar__predio', 'tem_projetor', 'tem_ar_condicionado']
    ordering_fields = ['nome', 'capacidade']
    lookup_field = 'slug'


class EquipamentoViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Equipamento.objects.filter(ativo=True).select_related('sala__andar__predio')
    serializer_class = EquipamentoSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nome', 'patrimonio', 'modelo', 'fabricante']
    filterset_fields = ['sala', 'estado_conservacao']
