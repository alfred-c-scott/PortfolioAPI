from fastapi import status
from fastapi import HTTPException
from fastapi import Depends
from fastapi import APIRouter
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

from app import models
from app import schemas
from app import oauth2

from app.database import get_db
from app import utils

router = APIRouter(
    prefix="/api/auth",
    tags=["API Authentication"],
)


@router.post('/machine_login', status_code=status.HTTP_200_OK, response_model=schemas.MachineToken)
async def machine_login(machine_credentials: OAuth2PasswordRequestForm = Depends(),
                        db: Session = Depends(get_db)):

    machine = db.query(models.Machine).filter(
        models.Machine.ggv_serial_number == machine_credentials.username).first()

    if not machine:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="invalid credentials")

    if not utils.verify(machine_credentials.password, machine.password):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,
                            detail="invalid credentials")

    data = schemas.MachineTokenData.model_validate(machine).model_dump()

    access_token = oauth2.create_api_token(data=data)

    return {'access_token': access_token, 'token_type': 'bearer'}
