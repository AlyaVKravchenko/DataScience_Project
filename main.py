from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from src.routers import auth, users
import shutil
import os
import logging
import tensorflow as tf
from tensorflow.keras.preprocessing import image
import numpy as np

app = FastAPI()

app.include_router(auth.router_auth, prefix="/api")
app.include_router(users.router_users, prefix="/api")

templates = Jinja2Templates(directory="src/templates")

UPLOAD_FOLDER = "upload_images"
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# Шлях до моделі
model_path = "ResNet50_model.h5"

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Перевірка наявності файлу
if not os.path.exists(model_path):
    logger.error(f"Model file not found at {model_path}")
else:
    model = tf.keras.models.load_model(model_path)
    logger.info(f"Model loaded successfully from {model_path}")

# Класи CIFAR-10
classes = ['airplane', 'automobile', 'bird', 'cat', 'deer', 'dog', 'frog', 'horse', 'ship', 'truck']

@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/upload/", response_class=HTMLResponse)
async def upload_image(request: Request, file: UploadFile = File(...)):
    file_path = os.path.join(UPLOAD_FOLDER, file.filename)
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Обробка зображення
    img = image.load_img(file_path, target_size=(32, 32))
    img_array = image.img_to_array(img)
    img_array = np.expand_dims(img_array, axis=0)
    img_array = img_array / 255.0

    # Прогнозування
    predictions = model.predict(img_array)
    logger.info(f"Predictions: {predictions}")
    predicted_class_index = np.argmax(predictions)
    predicted_class = classes[predicted_class_index]
    probability = predictions[0][predicted_class_index]
    logger.info(f"Predicted class: {predicted_class} with probability {probability}")

    # Створення словника з ймовірностями для кожного класу
    probabilities = {classes[i]: float(predictions[0][i]) for i in range(len(classes))}

    return templates.TemplateResponse("success.html", {"request": request, "filename": file.filename, "predicted_class": predicted_class, "probability": probability, "probabilities": probabilities})

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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
