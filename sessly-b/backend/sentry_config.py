"""
Sentry configuration for error tracking and monitoring.

To enable Sentry:
1. Sign up at https://sentry.io
2. Create a new project for Django
3. Get your DSN (Data Source Name)
4. Set SENTRY_DSN environment variable
"""

import os
import sentry_sdk
from sentry_sdk.integrations.django import DjangoIntegration
from sentry_sdk.integrations.logging import LoggingIntegration


def init_sentry(environment='production', debug=False):
    """
    Initialize Sentry SDK.
    
    Args:
        environment: Current environment (development, production)
        debug: Whether debug mode is enabled
    """
    dsn = os.getenv('SENTRY_DSN')
    
    if not dsn:
        print("⚠️  SENTRY_DSN not set - error monitoring disabled")
        print("   Sign up at https://sentry.io and set SENTRY_DSN environment variable")
        return
    
    # Configure Sentry
    sentry_sdk.init(
        dsn=dsn,
        environment=environment,
        
        # Set traces_sample_rate to 1.0 to capture 100% of transactions for performance monitoring
        # We recommend adjusting this value in production
        traces_sample_rate=1.0 if environment == 'development' else 0.1,
        
        # Send default PII (Personally Identifiable Information)
        send_default_pii=True,
        
        # Integrations
        integrations=[
            DjangoIntegration(),
            LoggingIntegration(
                level=None,        # Capture all log levels
                event_level=None   # Send all error logs to Sentry
            ),
        ],
        
        # Release tracking
        release=os.getenv('SENTRY_RELEASE', 'development'),
        
        # Before send hook to filter events
        before_send=before_send_filter,
    )
    
    print(f"✅ Sentry initialized for environment: {environment}")


def before_send_filter(event, hint):
    """
    Filter events before sending to Sentry.
    
    You can:
    - Filter out certain errors
    - Add custom context
    - Scrub sensitive data
    
    Return None to drop the event.
    """
    # Example: Don't send 404 errors to Sentry
    if 'exc_info' in hint:
        exc_type, exc_value, tb = hint['exc_info']
        if isinstance(exc_value, Exception):
            # Add custom filtering logic here
            pass
    
    return event


def set_user_context(user):
    """
    Set user context for Sentry events.
    
    Call this after user authentication to associate errors with users.
    """
    if not user or not user.is_authenticated:
        return
    
    sentry_sdk.set_user({
        'id': str(user.id),
        'username': user.username,
        'email': user.email,
    })


def capture_exception(error, **extra_context):
    """
    Manually capture an exception and send to Sentry.
    
    Args:
        error: Exception instance
        **extra_context: Additional context to attach
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_exception(error)


def capture_message(message, level='info', **extra_context):
    """
    Manually capture a message and send to Sentry.
    
    Args:
        message: Message text
        level: Log level (debug, info, warning, error, fatal)
        **extra_context: Additional context to attach
    """
    with sentry_sdk.push_scope() as scope:
        for key, value in extra_context.items():
            scope.set_extra(key, value)
        sentry_sdk.capture_message(message, level=level)
