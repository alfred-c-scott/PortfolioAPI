import re
from datetime import datetime
from typing import Optional


# installed
from pydantic import BaseModel
from pydantic import EmailStr
from pydantic import field_validator
from fastapi import UploadFile


class CustomerVerifyPhoneEmail(BaseModel):
    phone: str
    email: EmailStr

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^[0-9]{10}$', v):
            raise ValueError('phone number must be exactly 10 digits')
        return v


class CustomerVerifyPhoneCode(BaseModel):
    phone: str
    code: str

    @field_validator('phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^[0-9]{10}$', v):
            raise ValueError('Phone number must be exactly 10 digits')
        return v

    @field_validator('code')
    @classmethod
    def validate_pin(cls, v):
        if not re.match(r'^\d{6}$', v):
            raise ValueError('PIN must be 4 digits')
        return v


class CustomerStagingFiles(BaseModel):
    model_config = {
        "arbitrary_types_allowed": True
    }

    kiosk_img: UploadFile
    id_front: UploadFile
    id_back: UploadFile

    @field_validator('kiosk_img')
    @classmethod
    def validate_kiosk_img(cls, file: UploadFile):
        return cls._validate_image(file, "kiosk image")

    @field_validator('id_front')
    @classmethod
    def validate_id_front(cls, file: UploadFile):
        return cls._validate_image(file, "ID front image")

    @field_validator('id_back')
    @classmethod
    def validate_id_back(cls, file: UploadFile):
        return cls._validate_image(file, "ID back image")

    @classmethod
    def _validate_image(cls, file: UploadFile, file_type: str):
        ALLOWED_EXTENSIONS = ['.jpeg', '.jpg']
        ALLOWED_MIME_TYPES = ['image/jpeg']
        MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB limit

        if not file:
            raise ValueError(f"Missing {file_type}")

        filename = file.filename.lower()

        if not any(filename.endswith(ext) for ext in ALLOWED_EXTENSIONS):
            raise ValueError(f"Invalid file extension for {file_type}. Allowed: {ALLOWED_EXTENSIONS}")

        if file.content_type not in ALLOWED_MIME_TYPES:
            raise ValueError(f"Invalid MIME type for {file_type}. Allowed: {ALLOWED_MIME_TYPES}")

        try:
            file.file.seek(0, 2)
            size = file.file.tell()
            file.file.seek(0)

            if size > MAX_FILE_SIZE:
                raise ValueError(f"{file_type} exceeds maximum size of {MAX_FILE_SIZE / (1024 * 1024)}MB")
        except Exception as e:
            raise ValueError(f"Error checking file size: {str(e)}")

        return file


class CustomerStaging(BaseModel):
    location_id: int
    cell_phone: str
    email: EmailStr
    pin: str
    fingerprint: str
    kiosk_img: str
    id_front: str
    id_back: str

    @field_validator('location_id')
    @classmethod
    def validate_location_id(cls, v):
        if not isinstance(v, int):
            raise ValueError('location_id must be an integer')
        return v

    @field_validator('cell_phone')
    @classmethod
    def validate_phone(cls, v):
        if not re.match(r'^[0-9]{10}$', v):
            raise ValueError('Phone number must be exactly 10 digits')
        return v

    @field_validator('pin')
    @classmethod
    def validate_pin(cls, v):
        if not re.match(r'^\d{4}$', v):
            raise ValueError('PIN must be 4 digits')
        return v

    # TODO: will be binary data in prod
    @field_validator('fingerprint')
    @classmethod
    def validate_fingerprint(cls, v):
        if not re.match(r'^[A-Z0-9]{20}$', v):
            raise ValueError('Invalid fingerprint format')
        return v

    @field_validator('kiosk_img')
    @classmethod
    def validate_kiosk_img(cls, v):
        if "kiosk" not in v:
            raise ValueError("Invalid file name for kiosk_img")
        return v

    @field_validator('id_front')
    @classmethod
    def validate_id_front(cls, v):
        if "front" not in v:
            raise ValueError("Invalid file name for id_front")
        return v

    @field_validator('id_back')
    @classmethod
    def validate_id_back(cls, v):
        if "back" not in v:
            raise ValueError("Invalid file name for id_back")
        return v


