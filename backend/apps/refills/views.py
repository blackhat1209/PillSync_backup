from django.utils import timezone
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import is_admin
from apps.medications.models import Medicine
from ml.src.refill_prediction.engine import RefillPredictionEngine

from .models import RefillPrediction, RefillRequest
from .serializers import RefillPredictionSerializer, RefillRequestSerializer


class RefillPredictionViewSet(viewsets.ModelViewSet):
    serializer_class = RefillPredictionSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = RefillPrediction.objects.select_related("medicine", "patient_profile")
        if not is_admin(self.request.user):
            qs = qs.filter(patient_profile__user=self.request.user)
        profile_id = self.request.query_params.get("profile_id")
        if profile_id:
            qs = qs.filter(patient_profile_id=profile_id)
        return qs

    @action(detail=False, methods=["post"])
    def calculate(self, request):
        medicine = None
        medicine_id = request.data.get("medicine_id")
        if medicine_id:
            try:
                medicine = Medicine.objects.get(pk=medicine_id)
            except Medicine.DoesNotExist:
                return Response({"detail": "Medicine not found."}, status=404)
            if not is_admin(request.user) and medicine.patient_profile.user_id != request.user.id:
                return Response({"detail": "You do not have access to this medicine."}, status=403)
        stock = int(request.data.get("stock", medicine.stock_quantity if medicine else 60))
        daily_freq = float(request.data.get("daily_frequency", 2.0))
        qty_per_dose = float(request.data.get("qty_per_dose", 1.0))
        missed = int(request.data.get("missed_doses", 0))
        med_name = request.data.get("medicine_name", medicine.name if medicine else "Medication")
        res = RefillPredictionEngine.predict_depletion(
            initial_stock=stock,
            daily_dosage_frequency=daily_freq,
            quantity_per_dose=qty_per_dose,
            missed_doses=missed,
            medicine_name=med_name,
        )
        if medicine:
            profile = medicine.patient_profile
            RefillPrediction.objects.update_or_create(
                medicine=medicine,
                patient_profile=profile,
                defaults={
                    "current_stock": stock,
                    "daily_consumption": res["daily_consumption"],
                    "days_remaining": res["days_remaining"],
                    "estimated_depletion_date": res["depletion_date"],
                    "recommended_refill_date": res["recommended_refill_date"],
                    "is_low_stock": res["is_low_stock"],
                },
            )
        return Response(res, status=status.HTTP_200_OK)


class RefillRequestViewSet(viewsets.ModelViewSet):
    serializer_class = RefillRequestSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = RefillRequest.objects.select_related("medicine", "patient_profile")
        if not is_admin(self.request.user):
            qs = qs.filter(patient_profile__user=self.request.user)
        profile_id = self.request.query_params.get("profile_id")
        if profile_id:
            qs = qs.filter(patient_profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data.get("patient_profile")
        medicine = serializer.validated_data.get("medicine")
        if not profile or not medicine or medicine.patient_profile_id != profile.id:
            raise serializers.ValidationError("Medicine and patient profile must belong together.")
        if not is_admin(self.request.user) and profile.user_id != self.request.user.id:
            raise serializers.ValidationError("You do not have access to this profile.")
        serializer.save()
