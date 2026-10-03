from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.adherence.models import AdherenceLog
from apps.common.permissions import is_admin

from .models import AdherenceAnalyticsReport
from .serializers import AdherenceAnalyticsReportSerializer


class AdherenceAnalyticsViewSet(viewsets.ModelViewSet):
    serializer_class = AdherenceAnalyticsReportSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = AdherenceAnalyticsReport.objects.all()
        if not is_admin(self.request.user):
            qs = qs.filter(patient_profile__user=self.request.user)
        profile_id = self.request.query_params.get("profile_id")
        if profile_id:
            qs = qs.filter(patient_profile_id=profile_id)
        return qs

    @action(detail=False, methods=["get"])
    def trends(self, request):
        logs = AdherenceLog.objects.all()
        if not is_admin(request.user):
            logs = logs.filter(patient_profile__user=request.user)
        profile_id = request.query_params.get("profile_id")
        if profile_id:
            logs = logs.filter(patient_profile_id=profile_id)
        total = logs.count()
        taken = logs.filter(status=AdherenceLog.Status.TAKEN).count()
        missed = logs.filter(status=AdherenceLog.Status.MISSED).count()
        snoozed = logs.filter(status=AdherenceLog.Status.SNOOZED).count()
        days_data = []
        today = timezone.localdate()
        for i in range(6, -1, -1):
            day_date = today - timezone.timedelta(days=i)
            day_logs = logs.filter(action_date=day_date)
            day_taken = day_logs.filter(status=AdherenceLog.Status.TAKEN).count()
            day_missed = day_logs.filter(status=AdherenceLog.Status.MISSED).count()
            day_total = day_logs.count()
            days_data.append({
                "date": day_date.strftime("%b %d"),
                "taken": day_taken,
                "missed": day_missed,
                "percentage": round(day_taken / day_total * 100, 1) if day_total else 0,
            })
        return Response({
            "overall_adherence_pct": round(taken / total * 100, 1) if total else 0,
            "total_recorded": total,
            "taken_count": taken,
            "missed_count": missed,
            "snoozed_count": snoozed,
            "weekly_trends": days_data,
        })
