from django.db.models import Count, Avg
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.generics import get_object_or_404

from .models import Objective, KeyResult, GoalStatus
from .serializers import (
    ObjectiveSerializer,
    ObjectiveCreateSerializer,
    KeyResultSerializer,
    ObjectiveStatsSerializer,
)


class ObjectiveViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Objectives."""

    def get_serializer_class(self):
        if self.action in ['create', 'update', 'partial_update']:
            return ObjectiveCreateSerializer
        return ObjectiveSerializer

    def get_queryset(self):
        queryset = Objective.objects.filter(user=self.request.user).prefetch_related('key_results')

        # Filtros
        category = self.request.query_params.get('category')
        status_filter = self.request.query_params.get('status')

        if category:
            queryset = queryset.filter(category=category)
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        return queryset

    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Estadísticas generales de objetivos."""
        objectives = Objective.objects.filter(user=request.user)

        total = objectives.count()
        active = objectives.filter(status=GoalStatus.IN_PROGRESS).count()
        completed = objectives.filter(status=GoalStatus.COMPLETED).count()
        paused = objectives.filter(status=GoalStatus.PAUSED).count()

        # Calcular progreso promedio
        progress_sum = sum(obj.progress for obj in objectives)
        average_progress = round(progress_sum / total) if total > 0 else 0

        # Contar por categoría
        by_category = {}
        category_counts = objectives.values('category').annotate(count=Count('id'))
        for item in category_counts:
            by_category[item['category']] = item['count']

        data = {
            'total': total,
            'active': active,
            'completed': completed,
            'paused': paused,
            'average_progress': average_progress,
            'by_category': by_category,
        }

        serializer = ObjectiveStatsSerializer(data)
        return Response(serializer.data)

    @action(detail=True, methods=['get', 'post'], url_path='key-results')
    def key_results(self, request, pk=None):
        """Listar o crear key results de un objetivo."""
        objective = self.get_object()

        if request.method == 'GET':
            key_results = objective.key_results.all()
            serializer = KeyResultSerializer(key_results, many=True)
            return Response(serializer.data)

        elif request.method == 'POST':
            serializer = KeyResultSerializer(data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save(objective=objective)
            return Response(serializer.data, status=status.HTTP_201_CREATED)


class KeyResultViewSet(viewsets.ModelViewSet):
    """ViewSet para gestionar Key Results individuales."""

    serializer_class = KeyResultSerializer

    def get_queryset(self):
        return KeyResult.objects.filter(objective__user=self.request.user)
