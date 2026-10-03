from datetime import datetime, timedelta

from celery import shared_task
from django.utils import timezone

from .models import Reminder
from apps.medications.models import MedicationSchedule


@shared_task
def generate_daily_reminders():
    """Create today's pending reminders for active medication schedules.

    The task is idempotent: the same schedule/date/time gets one reminder.
    """
    now = timezone.localtime()
    today = now.date()
    created = 0
    for schedule in MedicationSchedule.objects.select_related("medicine", "patient_profile").filter(is_active=True):
        scheduled_dt = timezone.make_aware(datetime.combine(today, schedule.scheduled_time))
        _, was_created = Reminder.objects.get_or_create(
            schedule=schedule,
            patient_profile=schedule.patient_profile,
            scheduled_time=scheduled_dt,
            defaults={"title": f"Take {schedule.medicine.name}"},
        )
        created += int(was_created)
    return created
