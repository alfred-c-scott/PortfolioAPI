import sys
import os
import json
import base64

import jwt
from sqlalchemy.orm import Session
import httpx
from httpx import HTTPStatusError

from app.database import SessionLocal
from app.config import settings

sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))
"""
This Module emulates the behavior of a device commisioning
application on a machine that is in inventory and in warehouse
"""

GGV_URL = settings.ggv_base_url

db: Session = SessionLocal()

new_customer = dict()

MACHINE_CREDENTIALS = {
    'password': 'password123'
}

bad_input = False
msg = ""


def is_integer(input):
    try:
        int(input)
        return True
    except ValueError:
        return False


def extract_jwt_data(token):
    try:
        payload = jwt.decode(token, options={"verify_signature": False})
        return payload
    except jwt.PyJWTError:
        try:
            parts = token.split('.')
            if len(parts) != 3:
                raise ValueError("Not a valid JWT token format")

            payload_bytes = base64.b64decode(parts[1] + '=' * (4 - len(parts[1]) % 4))
            payload = json.loads(payload_bytes)
            return payload
        except Exception as e:
            raise ValueError(f"Failed to decode token: {str(e)}")


print('\n----------------------------------------')
print('-----------Machine Commission-----------\n')

while True:
    machine_serial = input('Enter GGV Serial Number:\n>  ')

    MACHINE_CREDENTIALS['username'] = machine_serial

    try:
        res = httpx.post(url=f"{GGV_URL}/api/auth/machine_login",
                         data=MACHINE_CREDENTIALS)

        if res.status_code == 200:
            print('\n')
            print('   **********************************')
            print('            Login Successful         ')
            print('   **********************************\n')
            jwt_data = extract_jwt_data(res.json()['access_token'])

            if jwt_data['location_id'] != 1:
                raise Exception(f"Machine is already assigned to location: {jwt_data['location_id']}")

            headers = {"Authorization": f"Bearer {res.json()['access_token']}"}
            break
        else:
            raise HTTPStatusError(f"HTTP Error: {res.status_code}", request=res.request, response=res)

    except HTTPStatusError as e:
        print(f"HTTP status error: {e}")
        print(f"Response: {e.response.text}")

    except httpx.RequestError as e:
        print(f"Request error: {e}")

    except Exception as e:
        print(f"Unexpected error: {e}")

while True:
    print('\n----------------------------------------')
    print('-----------Search For Location----------\n')
    if bad_input:
        print('   **********************************')
        print('             Invalid Input           ')
        print('   **********************************\n')
    choice = input('Would you like to:\n\n1. Search by Name\n2. Search by ID\n\n>  ')
    is_int = is_integer(choice)
    if is_int and int(choice) in [1, 2]:
        bad_input = False
        break
    else:
        bad_input = True

locations = None
location = None

while True:
    if int(choice) == 1:
        print()
        location_name = input('Enter Location Name:\n>  ')
        params = {'name': location_name}
        try:
            res = httpx.get(url=f"{GGV_URL}/api/locations/search",
                            params=params,
                            headers=headers)

            if res.status_code == 200:
                locations = res.json()
                break
            else:
                res.raise_for_status()

        except HTTPStatusError as e:
            if e.response.status_code == 404:
                print(res.json())
            elif e.response.status_code == 400:
                print(res.json()['detail'])
                print(res.json()['status_code'])
            else:
                raise HTTPStatusError(f"HTTP Error: {e.response.status_code}"
                                      f"request=e.request, response=e.response")

        except Exception as e:
            print(f"Unexpected error: {e}")

    elif int(choice) == 2:
        location_id = input('Enter Location ID:\n>  ')
        params = {'id': location_id}
        try:
            res = httpx.get(url=f"{GGV_URL}/api/locations/search",
                            params=params,
                            headers=headers)

            if res.status_code == 200:
                location = res.json()[0]
                break
            else:
                res.raise_for_status()

        except HTTPStatusError as e:
            if e.response.status_code == 404:
                print(res.json())
            elif e.response.status_code == 400:
                print(res.json()['detail'])
                print(res.json()['status_code'])
            else:
                raise HTTPStatusError(f"HTTP Error: {e.response.status_code}", request=e.request, response=e.response)

        except Exception as e:
            print(f"Unexpected error: {e}")

bad_input = False

while True:
    if locations is not None:
        for loc in locations:
            print(f"Loc ID:   {loc['id']}\n"
                  f"Name:     {loc['name']}{' # ' + loc['store_number'] if loc['store_number'] is not None else ''}\n")

        if not bad_input:
            location_id = input("select the id of the location you\n"
                                "want the machine assigned to\n>  ")

        else:
            print('\n*************************************\n'
                  '            INVALID INPUT            \n'
                  '*************************************\n')
            location_id = input("select the id of the location you\n"
                                "want the machine assigned to\n>  ")

        if is_integer(location_id):
            if int(location_id) in [loc['id'] for loc in locations]:
                location = [loc for loc in locations if loc['id'] == int(location_id)][0]
                print()
                print(f"Location Details:\n"
                      f"    ID:         {location['id']}\n"
                      f"    Name:       {location['name']}"
                      f"{' # ' + location['store_number'] if location['store_number'] is not None else ''}\n"
                      f"    Address 1:  {location['address1']}\n"
                      f"    Address 2:  {location['address2'] if location['address2'] is not None else ''}\n"
                      f"    City:       {location['city']}\n"
                      f"    State:      {location['state']}\n"
                      f"    Zip:        {location['zip']}\n")
                input(f"Press Enter to assign machine: {machine_serial} to this location:\n")
                break
            else:
                bad_input = True
                print(f"Invalid Location ID: {location_id}\n")
        else:
            bad_input = True

if location is not None:
    res = httpx.put(url=f"{GGV_URL}/api/machines/{location['id']}",
                    headers=headers)

    print(res.json())
    print(res.status_code)
