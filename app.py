from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io, base64, os
import cv2

app = Flask(__name__)

# === CARGAR MODELO ===
model_path = os.path.join("modelo", "modelo_emociones_v2.h5")
model = load_model(model_path)

# === ETIQUETAS DEL MODELO ===
class_names = ["feliz", "triste", "enojado", "sorprendido", "asustado"]

# === CLASIFICADOR DE ROSTROS ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# === FUNCIÓN DE PREPROCESAMIENTO ===
def preprocess_frame(frame_bytes):
    # Convertir bytes a imagen RGB
    img = Image.open(io.BytesIO(frame_bytes)).convert("RGB")
    img_np = np.array(img)

    # Convertir a escala de grises para detectar rostros
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Si hay rostros, usar el más grande
    if len(faces) > 0:
        largest_face = max(faces, key=lambda f: f[2] * f[3])
        (x, y, w, h) = largest_face
        img_np = img_np[y:y+h, x:x+w]
    # Si no hay rostros, usa la imagen completa

    # Redimensionar y normalizar
    img_resized = Image.fromarray(img_np).resize((224, 224))
    img_array = np.array(img_resized) / 255.0
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


# === RUTAS ===
@app.route("/")
def index():
    return render_template("index.html")

@app.route("/mimica")
def mimica():
    return render_template("mimica.html")

@app.route("/interactuar")
def interactuar():
    return render_template("interactuar.html")


# === ENDPOINT DE PREDICCIÓN ===
@app.route("/predict", methods=["POST"])
def predict():
    # Decodificar imagen
    data = request.json
    img_data = base64.b64decode(data["image"])
    img = preprocess_frame(img_data)

    # Hacer predicción directa
    pred = model.predict(img)
    emotion = class_names[np.argmax(pred)]

    return jsonify({"emotion": emotion})


# === EJECUCIÓN ===
if __name__ == "__main__":
    app.run(debug=True)
