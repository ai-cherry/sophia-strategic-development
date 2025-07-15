import smtplib
import ssl
from email.mime.text import MimeText
from email.mime.multipart import MimeMultipart
from email.mime.base import MimeBase
from email import encoders
from typing import List, Optional, Dict, Any
import logging
import asyncio
from datetime import datetime
import os
from jinja2 import Template, Environment, FileSystemLoader

from backend.core.auto_esc_config import get_config_value
from backend.utils.logging import get_logger

logger = get_logger(__name__)

class EmailService:
    """Email service for sending notifications and invitations"""
    
    def __init__(self):
        self.smtp_host = get_config_value("SMTP_HOST", "smtp.gmail.com")
        self.smtp_port = int(get_config_value("SMTP_PORT", "587"))
        self.smtp_username = get_config_value("SMTP_USERNAME", "sophia@payready.com")
        self.smtp_password = get_config_value("SMTP_PASSWORD", "")
        self.from_email = get_config_value("FROM_EMAIL", "sophia@payready.com")
        self.from_name = get_config_value("FROM_NAME", "Sophia AI")
        
        # Email templates directory
        self.template_dir = os.path.join(os.path.dirname(__file__), "../templates/email")
        self.jinja_env = Environment(loader=FileSystemLoader(self.template_dir))
        
        # Initialize email templates
        self._initialize_templates()

    def _initialize_templates(self):
        """Initialize email templates"""
        self.templates = {
            "user_invitation": {
                "subject": "Welcome to Sophia AI - Complete Your Registration",
                "template": """
                Hello {{ user_name }},

                You've been invited to join the Sophia AI platform by {{ inviter_name }}.

                Sophia AI is Pay Ready's executive AI orchestrator that provides strategic project management 
                and business intelligence across our entire organization.

                To complete your registration and set up your account, please click the link below:
                
                {{ invitation_link }}

                This invitation will expire in 7 days.

                Your Role: {{ role }}
                Department: {{ department }}

                If you have any questions, please contact your administrator.

                Best regards,
                The Sophia AI Team
                """,
                "html_template": """
                <!DOCTYPE html>
                <html>
                <head>
                    <style>
                        body { font-family: Arial, sans-serif; line-height: 1.6; color: #333; }
                        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
                        .header { background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 20px; text-align: center; }
                        .content { padding: 20px; background: #f9f9f9; }
                        .button { display: inline-block; padding: 12px 24px; background: #4F46E5; color: white; text-decoration: none; border-radius: 6px; margin: 20px 0; }
                        .footer { padding: 20px; text-align: center; font-size: 14px; color: #666; }
                    </style>
                </head>
                <body>
                    <div class="container">
                        <div class="header">
                            <h1>Welcome to Sophia AI</h1>
                            <p>Executive AI Orchestrator for Pay Ready</p>
                        </div>
                        <div class="content">
                            <h2>Hello {{ user_name }},</h2>
                            <p>You've been invited to join the Sophia AI platform by <strong>{{ inviter_name }}</strong>.</p>
                            
                            <p>Sophia AI is Pay Ready's executive AI orchestrator that provides strategic project management 
                            and business intelligence across our entire organization.</p>
                            
                            <p><strong>Your Details:</strong></p>
                            <ul>
                                <li>Role: {{ role }}</li>
                                <li>Department: {{ department }}</li>
                            </ul>
                            
                            <p>To complete your registration and set up your account, click the button below:</p>
                            
                            <a href="{{ invitation_link }}" class="button">Complete Registration</a>
                            
                            <p><em>This invitation will expire in 7 days.</em></p>
                            
                            <p>If you have any questions, please contact your administrator.</p>
                        </div>
                        <div class="footer">
                            <p>Best regards,<br>The Sophia AI Team</p>
                            <p>Pay Ready Inc. | Executive AI Platform</p>
                        </div>
                    </div>
                </body>
                </html>
                """
            },
            "password_reset": {
                "subject": "Sophia AI - Password Reset Request",
                "template": """
                Hello {{ user_name }},

                We received a request to reset your password for your Sophia AI account.

                To reset your password, please click the link below:
                
                {{ reset_link }}

                This link will expire in 1 hour.

                If you didn't request this password reset, please ignore this email.

                Best regards,
                The Sophia AI Team
                """
            },
            "account_locked": {
                "subject": "Sophia AI - Account Security Alert",
                "template": """
                Hello {{ user_name }},

                Your Sophia AI account has been temporarily locked due to multiple failed login attempts.

                Your account will be automatically unlocked at: {{ unlock_time }}

                If you believe this was unauthorized access, please contact your administrator immediately.

                Best regards,
                The Sophia AI Team
                """
            },
            "role_changed": {
                "subject": "Sophia AI - Role Updated",
                "template": """
                Hello {{ user_name }},

                Your role in the Sophia AI platform has been updated.

                Previous Role: {{ old_role }}
                New Role: {{ new_role }}
                Updated By: {{ updated_by }}

                Your new permissions will take effect on your next login.

                Best regards,
                The Sophia AI Team
                """
            }
        }

    async def send_email(
        self,
        to_email: str,
        subject: str,
        body: str,
        html_body: Optional[str] = None,
        attachments: Optional[List[Dict[str, Any]]] = None
    ) -> bool:
        """Send email to recipient"""
        try:
            # Create message
            message = MimeMultipart("alternative")
            message["Subject"] = subject
            message["From"] = f"{self.from_name} <{self.from_email}>"
            message["To"] = to_email

            # Add text part
            text_part = MimeText(body, "plain")
            message.attach(text_part)

            # Add HTML part if provided
            if html_body:
                html_part = MimeText(html_body, "html")
                message.attach(html_part)

            # Add attachments if provided
            if attachments:
                for attachment in attachments:
                    part = MimeBase("application", "octet-stream")
                    part.set_payload(attachment["data"])
                    encoders.encode_base64(part)
                    part.add_header(
                        "Content-Disposition",
                        f"attachment; filename= {attachment['filename']}"
                    )
                    message.attach(part)

            # Send email
            await self._send_smtp_email(message, to_email)
            
            logger.info(f"Email sent successfully to {to_email}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False

    async def _send_smtp_email(self, message: MimeMultipart, to_email: str):
        """Send email via SMTP"""
        context = ssl.create_default_context()
        
        with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
            server.starttls(context=context)
            server.login(self.smtp_username, self.smtp_password)
            server.sendmail(self.from_email, to_email, message.as_string())

    async def send_invitation_email(
        self,
        user_email: str,
        user_name: str,
        invitation_token: str,
        inviter_name: str,
        role: str,
        department: str = "Not specified"
    ) -> bool:
        """Send user invitation email"""
        try:
            template_data = self.templates["user_invitation"]
            
            # Generate invitation link
            invitation_link = f"https://sophia.payready.com/auth/accept-invitation?token={invitation_token}"
            
            # Template variables
            variables = {
                "user_name": user_name,
                "inviter_name": inviter_name,
                "invitation_link": invitation_link,
                "role": role,
                "department": department
            }

            # Render templates
            text_template = Template(template_data["template"])
            html_template = Template(template_data["html_template"])
            
            text_body = text_template.render(**variables)
            html_body = html_template.render(**variables)

            return await self.send_email(
                to_email=user_email,
                subject=template_data["subject"],
                body=text_body,
                html_body=html_body
            )

        except Exception as e:
            logger.error(f"Failed to send invitation email to {user_email}: {e}")
            return False

    async def send_password_reset_email(
        self,
        user_email: str,
        user_name: str,
        reset_token: str
    ) -> bool:
        """Send password reset email"""
        try:
            template_data = self.templates["password_reset"]
            
            # Generate reset link
            reset_link = f"https://sophia.payready.com/auth/reset-password?token={reset_token}"
            
            # Template variables
            variables = {
                "user_name": user_name,
                "reset_link": reset_link
            }

            # Render template
            text_template = Template(template_data["template"])
            text_body = text_template.render(**variables)

            return await self.send_email(
                to_email=user_email,
                subject=template_data["subject"],
                body=text_body
            )

        except Exception as e:
            logger.error(f"Failed to send password reset email to {user_email}: {e}")
            return False

    async def send_account_locked_email(
        self,
        user_email: str,
        user_name: str,
        unlock_time: datetime
    ) -> bool:
        """Send account locked notification email"""
        try:
            template_data = self.templates["account_locked"]
            
            # Template variables
            variables = {
                "user_name": user_name,
                "unlock_time": unlock_time.strftime("%Y-%m-%d %H:%M:%S UTC")
            }

            # Render template
            text_template = Template(template_data["template"])
            text_body = text_template.render(**variables)

            return await self.send_email(
                to_email=user_email,
                subject=template_data["subject"],
                body=text_body
            )

        except Exception as e:
            logger.error(f"Failed to send account locked email to {user_email}: {e}")
            return False

    async def send_role_changed_email(
        self,
        user_email: str,
        user_name: str,
        old_role: str,
        new_role: str,
        updated_by: str
    ) -> bool:
        """Send role changed notification email"""
        try:
            template_data = self.templates["role_changed"]
            
            # Template variables
            variables = {
                "user_name": user_name,
                "old_role": old_role,
                "new_role": new_role,
                "updated_by": updated_by
            }

            # Render template
            text_template = Template(template_data["template"])
            text_body = text_template.render(**variables)

            return await self.send_email(
                to_email=user_email,
                subject=template_data["subject"],
                body=text_body
            )

        except Exception as e:
            logger.error(f"Failed to send role changed email to {user_email}: {e}")
            return False

    async def send_bulk_notification(
        self,
        recipients: List[str],
        subject: str,
        body: str,
        html_body: Optional[str] = None
    ) -> Dict[str, bool]:
        """Send bulk notification to multiple recipients"""
        results = {}
        
        for recipient in recipients:
            try:
                success = await self.send_email(
                    to_email=recipient,
                    subject=subject,
                    body=body,
                    html_body=html_body
                )
                results[recipient] = success
                
                # Add small delay to prevent rate limiting
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Failed to send bulk email to {recipient}: {e}")
                results[recipient] = False

        return results

    def test_connection(self) -> bool:
        """Test SMTP connection"""
        try:
            context = ssl.create_default_context()
            
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls(context=context)
                server.login(self.smtp_username, self.smtp_password)
                
            logger.info("SMTP connection test successful")
            return True
            
        except Exception as e:
            logger.error(f"SMTP connection test failed: {e}")
            return False

    def get_email_stats(self) -> Dict[str, Any]:
        """Get email service statistics"""
        return {
            "smtp_host": self.smtp_host,
            "smtp_port": self.smtp_port,
            "from_email": self.from_email,
            "from_name": self.from_name,
            "templates_loaded": len(self.templates),
            "connection_status": "configured" if self.smtp_password else "not_configured"
        } 