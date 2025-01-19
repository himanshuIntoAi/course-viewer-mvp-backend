from typing import Optional
from fastapi import APIRouter, Depends
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

router = APIRouter(
    prefix="/countries",
    tags=["Countries"]
)

@router.post("/", response_model=Country, summary="Create a new country", description="Adds a new country to the database.")
def add_country(country: Country, session: Session = Depends(get_session)):
    """
    Endpoint to create a new country record.
    """
    return create_country(session, country)


@router.get("/{country_id}", response_model=Country, summary="Get country details by ID", description="Fetches the details of a country by its ID.")
def get_country(country_id: int, session: Session = Depends(get_session)):
    """
    Endpoint to fetch details of a specific country using its ID.
    """
    return read_country(session, country_id)

@router.get("/name/{country_name}", response_model=Country, summary="Get country by name", description="Fetches the details of a country by its exact name.")
def get_country_by_name(country_name: str, session: Session = Depends(get_session)):
    """
    Endpoint to fetch details of a specific country using its exact name.
    """
    return read_country_by_name(session, country_name)


@router.get("/search/", response_model=list[Country], summary="Search countries by name pattern", description="Searches for countries with names matching a given pattern.")
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


@router.get("/", response_model=list[Country], summary="Get all countries", description="Fetches a list of all countries.")
def get_all_countries(session: Session = Depends(get_session)):
    """
    Endpoint to fetch all country records.
    """
    return read_all_countries(session)


@router.put("/{country_id}", response_model=Country, summary="Update a country", description="Updates an existing country's details.")
def modify_country(country_id: int, updated_data: dict, session: Session = Depends(get_session)):
    """
    Endpoint to update the details of an existing country.
    """
    return update_country(session, country_id, updated_data)


@router.delete("/{country_id}", summary="Delete a country", description="Removes a country from the database.")
def remove_country(country_id: int, session: Session = Depends(get_session)):
    """
    Endpoint to delete a specific country by its ID.
    """
    delete_country(session, country_id)
    return {"message": f"Country with ID {country_id} has been deleted successfully."}
