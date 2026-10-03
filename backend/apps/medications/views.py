from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import is_admin
from apps.profiles.models import PatientProfile

from .models import MedicationSchedule, Medicine
from .serializers import MedicationScheduleSerializer, MedicineSerializer


class MedicineViewSet(viewsets.ModelViewSet):
    serializer_class = MedicineSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Medicine.objects.select_related("patient_profile")
        if is_admin(self.request.user):
            return qs
        qs = qs.filter(patient_profile__user=self.request.user)
        profile_id = self.request.query_params.get("profile_id")
        if profile_id:
            qs = qs.filter(patient_profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data.get("patient_profile")
        if not profile or (not is_admin(self.request.user) and profile.user_id != self.request.user.id):
            raise serializers.ValidationError({"patient_profile": "You do not have access to this profile."})
        serializer.save()


class MedicationScheduleViewSet(viewsets.ModelViewSet):
    serializer_class = MedicationScheduleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = MedicationSchedule.objects.select_related("medicine", "patient_profile")
        if is_admin(self.request.user):
            return qs
        qs = qs.filter(patient_profile__user=self.request.user)
        profile_id = self.request.query_params.get("profile_id")
        if profile_id:
            qs = qs.filter(patient_profile_id=profile_id)
        return qs

    def perform_create(self, serializer):
        profile = serializer.validated_data.get("patient_profile")
        medicine = serializer.validated_data.get("medicine")
        if not profile or not medicine or medicine.patient_profile_id != profile.id:
            raise serializers.ValidationError("Schedule, medicine and patient profile must belong together.")
        if not is_admin(self.request.user) and profile.user_id != self.request.user.id:
            raise serializers.ValidationError("You do not have access to this profile.")
        serializer.save()
