"""
Helper functions for standardized API responses.
"""

from rest_framework import status
from rest_framework.response import Response


def success_response(data=None, message=None, status_code=status.HTTP_200_OK):
    """
    Create a standardized success response.
    
    Args:
        data: The response data (optional)
        message: Success message (optional)
        status_code: HTTP status code (default: 200)
    
    Returns:
        Response with format:
        {
            "success": true,
            "data": {...},
            "message": "..." (optional)
        }
    """
    response_data = {
        "success": True,
    }
    
    if data is not None:
        response_data["data"] = data
    
    if message:
        response_data["message"] = message
    
    return Response(response_data, status=status_code)


def error_response(error_code, message, details=None, status_code=status.HTTP_400_BAD_REQUEST):
    """
    Create a standardized error response.
    
    Args:
        error_code: Error code constant (from ErrorCode class)
        message: Human-readable error message
        details: Optional field-specific error details
        status_code: HTTP status code (default: 400)
    
    Returns:
        Response with format:
        {
            "success": false,
            "error": {
                "code": "ERROR_CODE",
                "message": "...",
                "details": {...} (optional)
            }
        }
    """
    error_data = {
        "success": False,
        "error": {
            "code": error_code,
            "message": message,
        }
    }
    
    if details:
        error_data["error"]["details"] = details
    
    return Response(error_data, status=status_code)
