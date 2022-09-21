from datetime import timedelta
from http.client import HTTPException
from io import BytesIO
import mimetypes
import shutil
from fastapi import FastAPI, Request, Depends, status, Form, Response, Path, Depends, UploadFile, File, WebSocket, WebSocketDisconnect
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
from starlette.status import HTTP_400_BAD_REQUEST
from db import SessionLocal, engine, DBContext
import models, crud, schemas
from sqlalchemy.orm import Session
from fastapi_login import LoginManager
from dotenv import load_dotenv
import os
from typing import List
from passlib.context import CryptContext
from fastapi.responses import RedirectResponse
from fastapi.security import OAuth2PasswordRequestForm
from schemas import UploadImageForm
from fastapi.responses import HTMLResponse
import uuid
from pathlib import Path
import time

load_dotenv()
SECRET_KEY = os.getenv('SECRET_KEY')
ACCESS_TOKEN_EXPIRE_MINUTES=60

manager = LoginManager(SECRET_KEY, token_url="/", use_cookie=True)
manager.cookie_name = "auth"

pwd_ctx = CryptContext(schemes=["bcrypt"], deprecated="auto")


work_dir = 'static/uploads/'

app = FastAPI()

templates = Jinja2Templates(directory="templates")
app.mount("/static", StaticFiles(directory="static"), name="static")


# Make directory if uploads is not exists
if not os.path.exists(work_dir):
        # recursively create workdir/unique_id
    os.makedirs(work_dir)

def get_db():
    with DBContext() as db:
        yield db

def get_hashed_password(plain_password):
    return pwd_ctx.hash(plain_password)

def verify_password(plain_password, hashed_password):
    return pwd_ctx.verify(plain_password,hashed_password)

@manager.user_loader()
def get_user(username: str, db: Session = None):
    if db is None:
        with DBContext() as db:
            return crud.get_user_by_username(db=db,username=username)
    return crud.get_user_by_username(db=db,username=username)

def authenticate_user(username: str, password: str, db: Session = Depends(get_db)):
    user = crud.get_user_by_username(db=db,username=username)
    if not user:
        return None
    if not verify_password(plain_password=password,hashed_password=user.hashed_password):
        return None
    return user

class NotAuthenticatedException(Exception):
    pass

def not_authenticated_exception_handler(request, exception):
    
    return RedirectResponse("/")

manager.not_authenticated_exception = NotAuthenticatedException
app.add_exception_handler(NotAuthenticatedException, not_authenticated_exception_handler)



@app.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    return templates.TemplateResponse("dashboard.html", {"request": request, 
    "title": "Dashboard", 
    "user": user})

    
@app.get("/")
def get_login(request: Request):
    start = time.time()
    end = time.time()
    time_cal = round(end-start)
    print(time_cal)
    return templates.TemplateResponse("login.html", {"request": request, "title": "Login", "time": time_cal})

