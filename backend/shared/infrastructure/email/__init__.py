"""
Email Infrastructure Module

Fornece serviço de envio de emails via Mailgun.
"""

from backend.shared.infrastructure.email.email_service import (
    EmailService,
    get_email_service,
)

__all__ = ["EmailService", "get_email_service"]
