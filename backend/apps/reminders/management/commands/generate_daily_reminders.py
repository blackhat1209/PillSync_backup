from django.core.management.base import BaseCommand

from apps.reminders.tasks import generate_daily_reminders


class Command(BaseCommand):
    help = "Generate today's medication reminders"

    def handle(self, *args, **options):
        created = generate_daily_reminders()
        self.stdout.write(
            self.style.SUCCESS(
                f"Reminder generation completed. Created {created} reminder(s)."
            )
        )
