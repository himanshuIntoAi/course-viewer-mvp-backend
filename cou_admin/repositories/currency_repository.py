from sqlmodel import Session, select
from fastapi import HTTPException
from cou_admin.models.currency import Currency

def create_currency(session: Session, currency: Currency) -> Currency:
    session.add(currency)
    session.commit()
    session.refresh(currency)
    return currency

def read_currency(session: Session, currency_id: int) -> Currency:
    currency = session.get(Currency, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    return currency

def read_all_currencies(session: Session) -> list[Currency]:
    return session.exec(select(Currency)).all()

def update_currency(session: Session, currency_id: int, updated_data: dict) -> Currency:
    currency = session.get(Currency, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    for key, value in updated_data.items():
        setattr(currency, key, value)
    
    session.commit()
    session.refresh(currency)
    return currency

def delete_currency(session: Session, currency_id: int):
    currency = session.get(Currency, currency_id)
    if not currency:
        raise HTTPException(status_code=404, detail="Currency not found")
    
    session.delete(currency)
    session.commit() 