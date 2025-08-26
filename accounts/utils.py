
from rest_framework.views import exception_handler
from rest_framework.response import Response
# from django.forms import ValidationError
from rest_framework.exceptions import ValidationError
from rest_framework import status
import requests
from django.urls import reverse
from django.db import IntegrityError
from .models import ErrorLog  # Adjust the import based on your app structure
from django.utils.timezone import now
from django.core.mail import EmailMessage

from django.contrib.auth.models import BaseUserManager

class CustomUserManager(BaseUserManager):

    def _create_user(self, email, password, **extra_fields):
        if not email:
            raise ValueError('Users must have an email address')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        if password:
            user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', False)
        extra_fields.setdefault('is_superuser', False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self._create_user(email, password, **extra_fields)
class Util:
    @staticmethod
    def send_email(data):
        try:
            email = EmailMessage(
                to=[data['to_email']], subject=data['email_subject'], body=data['email_body'])

            email.send()
        except Exception as err:
            print(f"raised error while sending email: {err}")


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    # Base structure of the custom response
    result = {
        "error": True,
        "errors": [],
        "status_code": status.HTTP_500_INTERNAL_SERVER_ERROR,  # Default status code
    }

    # Details to log in the ErrorLog model
    error_level = "ERROR"  # Default log level
    error_message = str(exc)
    error_details = ""

    if response is not None:
        # Use the status code from the default response
        result['status_code'] = response.status_code

        # Extract errors from response data
        if isinstance(response.data, dict):
            for key, value in response.data.items():
                if isinstance(value, list):
                    for msg in value:
                        result['errors'].append(f"The {key} is {msg.lower()}.")
                else:
                    result['errors'].append(value)
            error_details = response.data
        else:
            result['errors'].append(response.data)
            error_details = response.data

    else:
        # Handle exceptions not processed by DRF's default exception handler
        if isinstance(exc, ValidationError):
            for field, errors in exc.detail.items():
                for msg in errors:
                    result['errors'].append(f"The {field} is {msg.lower()}.")
            error_details = exc.detail
        elif isinstance(exc, IntegrityError):
            error_message = "Email/Phone number already exists. Please check and try again."
            result['errors'].append(error_message)
        elif isinstance(exc, dict):
            for key, value in exc.items():
                result['errors'].append(f"The {key} is {value.lower()}.")
            error_details = exc
        else:
            result['errors'].append(str(exc))

    # Log the error in the ErrorLog model
    try:
        ErrorLog.objects.create(
            level=error_level,
            message=error_message,
            details=str(error_details) if error_details else None,
            timestamp=now()
        )
    except Exception as log_exc:
        # Avoid disrupting the exception handler due to logging errors
        print(f"Error logging failed: {log_exc}")

    # Return a DRF Response with the structured error data
    return Response(result, status=result["status_code"])
