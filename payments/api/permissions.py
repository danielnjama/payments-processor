from rest_framework.permissions import BasePermission

class IsAPIKeyAuthenticated(BasePermission):
    """
    Allows access only if request.user is an authenticated ExternalApp / AppClient.
    Works with APIKeyAuthentication.
    """
    def has_permission(self, request, view):
        return bool(request.user)  # True if ExternalApp/AppClient object exists
