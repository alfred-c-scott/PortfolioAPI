
from fastapi import status
from fastapi import HTTPException
from fastapi import Depends
from fastapi import APIRouter
from typing import List
from sqlalchemy.orm import Session

from app import models
from app import schemas
from app import oauth2
from app.database import get_db


router = APIRouter(
    prefix="/api/locations",
    tags=["Locations"],
)


# There is no validation or authentication on this endpoint because
# it is being used for testing only, will be deprecated and not be
# used in production.
@router.post('', status_code=status.HTTP_201_CREATED, response_model=schemas.GGVLocationResponse)
async def create_location(location: schemas.GGVLocationCreate,
                          db: Session = Depends(get_db),
                          machine: int = Depends(oauth2.current_machine)):

    new_location = models.Location(**location.model_dump())

    db.add(new_location)
    db.commit()
    db.refresh(new_location)

    return new_location


@router.get('/search', status_code=status.HTTP_200_OK, response_model=List[schemas.GGVLocationResponse])
async def search_for_location(db: Session = Depends(get_db),
                              params: schemas.LocationSearch = Depends(),
                              machine: int = Depends(oauth2.current_machine)):

    if params.name:
        locations = db.query(models.Location).filter(models.Location.name.ilike(f"%{params.name}%")).all()
        if locations:
            return locations
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"no locations found for name: {params.name}")

    elif params.id:
        # opted for a query of all machines here because the response_model schema is a list
        location = db.query(models.Location).filter(models.Location.id == params.id).first()
        if location:
            location_list = [location]
            return location_list
        else:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                detail=f"no locations found for id: {params.id}")

    raise HTTPException(
        status_code=status.HTTP_400_BAD_REQUEST,
        detail="No search parameters provided in request"
    )


@router.put('/{id}', status_code=status.HTTP_201_CREATED)
async def update_location(id: int, db: Session = Depends(get_db)):
    return {'msg': 'route verified'}


# TODO limit to superuser and manager
@router.put('/deactivate/{id}', status_code=status.HTTP_201_CREATED)
async def deactivate_location(id: int, db: Session = Depends(get_db)):
    return {'msg': 'route verified'}
