from django.utils import timezone
from rest_framework import serializers, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import is_admin

from .models import Reminder
from .serializers import ReminderSerializer
from .tasks import generate_daily_reminders


class ReminderViewSet(viewsets.ModelViewSet):
    serializer_class = ReminderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        generate_daily_reminders()

        qs = Reminder.objects.select_related(
            "patient_profile",
            "schedule",
            "schedule__medicine",
        )

        if is_admin(self.request.user):
            return qs

        qs = qs.filter(patient_profile__user=self.request.user)

        profile_id = self.request.query_params.get("profile_id")
        if profile_id:
            qs = qs.filter(patient_profile_id=profile_id)

        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data.get("patient_profile")

        if not profile or (
            not is_admin(self.request.user)
            and profile.user_id != self.request.user.id
        ):
            raise serializers.ValidationError(
                {
                    "patient_profile": (
                        "You do not have access to this profile."
                    )
                }
            )

        serializer.save()

    @action(detail=True, methods=["post"])
    def take(self, request, pk=None):
        reminder = self.get_object()

        reminder.status = Reminder.Status.TAKEN
        reminder.save(update_fields=["status"])

        return Response(ReminderSerializer(reminder).data)

    @action(detail=True, methods=["post"])
    def miss(self, request, pk=None):
        reminder = self.get_object()

        reminder.status = Reminder.Status.MISSED
        reminder.save(update_fields=["status"])

        return Response(ReminderSerializer(reminder).data)

    @action(detail=True, methods=["post"])
    def snooze(self, request, pk=None):
        reminder = self.get_object()

        minutes = int(request.data.get("minutes", 30))

        reminder.status = Reminder.Status.SNOOZED
        reminder.snoozed_until = (
            timezone.now() + timezone.timedelta(minutes=minutes)
        )
        reminder.save(
            update_fields=["status", "snoozed_until"]
        )

        return Response(ReminderSerializer(reminder).data)
