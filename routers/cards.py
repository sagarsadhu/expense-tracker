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


@router.get("/", response_class=HTMLResponse)
async def read_all_by_user(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    cards = (
        db.query(models.Accounts)
        .filter(models.Accounts.owner_id == user.get("id"))
        .all()
    )
    return templates.TemplateResponse(
        "cards.html", {"request": request, "cards": cards, "user": user}
    )


@router.get("/add-card", response_class=HTMLResponse)
async def add_new_card(request: Request, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    cardtypes = db.query(models.AccountTypes).all()
    return templates.TemplateResponse(
        "add-card.html", {"request": request, "user": user, "cardtypes": cardtypes}
    )


@router.post("/add-card", response_class=HTMLResponse)
async def create_card(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    card_type: int = Form(...),
    balance: float = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    card_model = models.Accounts()
    card_model.name = name
    card_model.description = description
    card_model.card_type = card_type
    card_model.balance = balance
    card_model.created_at = datetime.now()
    card_model.owner_id = user.get("id")

    db.add(card_model)
    db.commit()

    return RedirectResponse(url="/cards", status_code=status.HTTP_302_FOUND)


@router.get("/edit-card/{card_id}", response_class=HTMLResponse)
async def edit_card(request: Request, card_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    cardtypes = db.query(models.AccountTypes).all()
    card = db.query(models.Accounts).filter(models.Accounts.id == card_id).first()
    return templates.TemplateResponse(
        "edit-card.html",
        {"request": request, "card": card, "cardtypes": cardtypes, "user": user},
    )


@router.post("/edit-card/{card_id}", response_class=HTMLResponse)
async def edit_card_commit(
    request: Request,
    card_id: int,
    name: str = Form(...),
    description: str = Form(...),
    card_type: int = Form(...),
    balance: float = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    card_model = db.query(models.Accounts).filter(models.Accounts.id == card_id).first()

    card_model.name = name
    card_model.description = description
    card_model.card_type = card_type
    card_model.balance = balance

    db.add(card_model)
    db.commit()

    return RedirectResponse(url="/cards", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{card_id}")
async def delete_card(request: Request, card_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    card_model = (
        db.query(models.Accounts)
        .filter(models.Accounts.id == card_id)
        .filter(models.Accounts.owner_id == user.get("id"))
        .first()
    )

    if card_model is None:
        return RedirectResponse(url="/cards", status_code=status.HTTP_302_FOUND)

    db.query(models.Accounts).filter(models.Accounts.id == card_id).delete()

    db.commit()

    return RedirectResponse(url="/cards", status_code=status.HTTP_302_FOUND)
