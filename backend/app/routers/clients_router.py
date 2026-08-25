from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.client import Client
from app.core.utils import normalize_phone
from app.schemas.clients_schema import *


router = APIRouter(
    prefix="/clients",
    tags=["clients"],
)

@router.get("/by-phone/{phone}", response_model=ClientResponse)
def get_client_by_phone(
    phone: str,
    db: Session = Depends(get_db),
):
    phone = normalize_phone(phone)

    client = (
        db.query(Client)
        .filter(Client.phone == phone)
        .first()
    )

    if client is None:
        raise HTTPException(
            status_code=404,
            detail="Client not found",
        )

    return client


# @router.post("/")
# def create_client(
#     request: ClientCreate,
#     db: Session = Depends(get_db),
# ):
#     phone = normalize_phone(request.phone)

#     existing_client = (
#         db.query(Client)
#         .filter(Client.phone == phone)
#         .first()
#     )

#     if existing_client:
#         return {
#             "client": ClientResponse.model_validate(existing_client),
#             "is_existing": True,
#         }

#     client_obj = Client(
#         name=request.name,
#         email=request.email,
#         phone=phone,
#     )

#     db.add(client_obj)
#     db.commit()
#     db.refresh(client_obj)

#     return {
#         "client": ClientResponse.model_validate(client_obj),
#         "is_existing": False,
#     }