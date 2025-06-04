import uuid

from fastapi import status
from fastapi import HTTPException
from fastapi import Depends
from fastapi import APIRouter
from fastapi import UploadFile
from fastapi import File
from fastapi import Form

from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

from twilio.rest import Client

# local
from app import models
from app import schemas
from app import oauth2
from app import utils
from app.s3_config import s3_client
from app.s3_config import bucket_name
from app.database import get_db
from app.routers.api.helpers import twilio

client = Client()
router = APIRouter(
    prefix="/api/customer",
    tags=["Customer"],
)


@router.post('/phone/send_code')
async def send_code(payload: schemas.CustomerVerifyPhoneEmail,
                    db: Session = Depends(get_db),
                    machine: int = Depends(oauth2.current_machine)):

    phone_exists = db.query(models.Customer).filter(models.Customer.cell_phone == payload.phone).first()
    email_exists = db.query(models.Customer).filter(models.Customer.email == payload.email).first()

    if phone_exists and email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": "phone_and_email_dupe",
                "phone": payload.phone,
                "email": payload.email
            }
        )
    if phone_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": "phone_dupe",
                "phone": payload.phone
            }
        )
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": "email_dupe",
                "email": payload.email
            }
        )

    twilio_status = twilio.send_verification(payload.phone)

    return {"msg": f"Verification sent to {payload.phone}", "status": twilio_status}


@router.post('/phone/verify_code')
async def verify_code(payload: schemas.CustomerVerifyPhoneCode,
                      machine: int = Depends(oauth2.current_machine)):

    if twilio.check_verification(payload.phone, payload.code):
        return {"msg": "Phone number verified successfully!", "status": "approved"}
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Verification failed. Incorrect code or expired."
        )


@router.post('', status_code=status.HTTP_201_CREATED)
async def stage_customer(phone: str = Form(...),
                         email: str = Form(...),
                         pin: str = Form(...),
                         fingerprint: str = Form(...),
                         kiosk_img: UploadFile = File(...),
                         id_front: UploadFile = File(...),
                         id_back: UploadFile = File(...),
                         db: Session = Depends(get_db),
                         machine: int = Depends(oauth2.current_machine)):

    phone_exists = db.query(models.Customer).filter(models.Customer.cell_phone == phone).first()
    email_exists = db.query(models.Customer).filter(models.Customer.email == email).first()

    if phone_exists and email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": "phone_and_email_dupe",
                "phone": phone,
                "email": email
            }
        )
    if phone_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": "phone_dupe",
                "phone": phone
            }
        )
    if email_exists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={
                "reason": "email_dupe",
                "email": email
            }
        )

    try:
        files_data = schemas.CustomerStagingFiles(  # noqa: F841
            kiosk_img=kiosk_img,
            id_front=id_front,
            id_back=id_back
        )
    except ValueError as e:
        error_msg = str(e)
        if "Missing" in error_msg:
            error_msg = "file is missing"
        elif "Invalid file extension" in error_msg:
            error_msg = "invalid file extension"
        elif "Invalid MIME type" in error_msg:
            error_msg = "invalid MIME type"
        elif "Exceeds maximum file size" in error_msg:
            error_msg = "maximum file size exceeded"
        elif "Error checking file size" in error_msg:
            error_msg = "error checking file size"
        raise HTTPException(status_code=422, detail=error_msg)

    kiosk_img_uuid = str(uuid.uuid4())
    id_img_uuid = str(uuid.uuid4())

    kiosk_img_path = f"kiosk_img/location-{machine['location_id']}_machine-{machine['id']}_{kiosk_img_uuid}.jpeg"
    id_front_path = f"id_img/location-{machine['location_id']}_machine-{machine['id']}_{id_img_uuid}_front.jpeg"
    id_back_path = f"id_img/location-{machine['location_id']}_machine-{machine['id']}_{id_img_uuid}_back.jpeg"

    s3_client.upload_fileobj(kiosk_img.file, bucket_name, kiosk_img_path, ExtraArgs={'ContentType': 'image/jpeg'})
    s3_client.upload_fileobj(id_front.file, bucket_name, id_front_path, ExtraArgs={'ContentType': 'image/jpeg'})
    s3_client.upload_fileobj(id_back.file, bucket_name, id_back_path, ExtraArgs={'ContentType': 'image/jpeg'})

    try:
        customer_data = schemas.CustomerStaging(
            location_id=machine['location_id'],
            cell_phone=phone,
            email=email,
            pin=pin,
            fingerprint=fingerprint,
            kiosk_img=kiosk_img_path,
            id_front=id_front_path,
            id_back=id_back_path
        )

    except ValueError as e:
        error_msg = str(e)
        if "PIN must be 4 digits" in error_msg:
            error_msg = "pin must be 4 digits"
        elif "Phone number must be exactly 10 digits" in error_msg:
            error_msg = "phone must be exactly 10 digits"
        elif "Invalid fingerprint format" in error_msg:
            error_msg = "fingerprint has invalid format"
        elif "id_back" in error_msg:
            error_msg = "id_back has invalid format"
        elif "id_front" in error_msg:
            error_msg = "id_front has invalid format"
        elif "kiosk_img" in error_msg:
            error_msg = "kiosk_img has invalid format"

        raise HTTPException(status_code=422, detail=error_msg)

    hashed_customer_dict = customer_data.model_dump()
    hashed_customer_dict['pin'] = utils.hash(pin)

    try:
        new_customer = models.CustomerStaging(**hashed_customer_dict)
        db.add(new_customer)
        db.commit()
        db.refresh(new_customer)
    except IntegrityError:
        raise HTTPException(status_code=409, detail="Customer data already exists")
