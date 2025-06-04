from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def hash(password: str):
    return pwd_context.hash(password)


def verify(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


def convert_timezone(tz_input):
    timezone_map = {
        "America/New_York": "EST",
        "America/Chicago": "CST",
        "America/Denver": "MST",
        "America/Los_Angeles": "PST"
    }
    try:
        return timezone_map[tz_input]
    except KeyError as e:
        print(f"Error: {e}")


def transform_location(api_response):
    transformed = {
        "atws_location_id": api_response["id"],
        "name": api_response["name"],
        "address1": api_response["address1"],
        "address2": api_response.get("address2"),
        "city": api_response["city"],
        "state": api_response["state"],
        "zip": api_response["zip"],
        "phone": api_response["phone"],
        "email": api_response["email"],
        "contact_name": api_response["contact_name"],
        "contact_phone": api_response["contact_phone"],
        "contact_email": api_response["contact_email"],
        "is_active": api_response["active"],
        "timezone": convert_timezone(api_response["timezone"]),
        "latitude": str(api_response["geo_data"]["latitude"]),
        "longitude": str(api_response["geo_data"]["longitude"])
    }

    return transformed
