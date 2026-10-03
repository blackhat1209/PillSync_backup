import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient

from apps.adherence.models import AdherenceLog
from apps.analytics.models import AdherenceAnalyticsReport
from apps.analytics.services.aggregations import (
    get_active_medicines,
    get_adherence_summary,
    get_dashboard_summary,
    get_medicine_history,
    get_medicine_summary,
    get_refill_summary,
)
from apps.medications.models import MedicationSchedule, Medicine
from apps.profiles.models import PatientProfile
from apps.refills.models import RefillPrediction, RefillRequest


@pytest.mark.django_db
def test_adherence_analytics_report():
    profile = PatientProfile.objects.create(
        name="Analytics User",
        relationship="Self",
    )

    report = AdherenceAnalyticsReport.objects.create(
        patient_profile=profile,
        period=AdherenceAnalyticsReport.Period.WEEKLY,
        taken_doses=14,
        missed_doses=1,
        adherence_percentage=93.3,
    )

    assert report.patient_profile == profile
    assert report.period == "Weekly"
    assert report.adherence_percentage == 93.3


@pytest.mark.django_db
def test_medicine_summary():
    profile = PatientProfile.objects.create(
        name="Medicine User",
        relationship="Self",
    )

    Medicine.objects.create(
        patient_profile=profile,
        name="Active Medicine",
        is_active=True,
    )

    Medicine.objects.create(
        patient_profile=profile,
        name="Inactive Medicine",
        is_active=False,
    )

    summary = get_medicine_summary(profile)

    assert summary == {
        "total": 2,
        "active": 1,
        "inactive": 1,
    }


@pytest.mark.django_db
def test_adherence_summary():
    profile = PatientProfile.objects.create(
        name="Adherence User",
        relationship="Self",
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="Test Medicine",
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="Test Medicine",
        action_date="2026-10-03",
        action_time="08:00 AM",
        status=AdherenceLog.Status.TAKEN,
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="Test Medicine",
        action_date="2026-10-03",
        action_time="12:00 PM",
        status=AdherenceLog.Status.MISSED,
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="Test Medicine",
        action_date="2026-10-03",
        action_time="06:00 PM",
        status=AdherenceLog.Status.SNOOZED,
    )

    summary = get_adherence_summary(profile)

    assert summary == {
        "percentage": 33.3,
        "total": 3,
        "taken": 1,
        "missed": 1,
        "snoozed": 1,
    }


@pytest.mark.django_db
def test_refill_summary():
    profile = PatientProfile.objects.create(
        name="Refill User",
        relationship="Self",
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="Refill Medicine",
    )

    RefillPrediction.objects.create(
        patient_profile=profile,
        medicine=medicine,
        is_low_stock=True,
        estimated_depletion_date="2026-10-10",
        recommended_refill_date="2026-10-07",
    )

    RefillRequest.objects.create(
        patient_profile=profile,
        medicine=medicine,
        status=RefillRequest.Status.PENDING,
    )

    RefillRequest.objects.create(
        patient_profile=profile,
        medicine=medicine,
        status=RefillRequest.Status.APPROVED,
    )

    RefillRequest.objects.create(
        patient_profile=profile,
        medicine=medicine,
        status=RefillRequest.Status.FULFILLED,
    )

    summary = get_refill_summary(profile)

    assert summary == {
        "low_stock": 1,
        "pending_requests": 1,
        "approved_requests": 1,
        "fulfilled_requests": 1,
    }


@pytest.mark.django_db
def test_active_medicines():
    profile = PatientProfile.objects.create(
        name="Active User",
        relationship="Self",
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="Test Vitamin",
        category=Medicine.Category.VITAMINS,
        dosage="1 Tablet",
        stock_quantity=30,
        unit="tablets",
        instructions="Take after breakfast",
        is_active=True,
    )

    MedicationSchedule.objects.create(
        medicine=medicine,
        patient_profile=profile,
        time_slot="Morning",
        scheduled_time="08:00",
        dosage_amount="1 Tablet",
        frequency="1 / day",
        is_active=True,
    )

    medicines = get_active_medicines(profile)

    assert len(medicines) == 1
    assert medicines[0]["name"] == "Test Vitamin"
    assert medicines[0]["stock_quantity"] == 30
    assert len(medicines[0]["schedules"]) == 1
    assert medicines[0]["schedules"][0]["time_slot"] == "Morning"


@pytest.mark.django_db
def test_medicine_history():
    profile = PatientProfile.objects.create(
        name="History User",
        relationship="Self",
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="History Medicine",
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="History Medicine",
        dosage="1 Tablet",
        action_date="2026-10-03",
        action_time="08:00 AM",
        status=AdherenceLog.Status.TAKEN,
        notes="Taken dose",
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="History Medicine",
        dosage="1 Tablet",
        action_date="2026-10-03",
        action_time="12:00 PM",
        status=AdherenceLog.Status.MISSED,
        notes="Missed dose",
    )

    history = get_medicine_history(profile)

    assert len(history) == 2
    assert history[0]["status"] == AdherenceLog.Status.MISSED
    assert history[1]["status"] == AdherenceLog.Status.TAKEN


@pytest.mark.django_db
def test_dashboard_summary():
    profile = PatientProfile.objects.create(
        name="Dashboard User",
        relationship="Self",
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="Dashboard Medicine",
        is_active=True,
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="Dashboard Medicine",
        action_date="2026-10-03",
        action_time="08:00 AM",
        status=AdherenceLog.Status.TAKEN,
    )

    summary = get_dashboard_summary(profile)

    assert summary["medicines"]["total"] == 1
    assert summary["medicines"]["active"] == 1
    assert summary["adherence"]["total"] == 1
    assert summary["adherence"]["taken"] == 1
    assert summary["adherence"]["percentage"] == 100.0
    assert summary["refills"]["low_stock"] == 0


