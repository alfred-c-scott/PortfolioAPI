import json
import httpx
import sys
import os

from app.config import settings
from dev.modules.utils import fake_id

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

GGV_URL = settings.ggv_base_url

new_customer = dict()

MACHINE_CREDENTIALS = {
    'username': '123456799',
    'password': 'password123'
}

print('\n-------Sign Up--------------------------\n')

input('Press Any Key to Authorize Machine')

res = httpx.post(url=f"{GGV_URL}/api/auth/machine_login",
                 data=MACHINE_CREDENTIALS)

print(f"\nstatus: {res.status_code}")

if res.status_code == 200:
    token = res.json()['access_token']
    print(token, end='\n\n')

headers = {"Authorization": f"Bearer {token}"}

print('\n-------Enter Contact Info---------------\n')

while True:
    new_customer['phone'] = input('Enter Phone Number:\n> ')
    new_customer['email'] = input('Enter Email:\n> ')

    res = httpx.post(url=f"{GGV_URL}/api/customer/phone/send_code",
                     json={"phone": new_customer['phone'], "email": new_customer['email']},
                     headers=headers)

    if res.status_code == 200:
        break

print(f"status: {res.status_code}")
print(f"body:\n{json.dumps(res.json(), indent=4)}")
print(f"\nVerification code sent to {new_customer['phone']}\n")

print('\n-------Enter Code-----------------------\n')

while True:
    code = input('Enter Code:\n> ')

    res = httpx.post(url=f"{GGV_URL}/api/customer/phone/verify_code",
                     json={"phone": new_customer['phone'], "code": code},
                     headers=headers)

    print(f"status: {res.status_code}")
    print(f"body:\n{json.dumps(res.json(), indent=4)}")

    if res.status_code == 200:
        break

while True:
    print('\n-------Choose PIN-----------------------\n')

    new_customer['pin'] = input('Enter PIN:\n> ')
    pin = input('Confirm PIN:\n> ')

    if new_customer['pin'] != pin:
        print('\nPINs do not match')
    else:
        break

print('\n-------Take Kiosk Photo-----------------\n')

input('Press Any Key to continue\n')

print('\n-------Enroll Fingerprint---------------\n')

input('Press Any Key to continue\n')

new_customer['fingerprint'] = 'KS4KK27LEK7D86SKE7D7'

print('\n-------Scan ID Card---------------------\n')

input('Press Any Key to continue\n')

fake_id.generate()

print('\n-------Create Customer------------------\n')

try:
    files = {
        'kiosk_img': ('kiosk_photo.jpeg', open('dev/images/kiosk/kiosk_photo.jpeg', 'rb'), 'image/jpeg'),
        'id_front': ('fake_dl_front.jpeg', open('dev/images/id_card/jpeg/fake_dl_front.jpeg', 'rb'), 'image/jpeg'),
        'id_back': ('fake_dl_back.jpeg', open('dev/images/id_card/jpeg/fake_dl_back.jpeg', 'rb'), 'image/jpeg')
    }
    res = httpx.post(url=f"{GGV_URL}/api/customer",
                     data=new_customer,
                     files=files,
                     headers=headers)

except FileNotFoundError as e:
    print(f"Error: File not found - {e}")
    exit(1)
finally:
    for file in files.values():
        file[1].close()

print(f"status: {res.status_code}")
print(f"body:\n{json.dumps(res.json(), indent=4)}")

print('\n-------Sign Up Complete-----------------\n')
