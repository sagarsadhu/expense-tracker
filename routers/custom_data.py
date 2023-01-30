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


@router.get("/{cd_type}", response_class=HTMLResponse)
async def read_all_by_user(
    request: Request, cd_type: str, db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    custom_data = {}
    if cd_type == "account-type":
        custom_data = (
            db.query(models.AccountTypes)
            .filter(models.AccountTypes.owner_id == user.get("id"))
            .all()
        )
    elif cd_type == "income-type":
        custom_data = (
            db.query(models.IncomeTypes)
            .filter(models.IncomeTypes.owner_id == user.get("id"))
            .all()
        )
    elif cd_type == "expense-type":
        custom_data = (
            db.query(models.ExpenseTypes)
            .filter(models.ExpenseTypes.owner_id == user.get("id"))
            .all()
        )
    return templates.TemplateResponse(
        "custom-data.html",
        {
            "request": request,
            "custom_data": custom_data,
            "cd_type": cd_type,
            "user": user,
        },
    )


@router.get("/add-custom-data/{cd_type}", response_class=HTMLResponse)
async def add_new_custom_data(request: Request, cd_type: str):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse(
        "add-custom-data.html", {"request": request, "cd_type": cd_type, "user": user}
    )


@router.post("/add-custom-data/{cd_type}", response_class=HTMLResponse)
async def create_custom_data(
    request: Request,
    cd_type: str,
    name: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    if cd_type == "account-type":
        custom_data_model = models.AccountTypes()
    elif cd_type == "income-type":
        custom_data_model = models.IncomeTypes()
    elif cd_type == "expense-type":
        custom_data_model = models.ExpenseTypes()

    custom_data_model.name = name
    custom_data_model.description = description
    custom_data_model.owner_id = user.get("id")

    db.add(custom_data_model)
    db.commit()

    return RedirectResponse(
        url=f"/custom-data/{cd_type}", status_code=status.HTTP_302_FOUND
    )


@router.get("/edit-custom-data/{cd_type}/{cd_id}", response_class=HTMLResponse)
async def add_new_card(
    request: Request,
    cd_type: str,
    cd_id: int,
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    cd_model = {}
    if cd_type == "account-type":
        cd_model = (
            db.query(models.AccountTypes)
            .filter(models.AccountTypes.id == cd_id)
            .first()
        )
    elif cd_type == "income-type":
        cd_model = (
            db.query(models.IncomeTypes).filter(models.IncomeTypes.id == cd_id).first()
        )
    elif cd_type == "expense-type":
        cd_model = (
            db.query(models.ExpenseTypes)
            .filter(models.ExpenseTypes.id == cd_id)
            .first()
        )

    return templates.TemplateResponse(
        "edit-custom-data.html",
        {"request": request, "custom_data": cd_model, "cd_type": cd_type, "user": user},
    )


@router.post("/edit-custom-data/{cd_type}/{cd_id}", response_class=HTMLResponse)
async def edit_card_commit(
    request: Request,
    cd_type: str,
    cd_id: int,
    name: str = Form(...),
    description: str = Form(...),
    db: Session = Depends(get_db),
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    if cd_type == "account-type":
        cd_model = (
            db.query(models.AccountTypes)
            .filter(models.AccountTypes.id == cd_id)
            .first()
        )
    elif cd_type == "income-type":
        cd_model = (
            db.query(models.IncomeTypes).filter(models.IncomeTypes.id == cd_id).first()
        )
    elif cd_type == "expense-type":
        cd_model = (
            db.query(models.ExpenseTypes)
            .filter(models.ExpenseTypes.id == cd_id)
            .first()
        )

    cd_model.name = name
    cd_model.description = description

    db.add(cd_model)
    db.commit()

    return RedirectResponse(
        url=f"/custom-data/{cd_type}", status_code=status.HTTP_302_FOUND
    )


@router.get("/delete/{cd_type}/{cd_id}")
async def delete_card(
    request: Request, cd_type: str, cd_id: int, db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)

    if cd_type == "account-type":
        cd_model = models.AccountTypes
    elif cd_type == "income-type":
        cd_model = models.IncomeTypes
    elif cd_type == "expense-type":
        cd_model = models.ExpenseTypes

    cd_check_model = (
        db.query(cd_model)
        .filter(cd_model.id == cd_id)
        .filter(cd_model.owner_id == user.get("id"))
        .first()
    )

    if cd_check_model is None:
        return RedirectResponse(url="/cards", status_code=status.HTTP_302_FOUND)

    db.query(cd_model).filter(cd_model.id == cd_id).delete()

    db.commit()

    return RedirectResponse(
        url=f"/custom-data/{cd_type}", status_code=status.HTTP_302_FOUND
    )
