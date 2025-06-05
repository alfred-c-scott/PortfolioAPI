from datetime import datetime
from datetime import timedelta


# installed
from fastapi import Depends
from fastapi import HTTPException
from fastapi.requests import Request
from fastapi import status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt
from jose import JWTError


# local
from .config import settings

# TODO - not needed delete in future
oauth2_scheme = OAuth2PasswordBearer(tokenUrl='api/auth/login')
# web_oauth2_scheme = OAuth2PasswordBearer(tokenUrl='web/auth/login')


SECRET_KEY = settings.oauth2_secret_key
ALGORITHM = settings.oauth2_algorithm
API_EXPIRE_MINUTES = settings.oauth2_api_expire
WEB_EXPIRE_MINUTES = settings.oauth2_web_expire


def create_api_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=API_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except jwt.JWTError as e:
        # TODO Log error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating access token: {str(e)}"
        )

    return encoded_jwt


def verify_access_token(token: str, credentials_exception):
    try:
        token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

    except JWTError:
        # TODO Log error
        raise credentials_exception

    return token_data


def current_machine(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    token_data = verify_access_token(token, credentials_exception)

    return token_data
# region Unused permissions for api
# def verify_token(token: str, to_verify: dict):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     not_staff_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="User is not staff",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     not_manager_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="User is not manager",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     not_superuser_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="User is not superuser",
#         headers={"WWW-Authenticate": "Bearer"},
#     )
#     not_active_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="User is not active",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     if to_verify == 'staff':
#         try:
#             token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             if not token_data['is_staff']:
#                 raise not_staff_exception
#         except JWTError:
#             raise credentials_exception

#     if to_verify == 'manager':
#         try:
#             token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             if not token_data['is_manager']:
#                 raise not_manager_exception
#         except JWTError:
#             raise credentials_exception

#     if to_verify == 'superuser':
#         try:
#             token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#             if not token_data['is_superuser']:
#                 raise not_superuser_exception
#         except JWTError:
#             raise credentials_exception

#     try:
#         token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         if not token_data['is_active']:
#             raise not_active_exception
#     except JWTError:
#         raise credentials_exception

#     return token_data


# def is_staff(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):

#     tor_verify: str = 'staff'

#     token_data = verify_token(token=token, to_verify=tor_verify)

#     staff = db.query(models.Staff).filter(models.Staff.id == token_data['id']).first()

#     return staff


# def is_manager(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):

#     tor_verify: str = 'manager'

#     token_data = verify_token(token=token, to_verify=tor_verify)

#     staff = db.query(models.Staff).filter(models.Staff.id == token_data['id']).first()

#     return staff


# def is_superuser(token: str = Depends(oauth2_scheme), db: Session = Depends(database.get_db)):

#     tor_verify: str = 'superuser'

#     token_data = verify_token(token=token, to_verify=tor_verify)

#     staff = db.query(models.Staff).filter(models.Staff.id == token_data['id']).first()

#     return staff
# endregion


def create_web_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=WEB_EXPIRE_MINUTES)
    to_encode.update({'exp': expire})
    try:
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    except jwt.JWTError as e:
        # TODO Log error
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating access token: {str(e)}"
        )

    return encoded_jwt


def verify_web_token(token: str, to_verify: str):
    try:
        token_data = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])

        if not token_data.get('is_active', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not active"
            )
        if to_verify == 'staff' and not token_data.get('is_staff', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not staff"
            )
        elif to_verify == 'manager' and not token_data.get('is_manager', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not manager"
            )
        elif to_verify == 'superuser' and not token_data.get('is_superuser', False):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User is not superuser"
            )

        # Just return token data - middleware handles token refresh
        return token_data

    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials"
        )


def web_staff(request: Request):
    token = request.cookies.get("access_token")

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token_data = verify_web_token(token=token, to_verify='staff')
    return token_data


def web_manager(request: Request):
    token = request.cookies.get("access_token")

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token_data = verify_web_token(token=token, to_verify='manager')
    return token_data


def web_superuser(request: Request):
    token = request.cookies.get("access_token")

    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated"
        )

    token_data = verify_web_token(token=token, to_verify='superuser')
    return token_data