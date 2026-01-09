"""
Email Service - Send verification and notification emails
"""
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Optional
from jinja2 import Template

from app.core.config import settings


class EmailService:
    """Service for sending emails"""
    
    VERIFICATION_TEMPLATE = """
    <!DOCTYPE html>
    <html>
    <head>
        <style>
            body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
            .container { max-width: 600px; margin: 0 auto; padding: 20px; }
            .header { background: #4F46E5; color: white; padding: 20px; text-align: center; }
            .content { padding: 20px; background: #f9f9f9; }
            .button { 
                display: inline-block; 
                padding: 12px 24px; 
                background: #4F46E5; 
                color: white; 
                text-decoration: none; 
                border-radius: 4px;
                margin: 20px 0;
            }
            .footer { padding: 20px; text-align: center; font-size: 12px; color: #666; }
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>License Manager</h1>
            </div>
            <div class="content">
                <h2>Verify Your Email</h2>
                <p>Hello {{ full_name or 'there' }},</p>
                <p>Thank you for registering with License Manager. Please click the button below to verify your email address:</p>
                <p style="text-align: center;">
                    <a href="{{ verification_url }}" class="button">Verify Email</a>
                </p>
                <p>Or copy and paste this link into your browser:</p>
                <p style="word-break: break-all;">{{ verification_url }}</p>
                <p>This link will expire in 24 hours.</p>
            </div>
            <div class="footer">
                <p>&copy; {{ year }} License Manager. All rights reserved.</p>
            </div>
        </div>
    </body>
    </html>
    """
    
    @staticmethod
    async def send_email(
        to_email: str,
        subject: str,
        html_content: str,
        text_content: Optional[str] = None
    ) -> bool:
        """Send an email"""
        if not settings.SMTP_USER or not settings.SMTP_PASSWORD:
            # Email not configured, skip sending
            print(f"[EMAIL] Would send to {to_email}: {subject}")
            return True
        
        try:
            message = MIMEMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{settings.EMAIL_FROM_NAME} <{settings.EMAIL_FROM}>"
            message["To"] = to_email
            
            # Add text part
            if text_content:
                part1 = MIMEText(text_content, "plain")
                message.attach(part1)
            
            # Add HTML part
            part2 = MIMEText(html_content, "html")
            message.attach(part2)
            
            # Send email
            await aiosmtplib.send(
                message,
                hostname=settings.SMTP_HOST,
                port=settings.SMTP_PORT,
                username=settings.SMTP_USER,
                password=settings.SMTP_PASSWORD,
                start_tls=True,
            )
            return True
        except Exception as e:
            print(f"[EMAIL ERROR] Failed to send email: {e}")
            return False
    
    @classmethod
    async def send_verification_email(
        cls,
        to_email: str,
        token: str,
        full_name: Optional[str] = None
    ) -> bool:
        """Send email verification email"""
        from datetime import datetime
        
        verification_url = f"{settings.FRONTEND_URL}/verify-email?token={token}"
        
        template = Template(cls.VERIFICATION_TEMPLATE)
        html_content = template.render(
            full_name=full_name,
            verification_url=verification_url,
            year=datetime.now().year
        )
        
        return await cls.send_email(
            to_email=to_email,
            subject="Verify Your Email - License Manager",
            html_content=html_content,
            text_content=f"Verify your email by visiting: {verification_url}"
        )
