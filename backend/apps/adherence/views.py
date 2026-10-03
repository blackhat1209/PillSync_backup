from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import is_admin

from .models import AdherenceLog
from .serializers import AdherenceLogSerializer


class AdherenceLogViewSet(viewsets.ModelViewSet):
    serializer_class = AdherenceLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = AdherenceLog.objects.select_related("patient_profile", "medicine", "schedule")
        if not is_admin(self.request.user):
            qs = qs.filter(patient_profile__user=self.request.user)
        profile_id = self.request.query_params.get("profile_id")
        status_param = self.request.query_params.get("status")
        if profile_id:
            qs = qs.filter(patient_profile_id=profile_id)
        if status_param:
            qs = qs.filter(status=status_param)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data.get("patient_profile")
        if not profile or (not is_admin(self.request.user) and profile.user_id != self.request.user.id):
            raise serializers.ValidationError({"patient_profile": "You do not have access to this profile."})
        serializer.save()

    @action(detail=False, methods=["get"])
    def summary(self, request):
        qs = self.get_queryset()
        total_logs = qs.count()
        taken_count = qs.filter(status=AdherenceLog.Status.TAKEN).count()
        missed_count = qs.filter(status=AdherenceLog.Status.MISSED).count()
        snoozed_count = qs.filter(status=AdherenceLog.Status.SNOOZED).count()
        adherence_percentage = round((taken_count / total_logs) * 100, 1) if total_logs else 0
        return Response({
            "total_logs": total_logs,
            "taken_count": taken_count,
            "missed_count": missed_count,
            "snoozed_count": snoozed_count,
            "adherence_percentage": adherence_percentage,
        })