@pytest.mark.django_db
def test_dashboard_api():
    user = get_user_model().objects.create_user(
        username="dashboarduser",
        password="TestPassword123!",
    )

    profile = PatientProfile.objects.create(
        user=user,
        name="Dashboard User",
        relationship="Self",
        is_primary=True,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/analytics/dashboard/")

    assert response.status_code == 200
    assert response.data["profile_id"] == profile.id
    assert response.data["profile_name"] == "Dashboard User"
    assert "medicines" in response.data
    assert "adherence" in response.data
    assert "refills" in response.data


@pytest.mark.django_db
def test_active_medicines_api():
    user = get_user_model().objects.create_user(
        username="medicineuser",
        password="TestPassword123!",
    )

    profile = PatientProfile.objects.create(
        user=user,
        name="Medicine User",
        relationship="Self",
        is_primary=True,
    )

    Medicine.objects.create(
        patient_profile=profile,
        name="API Vitamin",
        is_active=True,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/analytics/active_medicines/")

    assert response.status_code == 200
    assert response.data["profile_id"] == profile.id
    assert len(response.data["medicines"]) == 1
    assert response.data["medicines"][0]["name"] == "API Vitamin"


@pytest.mark.django_db
def test_medicine_history_api():
    user = get_user_model().objects.create_user(
        username="historyuser",
        password="TestPassword123!",
    )

    profile = PatientProfile.objects.create(
        user=user,
        name="History User",
        relationship="Self",
        is_primary=True,
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="API Medicine",
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="API Medicine",
        action_date="2026-10-03",
        action_time="08:00 AM",
        status=AdherenceLog.Status.TAKEN,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/analytics/medicine_history/")

    assert response.status_code == 200
    assert response.data["profile_id"] == profile.id
    assert len(response.data["history"]) == 1
    assert response.data["history"][0]["medicine_name"] == "API Medicine"
    assert response.data["history"][0]["status"] == "Taken"

@pytest.mark.django_db
def test_refill_predictions_api():
    user = get_user_model().objects.create_user(
        username="refill_api_user",
        password="password123",
    )

    profile = PatientProfile.objects.create(
        user=user,
        name="Refill API User",
        relationship="Self",
        is_primary=True,
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="Refill Test Medicine",
        category=Medicine.Category.VITAMINS,
        dosage="1 Tablet",
        stock_quantity=10,
        unit="tablets",
        instructions="Take after breakfast",
    )

    RefillPrediction.objects.create(
        patient_profile=profile,
        medicine=medicine,
        current_stock=10,
        daily_consumption=2,
        days_remaining=5,
        estimated_depletion_date="2026-10-08",
        recommended_refill_date="2026-10-05",
        is_low_stock=True,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(
        "/api/analytics/refill_predictions/"
    )

    assert response.status_code == 200

    data = response.json()

    assert data["profile_id"] == profile.id
    assert data["profile_name"] == "Refill API User"
    assert len(data["predictions"]) == 1

    prediction = data["predictions"][0]

    assert prediction["medicine_id"] == medicine.id
    assert prediction["medicine_name"] == "Refill Test Medicine"
    assert prediction["current_stock"] == 10
    assert prediction["daily_consumption"] == 2
    assert prediction["days_remaining"] == 5
    assert prediction["is_low_stock"] is True
@pytest.mark.django_db
def test_consistency_api():
    user = get_user_model().objects.create_user(
        username="consistencyuser",
        password="TestPassword123!",
    )

    profile = PatientProfile.objects.create(
        user=user,
        name="Consistency User",
        relationship="Self",
        is_primary=True,
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="Consistency Medicine",
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="Consistency Medicine",
        action_date="2026-10-03",
        action_time="08:00 AM",
        status=AdherenceLog.Status.TAKEN,
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="Consistency Medicine",
        action_date="2026-10-03",
        action_time="12:00 PM",
        status=AdherenceLog.Status.MISSED,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/analytics/consistency/")

    assert response.status_code == 200
    assert response.data["profile_id"] == profile.id
    assert response.data["profile_name"] == "Consistency User"
    assert response.data["total_recorded"] == 2
    assert response.data["taken_doses"] == 1
    assert response.data["missed_doses"] == 1
    assert response.data["snoozed_doses"] == 0
    assert response.data["consistency_score"] == 50.0
@pytest.mark.django_db
def test_consistency_api():
    user = get_user_model().objects.create_user(
        username="consistencyuser",
        password="TestPassword123!",
    )

    profile = PatientProfile.objects.create(
        user=user,
        name="Consistency User",
        relationship="Self",
        is_primary=True,
    )

    medicine = Medicine.objects.create(
        patient_profile=profile,
        name="Consistency Medicine",
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="Consistency Medicine",
        action_date="2026-10-03",
        action_time="08:00 AM",
        status=AdherenceLog.Status.TAKEN,
    )

    AdherenceLog.objects.create(
        patient_profile=profile,
        medicine=medicine,
        medicine_name="Consistency Medicine",
        action_date="2026-10-03",
        action_time="12:00 PM",
        status=AdherenceLog.Status.MISSED,
    )

    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get("/api/analytics/consistency/")

    assert response.status_code == 200
    assert response.data["profile_id"] == profile.id
    assert response.data["profile_name"] == "Consistency User"
    assert response.data["total_recorded"] == 2
    assert response.data["taken_doses"] == 1
    assert response.data["missed_doses"] == 1
    assert response.data["snoozed_doses"] == 0
    assert response.data["consistency_score"] == 50.0
