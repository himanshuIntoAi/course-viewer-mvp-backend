from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session
from common.database import get_session
from cou_admin.models.country import Country
from cou_admin.repositories.country_repository import (
    create_country,
    read_country,
    read_all_countries,
    update_country,
    delete_country,
    read_country_by_name,
    search_countries_like
)
from cou_admin.schemas.country_schema import CountryCreate, CountryRead, CountryUpdate
from datetime import datetime, timezone

router = APIRouter(
    prefix="/countries",
    tags=["Countries"]
)

@router.post("/", response_model=CountryRead, summary="Create a new country", description="Adds a new country to the database.")
def add_country(country_data: CountryCreate, session: Session = Depends(get_session)):
    """
    Endpoint to create a new country record.
    """
    country = Country(
        name=country_data.name,
        created_by=country_data.created_by,
        updated_by=country_data.created_by,  # Initially same as created_by
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
        active=True
    )
    return create_country(session, country)

@router.get("/{country_id}", response_model=CountryRead, summary="Get country details by ID", description="Fetches the details of a country by its ID.")
def get_country(country_id: int, session: Session = Depends(get_session)):
    """
    Endpoint to fetch details of a specific country using its ID.
    """
    return read_country(session, country_id)

@router.get("/name/{country_name}", response_model=CountryRead, summary="Get country by name", description="Fetches the details of a country by its exact name.")
def get_country_by_name(country_name: str, session: Session = Depends(get_session)):
    """
    Endpoint to fetch details of a specific country using its exact name.
    """
    return read_country_by_name(session, country_name)

@router.get("/search/", response_model=list[CountryRead], summary="Search countries by name pattern", description="Searches for countries with names matching a given pattern.")
def search_countries(
    query: Optional[str] = None,
    starts_with: Optional[str] = None,
    ends_with: Optional[str] = None,
    session: Session = Depends(get_session)
):
    """
    Endpoint to search for countries with names matching a given pattern.
    Allows filtering by 'query' (anywhere), 'starts_with', and 'ends_with'.
    """
    if query:
        return search_countries_like(session, f"%{query}%")
    elif starts_with:
        return search_countries_like(session, f"{starts_with}%")
    elif ends_with:
        return search_countries_like(session, f"%{ends_with}")
    else:
        raise HTTPException(status_code=400, detail="At least one filter parameter (query, starts_with, or ends_with) must be provided.")

@router.get("/", response_model=list[CountryRead], summary="Get all countries", description="Fetches a list of all countries.")
def get_all_countries(session: Session = Depends(get_session)):
    """
    Endpoint to fetch all country records.
    """
    return read_all_countries(session)

@router.put("/{country_id}", response_model=CountryRead, summary="Update a country", description="Updates an existing country's details.")
def modify_country(
    country_id: int, 
    country_data: CountryUpdate,
    session: Session = Depends(get_session)
):
    """
    Endpoint to update the details of an existing country.
    """
    update_dict = country_data.dict(exclude_unset=True)
    update_dict["updated_at"] = datetime.now(timezone.utc)
    
    return update_country(session, country_id, update_dict)

@router.delete("/{country_id}", summary="Delete a country", description="Removes a country from the database.")
def remove_country(country_id: int, session: Session = Depends(get_session)):
    """
    Endpoint to delete a specific country by its ID.
    """
    delete_country(session, country_id)
    return {"message": f"Country with ID {country_id} has been deleted successfully."}
