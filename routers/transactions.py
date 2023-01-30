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


@router.get("/{card_id}", response_class=HTMLResponse)
async def read_all_by_user(
    request: Request, card_id: int, db: Session = Depends(get_db)
):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url="/auth", status_code=status.HTTP_302_FOUND)
    transactions = (
        db.query(models.Transactions)
        .filter(models.Transactions.account_id == card_id)
        .filter(models.Transactions.owner_id == user.get("id"))
        .all()
    )
    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request,
            "transactions": transactions,
            "user": user,
        },
    )
