from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.authentication import CSRFCheck
from rest_framework import exceptions
from django.utils.translation import gettext as _

def enforce_csrf(request):
    """
    Enforce CSRF validation.
    """
    def dummy_get_response(request):
        return None
    # populates request.META['CSRF_COOKIE'], which is used in process_view()
    check = CSRFCheck(dummy_get_response)
    check.process_request(request)
    reason = check.process_view(request, None, (), {})
    if reason:
        # CSRF failed, bail with explicit error message
        raise exceptions.PermissionDenied(_('CSRF Failed: %s') % reason)

class CustomJWTAuthentication(JWTAuthentication):
    
    def authenticate(self, request):
        header = self.get_header(request)
        if header is None:
            return None

        raw_token = self.get_raw_token(header)
        if raw_token is None:
            return None

        validated_token = self.get_validated_token(raw_token)
        enforce_csrf(request)
        return self.get_user(validated_token), validated_token
