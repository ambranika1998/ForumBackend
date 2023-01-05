from django.utils.translation import gettext_lazy as _
from rest_framework import status
from rest_framework.exceptions import ValidationError, _get_error_details


class ForumValidationError(ValidationError):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = _('Invalid input.')
    default_code = 'invalid'

    def __init__(self, detail=None, code=None):
        if detail is None:
            detail = self.default_detail
        else:
            self.status_code = status.HTTP_500_INTERNAL_SERVER_ERROR
        if code is None:
            code = self.default_code

        # For validation failures, we may collect many errors together,
        # so the details should always be coerced to a list if not already.
        if not isinstance(detail, dict) and not isinstance(detail, list):
            detail = detail

        self.detail = _get_error_details(detail, code)


class ForumCustomException(BaseException):
    message = None

    def __init__(self, message):
        super()
        self.message = message
