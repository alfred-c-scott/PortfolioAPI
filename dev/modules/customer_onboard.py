import sys
import io
import base64


from sqlalchemy.orm import Session
from PIL import Image
import httpx
from httpx import BasicAuth

from app import models
from app.database import SessionLocal
from app.schemas import ATWSIdImage
from app.schemas import ATWSAddress
from app.schemas import ATWSCustomerImage
from app.schemas import ATWSCustomerIdentification
from app.schemas import ATWSCustomer
from app.config import settings
from app.s3_config import s3_client
from app.s3_config import bucket_name
from app.routers.api.helpers import azure

db: Session = SessionLocal()

atws_auth = BasicAuth(
    username=settings.atws_api_key,
    password=''
)

print('\n----------------------------------------')
print('------------Customer Onboard------------\n')

input('Press Any Key to continue\n')

staged_customers = db.query(models.CustomerStaging).all()
print(f"Number of Staged Customers: {len(staged_customers)}\n\n")

print('\n----------------------------------------')
print('-----------Process ID Barcode-----------\n')

input('Press Any Key to continue\n\n')

first_in_queue = db.query(models.CustomerStaging).order_by(models.CustomerStaging.created).first()

if first_in_queue is not None:
    try:
        # get id back from s3 bucket
        res = s3_client.get_object(Bucket=bucket_name, Key=first_in_queue.id_back)
        image_content = res['Body'].read()
        image = Image.open(io.BytesIO(image_content))
        buffered = io.BytesIO()
        image.save(buffered, format=image.format)
        image_bytes = buffered.getvalue()
        id_back_base64 = base64.b64encode(image_bytes).decode('utf-8')

    except Exception as e:
        print(f"Error processing id back from S3: {e}")

    try:
        # get id front from s3 bucket
        res = s3_client.get_object(Bucket=bucket_name, Key=first_in_queue.id_front)
        image_content = res['Body'].read()
        image = Image.open(io.BytesIO(image_content))
        buffered = io.BytesIO()
        image.save(buffered, format=image.format)
        image_bytes = buffered.getvalue()
        id_front_base64 = base64.b64encode(image_bytes).decode('utf-8')

    except Exception as e:
        print(f"Error processing id front from S3: {e}")

    try:
        # get kiosk image from s3 bucket
        res = s3_client.get_object(Bucket=bucket_name, Key=first_in_queue.kiosk_img)
        image_content = res['Body'].read()
        image = Image.open(io.BytesIO(image_content))
        buffered = io.BytesIO()
        image.save(buffered, format=image.format)
        image_bytes = buffered.getvalue()
        kiosk_img_base64 = base64.b64encode(image_bytes).decode('utf-8')

    except Exception as e:
        print(f"Error processing kiosk image from S3: {e}")

    try:
        # azure pdf417 barcode processing
        barcode_value = azure.analyze_id_barcodes(id_back_base64)
        pdf417_data = azure.parse_barcode_data(barcode_value)

    except Exception as e:
        print(f"Error processing barcode: {e}")

else:
    print("System Exit: No customers in queue\n")
    sys.exit(1)

print('\n----------------------------------------')
print('--------Compare ID Data to Image--------\n')

input('Press Any Key to continue\n')
print(f"first           :  {pdf417_data['first_name']}")
print(f"middle          :  {pdf417_data['middle_name']}")
print(f"last            :  {pdf417_data['last_name']}")
print(f"id_type         :  {pdf417_data['id_type']}")
print(f"id_num          :  {pdf417_data['id_number']}")
print(f"sex             :  {pdf417_data['sex']}")
print(f"height          :  {pdf417_data['height']}")
print(f"height_units    :  {pdf417_data['height_units']}")
print(f"eye_color       :  {pdf417_data['eye_color']}")
print(f"date_of_birth   :  {pdf417_data['date_of_birth']}")
print(f"issue_date      :  {pdf417_data['issue_date']}")
print(f"expire_date     :  {pdf417_data['expiration_date']}")
print(f"address         :  {pdf417_data['address1']}")
print(f"city            :  {pdf417_data['city']}")
print(f"state           :  {pdf417_data['state']}")
print(f"zip             :  {pdf417_data['zip']}")
print(f"country         :  {pdf417_data['country']}\n")

print('\n----------------------------------------')
print('-----------Edit Customer Data-----------\n')

print('  ---------------------------------')
print('  |  Demo Module does not support  |')
print('  |      editing customer data     |')
print('  ---------------------------------\n')
input('Press Any Key to continue\n')

print('\n----------------------------------------')
print("--------Build ATWS Customer Payload-------\n")
try:
    id_front = ATWSIdImage(
        image=id_front_base64,
    )
except Exception as e:
    print(f"Error processing id front: {e}")

try:
    id_back = ATWSIdImage(
        image=id_back_base64,
    )
except Exception as e:
    print(f"Error processing id back: {e}")

try:
    customer_identification = ATWSCustomerIdentification(
        id_type=pdf417_data['id_type'],
        id_number=pdf417_data['id_number'],
        issuer=pdf417_data['state'],
        expiration_date=pdf417_data['expiration_date'],
        front_image=id_front,
        back_image=id_back
    )
except Exception as e:
    print(f"Error processing customer identification: {e}")

try:
    address = ATWSAddress(
        address1=pdf417_data['address1'],
        city=pdf417_data['city'],
        state=pdf417_data['state'],
        zip=pdf417_data['zip']
    )
except Exception as e:
    print(f"Error processing customer address: {e}")

try:
    customer_image = ATWSCustomerImage(
        image=kiosk_img_base64,
        date=first_in_queue.created.strftime('%Y-%m-%d')
    )
except Exception as e:
    print(f"Error processing kiosk image: {e}")

location = db.query(models.Location).filter(models.Location.id == first_in_queue.location_id).first()
print(f"atws_location_id: {location.atws_location_id}")
input('CTRL+C to exit\n')

try:
    atws_customer = ATWSCustomer(
        location_id=location.atws_location_id,
        first_name=pdf417_data['first_name'],
        middle_name=pdf417_data['middle_name'],
        last_name=pdf417_data['last_name'],
        date_of_birth=pdf417_data['date_of_birth'],
        gender=pdf417_data['sex'],
        address=address,
        cell_phone=first_in_queue.cell_phone,
        customer_identification=customer_identification,
        customer_image=customer_image,
    )
except Exception as e:
    print(f"Error building ATWSCustomer payload: {e}")

input('Press Any Key to continue\n')

try:
    res = httpx.post(url=f"{settings.atws_base_url}/customers",
                     json=atws_customer.model_dump(exclude_none=True),
                     auth=atws_auth)
    if res.status_code == 201:
        print(f"status_code: {res.status_code} - created")
        atws_customer_id = res.json()['id']
except Exception as e:
    print(f"Error processing request: {e}")


print(f"atws_customer_id: {atws_customer_id}")
print('\n----------------------------------------')
print('------------Sign Up Complete------------\n')
