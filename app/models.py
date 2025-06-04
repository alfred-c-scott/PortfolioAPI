from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import Float
from sqlalchemy import String
from sqlalchemy import Boolean
from sqlalchemy import ForeignKey
from sqlalchemy import Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql.expression import text
from sqlalchemy.sql.sqltypes import TIMESTAMP

# local
from app.database import Base


class Staff(Base):
    __tablename__ = "staff"

    id = Column(Integer, primary_key=True, nullable=False)
    first_name = Column(String, nullable=False)
    middle_name = Column(String, nullable=True)
    last_name = Column(String, nullable=False)
    username = Column(String, nullable=False, unique=True)
    email = Column(String, nullable=False, unique=True)
    phone = Column(String, nullable=False)
    is_active = Column(Boolean, server_default="TRUE", nullable=False)
    is_tech = Column(Boolean, server_default="FALSE", nullable=False)
    is_staff = Column(Boolean, server_default="FALSE", nullable=False)
    is_manager = Column(Boolean, server_default="FALSE", nullable=False)
    is_admin = Column(Boolean, server_default="FALSE", nullable=False)
    is_superuser = Column(Boolean, server_default="FALSE", nullable=False)
    password = Column(String, nullable=False)
    created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# class Location(Base):
#     __tablename__ = "locations"

#     id = Column(Integer, primary_key=True, nullable=False)
#     atws_location_id = Column(String, nullable=False, unique=True)
#     name = Column(String, nullable=False)
#     store_number = Column(String, nullable=True)
#     address1 = Column(String, nullable=False)
#     address2 = Column(String, nullable=True)
#     city = Column(String, nullable=False)
#     state = Column(String, nullable=False)
#     zip = Column(String, nullable=False)
#     phone = Column(String, nullable=False)
#     email = Column(String, nullable=False)
#     contact_name = Column(String, nullable=False)
#     contact_email = Column(String, nullable=False)
#     contact_phone = Column(String, nullable=False)
#     is_active = Column(Boolean, server_default="TRUE", nullable=False)
#     timezone = Column(String, nullable=False)
#     location_type = Column(String, nullable=True)
#     latitude = Column(Float(precision=24), nullable=False)
#     longitude = Column(Float(precision=24), nullable=False)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
#     # TODO: add store hours

#     machines = relationship("Machine", back_populates="location")


# class Machine(Base):
#     __tablename__ = "machines"

#     id = Column(Integer, primary_key=True, nullable=False)
#     # NOTE: all machines populated with password123 via database population script for developmnet- tpm, cpu, or other id for production # noqa: E501
#     # TODO: on_delete i don't want to delete the machine. i want to change the location to warehouse
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
#     password = Column(String, nullable=False)
#     manufacturer = Column(String, nullable=False)
#     model_number = Column(String, nullable=False)
#     serial_number = Column(String, nullable=False, unique=True)
#     ggv_serial_number = Column(String, nullable=False, unique=True)
#     software_version = Column(String, nullable=False)
#     commission_date = Column(TIMESTAMP(timezone=True), nullable=True)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
#     location = relationship("Location", back_populates="machines")


# class Customer(Base):
#     __tablename__ = "customers"

#     id = Column(Integer, primary_key=True, nullable=False)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
#     atws_customer_id = Column(String, nullable=False, unique=True)
#     pin = Column(String, nullable=False)
#     first_name = Column(String, nullable=False)
#     middle_name = Column(String, nullable=True)
#     last_name = Column(String, nullable=False)
#     cell_phone = Column(String, nullable=False, unique=True)
#     home_phone = Column(String, nullable=True, unique=True)
#     email = Column(String, nullable=False)
#     ssn = Column(String, nullable=True, unique=True)
#     status = Column(String, nullable=False)
#     fingerprint = Column(String, nullable=True, unique=True)
#     verified = Column(Boolean, server_default="FALSE", nullable=False)
#     verified_by = Column(String, ForeignKey("staff.username"), nullable=True)
#     verified_date = Column(TIMESTAMP(timezone=True), nullable=True)
#     # TODO: we will need a seperate table to handle an archive of updated customers and related data
#     updated_by = Column(String, ForeignKey("staff.username"), nullable=True)
#     updated_date = Column(TIMESTAMP(timezone=True), nullable=True)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# class Identity(Base):
#     __tablename__ = "identities"

#     id = Column(Integer, primary_key=True, nullable=False)
#     customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
#     current_identity = Column(Boolean, server_default="TRUE", nullable=False)
#     first_name = Column(String, nullable=False)
#     middle_name = Column(String, nullable=True)
#     last_name = Column(String, nullable=True)
#     id_type = Column(String, nullable=False)
#     id_number = Column(String, nullable=False)
#     sex = Column(String, nullable=False)
#     height = Column(String, nullable=False)
#     height_unit = Column(String, nullable=False)
#     date_of_birth = Column(String, nullable=False)
#     eye_color = Column(String, nullable=False)
#     issue_date = Column(String, nullable=False)
#     expire_date = Column(String, nullable=False)
#     address1 = Column(String, nullable=False)
#     address2 = Column(String, nullable=True)
#     city = Column(String, nullable=False)
#     state = Column(String, nullable=False)
#     zip = Column(String, nullable=False)
#     country = Column(String, nullable=False)
#     # TODO: we will change to url and add s3 bucket for production
#     id_front = Column(Text, nullable=False)
#     id_back = Column(Text, nullable=False)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# class CustomerAddress(Base):
#     __tablename__ = "customer_addresses"

#     id = Column(Integer, primary_key=True, nullable=False)
#     current_address = Column(Boolean, server_default="TRUE", nullable=False)
#     customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
#     address1 = Column(String, nullable=False)
#     address2 = Column(String, nullable=True)
#     city = Column(String, nullable=False)
#     state = Column(String, nullable=False)
#     zip = Column(String, nullable=False)
#     country = Column(String, nullable=False)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# class KioskPhoto(Base):
#     __tablename__ = "kiosk_photos"

#     id = Column(Integer, primary_key=True, nullable=False)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
#     customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
#     # TODO: we will change to url and add s3 bucket for production
#     img_jpeg = Column(Text, nullable=False)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# class CustomerStaging(Base):
#     __tablename__ = "customer_staging"

#     id = Column(Integer, primary_key=True, nullable=False)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
#     cell_phone = Column(String, nullable=False, unique=True)
#     email = Column(String, nullable=False)
#     # TODO: fingerprint will not be string in production
#     fingerprint = Column(String, nullable=True, unique=False)
#     pin = Column(String, nullable=False)
#     kiosk_img = Column(Text, nullable=True)
#     id_front = Column(Text, nullable=True)
#     id_back = Column(Text, nullable=True)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# TODO: Mark for deletion
# region
# class KioskPhotoStaging(Base):
#     __tablename__ = "kiosk_photos_staging"

#     id = Column(Integer, primary_key=True, nullable=False)
#     customer_staging_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# class IdentityStaging(Base):
#     __tablename__ = "identity_staging"

#     id = Column(Integer, primary_key=True, nullable=False)
#     customer_staging_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)

#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
# endregion


# # Will be unused until we have placements in FL
# class FloridaCompliance(Base):
#     __tablename__ = "florida_compliance"

#     id = Column(Integer, primary_key=True, nullable=False)
#     location_id = Column(Integer, ForeignKey("locations.id"), nullable=False)
#     license_number = Column(String, nullable=False)
#     username = Column(String, nullable=False)
#     password = Column(String, nullable=False)
#     email = Column(String, nullable=False)
#     is_active = Column(Boolean, server_default="TRUE", nullable=False)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# class Maker(Base):
#     __tablename__ = "makers"

#     id = Column(Integer, primary_key=True, nullable=False)
#     atws_maker_id = Column(String, nullable=False)
#     aba_number = Column(String, nullable=False)
#     account_number = Column(String, nullable=False)
#     status = Column(String, nullable=False)
#     kind = Column(String, nullable=False)
#     name = Column(String, nullable=False)
#     address1 = Column(String, nullable=True)
#     address2 = Column(String, nullable=True)
#     city = Column(String, nullable=True)
#     state = Column(String, nullable=True)
#     zip = Column(String, nullable=True)
#     phone = Column(String, nullable=True)
#     alt_phone = Column(String, nullable=True)
#     # TODO: we will need a seperate table to handle an archive of updated makers and related data
#     updated_by = Column(String, ForeignKey("staff.username"), nullable=True)
#     updated_date = Column(TIMESTAMP(timezone=True), nullable=True)
#     created_by = Column(String, ForeignKey("staff.username"), nullable=True)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))


# class Check(Base):
#     __tablename__ = "checks"

#     id = Column(Integer, primary_key=True, nullable=False)
#     maker_id = Column(Integer, ForeignKey("makers.id"), nullable=False)
#     atws_check_id = Column(String, nullable=False)
#     atws_maker_id = Column(String, nullable=False)
#     check_number = Column(String, nullable=False)
#     check_date = Column(String, nullable=False)
#     raw_micr = Column(String, nullable=False)
#     amount = Column(String, nullable=False)
#     hand_keyed = Column(Boolean, server_default="FALSE", nullable=False)
#     # postgres json
#     atws_iqa = Column(JSON, nullable=False)
#     atws_usability = Column(JSON, nullable=False)
#     payee_is_business = Column(Boolean, server_default="FALSE", nullable=False)
#     payee_name = Column(String, nullable=False)
#     # kind only if the check type is different than the maker's type
#     kind = Column(String, nullable=True)
#     img_front_jpeg_url = Column(Text, nullable=False)
#     img_back_jpeg_url = Column(Text, nullable=False)
#     img_front_tiff_url = Column(Text, nullable=False)
#     img_back_tiff_url = Column(Text, nullable=False)
#     created = Column(TIMESTAMP(timezone=True), nullable=False, server_default=text("now()"))
