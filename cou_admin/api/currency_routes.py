from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from common.database import get_session
from cou_admin.models.currency import Currency
from cou_admin.repositories.currency_repository import (
    create_currency,
    read_currency,
    read_all_currencies,
    update_currency,
    delete_currency,
)
from cou_admin.schemas.currency_schema import CurrencyCreate, CurrencyRead, CurrencyUpdate
from datetime import datetime, timezone

router = APIRouter(
    prefix="/currencies",
    tags=["Currencies"]
)

@router.post("/", response_model=CurrencyRead, summary="Create a new currency", description="Adds a new currency to the database.")
def add_currency(currency_data: CurrencyCreate, session: Session = Depends(get_session)):
    """
    Endpoint to create a new currency record.
    """
    # Create a Currency instance with default values for required fields
    currency = Currency(
        name=currency_data.name,
        symbol=currency_data.symbol,
        country_id=currency_data.country_id,
        created_by=currency_data.created_by,
        updated_by=currency_data.created_by,  # Initially same as created_by
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        active=True
    )
    return create_currency(session, currency)

@router.get("/{currency_id}", response_model=CurrencyRead, summary="Get currency details by ID", description="Fetches the details of a currency by its ID.")
def get_currency(currency_id: int, session: Session = Depends(get_session)):
    """
    Endpoint to fetch details of a specific currency using its ID.
    """
    return read_currency(session, currency_id)

@router.get("/", response_model=list[CurrencyRead], summary="Get all currencies", description="Fetches a list of all currencies.")
def get_all_currencies(session: Session = Depends(get_session)):
    """
    Endpoint to fetch all currency records.
    """
    return read_all_currencies(session)

@router.put("/{currency_id}", response_model=CurrencyRead, summary="Update currency details", description="Updates an existing currency's details.")
def modify_currency(
    currency_id: int, 
    currency_data: CurrencyUpdate, 
    session: Session = Depends(get_session)
):
    """
    Endpoint to update the details of an existing currency.
    """
    # Convert the currency_data to a dictionary and add updated_at
    update_dict = currency_data.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.now(timezone.utc)
    
    return update_currency(session, currency_id, update_dict)

@router.delete("/{currency_id}", summary="Delete a currency", description="Removes a currency from the database.")
def remove_currency(currency_id: int, session: Session = Depends(get_session)):
    """
    Endpoint to delete a specific currency by its ID.
    """
    delete_currency(session, currency_id)
    return {"message": f"Currency with ID {currency_id} has been deleted successfully."} 