from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import is_admin

from .models import PatientProfile
from .serializers import PatientProfileSerializer


class PatientProfileViewSet(viewsets.ModelViewSet):
    serializer_class = PatientProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if is_admin(self.request.user):
            return PatientProfile.objects.all()
        return PatientProfile.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def perform_update(self, serializer):
        serializer.save(user=self.get_object().user)

    @action(detail=True, methods=["post"])
    def set_primary(self, request, pk=None):
        profile = self.get_object()
        PatientProfile.objects.filter(user=profile.user).update(is_primary=False)
        profile.is_primary = True
        profile.save(update_fields=["is_primary", "updated_at"])
        return Response(PatientProfileSerializer(profile).data)
