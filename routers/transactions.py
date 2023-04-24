from datetime import datetime
import sys

sys.path.append("..")

from starlette.responses import RedirectResponse
from starlette import status
from sqlalchemy.orm import Session
from fastapi import Depends, APIRouter, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

import models
from database import engine, SessionLocal
from .auth import get_current_user


router = APIRouter()

models.Base.metadata.create_all(bind=engine)

templates = Jinja2Templates(directory="templates")


def get_db():
    try:
        db = SessionLocal()
        yield db
    finally:
        db.close()


@router.get("/card/{card_id}", response_class=HTMLResponse)
async def read_all_by_user(
    request: Request, card_id: int, db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    incomes = (
        db.query(models.Incomes)
        .filter(models.Incomes.account_id == card_id)
        .filter(models.Incomes.owner_id == user.get("id"))
        .filter(models.Incomes.is_active == True)
        .all()
    )
    expenses = (
        db.query(models.Expenses)
        .filter(models.Expenses.account_id == card_id)
        .filter(models.Expenses.owner_id == user.get("id"))
        .filter(models.Expenses.is_active == True)
        .all()
    )
    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            "incomes": incomes,
            "expenses": expenses,
            "user": user,
            "card_id": card_id
        },
    )


@router.get("/card/{card_id}/add-income", response_class=HTMLResponse)
async def add_new_income(request: Request, card_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    # importance = ['Essential', 'Have to have', 'Nice to have', 'Should not have']
    account = db.query(models.Accounts).filter(models.Accounts.id == card_id).first()
    options = (
    db.query(models.IncomeTypes)
    .filter(models.IncomeTypes.owner_id == user.get("id"))
    .all()
    )
    return templates.TemplateResponse(
        "add-income.html", {"request": request, "user": user,  "options": options,"account" : account }
    )


@router.post("/card/{card_id}/add-income", response_class=HTMLResponse)
async def create_income(request: Request, card_id: int, t_type: int= Form(...), amount: float= Form(...), description: str= Form(...), db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    # adding income 
    income_model = models.Incomes()
    income_model.amount = amount
    income_model.description = description
    income_model.is_active = True
    income_model.t_type = t_type
    income_model.created_at = datetime.now()
    income_model.modified_at = datetime.now()
    income_model.owner_id = user.get("id")
    income_model.account_id = card_id

    db.add(income_model)
    db.commit()

    return RedirectResponse(url=f"/transactions/card/{card_id}", status_code=status.HTTP_302_FOUND)
    
    

@router.get("/card/{card_id}/edit-income/{transaction_id}", response_class=HTMLResponse)
async def edit_income(request: Request, card_id: int, transaction_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    # importance = ['Essential', 'Have to have', 'Nice to have', 'Should not have']
    account = db.query(models.Accounts).filter(models.Accounts.id == card_id).first()
    options = (
    db.query(models.IncomeTypes)
    .filter(models.IncomeTypes.owner_id == user.get("id"))
    .all()
    )
    income = db.query(models.Incomes).filter(models.Incomes.account_id == card_id).filter(models.Incomes.id == transaction_id).first()
    return templates.TemplateResponse(
        "edit-income.html", {"request": request, "user": user,  "options": options,"account" : account, "income": income }
    )