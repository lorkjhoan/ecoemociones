from flask import Flask, render_template, request, jsonify
from tensorflow.keras.models import load_model
import numpy as np
from PIL import Image
import io, base64, os
import cv2

app = Flask(__name__)

# === CARGAR MODELO ===
model_path = os.path.join("modelo", "modelo_affectnet_v1.h5")
model = load_model(model_path)

# === ETIQUETAS DEL MODELO ===
class_names = ['asustado', 'enojado', 'feliz', 'sorprendido', 'triste']

# === UMBRAL DE CONFIANZA ===
# Si el modelo está menos seguro que esto, no cambiamos la mascota
UMBRAL_CONFIANZA = 0.50

# === CLASIFICADOR DE ROSTROS ===
face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + "haarcascade_frontalface_default.xml")

# === FUNCIÓN DE PREPROCESAMIENTO ===
def preprocess_frame(frame_bytes, ya_recortada=False):
    # Convertir bytes a imagen RGB
    img = Image.open(io.BytesIO(frame_bytes)).convert("RGB")
    img_np = np.array(img)

    # La cara ya viene recortada por MediaPipe desde el navegador:
    # no se usa Haar Cascade, solo se redimensiona y normaliza
    if ya_recortada:
        img_resized = Image.fromarray(img_np).resize((100, 100))
        img_array = np.array(img_resized) / 255.0
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    # Respaldo: buscar la cara en el fotograma completo con Haar Cascade
    # Convertir a escala de grises para detectar rostros
    gray = cv2.cvtColor(img_np, cv2.COLOR_RGB2GRAY)
    faces = face_cascade.detectMultiScale(gray, scaleFactor=1.3, minNeighbors=5)

    # Si no hay rostros, no se predice nada
    if len(faces) == 0:
        return None

    # Si hay rostros, usar el más grande
    largest_face = max(faces, key=lambda f: f[2] * f[3])
    (x, y, w, h) = largest_face
    img_np = img_np[y:y+h, x:x+w]

    # Redimensionar y normalizar
    img_resized = Image.fromarray(img_np).resize((100, 100))
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
    # === VALIDAR DATOS RECIBIDOS ===
    data = request.get_json(silent=True)
    if not data or not data.get("image"):
        return jsonify({"error": "No se recibió ninguna imagen"}), 400

    # True si el navegador ya recortó la cara con MediaPipe
    recortada = bool(data.get("recortada", False))

    # === DECODIFICAR Y PREPROCESAR IMAGEN ===
    try:
        img_data = base64.b64decode(data["image"])
        img = preprocess_frame(img_data, ya_recortada=recortada)
    except Exception:
        return jsonify({"error": "La imagen no es válida"}), 400

    # === SIN ROSTRO DETECTADO ===
    if img is None:
        return jsonify({"status": "sin_rostro"})

    # === PREDICCIÓN ===
    # Llamada directa al modelo: más rápida que model.predict() para una sola imagen
    probs = model(img, training=False).numpy()[0]

    idx = int(np.argmax(probs))
    confidence = float(probs[idx])
    emotion = class_names[idx]

    # === RESULTADO DUDOSO ===
    if confidence < UMBRAL_CONFIANZA:
        return jsonify({"status": "dudoso", "emotion": emotion, "confidence": confidence})

    return jsonify({"status": "ok", "emotion": emotion, "confidence": confidence})


# === EJECUCIÓN ===
if __name__ == "__main__":
    # El modo debug solo se activa si la variable de entorno FLASK_DEBUG vale "1"
    debug = os.environ.get("FLASK_DEBUG", "0") == "1"
    app.run(debug=debug)
