from datetime import timedelta
from http import client
import random

import brevo_python
from brevo_python.rest import ApiException

from fastapi import HTTPException
from pydantic import BaseModel, EmailStr
from constants.global_constants import ACCESS_TOKEN_EXPIRE_MINUTES
from controllers.brevo_controller import FROM_EMAIL, client
from controllers.db_controller import conn
from controllers.redis_controller import redis_client

from models.signup_request_model import SignUpRequest
from utilities.password.password_utilities import hash_password
from utilities.token.token_utilities import create_access_token, create_email_verification_token, create_refresh_token, verify_email_token

class OTPData(BaseModel):
    otp: int
    email: EmailStr

def add_partial_user_to_db(data: SignUpRequest):
    cursor = conn.cursor()
    try:
        hashed_pw = hash_password(data.password)
        email = verify_email_token(data.email_hash)

        cursor.execute("""
            INSERT INTO USERS (email, password_hash) VALUES (%s, %s) RETURNING id;
        """, (email, hashed_pw))
        user_id = cursor.fetchone()[0]
        conn.commit()

        access_token = create_access_token(
            data={"id": user_id, "email": email},
            expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        )
        refresh_token = create_refresh_token(
            data={"id": user_id, "email": email}
        )

        return {
            "status": "success",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user_id": user_id
        }

    except Exception as e:
        conn.rollback()
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")
    finally:
        cursor.close()



def send_otp_email(to_email: str, otp: str):
    html = f"""
    <div style="font-family: Arial, sans-serif; max-width: 600px; margin: auto; padding: 20px; background: #f9f9f9; border-radius: 8px; border: 1px solid #ddd;">
        <h2 style="color: #2a2a2a;">🔐 Your LinkUp OTP Code</h2>
        <p style="font-size: 16px; color: #333;">
            Hello, your one-time password (OTP) is:
        </p>
        <p style="font-size: 28px; font-weight: bold; color: #007BFF; margin: 10px 0;">
            {otp}
        </p>
        <p style="font-size: 14px; color: #555;">
            This OTP is valid for 5 minutes. Please don’t share it with anyone.
        </p>
        <hr style="margin: 30px 0;">
        <footer style="font-size: 12px; color: #888; text-align: center;">
            LinkUp — more than just classmates<br>
            If you didn’t request this, you can safely ignore this email.
        </footer>
    </div>
    """
    payload = brevo_python.SendSmtpEmail(
        sender={"name": "LinkUp OTP", "email": 'ebin67891234@gmail.com'},
        to=[{"email": to_email}],
        subject="Your OTP Code",
        html_content=html
    )
    try:
        client.send_transac_email(payload)
    except ApiException as e:
        raise HTTPException(status_code=500, detail=f"Email send failed: {e.body}")
    
def generate_otp():
    # return str(random.randint(100000, 999999))
    return 123456

def store_otp(email: str, otp: str):
    redis_client.setex(f"otp:{email}", timedelta(minutes=5), otp)
 
def verify_otp_internal(data : OTPData):
    try:
        stored_otp = redis_client.get(f"otp:{data.email}")
        if stored_otp is None:
            raise HTTPException(status_code=400, detail="OTP expired or not found")
        elif str(stored_otp.decode()) != str(data.otp):
            raise HTTPException(status_code=400, detail="Invalid OTP")
        elif str(stored_otp.decode()) == str(data.otp):
            return {"status": "success", "email_hash": create_email_verification_token(email=data.email)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"OTP verification failed: {str(e)}")