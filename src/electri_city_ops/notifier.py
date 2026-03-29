from __future__ import annotations

from email.message import EmailMessage
import logging
import smtplib

from electri_city_ops.config import EmailNotificationConfig


def send_email_summary(
    email_config: EmailNotificationConfig,
    subject: str,
    body: str,
    logger: logging.Logger,
) -> bool:
    if not email_config.enabled:
        return False
    if not email_config.is_complete():
        logger.warning("email enabled but SMTP config is incomplete")
        return False

    message = EmailMessage()
    message["Subject"] = subject
    message["From"] = email_config.sender
    message["To"] = ", ".join(email_config.recipients)
    message.set_content(body)

    with smtplib.SMTP(email_config.smtp_host, email_config.smtp_port, timeout=15) as smtp:
        if email_config.starttls:
            smtp.starttls()
        smtp.login(email_config.smtp_username, email_config.smtp_password)
        smtp.send_message(message)
    logger.info("email notification sent to %s", ", ".join(email_config.recipients))
    return True