class ATWSGeoData(BaseModel):
    latitude: float
    longitude: float

    @field_validator('latitude', mode='before')
    @classmethod
    def validate_latitude(cls, v):
        # not sending location data to ATWS, must be 0
        if v != 0.0:
            raise ValueError("ATWS latitude must be 0.0")
        if not isinstance(v, (int, float)):
            raise TypeError("Latitude must be a number")
        return float(v)

    @field_validator('longitude', mode='before')
    @classmethod
    def validate_longitude(cls, v):
        # not sending location data to ATWS, must be 0
        if v != 0.0:
            raise ValueError("ATWS longitude must be 0.0")
        if not isinstance(v, (int, float)):
            raise TypeError("Longitude must be a number")
        return float(v)


class ATWSLocation(BaseModel):
    # ATWS swagger says the id field is optional
    # but after testing it's required ????
    id: str = ''
    business_id: str
    name: str
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    zip: str
    phone: str
    email: str
    contact_name: str
    contact_phone: str
    contact_email: str
    active: bool
    timezone: str
    # ALL_TRUST: clarify purpose of guarantee
    # guarantee: Optional[str]
    geo_data: Optional[ATWSGeoData]
    notes: str = None

    @field_validator('phone', 'contact_phone')
    @classmethod
    def validate_phone_number(cls, v):
        # Check if the value is a string of 10 digits only
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Phone number must be 10 digits with no special characters - 1234567890')
        return v

    @field_validator('state')
    @classmethod
    def validate_state(cls, v):
        states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        if len(v) != 2:
            raise ValueError('State code must be 2 characters')
        if v.upper() not in states:
            raise ValueError('Invalid state code')
        if v.upper() != v:
            raise ValueError('State code must be uppercase')
        return v

    @field_validator('zip')
    @classmethod
    def validate_zip(cls, v):
        if not re.match(r'^\d{5}$', v):
            raise ValueError('Zip code must be 5 digits')
        return v

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v):
        timezones = [
            "America/New_York",
            "America/Chicago",
            "America/Denver",
            "America/Los_Angele"
        ]
        if v not in timezones:
            raise ValueError('Invalid timezone - must be one of the following: "America/New_York", "America/Chicago", "America/Denver", "America/Los_Angeles"')
        return v

    # TODO: validate Timezone


class GGVLocationCreate(BaseModel):
    atws_location_id: str
    name: str
    store_number: Optional[str] = None
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    zip: str
    phone: str
    email: EmailStr
    contact_name: str
    contact_phone: str
    contact_email: EmailStr
    is_active: bool
    timezone: str
    location_type: Optional[str] = None
    latitude: float
    longitude: float

    @field_validator('phone', 'contact_phone')
    @classmethod
    def validate_phone_number(cls, v):
        # Check if the value is a string of 10 digits only
        if not re.match(r'^\d{10}$', v):
            raise ValueError('Phone number must be 10 digits with no special characters - 1234567890')
        return v

    @field_validator('state')
    @classmethod
    def validate_state(cls, v):
        states = [
            'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
            'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
            'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
            'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
            'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY'
        ]
        if len(v) != 2:
            raise ValueError('State code must be 2 characters')
        if v.upper() not in states:
            raise ValueError('Invalid state code')
        if v.upper() != v:
            raise ValueError('State code must be uppercase')
        return v

    @field_validator('zip')
    @classmethod
    def validate_zip(cls, v):
        if not re.match(r'^\d{5}$', v):
            raise ValueError('Zip code must be 5 digits')
        return v

    @field_validator('latitude', mode='before')
    @classmethod
    def validate_latitude(cls, v):
        if not -90.0 <= v <= 90.0:
            raise ValueError("ATWS latitude must be between -90.0 and 90.0")
        if not isinstance(v, (int, float)):
            raise TypeError("Latitude must be a number")
        return float(v)

    @field_validator('longitude', mode='before')
    @classmethod
    def validate_longitude(cls, v):
        if not -180.0 <= v <= 180.0:
            raise ValueError("ATWS longitude must be between -180.0 and 180.0")
        if not isinstance(v, (int, float)):
            raise TypeError("Longitude must be a number")
        return float(v)

    @field_validator('timezone')
    @classmethod
    def validate_timezone(cls, v):
        timezones = [
            "ET",
            "CT",
            "MT",
            "PT"
        ]
        if v not in timezones:
            raise ValueError('Invalid timezone - must be one of the following: "ET", "CT", "MT", "PT"')
        return v

    @field_validator('location_type')
    @classmethod
    def validate_location_type(cls, v):
        location_types = [
            "Convenience",
            "Grocery",
            "Pharmacy",
            "Liquor",
            "Other"
        ]
        if v not in location_types:
            raise ValueError('Invalid location type - must be one of the following: "Convenience", "Grocery", "Pharmacy", "Liquor", "Other"')
        return v


