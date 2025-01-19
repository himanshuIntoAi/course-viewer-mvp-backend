# cou_admin/repositories/country_repository.py
from sqlmodel import Session, select
from fastapi import HTTPException
from cou_admin.models.country import Country

def create_country(session: Session, country: Country) -> Country:
    session.add(country)
    session.commit()
    session.refresh(country)
    return country

def read_country(session: Session, country_id: int) -> Country:
    country = session.get(Country, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    return country

def read_all_countries(session: Session) -> list[Country]:
    return session.exec(select(Country)).all()

def update_country(session: Session, country_id: int, updated_data: dict) -> Country:
    country = session.get(Country, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    for key, value in updated_data.items():
        setattr(country, key, value)
    session.commit()
    session.refresh(country)
    return country


def read_country_by_name(session: Session, country_name: str) -> Country:
    """
    Fetch a country by its exact name.
    """
    country = session.exec(select(Country).where(Country.name == country_name)).first()
    if not country:
        raise HTTPException(status_code=404, detail=f"Country with name '{country_name}' not found.")
    return country


def search_countries_like(session: Session, pattern: str) -> list[Country]:
    """
    Search for countries with names matching the given SQL pattern.
    """
    countries = session.exec(select(Country).where(Country.name.like(pattern))).all()
    if not countries:
        raise HTTPException(status_code=404, detail=f"No countries found matching pattern '{pattern}'.")
    return countries.scalars().all()


def delete_country(session: Session, country_id: int) -> Country:
    country = session.get(Country, country_id)
    if not country:
        raise HTTPException(status_code=404, detail="Country not found")
    session.delete(country)
    session.commit()
    return country  # Explicitly return the deleted country
