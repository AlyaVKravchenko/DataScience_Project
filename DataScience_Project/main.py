from fastapi import FastAPI, File, UploadFile
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from src.routers import auth, users
from fastapi import Request
import shutil
import os

app = FastAPI()

app.include_router(auth.router_auth, prefix="/api")
app.include_router(users.router_users, prefix="/api")

# Оновлюємо шлях до папки з шаблонами
templates = Jinja2Templates(directory="src/templates")


# Папка для збереження завантажених зображень
UPLOAD_FOLDER = "upload_images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)


@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.post("/upload/", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...)):
    with open(os.path.join(UPLOAD_FOLDER, file.filename), "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)
    return templates.TemplateResponse("success.html", {"request": request, "filename": file.filename})


@app.get("/image/{filename}", response_class=HTMLResponse)
async def show_image(request: Request, filename):
    return templates.TemplateResponse("image.html", {"request": request, "filename": filename})


@app.get("/get_image/{filename}")
async def get_image(filename):
    return FileResponse(os.path.join(UPLOAD_FOLDER, filename))


@app.get("/all_images", response_class=HTMLResponse)
async def show_all_images(request: Request):
    images = os.listdir(UPLOAD_FOLDER)
    return templates.TemplateResponse("all_images.html", {"request": request, "images": images})