@app.post("/")
def login(request: Request, form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    start = time.time()
    user = authenticate_user(username=form_data.username,password=form_data.password,db=db)
    if not user:
        return templates.TemplateResponse("login.html", {"request": request,
        "title": "Login",
        "invalid": True}, status_code=status.HTTP_401_UNAUTHORIZED)
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = manager.create_access_token(
        data={"sub": user.username},
        expires=access_token_expires
    )
    resp = RedirectResponse("/dashboard", status_code=status.HTTP_302_FOUND)
    manager.set_cookie(resp,access_token)

    end = time.time()
    time_cal = round(end-start)
    print(time_cal)
    print('It took {} seconds to finish login function execution.'.format(round(end-start)))
    return resp

@app.get("/register")
def get_register(request: Request):
    return templates.TemplateResponse("register.html", {"request": request, "title": "Register"})

@app.post("/register")
def register(request: Request,
username: str = Form(...),
email: str = Form(...),
name: str = Form(...),
password: str = Form(...),
db: Session = Depends(get_db)):
    hashed_password = get_hashed_password(password)
    invalid = False
    if crud.get_user_by_username(db=db,username=username):
        invalid = True
    if crud.get_user_by_email(db=db,email=email):
        invalid = True
    
    if not invalid:
        crud.create_user(db=db, user=schemas.UserCreate(username=username,email=email,name=name,hashed_password=hashed_password))
        response = RedirectResponse("/login", status_code=status.HTTP_302_FOUND)
        return response
    else:
        return templates.TemplateResponse("register.html",{"request": request, "title": "Register", "invalid": True},
        status_code=HTTP_400_BAD_REQUEST)

@app.get("/logout")
def logout(response: Response):
    response = RedirectResponse("/")
    manager.set_cookie(response,None)
    return response


@app.post('/dashboard', response_class=HTMLResponse)
async def upload(request: Request, file: UploadFile = File(..., media_type="image/png"), db: Session = Depends(get_db), user: schemas.User = Depends(manager)):
    start = time.time()
    
    if file.content_type =="image/png":
       
        try:

            with open("static/uploads/"+file.filename, 'wb') as buffer:
                shutil.copyfileobj(file.file, buffer)
            url = str("static/uploads/"+file.filename)
            print("saved at", url )
            from PIL import Image
            image = Image.open(url)
            image.thumbnail((100,90))
            thumb_io = BytesIO()
            imgtype = "PNG"
            thumbnail_make_filepath = url.strip('.png')
            # print(imgtype)
            image.save(thumbnail_make_filepath + "_thumbnail"+".png")
            display_thumbnail =str(thumbnail_make_filepath + "_thumbnail"+".png")

            end = time.time()
            time_cal = round(end-start)
            print(time_cal)
            print('It took {} seconds to finish Upload image function execution.'.format(round(end-start)))

        except Exception:
            return {"message": "There was an error uploading the file"}
        finally:
            file.file.close()

     
        return templates.TemplateResponse("dashboard.html", {"request": request, "filepath":file.filename, "thumbnail":display_thumbnail, "imagefile":url, "time":time_cal, "user": user})

    if file.content_type!="image/png":
        print("Invalid file")

        return templates.TemplateResponse("dashboard.html", {"request": request,"image_invalid": True, "user": user})


@app.post('/dashboard', response_class=HTMLResponse)
async def gan_process(request: Request, file: bytes = File()):

    start = time.time()
    file = "test.png" # this is a fixed image for the dummy function
    print(len(file)) 
    filepath_url = 'static/uploads/test.png'
    end = time.time()
    time_cal = {}.format(round(end-start))
    print(time_cal)
    print('It took {} seconds to finish GAN processing function execution.'.format(round(end-start)))

    return filepath_url

@app.post('/dashboard')
async def generate_3d_model(file: bytes = File()):

    file = "/static/akshay kumar.glb" # this is a fixed image for the dummy function

    return file


@app.websocket("/ws")
async def send_data(websocket:WebSocket):
    print('CONNECTING...')
    await websocket.accept()

    try:
        # send "Connection established" message to client
        await websocket.send_text("Connection established!")

        while True:
            print('CONNECTION OPEN')
            try:
                await websocket.receive_text()
                resp = {
                "message":"message from websocket"
                }
                await websocket.send_json(resp)
            except Exception as e:
                print(e)
                print("CONNECTION DEAD...")
                break
            #print("CONNECTION DEAD...")

    except WebSocketDisconnect:
        print("Client disconnected")


@app.get("/logs")
async def get(request: Request) -> templates.TemplateResponse:
    """Log file viewer

    Args:
        request (Request): Default web request.

    Returns:
        TemplateResponse: Jinja template with context data.
    """
    #context = {"title": "FastAPI Streaming Log Viewer over WebSockets", "log_file": log_file}
    return templates.TemplateResponse("logs.html", {"request": request})

