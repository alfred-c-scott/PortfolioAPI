'''
This module emulates the behavior of a staff member with is_manager permissions
the is_manager staff member will log into the Gigavend web application to create
a new location in practice
'''

import json
import sys

import httpx
from httpx import HTTPStatusError
from httpx import BasicAuth
from httpx import RequestError

from app.config import settings
from app.schemas import (
    ATWSLocation,
    ATWSGeoData,
    GGVLocationCreate
)

GGV_BASE_URL = settings.ggv_base_url
ATWS_BASE_URL = settings.atws_base_url
ATWS_API_KEY = settings.atws_api_key
ATWS_BUSINESS_ID = settings.atws_business_id

MACHINE_CREDENTIALS = {
    'username': '123456799',
    'password': 'password123'
}

atws_auth = BasicAuth(username=ATWS_API_KEY, password='')

# the default geo data will be sent for the ATWS location only
# for the gigavend/ggv locations table we will store the location
atws_geo_data = ATWSGeoData(
    latitude=0.00000,
    longitude=0.00000
)


def is_integer(input):
    try:
        int(input)
        return True
    except ValueError:
        return False


def validate_geo_data(input_str):
    try:
        float_value = float(input_str)  # noqa: F841

        parts = input_str.split('.')
        if len(parts) != 2:
            return False

        decimal_part = parts[1]
        return len(decimal_part) >= 6

    except ValueError:
        return False

print('\n----------------------------------------')
print('-----------Authenticate Machine----------\n')

input('Press ENTER to Authenticate Machine\n')

res = httpx.post(url=f"{GGV_BASE_URL}/api/auth/machine_login",
                 data=MACHINE_CREDENTIALS)

print(f"\nstatus: {res.status_code}")

if res.status_code == 200:
    token = res.json()['access_token']
    print(token, end='\n\n')

headers = {"Authorization": f"Bearer {token}"}


print(f"status: {res.status_code}")
print(f"body:\n{json.dumps(res.json(), indent=4)}")

print('\n----------------------------------------')
print('-------------Create Location------------\n')

input('Press ENTER to continue\n')

print('\n----------------------------------------')
print('----------Enter Business Details---------\n')

name = input('Business Name:\n> ')
store_number = input('\nStore Number:\n> ')
address1 = input('\nAddress 1:\n> ')
address2 = input('\nAddress 2: (Blank if none)\n> ')
if address2 == '':
    address2 = None
city = input('\nCity:\n> ')
state = input('\nState:\n> ')
zip = input('\nZip Code:\n> ')
phone = input('\nPhone:\n> ')
email = input('\nEmail:\n> ')
contact_name = input('\nContact Name:\n> ')
contact_phone = input('\nContact Phone:\n> ')
contact_email = input('\nContact Email:\n> ')

while True:
    choice = input('\nLocation Type:\n'
                   '   1  Convenience\n'
                   '   2  Grocery\n'
                   '   3  Pharmacy\n'
                   '   4  Liquor\n'
                   '   5  Other\n\n> ')
    if is_integer(choice) and 1 <= int(choice) <= 5:
        if choice == '1':
            location_type = 'Convenience'
            break
        elif choice == '2':
            location_type = 'Grocery'
            break
        elif choice == '3':
            location_type = 'Pharmacy'
            break
        elif choice == '4':
            location_type = 'Liquor'
            break
        elif choice == '5':
            location_type = 'Other'
            break
    else:
        print()
        print('***************************')
        print('Invalid Input. Please enter\n'
              'an integer:  1, 2, 3, 4, or 5\n')

while True:
    choice = input('\nActive: (0 = False, 1 = True)\n> ')
    if is_integer(choice) and 0 <= int(choice) <= 1:
        if choice == '0':
            active = False
        elif choice == '1':
            active = True
        break
    else:
        print()
        print('***************************')
        print('Invalid Input. Please enter\n'
              '0 for False or 1 for True\n')