class GGVLocationResponse(BaseModel):
    id: int
    atws_location_id: str
    name: str
    store_number: Optional[str] = None
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    zip: str
    phone: str
    email: EmailStr
    contact_name: str
    contact_phone: str
    contact_email: EmailStr
    is_active: bool
    timezone: str
    location_type: Optional[str] = None
    latitude: float
    longitude: float


class ATWSIdImage(BaseModel):
    image_type: str = "jpeg"
    image: str


class ATWSAddress(BaseModel):
    address1: str
    address2: Optional[str] = None
    city: str
    state: str
    zip: str


class ATWSCustomerIdentification(BaseModel):
    id_type: str
    id_number: str
    issuer: str
    expiration_date: str
    front_image: ATWSIdImage
    back_image: ATWSIdImage


class ATWSCustomerImage(BaseModel):
    image_type: str = "jpeg"
    image: str
    date: str


class ATWSCustomer(BaseModel):
    location_id: str
    first_name: str
    middle_name: Optional[str] = None
    last_name: str
    date_of_birth: str
    gender: str
    address: ATWSAddress
    cell_phone: str
    status: str = "neutral"
    rec_marketing_messages: bool = False
    customer_identification: ATWSCustomerIdentification
    customer_image: ATWSCustomerImage
    notes: str = "[]"
    no_duplicate_check: bool = False
    # allowed values are 'mobile', 'kiosk', and 'webapp', defaults to 'webapp',
    captured: str = "kiosk"


class StaffResponse(BaseModel):
    id: int
    first_name: str
    middle_name: str
    last_name: str
    username: str
    email: str
    is_active: bool
    is_staff: bool
    is_manager: bool
    is_superuser: bool
    created: datetime


class StaffCreate(BaseModel):
    first_name: str
    middle_name: str
    last_name: str
    username: str
    password: str
    email: EmailStr
    is_active: bool
    is_staff: bool
    is_manager: bool
    is_superuser: bool


class StaffTokenData(BaseModel):
    model_config = {
        "from_attributes": True
    }
    id: int
    first_name: str
    last_name: str
    is_active: bool
    is_staff: bool
    is_manager: bool
    is_superuser: bool


class LocationSearch(BaseModel):
    name: Optional[str] = None
    id: Optional[int] = None


# class MachineCreate(BaseModel):
#     location_id: int
#     manufacturer: str
#     model_number: str
#     serial_number: str
#     ggv_serial_number: str
#     sdk_version: Optional[str] = None
#     software_version: str


class MachineAssign(BaseModel):
    location_id: int


class MachineTokenData(BaseModel):
    model_config = {
        "from_attributes": True
    }
    id: int
    location_id: int
    ggv_serial_number: str


class MachineToken(BaseModel):
    access_token: str
    token_type: str


class MachineUpdatePassword(BaseModel):
    ggv_serial_number: str
    current_password: str
    new_password: str
