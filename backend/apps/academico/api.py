"""API serializers e views para módulo acadêmico."""
from rest_framework import serializers, viewsets, filters
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from .models import Professor, Disciplina, Turma


class ProfessorSerializer(serializers.ModelSerializer):
    nome = serializers.CharField(source='usuario.nome_completo', read_only=True)
    email = serializers.CharField(source='usuario.email', read_only=True)
    titulacao_display = serializers.CharField(source='get_titulacao_display', read_only=True)

    class Meta:
        model = Professor
        fields = ['id', 'nome', 'email', 'siape', 'titulacao', 'titulacao_display',
                  'area_atuacao', 'lattes', 'slug']


class DisciplinaSerializer(serializers.ModelSerializer):
    class Meta:
        model = Disciplina
        fields = ['id', 'codigo', 'nome', 'carga_horaria', 'creditos',
                  'modalidade', 'departamento', 'slug']


class TurmaSerializer(serializers.ModelSerializer):
    disciplina_nome = serializers.CharField(source='disciplina.nome', read_only=True)
    disciplina_codigo = serializers.CharField(source='disciplina.codigo', read_only=True)
    professor_nome = serializers.SerializerMethodField()
    periodo = serializers.CharField(read_only=True)

    class Meta:
        model = Turma
        fields = ['id', 'codigo', 'disciplina', 'disciplina_nome', 'disciplina_codigo',
                  'professor', 'professor_nome', 'ano', 'semestre', 'periodo',
                  'vagas', 'matriculados', 'slug']

    def get_professor_nome(self, obj):
        if obj.professor:
            return obj.professor.usuario.nome_completo
        return None


class ProfessorViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Professor.objects.filter(ativo=True).select_related('usuario')
    serializer_class = ProfessorSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['usuario__first_name', 'usuario__last_name', 'siape', 'area_atuacao']
    ordering_fields = ['usuario__first_name']
    lookup_field = 'slug'


class DisciplinaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Disciplina.objects.filter(ativo=True)
    serializer_class = DisciplinaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['nome', 'codigo', 'departamento']
    filterset_fields = ['modalidade', 'departamento']
    lookup_field = 'slug'


class TurmaViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Turma.objects.filter(ativo=True).select_related('disciplina', 'professor__usuario')
    serializer_class = TurmaSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    filter_backends = [filters.SearchFilter, DjangoFilterBackend]
    search_fields = ['codigo', 'disciplina__nome', 'disciplina__codigo']
    filterset_fields = ['ano', 'semestre', 'professor']
    lookup_field = 'slug'
