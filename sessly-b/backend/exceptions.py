"""
Custom exception handler and error codes for standardized API responses.
"""

from rest_framework import status
from rest_framework.exceptions import APIException
from rest_framework.views import exception_handler


class ErrorCode:
    """Standard error codes for client-side handling."""
    
    # Authentication & Authorization
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    WRONG_PASSWORD = "WRONG_PASSWORD"
    EMAIL_ALREADY_EXISTS = "EMAIL_ALREADY_EXISTS"
    USERNAME_ALREADY_EXISTS = "USERNAME_ALREADY_EXISTS"
    EMAIL_NOT_VERIFIED = "EMAIL_NOT_VERIFIED"
    INVALID_TOKEN = "INVALID_TOKEN"
    TOKEN_EXPIRED = "TOKEN_EXPIRED"
    UNAUTHORIZED = "UNAUTHORIZED"
    PERMISSION_DENIED = "PERMISSION_DENIED"
    
    # Validation
    VALIDATION_ERROR = "VALIDATION_ERROR"
    INVALID_INPUT = "INVALID_INPUT"
    REQUIRED_FIELD = "REQUIRED_FIELD"
    
    # Business Logic
    SLOT_UNAVAILABLE = "SLOT_UNAVAILABLE"
    PAST_BOOKING = "PAST_BOOKING"
    SERVICE_NOT_FOUND = "SERVICE_NOT_FOUND"
    BUSINESS_NOT_FOUND = "BUSINESS_NOT_FOUND"
    APPOINTMENT_NOT_FOUND = "APPOINTMENT_NOT_FOUND"
    
    # Email Verification
    INVALID_VERIFICATION_CODE = "INVALID_VERIFICATION_CODE"
    VERIFICATION_CODE_EXPIRED = "VERIFICATION_CODE_EXPIRED"
    VERIFICATION_CODE_USED = "VERIFICATION_CODE_USED"
    
    # Generic
    NOT_FOUND = "NOT_FOUND"
    SERVER_ERROR = "SERVER_ERROR"
    BAD_REQUEST = "BAD_REQUEST"


class BaseAPIException(APIException):
    """Base exception for custom API errors with error codes."""
    
    error_code = ErrorCode.SERVER_ERROR
    
    def __init__(self, detail=None, code=None, error_code=None):
        super().__init__(detail, code)
        if error_code:
            self.error_code = error_code


class EmailAlreadyExistsError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ten adres email jest już zarejestrowany"
    error_code = ErrorCode.EMAIL_ALREADY_EXISTS


class UsernameAlreadyExistsError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Ta nazwa użytkownika jest już zajęta"
    error_code = ErrorCode.USERNAME_ALREADY_EXISTS


class WrongPasswordError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Nieprawidłowe hasło"
    error_code = ErrorCode.WRONG_PASSWORD


class InvalidCredentialsError(BaseAPIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = "Nieprawidłowy email lub hasło"
    error_code = ErrorCode.INVALID_CREDENTIALS


class EmailNotVerifiedError(BaseAPIException):
    status_code = status.HTTP_403_FORBIDDEN
    default_detail = "Potwierdź adres email zanim się zalogujesz"
    error_code = ErrorCode.EMAIL_NOT_VERIFIED


class InvalidVerificationCodeError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Nieprawidłowy kod weryfikacyjny"
    error_code = ErrorCode.INVALID_VERIFICATION_CODE


class VerificationCodeExpiredError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Kod weryfikacyjny wygasł"
    error_code = ErrorCode.VERIFICATION_CODE_EXPIRED


class VerificationCodeUsedError(BaseAPIException):
    status_code = status.HTTP_400_BAD_REQUEST
    default_detail = "Kod weryfikacyjny został już wykorzystany"
    error_code = ErrorCode.VERIFICATION_CODE_USED


def custom_exception_handler(exc, context):
    """
    Custom exception handler that formats all errors consistently.
    
    Returns:
        {
            "success": false,
            "error": {
                "code": "ERROR_CODE",
                "message": "Human readable message",
                "details": {...}  // Optional field-specific errors
            }
        }
    """
    # Call DRF's default exception handler first
    response = exception_handler(exc, context)
    
    if response is not None:
        # Get error code
        error_code = getattr(exc, 'error_code', None)
        if not error_code:
            # Map DRF exceptions to error codes
            if response.status_code == status.HTTP_404_NOT_FOUND:
                error_code = ErrorCode.NOT_FOUND
            elif response.status_code == status.HTTP_401_UNAUTHORIZED:
                error_code = ErrorCode.UNAUTHORIZED
            elif response.status_code == status.HTTP_403_FORBIDDEN:
                error_code = ErrorCode.PERMISSION_DENIED
            elif response.status_code == status.HTTP_400_BAD_REQUEST:
                error_code = ErrorCode.VALIDATION_ERROR
            else:
                error_code = ErrorCode.SERVER_ERROR
        
        # Extract message
        if isinstance(response.data, dict):
            message = response.data.get('detail', None)
            if not message:
                # For validation errors, get first error message
                first_key = next(iter(response.data.keys()), None)
                if first_key:
                    first_value = response.data[first_key]
                    if isinstance(first_value, list):
                        message = first_value[0] if first_value else str(exc)
                    else:
                        message = str(first_value)
                else:
                    message = str(exc)
        else:
            message = str(exc)
        
        # Format standardized error response
        error_response = {
            'success': False,
            'error': {
                'code': error_code,
                'message': message,
            }
        }
        
        # Add field-specific errors for validation errors
        if isinstance(response.data, dict) and 'detail' not in response.data:
            # This is likely a validation error with field-specific messages
            error_response['error']['details'] = response.data
        
        response.data = error_response
    
    return response
