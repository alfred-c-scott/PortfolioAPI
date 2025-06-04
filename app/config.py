from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    model_config = {
        "env_file": ".env"
    }

    db_hostname: str
    db_port: str
    db_password: str
    db_name: str
    db_username: str
    oauth2_secret_key: str
    oauth2_algorithm: str
    oauth2_api_expire: int
    oauth2_web_expire: int
    ggv_base_url: str
    # atws_business_id: str
    # atws_location_id: str
    # atws_base_url: str
    # atws_api_key: str
    azure_key_1: str
    azure_key_2: str
    azure_region: str
    azure_endpoint: str
    twilio_account_sid: str
    twilio_auth_token: str
    # twilio_phone_number: str
    twilio_verify_service_sid: str
    s3_endpoint: str
    s3_access_key: str
    s3_secret_key: str


settings = Settings()
