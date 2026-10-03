from django.db.models import Count, Q
from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.adherence.models import AdherenceLog
from apps.common.permissions import is_admin
from apps.profiles.models import PatientProfile

from .models import AdherenceAnalyticsReport
from .serializers import AdherenceAnalyticsReportSerializer
from .services.aggregations import (
    get_active_medicines,
    get_consistency_summary,
    get_dashboard_summary,
    get_medicine_history,
    get_refill_predictions,
)


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

    def _get_profile(self, request):
        profile_id = request.query_params.get("profile_id")

        if is_admin(request.user) and profile_id:
            return get_object_or_404(PatientProfile, id=profile_id)

        return get_object_or_404(
            PatientProfile,
            user=request.user,
            is_primary=True,
        )

    @action(detail=False, methods=["get"])
    def dashboard(self, request):
        profile = self._get_profile(request)

        return Response({
            "profile_id": profile.id,
            "profile_name": profile.name,
            **get_dashboard_summary(profile),
        })
    @action(detail=False, methods=["get"])
    def active_medicines(self, request):
        profile = self._get_profile(request)

        return Response({
            "profile_id": profile.id,
            "profile_name": profile.name,
            "medicines": get_active_medicines(profile),
        })

    @action(detail=False, methods=["get"])
    def medicine_history(self, request):
        profile = self._get_profile(request)

        return Response({
            "profile_id": profile.id,
            "profile_name": profile.name,
            "history": get_medicine_history(profile),
        })
    @action(detail=False, methods=["get"])
    def trends(self, request):
        logs = AdherenceLog.objects.all()

        if not is_admin(request.user):
            logs = logs.filter(patient_profile__user=request.user)

        profile_id = request.query_params.get("profile_id")

        if profile_id:
            logs = logs.filter(patient_profile_id=profile_id)

        summary = logs.aggregate(
            total=Count("id"),
            taken=Count(
                "id",
                filter=Q(status=AdherenceLog.Status.TAKEN),
            ),
            missed=Count(
                "id",
                filter=Q(status=AdherenceLog.Status.MISSED),
            ),
            snoozed=Count(
                "id",
                filter=Q(status=AdherenceLog.Status.SNOOZED),
            ),
        )

        today = timezone.localdate()
        start_date = today - timezone.timedelta(days=6)

        daily_data = logs.filter(
            action_date__range=(start_date, today)
        ).values("action_date").annotate(
            total=Count("id"),
            taken=Count(
                "id",
                filter=Q(status=AdherenceLog.Status.TAKEN),
            ),
            missed=Count(
                "id",
                filter=Q(status=AdherenceLog.Status.MISSED),
            ),
        )

        daily_lookup = {
            item["action_date"]: item
            for item in daily_data
        }

        days_data = []

        for i in range(6, -1, -1):
            day_date = today - timezone.timedelta(days=i)
            day_data = daily_lookup.get(day_date)

            if day_data:
                day_taken = day_data["taken"]
                day_missed = day_data["missed"]
                day_total = day_data["total"]

                percentage = (
                    round(day_taken / day_total * 100, 1)
                    if day_total
                    else 0
                )
            else:
                day_taken = 0
                day_missed = 0
                percentage = 0

            days_data.append({
                "date": day_date.strftime("%b %d"),
                "taken": day_taken,
                "missed": day_missed,
                "percentage": percentage,
            })

        total = summary["total"] or 0
        taken = summary["taken"] or 0

        return Response({
            "overall_adherence_pct": (
                round(taken / total * 100, 1)
                if total
                else 0
            ),
            "total_recorded": total,
            "taken_count": taken,
            "missed_count": summary["missed"] or 0,
            "snoozed_count": summary["snoozed"] or 0,
            "weekly_trends": days_data,
        })
    @action(detail=False, methods=["get"])
    def consistency(self, request):
        profile = self._get_profile(request)

        return Response({
            "profile_id": profile.id,
            "profile_name": profile.name,
            **get_consistency_summary(profile),
        })
    @action(detail=False, methods=["get"])
    def refill_predictions(self, request):
        profile = self._get_profile(request)

        return Response({
            "profile_id": profile.id,
            "profile_name": profile.name,
            "predictions": get_refill_predictions(profile),
        })
