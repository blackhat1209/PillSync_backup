from django.db.models import Count, Q

from apps.adherence.models import AdherenceLog
from apps.medications.models import Medicine
from apps.refills.models import RefillPrediction, RefillRequest


def get_medicine_summary(profile):
    data = Medicine.objects.filter(
        patient_profile=profile
    ).aggregate(
        total=Count("id"),
        active=Count("id", filter=Q(is_active=True)),
        inactive=Count("id", filter=Q(is_active=False)),
    )

    return {
        "total": data["total"] or 0,
        "active": data["active"] or 0,
        "inactive": data["inactive"] or 0,
    }


def get_adherence_summary(profile):
    data = AdherenceLog.objects.filter(
        patient_profile=profile
    ).aggregate(
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

    total = data["total"] or 0
    taken = data["taken"] or 0

    return {
        "percentage": round(taken / total * 100, 1) if total else 0,
        "total": total,
        "taken": taken,
        "missed": data["missed"] or 0,
        "snoozed": data["snoozed"] or 0,
    }

	

def get_consistency_summary(profile):
    data = AdherenceLog.objects.filter(
        patient_profile=profile
    ).aggregate(
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

    total = data["total"] or 0
    taken = data["taken"] or 0

    return {
        "consistency_score": round(
            taken / total * 100, 1
        ) if total else 0,
        "total_recorded": total,
        "taken_doses": taken,
        "missed_doses": data["missed"] or 0,
        "snoozed_doses": data["snoozed"] or 0,
    }
def get_refill_summary(profile):
    predictions = RefillPrediction.objects.filter(
        patient_profile=profile
    )

    requests = RefillRequest.objects.filter(
        patient_profile=profile
    )

    prediction_data = predictions.aggregate(
        low_stock=Count(
            "id",
            filter=Q(is_low_stock=True),
        ),
    )

    request_data = requests.aggregate(
        pending=Count(
            "id",
            filter=Q(status=RefillRequest.Status.PENDING),
        ),
        approved=Count(
            "id",
            filter=Q(status=RefillRequest.Status.APPROVED),
        ),
        fulfilled=Count(
            "id",
            filter=Q(status=RefillRequest.Status.FULFILLED),
        ),
    )

    return {
        "low_stock": prediction_data["low_stock"] or 0,
        "pending_requests": request_data["pending"] or 0,
        "approved_requests": request_data["approved"] or 0,
        "fulfilled_requests": request_data["fulfilled"] or 0,
    }


def get_dashboard_summary(profile):
    return {
        "medicines": get_medicine_summary(profile),
        "adherence": get_adherence_summary(profile),
        "refills": get_refill_summary(profile),
    }


def get_active_medicines(profile):
    medicines = Medicine.objects.filter(
        patient_profile=profile,
        is_active=True,
    ).prefetch_related("schedules")

    return [
        {
            "id": medicine.id,
            "name": medicine.name,
            "category": medicine.category,
            "dosage": medicine.dosage,
            "stock_quantity": medicine.stock_quantity,
            "unit": medicine.unit,
            "instructions": medicine.instructions,
            "schedules": [
                {
                    "id": schedule.id,
                    "time_slot": schedule.time_slot,
                    "scheduled_time": schedule.scheduled_time.strftime("%H:%M:%S"),
                    "dosage_amount": schedule.dosage_amount,
                    "frequency": schedule.frequency,
                }
                for schedule in medicine.schedules.all()
                if schedule.is_active
            ],
        }
        for medicine in medicines
    ]


def get_medicine_history(profile):
    logs = (
        AdherenceLog.objects
        .filter(patient_profile=profile)
        .select_related("medicine", "schedule")
        .order_by("-action_date", "-logged_at")
    )

    return [
        {
            "id": log.id,
            "medicine_id": log.medicine_id,
            "medicine_name": log.medicine_name,
            "dosage": log.dosage,
            "action_date": log.action_date,
            "action_time": log.action_time,
            "status": log.status,
            "notes": log.notes,
        }
        for log in logs
    ]



def get_refill_predictions(profile):
    predictions = (
        RefillPrediction.objects
        .filter(patient_profile=profile)
        .select_related("medicine")
        .order_by("estimated_depletion_date")
    )

    return [
        {
            "id": prediction.id,
            "medicine_id": prediction.medicine_id,
            "medicine_name": prediction.medicine.name,
            "current_stock": prediction.current_stock,
            "daily_consumption": prediction.daily_consumption,
            "days_remaining": prediction.days_remaining,
            "estimated_depletion_date": prediction.estimated_depletion_date,
            "recommended_refill_date": prediction.recommended_refill_date,
            "is_low_stock": prediction.is_low_stock,
        }
        for prediction in predictions
    ]