while True:
    choice = input('\nTimezone:\n'
                   '   1  America/New_York\n'
                   '   2  America/Chicago\n'
                   '   3  America/Denver\n'
                   '   4  America/Los_Angeles\n\n> ')
    if is_integer(choice) and 1 <= int(choice) <= 4:
        if choice == '1':
            timezone = 'America/New_York'
        elif choice == '2':
            timezone = 'America/Chicago'
        elif choice == '3':
            timezone = 'America/Denver'
        elif choice == '4':
            timezone = 'America/Los_Angeles'
        break
    else:
        print()
        print('***************************')
        print('Invalid Input. Please enter\n'
              'an integer:  1, 2, 3, or 4')

while True:
    choice = input('\nLatitude: (6 decimal places)\n> ')
    if validate_geo_data(choice):
        latitude = float(choice)
        break
    else:
        print()
        print('***************************')
        print('Invalid Input. Please enter\n'
              'a number with six decimals\n'
              'of precision')

while True:
    choice = input('\nLongitude: (6 decimal places)\n> ')
    if validate_geo_data(choice):
        longitude = float(choice)
        break
    else:
        print()
        print('***************************')
        print('Invalid Input. Please enter\n'
              'a number with six decimals\n'
              'of precision')

notes = '[]'

try:
    atws_geo_data = ATWSGeoData(
        latitude=0.0,
        longitude=0.0
    )
except Exception as e:
    print(f"Error: {e}")

try:
    atws_location = ATWSLocation(
        business_id=ATWS_BUSINESS_ID,
        name=f"{name} {'#'+store_number if store_number else ''}",
        address1=address1,
        address2=address2,
        city=city,
        state=state,
        zip=zip,
        phone=phone,
        email=email,
        contact_name=contact_name,
        contact_phone=contact_phone,
        contact_email=contact_email,
        active=active,
        timezone=timezone,
        florida_compliance_settings=None,
        geo_data=atws_geo_data,
        notes="[]"
    )
except Exception as e:
    print(f"Error: {e}")

try:
    res = httpx.post(url=f"{ATWS_BASE_URL}/locations",
                     json=atws_location.model_dump(exclude_none=True),
                     auth=atws_auth)
    if res.status_code != 201:
        raise HTTPStatusError
    atws_location_id = res.json()['id']
    print(f"atws_location_id: {atws_location_id}" )
    print(json.dumps(res.json(), indent=4))
except HTTPStatusError as e:
    print(f"HTTPStatusError: {e.response.status_code}")
    sys.exit(1)
except RequestError as e:
    print(f"Request Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected Error: {e}")
    sys.exit(1)

if timezone == 'America/New_York':
    timezone = 'ET'
elif timezone == 'America/Chicago':
    timezone = 'CT'
elif timezone == 'America/Denver':
    timezone = 'MT'
elif timezone == 'America/Los_Angeles':
    timezone = 'PT'

try:
    ggv_location = GGVLocationCreate(
        atws_location_id=atws_location_id,
        name=name,
        address1=address1,
        city=city,
        state=state,
        zip=zip,
        phone=phone,
        email=email,
        contact_name=contact_name,
        contact_phone=contact_phone,
        contact_email=contact_email,
        is_active=active,
        timezone=timezone,
        location_type=location_type,
        latitude=latitude,
        longitude=longitude
    )
except Exception as e:
    print(f"Error: {e}")
    sys.exit(1)

try:
    res = httpx.post(url=f"{GGV_BASE_URL}/api/locations",
                     json=ggv_location.model_dump(exclude_none=True),
                     headers=headers)

    if res.status_code != 201:
        raise HTTPStatusError
    print(json.dumps(res.json(), indent=4))
except HTTPStatusError as e:
    print(f"HTTPStatusError: {e.response.status_code}")
    sys.exit(1)
except RequestError as e:
    print(f"Request Error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"Unexpected Error: {e}")
    sys.exit(1)

print

input('\nPress ENTER to end\n')
