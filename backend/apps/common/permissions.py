from rest_framework.permissions import BasePermission


class IsAuthenticatedOrReadOnlyForDocs(BasePermission):
    """Authenticated users only; kept explicit for API readability."""

    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated)


def is_admin(user):
    return bool(user and user.is_authenticated and (user.is_staff or getattr(user, "role", None) == "ADMIN"))


def owned_profile_ids(user):
    if is_admin(user):
        return None
    return list(user.patient_profiles.values_list("id", flat=True))
