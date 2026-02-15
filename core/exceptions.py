from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework.response import Response
from rest_framework import status


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Make sure we never leak sensitive info
    if response is not None:
        if 'detail' not in response.data:
            response.data = {"detail": "An error occurred."}

        # Hide 500 errors in production
        if response.status_code == 500 and not settings.DEBUG:
            response.data = {"detail": "Internal server error."}
            response.status_code = 500

    return response
