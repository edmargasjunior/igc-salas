"""URLs da API acadêmica."""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api import ProfessorViewSet, DisciplinaViewSet, TurmaViewSet

router = DefaultRouter()
router.register('professores', ProfessorViewSet, basename='api-professor')
router.register('disciplinas', DisciplinaViewSet, basename='api-disciplina')
router.register('turmas', TurmaViewSet, basename='api-turma')

urlpatterns = [
    path('', include(router.urls)),
]
