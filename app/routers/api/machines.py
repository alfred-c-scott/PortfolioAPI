from fastapi import status
from fastapi import HTTPException
from fastapi import Depends
from fastapi import APIRouter
from sqlalchemy.orm import Session

from app import models
from app import oauth2
from app.database import get_db


router = APIRouter(
    prefix="/api/machines",
    tags=["Machines"],
)


@router.post('', status_code=status.HTTP_201_CREATED)
async def create_machine(db: Session = Depends(get_db)):
    return {'msg': 'route verified'}


@router.put('/{location_id}', status_code=status.HTTP_201_CREATED)
async def assign_machine(location_id: int,
                         db: Session = Depends(get_db),
                         machine: int = Depends(oauth2.current_machine)):

    machine_query = db.query(models.Machine).filter(models.Machine.id == machine['id'])
    db_machine = machine_query.first()

    if not db_machine:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"no machine found for id: {machine['id']}")

    location_query = db.query(models.Location).filter(models.Location.id == location_id)
    db_location = location_query.first()

    if not db_location:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail=f"no location found for id: {location_id}")

    machine_query.update({'location_id': location_id}, synchronize_session=False)
    db.commit()
    db.refresh(db_machine)

    return {'msg': 'route verified'}


@router.put('/decommission/{id}', status_code=status.HTTP_201_CREATED)
async def decommision_machine(id: int, db: Session = Depends(get_db)):
    return {'msg': 'route verified'}
