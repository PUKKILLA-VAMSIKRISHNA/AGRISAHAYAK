from flask import current_app, render_template, request
from flask_mail import Message
import random
import string
from datetime import datetime, timedelta
from extensions import db
import logging
import smtplib
import ssl
import time
from models import EmailVerification, PasswordReset

# Set up logging
logger = logging.getLogger(__name__)

def generate_otp():
    """Generate a 6-digit OTP"""
    return ''.join(random.choices(string.digits, k=6))

def generate_reset_token():
    """Generate a secure token for password reset"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=32))

def send_verification_email(email, otp):
    """Send verification email with OTP"""
    max_retries = 3
    retry_delay = 5  # seconds
    
    for attempt in range(max_retries):
        try:
            msg = Message('Verify Your Email - AgriSahayak',
                        sender=('AgriSahayak', 'agrisahayak2025@gmail.com'),
                        recipients=[email])
            
            # Add email headers to improve deliverability
            msg.headers = {
                'List-Unsubscribe': f'<mailto:{current_app.config["MAIL_USERNAME"]}>',
                'Precedence': 'bulk',
                'X-Auto-Response-Suppress': 'OOF, AutoReply'
            }
            
            # Render HTML template
            msg.html = render_template('email/verify_email.html',
                                    otp=otp,
                                    email=email,
                                    expiry_minutes=10)
            
            # Add plain text version as fallback
            msg.body = f"""
            Your AgriSahayak verification code is: {otp}
            
            This code will expire in 10 minutes.
            
            If you didn't request this code, please ignore this email.
            """
            
            logger.info(f"Attempting to send email to {email} (Attempt {attempt + 1}/{max_retries})")
            logger.debug(f"Mail configuration: MAIL_SERVER={current_app.config['MAIL_SERVER']}, "
                        f"MAIL_PORT={current_app.config['MAIL_PORT']}, "
                        f"MAIL_USE_SSL={current_app.config['MAIL_USE_SSL']}, "
                        f"MAIL_USE_TLS={current_app.config['MAIL_USE_TLS']}")
            
            # Send email using Flask-Mail
            current_app.extensions['mail'].send(msg)
            logger.info(f"Email sent successfully to {email}")
            return True
            
        except smtplib.SMTPAuthenticationError as e:
            logger.error(f"SMTP Authentication Error: {str(e)}")
            if attempt == max_retries - 1:
                raise Exception("Failed to authenticate with email server. Please check your email credentials.")
            time.sleep(retry_delay)
            
        except smtplib.SMTPException as e:
            logger.error(f"SMTP Error: {str(e)}")
            if attempt == max_retries - 1:
                raise Exception("Failed to send email. Please try again later.")
            time.sleep(retry_delay)
            
        except Exception as e:
            logger.error(f"Unexpected error: {str(e)}")
            if attempt == max_retries - 1:
                raise Exception(f"Failed to send verification email: {str(e)}")
            time.sleep(retry_delay)
    
    return False

def send_password_reset_email(email, token):
    """Send password reset email with token"""
    base_url = current_app.config.get('BASE_URL')
    if not base_url or base_url == 'http://localhost:5000':
        # Use the request host if BASE_URL is not set or is localhost
        base_url = request.url_root.rstrip('/')
    reset_url = f"{base_url}/reset_password/{token}"
    
    msg = Message('Reset Your Password - AgriSahayak',
                  sender=('AgriSahayak', 'agrisahayak2025@gmail.com'),
                  recipients=[email])
    
    # Add email headers to improve deliverability
    msg.headers = {
        'List-Unsubscribe': f'<mailto:{current_app.config["MAIL_USERNAME"]}>',
        'Precedence': 'bulk',
        'X-Auto-Response-Suppress': 'OOF, AutoReply'
    }
    
    # Render HTML template
    msg.html = render_template('email/reset_password.html',
                             reset_url=reset_url,
                             email=email,
                             expiry_hours=1)
    
    # Add plain text version as fallback
    msg.body = f"""
    To reset your AgriSahayak password, click the following link:
    {reset_url}
    
    This link will expire in 1 hour.
    
    If you didn't request this password reset, please ignore this email.
    """
    
    current_app.extensions['mail'].send(msg)

def verify_otp(email, otp):
    """Verify the OTP for email verification
    
    Args:
        email (str): The email address to verify
        otp (str): The OTP code to verify
        
    Returns:
        bool: True if verification is successful, False otherwise
    """
    try:
        # Find the most recent unverified OTP for this email
        verification = EmailVerification.query.filter_by(
            email=email,
            is_verified=False
        ).order_by(EmailVerification.created_at.desc()).first()
        
        if not verification:
            logger.warning(f"No unverified OTP found for email: {email}")
            return False
            
        # Check if OTP has expired (10 minutes)
        if datetime.utcnow() - verification.created_at > timedelta(minutes=10):
            logger.warning(f"OTP expired for email: {email}")
            return False
            
        # Verify the OTP
        if verification.otp == otp:
            # Mark the verification as used
            verification.is_verified = True
            db.session.commit()
            logger.info(f"OTP verified successfully for email: {email}")
            return True
            
        logger.warning(f"Invalid OTP for email: {email}")
        return False
        
    except Exception as e:
        logger.error(f"Error verifying OTP: {str(e)}")
        return False

def verify_reset_token(token):
    """Verify password reset token"""
    reset = PasswordReset.query.filter_by(
        token=token,
        is_used=False
    ).first()
    
    if not reset:
        return False
    
    # Check if token has expired (1 hour)
    if datetime.utcnow() - reset.created_at > timedelta(hours=1):
        return False
    
    return reset.email 
