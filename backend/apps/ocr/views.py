from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from rest_framework import serializers, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from apps.common.permissions import is_admin
from ml.src.ocr.recognizer import OCRRecognizer

from .models import OCRExtractionLog
from .serializers import OCRExtractionLogSerializer


class OCRExtractionViewSet(viewsets.ModelViewSet):
    serializer_class = OCRExtractionLogSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = OCRExtractionLog.objects.select_related("patient_profile")
        if not is_admin(self.request.user):
            qs = qs.filter(patient_profile__user=self.request.user)
        profile_id = self.request.query_params.get("profile_id")
        if profile_id:
            qs = qs.filter(patient_profile_id=profile_id)
        return qs

    @action(detail=False, methods=["post"])
    def extract(self, request):
        """Accept either raw_text JSON or an uploaded prescription image."""
        raw_text = request.data.get("raw_text")
        if raw_text:
            result = OCRRecognizer.extract_prescription_text(raw_text)
            return Response(result)

        uploaded = request.FILES.get("image")
        if not uploaded:
            return Response({"detail": "Provide raw_text or an image file."}, status=400)

        path = default_storage.save(f"ocr/{uploaded.name}", ContentFile(uploaded.read()))
        try:
            result = OCRRecognizer.extract_image(default_storage.path(path))
        except Exception as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_422_UNPROCESSABLE_ENTITY)
        result["image_url"] = default_storage.url(path)
        return Response(result)

    def perform_create(self, serializer):
        profile = serializer.validated_data.get("patient_profile")
        if not profile or (not is_admin(self.request.user) and profile.user_id != self.request.user.id):
            raise serializers.ValidationError({"patient_profile": "You do not have access to this profile."})
        serializer.save()
