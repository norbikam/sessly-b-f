"""
Logging configuration for Sessly application.
"""

import logging
import sys

# Color codes for terminal output
COLORS = {
    'DEBUG': '\033[36m',      # Cyan
    'INFO': '\033[32m',       # Green
    'WARNING': '\033[33m',    # Yellow
    'ERROR': '\033[31m',      # Red
    'CRITICAL': '\033[35m',   # Magenta
    'RESET': '\033[0m',       # Reset
}


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for terminal output."""
    
    def format(self, record):
        levelname = record.levelname
        if levelname in COLORS:
            record.levelname = f"{COLORS[levelname]}{levelname}{COLORS['RESET']}"
        return super().format(record)


def get_logging_config(debug=False, environment='development'):
    """
    Get logging configuration based on environment.
    
    Args:
        debug: Whether debug mode is enabled
        environment: Current environment (development, production)
    
    Returns:
        Dictionary with logging configuration
    """
    log_level = 'DEBUG' if debug else 'INFO'
    
    config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'verbose': {
                'format': '{levelname} {asctime} {module} {process:d} {thread:d} {message}',
                'style': '{',
            },
            'simple': {
                'format': '{levelname} {asctime} {message}',
                'style': '{',
            },
            'colored': {
                '()': 'backend.logging_config.ColoredFormatter',
                'format': '{levelname} {asctime} [{name}] {message}',
                'style': '{',
                'datefmt': '%Y-%m-%d %H:%M:%S',
            },
        },
        'filters': {
            'require_debug_false': {
                '()': 'django.utils.log.RequireDebugFalse',
            },
            'require_debug_true': {
                '()': 'django.utils.log.RequireDebugTrue',
            },
        },
        'handlers': {
            'console': {
                'level': log_level,
                'class': 'logging.StreamHandler',
                'formatter': 'colored' if debug else 'simple',
                'stream': sys.stdout,
            },
            'file': {
                'level': 'INFO',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/sessly.log',
                'maxBytes': 1024 * 1024 * 15,  # 15MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
            'error_file': {
                'level': 'ERROR',
                'class': 'logging.handlers.RotatingFileHandler',
                'filename': 'logs/errors.log',
                'maxBytes': 1024 * 1024 * 15,  # 15MB
                'backupCount': 10,
                'formatter': 'verbose',
            },
        },
        'loggers': {
            'django': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
            'django.request': {
                'handlers': ['console', 'error_file'],
                'level': 'ERROR',
                'propagate': False,
            },
            'django.security': {
                'handlers': ['console', 'error_file'],
                'level': 'WARNING',
                'propagate': False,
            },
            'users': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
            'businesses': {
                'handlers': ['console', 'file'],
                'level': log_level,
                'propagate': False,
            },
            # Root logger
            '': {
                'handlers': ['console', 'file'],
                'level': log_level,
            },
        },
    }
    
    # In production, don't use colored formatter and reduce console logging
    if environment == 'production':
        config['handlers']['console']['formatter'] = 'simple'
        config['handlers']['console']['level'] = 'WARNING'
    
    return config


# Utility functions for logging important events

def log_user_action(logger, user, action, details=None):
    """
    Log user actions.
    
    Args:
        logger: Logger instance
        user: User object or username
        action: Action description
        details: Additional details (optional)
    """
    username = user.username if hasattr(user, 'username') else str(user)
    message = f"User '{username}' {action}"
    if details:
        message += f" - {details}"
    logger.info(message)


def log_business_action(logger, business, action, user=None, details=None):
    """
    Log business-related actions.
    
    Args:
        logger: Logger instance
        business: Business object or name
        action: Action description
        user: User who performed the action (optional)
        details: Additional details (optional)
    """
    business_name = business.name if hasattr(business, 'name') else str(business)
    message = f"Business '{business_name}' {action}"
    if user:
        username = user.username if hasattr(user, 'username') else str(user)
        message += f" by user '{username}'"
    if details:
        message += f" - {details}"
    logger.info(message)


def log_appointment_action(logger, appointment, action, user=None, details=None):
    """
    Log appointment-related actions.
    
    Args:
        logger: Logger instance
        appointment: Appointment object or ID
        action: Action description
        user: User who performed the action (optional)
        details: Additional details (optional)
    """
    appt_id = appointment.id if hasattr(appointment, 'id') else str(appointment)
    message = f"Appointment {appt_id} {action}"
    if user:
        username = user.username if hasattr(user, 'username') else str(user)
        message += f" by user '{username}'"
    if details:
        message += f" - {details}"
    logger.info(message)
