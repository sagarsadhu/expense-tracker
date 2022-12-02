import sys

sys.path.append("..")

from starlette.responses import RedirectResponse
from starlette import status

from fastapi import Depends, HTTPException, APIRouter, Request, Form
import models
from database import engine, SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user

from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

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
    cards = db.query(models.Cards).filter(models.Cards.owner_id == user.get('id')).all()
    return templates.TemplateResponse('index.html', {'request': request, 'cards': cards, 'user': user})


@router.get('/add-card', response_class=HTMLResponse)
async def add_new_card(request: Request):
    user = await get_current_user(request)
    if user is None:
        return RedirectResponse(url='/auth', status_code=status.HTTP_302_FOUND)
    return templates.TemplateResponse('add-card.html', {'request': request, 'user': user})
