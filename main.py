from fastapi import FastAPI, File, UploadFile, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
import shutil
import os
import logging
import tensorflow as tf
import numpy as np
from PIL import Image  
import cv2

app = FastAPI()

templates = Jinja2Templates(directory="src/templates")

UPLOAD_FOLDER = "upload_images"
PROCESSED_FOLDER = "processed_images"

# Створення папок, якщо вони не існують
for folder in [UPLOAD_FOLDER, PROCESSED_FOLDER]:
    if not os.path.exists(folder):
        os.makedirs(folder)

# Шлях до моделі
model_path = "CNN_50_epochs.h5"

# Налаштування логування
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Перевірка наявності файлу моделі
if not tf.io.gfile.exists(model_path):
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
    processed_file_path = os.path.join(PROCESSED_FOLDER, file.filename)

    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # Зчитування та обробка зображення за допомогою OpenCV та numpy
    file.file.seek(0)  # Повернення до початку файлу
    img_bytes = await file.read()
    nparr = np.frombuffer(img_bytes, np.uint8)
    
    try:
        img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
        img = cv2.resize(img, (32, 32))
        img = img.astype('float32') / 255.0
        img = np.expand_dims(img, axis=0)

        # Прогнозування
        predictions = model.predict(img)
        logger.info(f"Predictions: {predictions}")
        predicted_class_index = np.argmax(predictions)
        predicted_class = classes[predicted_class_index]
        probability = predictions[0][predicted_class_index]
        logger.info(f"Predicted class: {predicted_class} with probability {probability}")

        # Збереження обробленого зображення
        processed_img = Image.fromarray((img[0] * 255).astype(np.uint8))
        processed_img.save(processed_file_path)

        # Створення словника з ймовірностями для кожного класу
        probabilities = {classes[i]: float(predictions[0][i]) for i in range(len(classes))}

        return templates.TemplateResponse("success.html", {
            "request": request, 
            "filename": file.filename, 
            "predicted_class": predicted_class, 
            "probability": probability, 
            "probabilities": probabilities
        })
    except Exception as e:
        logger.error(f"Error processing image: {e}")
        return templates.TemplateResponse("error.html", {"request": request, "message": "Error processing image"})

@app.get("/image/{filename}", response_class=HTMLResponse)
async def show_image(request: Request, filename):
    return templates.TemplateResponse("image.html", {"request": request, "filename": filename})

@app.get("/get_image/{filename}")
async def get_image(filename):
    return FileResponse(os.path.join(UPLOAD_FOLDER, filename))

@app.get("/get_processed_image/{filename}")
async def get_processed_image(filename):
    return FileResponse(os.path.join(PROCESSED_FOLDER, filename))

@app.get("/all_images", response_class=HTMLResponse)
async def show_all_images(request: Request):
    images = os.listdir(UPLOAD_FOLDER)
    return templates.TemplateResponse("all_images.html", {"request": request, "images": images})

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000, log_level="info")
