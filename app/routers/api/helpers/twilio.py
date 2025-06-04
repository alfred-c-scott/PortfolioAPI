# installed
from twilio.rest import Client
from twilio.base.exceptions import TwilioRestException
from fastapi import HTTPException, status


# local
from app.config import settings
client = Client()


def send_verification(phone_number: str) -> str:
    # TODO: pip install phonenumbers to validate phone number
    transformed_phone_number = "+1" + phone_number
    try:
        verification = client.verify.v2.services(settings.twilio_verify_service_sid).verifications.create(
            to=transformed_phone_number,
            channel="sms"
        )
        return verification.status
    except TwilioRestException as e:
        # TODO: See twilio documentation for more error codes
        if e.code == 60200:  # Invalid phone number format
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid phone number format. Use E.164 format (e.g., +12345678900)."
            )
        elif e.code == 60203:  # Max attempts reached
            raise HTTPException(
                status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                detail="Maximum verification attempts reached. Please try again later."
            )
        if e.code == 60202:  # Phone number not verified in trial mode
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Trial account: Please verify this phone number in the Twilio Console."
            )
        else:  # Generic Twilio error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Twilio error: {e.msg} (Error Code: {e.code})"
            )
    except Exception as e:  # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


# Helper function to check verification code
def check_verification(phone_number: str, code: str) -> bool:
    transformed_phone_number = "+1" + phone_number
    try:
        verification_check = client.verify.v2.services(settings.twilio_verify_service_sid).verification_checks.create(
            to=transformed_phone_number,
            code=code
        )
        if verification_check.status == "approved":
            return True
        else:
            return False
    except TwilioRestException as e:
        if e.code == 60610:  # Invalid or expired code
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid or expired verification code."
            )
        else:  # Generic Twilio error
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Twilio error: {e.msg} (Error Code: {e.code})"
            )
    except Exception as e:  # Catch any other unexpected errors
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )
