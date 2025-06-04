import string
import json
import random


# installed
from sqlalchemy.orm import Session
import requests
from requests.auth import HTTPBasicAuth
from sqlalchemy.exc import IntegrityError
from psycopg2.errors import UniqueViolation


# local
from app.models import Staff
# from app.models import Location
# from app.models import Machine
# from app.models import Customer
from app.database import SessionLocal
from app.utils import hash
from app.config import settings


def generate_random_string(length=16):
    characters = string.ascii_uppercase + string.digits
    random_string = ''.join(random.choice(characters) for _ in range(length))
    return random_string


# def transform_customer(atws_customers):
    customers = list()
    db = SessionLocal()
    locations = db.query(Location).all()

    for customer in atws_customers:
        location = random.choice(locations)
        customer = Customer(
            location_id=location.id,
            atws_customer_id=customer.get('id'),
            pin=hash('0000'),
            first_name=customer.get('first_name'),
            middle_name=customer.get('middle_name'),
            last_name=customer.get('last_name'),
            cell_phone=customer.get('cell_phone'),
            home_phone=customer.get('home_phone'),
            email=customer.get('first_name') + "." + customer.get('last_name') + str(random.randint(0, 1000)) + "@gigavend.com",
            ssn=random.randint(100000000, 999999999),
            status=customer.get('status'),
            fingerprint=generate_random_string()
        )
        customers.append(customer)

    return customers


def generate_test_staff():
    staff_entries = []
    password = hash("password123")
    alfred = Staff(
        first_name="Alfred",
        middle_name="C",
        last_name="Scott",
        username="alfred",
        email="alfred@gigavend.com",
        phone="8594336773",
        is_active=True,
        is_staff=True,
        is_tech=True,
        is_manager=True,
        is_admin=True,
        is_superuser=True,
        password=password
    )
    staff_entries.append(alfred)
    password = hash("password123")

    gary = Staff(
        first_name="Gary",
        middle_name="D",
        last_name="Houck",
        username="gary",
        email="gary@gigavend.com",
        phone="8595555555",
        is_active=True,
        is_staff=True,
        is_tech=True,
        is_manager=True,
        is_admin=True,
        is_superuser=True,
        password=password
    )
    staff_entries.append(gary)

    return staff_entries


# def get_locations():
#     locations = list()
#     warehouse1 = Location(
#         atws_location_id="1",
#         name="Warehouse 1",
#         address1="401 E Fifth St",
#         address2="",
#         city="Lexington",
#         state="KY",
#         zip="40508",
#         phone="8594336773",
#         email="dev@gigavend.com",
#         contact_name="Dev",
#         contact_email="dev@gigavend.com",
#         contact_phone="8594336773",
#         is_active=False,
#         timezone="EST",
#         location_type="warehouse",
#         latitude="38.0479591",
#         longitude="-84.4831798"
#     )
#     locations.append(warehouse1)

#     return locations


# def get_machines():
    machines = list()
    base_serial = 123456789  # Starting serial number
    for i in range(10):
        serial_number = str(base_serial + i)  # Increment serial number
        ggv_serial_number = str(base_serial + i * 10)  # Increment ggv_serial_number differently
        machine = Machine(
            location_id=1,
            password=hash('password123'),  # Assuming hash() is defined elsewhere
            manufacturer="GenMega",
            model_number="K1",
            serial_number=serial_number,
            ggv_serial_number=ggv_serial_number,
            software_version="1.0.0",
        )
        machines.append(machine)

    return machines


# def get_customers():
#     atws_customers = json.load(open('dev/customers.json', 'r'))

#     return transform_customer(atws_customers)


def populate_staff():
    db: Session = SessionLocal()
    staff_entries = generate_test_staff()
    for staff_entry in staff_entries:
        try:
            db.add(staff_entry)
            db.commit()
            print("\n-------------Test Staff Added-------------\n")
        except IntegrityError as e:
            db.rollback()
            if isinstance(e.orig, UniqueViolation):
                error_msg = e.orig.pgerror.split('\n')
                for i, line in enumerate(error_msg):
                    if line.startswith("ERROR:") or line.startswith("DETAIL:"):
                        print(line.strip())
                        if line.startswith("DETAIL:") and i < len(error_msg) - 1:
                            print()
            else:
                print(f"Other IntegrityError: {str(e)}")
        except Exception as e:
            db.rollback()
            print(f"Unexpected Error: {str(e)}")
    db.close()


# def populate_locations():
#     db: Session = SessionLocal()
#     locations = get_locations()
#     for location in locations:
#         try:
#             db.add(location)
#             db.commit()
#             print("\n-----------Test Location Added-----------\n")
#         except IntegrityError as e:
#             db.rollback()
#             if isinstance(e.orig, UniqueViolation):
#                 error_msg = e.orig.pgerror.split('\n')
#                 for line in error_msg:
#                     if line.startswith("ERROR:") or line.startswith("DETAIL:"):
#                         print(line.strip())
#                 print()
#             else:
#                 print(f"Other IntegrityError: {str(e)}")
#         except Exception as e:
#             db.rollback()
#             print(f"Unexpected Error: {str(e)}")
#     db.close()


# def populate_machines():
#     db: Session = SessionLocal()
#     machines = get_machines()
#     for machine in machines:
#         try:
#             db.add(machine)
#             db.commit()
#             print("\n-----------Test Machine Added------------\n")
#         except IntegrityError as e:
#             db.rollback()
#             if isinstance(e.orig, UniqueViolation):
#                 error_msg = e.orig.pgerror.split('\n')
#                 for line in error_msg:
#                     if line.startswith("ERROR:") or line.startswith("DETAIL:"):
#                         print(line.strip())
#                 print()
#             else:
#                 print(f"Other IntegrityError: {str(e)}")
#         except Exception as e:
#             db.rollback()
#             print(f"Unexpected Error: {str(e)}")
#     db.close()


# def populate_customers():
#     db: Session = SessionLocal()
#     customers = get_customers()
#     for customer in customers:
#         try:
#             db.add(customer)
#             db.commit()
#             print("\n-----------Test Customer Added------------\n")
#         except IntegrityError as e:
#             db.rollback()
#             if isinstance(e.orig, UniqueViolation):
#                 error_msg = e.orig.pgerror.split('\n')
#                 for line in error_msg:
#                     if line.startswith("ERROR:") or line.startswith("DETAIL:"):
#                         print(line.strip())
#                 print()
#             else:
#                 print(f"Other IntegrityError: {str(e)}")


if __name__ == "__main__":
    populate_staff()
    # populate_locations()
    # populate_machines()
    # populate_customers()
