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
        .all()
    )
    expenses = (
        db.query(models.Expenses)
        .filter(models.Expenses.account_id == card_id)
        .filter(models.Expenses.owner_id == user.get("id"))
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


@router.get("/card/{card_id}/add-transaction/{t_type}", response_class=HTMLResponse)
async def add_new_transaction(request: Request, card_id: int, t_type: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    importance = ['Essential', 'Have to have', 'Nice to have', 'Should not have']
    account = db.query(models.Accounts).filter(models.Accounts.id == card_id).first()
    if t_type == 1:
        options = (
        db.query(models.IncomeTypes)
        .filter(models.IncomeTypes.owner_id == user.get("id"))
        .all()
        )
    else:
        options = (
        db.query(models.ExpenseTypes)
        .filter(models.ExpenseTypes.owner_id == user.get("id"))
        .all()
        )
    return templates.TemplateResponse(
        "add-transaction.html", {"request": request, "user": user, "importance": importance, "options": options, "t_type" : t_type, "account" : account}
    )


@router.post("/card/{card_id}/add-transaction/{t_type}", response_class=HTMLResponse)
async def create_new_transaction(request: Request, card_id: int, t_type: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    
    

