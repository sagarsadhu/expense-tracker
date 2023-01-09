from fastapi import FastAPI, status
from starlette.staticfiles import StaticFiles
from starlette.responses import RedirectResponse

import models
from database import engine
from routers import account_types, auth, cards

app = FastAPI()

models.Base.metadata.create_all(bind=engine)

app.mount("/static", StaticFiles(directory='static'), name='static')

@app.get("/")
async def root():
    return RedirectResponse(url='/cards', status_code=status.HTTP_302_FOUND)

app.include_router(
    account_types.router,
    prefix='/account-types',
    tags=['account-types'],
    responses={404: {"description": "Not found"}}
)
app.include_router(
    auth.router,
    prefix="/auth",
    tags=['auth'],
    responses={401: {'user': 'Not Authorized'}}
)
app.include_router(
    cards.router,
    prefix='/cards',
    tags=['cards'],
    responses={404: {"description": "Not found"}}
)