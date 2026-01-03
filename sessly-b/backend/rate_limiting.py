"""
Rate limiting decorators and middleware for API protection.

Uses django-ratelimit package. Install with:
pip install django-ratelimit
"""

from functools import wraps
from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response

from backend.exceptions import ErrorCode
from backend.responses import error_response


def simple_rate_limit(key_prefix, rate, method='POST'):
    """
    Simple rate limiting decorator.
    
    Args:
        key_prefix: Prefix for cache key
        rate: Rate limit (e.g., '5/m' for 5 per minute, '100/h' for 100 per hour)
        method: HTTP method to rate limit (default: POST)
    
    Usage:
        @simple_rate_limit('login', '5/m')
        def login_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if request.method != method:
                return view_func(request, *args, **kwargs)
            
            # Parse rate
            limit, period = rate.split('/')
            limit = int(limit)
            
            # Convert period to seconds
            period_seconds = {
                's': 1,
                'm': 60,
                'h': 3600,
                'd': 86400,
            }.get(period, 60)
            
            # Generate cache key based on IP
            ip = get_client_ip(request)
            cache_key = f'ratelimit:{key_prefix}:{ip}'
            
            # Get current count
            current_count = cache.get(cache_key, 0)
            
            if current_count >= limit:
                return error_response(
                    error_code=ErrorCode.BAD_REQUEST,
                    message=f"Przekroczono limit żądań. Spróbuj ponownie za {period_seconds} sekund.",
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS
                )
            
            # Increment counter
            cache.set(cache_key, current_count + 1, period_seconds)
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator


def get_client_ip(request):
    """
    Get client IP address from request.
    
    Handles proxy headers correctly.
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


# Pre-configured rate limiters for common endpoints

def rate_limit_auth(func):
    """Rate limit authentication endpoints (5 per minute)."""
    return simple_rate_limit('auth', '5/m')(func)


def rate_limit_registration(func):
    """Rate limit registration endpoint (3 per hour)."""
    return simple_rate_limit('register', '3/h')(func)


def rate_limit_api(func):
    """Rate limit general API endpoints (100 per minute)."""
    return simple_rate_limit('api', '100/m')(func)


def rate_limit_booking(func):
    """Rate limit booking endpoints (10 per minute)."""
    return simple_rate_limit('booking', '10/m')(func)
