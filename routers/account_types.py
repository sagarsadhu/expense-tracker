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
    account_types = db.query(models.AccountTypes).filter(models.AccountTypes.owner_id == user.get("id")).all()
    return templates.TemplateResponse(
        "account_types.html", {"request": request, "account_types": account_types, "user": user}
    )


@router.get("/add-account-type", response_class=HTMLResponse)
async def add_new_card(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse("add-account-type.html", {"request": request, "user": user})


@router.post("/add-account-type", response_class=HTMLResponse)
async def create_card(
    request: Request,
    name: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    account_type_model = models.AccountTypes()
    account_type_model.name = name
    account_type_model.description = description
    account_type_model.owner_id = user.get("id")

    db.add(account_type_model)
    db.commit()

    return RedirectResponse(url="/account-types", status_code=status.HTTP_302_FOUND)


@router.get("/edit-account-type/{account_type_id}", response_class=HTMLResponse)
async def add_new_card(request: Request, account_type_id: int, db: Session = Depends(get_db), ):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    account_type_model = db.query(models.AccountTypes).filter(models.AccountTypes.id == account_type_id).first()
    return templates.TemplateResponse("edit-account-type.html", {"request": request, "account_type": account_type_model, "user": user})


@router.post("/edit-account-type/{account_type_id}", response_class=HTMLResponse)
async def edit_card_commit(
    request: Request,
    account_type_id: int,
    name: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    account_type_model = db.query(models.AccountTypes).filter(models.AccountTypes.id == account_type_id).first()

    account_type_model.name = name
    account_type_model.description = description

    db.add(account_type_model)
    db.commit()

    return RedirectResponse(url="/account-types", status_code=status.HTTP_302_FOUND)


@router.get("/delete/{account_type_id}")
async def delete_card(request: Request, account_type_id: int, db: Session = Depends(get_db)):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    account_type_model = (
        db.query(models.AccountTypes)
        .filter(models.AccountTypes.id == account_type_id)
        .filter(models.AccountTypes.owner_id == user.get("id"))
        .first()
    )

    if account_type_model is None:
        return RedirectResponse(url="/cards", status_code=status.HTTP_302_FOUND)

    db.query(models.AccountTypes).filter(models.AccountTypes.id == account_type_id).delete()

    db.commit()

    return RedirectResponse(url="/account-types", status_code=status.HTTP_302_FOUND)