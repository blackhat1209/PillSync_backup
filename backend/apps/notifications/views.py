from rest_framework import serializers, viewsets
from rest_framework.permissions import IsAuthenticated

from apps.common.permissions import is_admin

from .models import Notification
from .serializers import NotificationSerializer


class NotificationViewSet(viewsets.ModelViewSet):
    serializer_class = NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Notification.objects.select_related("patient_profile")
        if not is_admin(self.request.user):
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
