# EcoEmociones 🐾

Aplicación web que usa **inteligencia artificial** para reconocer emociones en el rostro a través de la cámara y las refleja en una **mascota virtual**. Está pensada como una herramienta lúdica para trabajar el reconocimiento y la expresión de emociones mediante dos minijuegos.

---

## ✨ Funcionalidades

### 🎭 Mímica emocional (`/mimica`)
- Activa la cámara web del navegador.
- Cada **1,5 segundos** captura un fotograma y lo envía al servidor.
- Cada predicción se envía solo cuando termina la anterior, para no saturar el servidor.
- Para evitar cambios bruscos, la mascota muestra la emoción más frecuente de las últimas 5 predicciones.
- El servidor detecta el rostro, lo recorta y un modelo de red neuronal predice la emoción.
- La mascota cambia su expresión para **imitar la emoción detectada** y se muestra el resultado en pantalla.

### 😺 Interactuar con la mascota (`/interactuar`)
Minijuego sin cámara en el que la mascota reacciona a lo que hace el usuario con el mouse:

| Acción | Reacción de la mascota |
|---|---|
| Mantener presionado el clic sobre ella (acariciar) | 😊 Feliz, con corazones animados |
| Varios clics rápidos seguidos | 😠 Enojada |
| Pasar el mouse por encima | 😮 Sorprendida |
| Hacer clic en el fantasma | 😱 Asustada |
| No interactuar durante un rato | 😢 Triste |

---

## 🧠 ¿Cómo funciona el reconocimiento de emociones?

```
Navegador (cámara)
        │
        ▼
MediaPipe Face Landmarker (en el navegador): detecta la cara
        │  recorte cuadrado con 20 % de margen
        ▼
POST /predict  { "image": "<recorte en base64>", "recortada": true }
        │  solo se envía el recorte de la cara
        ▼
Servidor: redimensión a 100×100 px → normalización (0–1)
        │
        ▼
Modelo Keras/TensorFlow (modelo_affectnet_v1.h5)
        │
        ▼
Respuesta JSON: { "status": "ok", "emotion": "feliz", "confidence": 0.87 }
```

- La cara se detecta y se recorta en el navegador con **MediaPipe Face Landmarker**, que funciona mejor que Haar Cascade con poca luz o con la cara inclinada. Al servidor solo llega el recorte de la cara.
- Si MediaPipe no ve ninguna cara, no se llama al servidor y la interfaz le pide al usuario acercarse a la cámara.
- **Respaldo:** si MediaPipe no está disponible (sin internet, navegador incompatible o error), el navegador envía el fotograma completo sin `"recortada"` y el servidor detecta la cara con **OpenCV (Haar Cascade)**, tomando el rostro más grande. En ese caso, si no hay rostro se responde `{ "status": "sin_rostro" }`.
- La malla y los puntos de la cara nunca se dibujan sobre el video (bajo impacto sensorial). Para verificar la detección, abre `/mimica?debug=1`: se dibuja solo un rectángulo alrededor de la cara.
- Si la confianza del modelo es menor al 50 % (`UMBRAL_CONFIANZA` en `app.py`), se responde `"status": "dudoso"` y la mascota no cambia, para evitar resultados erróneos.
- El modelo clasifica **5 emociones**: `asustado`, `enojado`, `feliz`, `sorprendido` y `triste`.
- El nombre del modelo indica que fue entrenado a partir del dataset **AffectNet**.

---

## 🛠️ Tecnologías

| Capa | Herramientas |
|---|---|
| Backend | Python, Flask |
| IA / Visión | TensorFlow / Keras, OpenCV, NumPy, Pillow |
| Frontend | HTML, CSS, JavaScript (API `getUserMedia` y `fetch`), plantillas Jinja2, MediaPipe Tasks Vision (detección de rostro en el navegador) |

---

## 📁 Estructura del proyecto

```
ecoemociones/
├── app.py                 # Servidor Flask: rutas, preprocesamiento y predicción
├── requirements.txt       # Dependencias de Python
├── modelo/                # modelo_affectnet_v1.h5 (descargar desde Releases)
├── static/
│   ├── css/
│   │   └── eco.css        # Estilos compartidos de todas las páginas
│   ├── mediapipe/
│   │   └── face_landmarker.task  # Modelo de MediaPipe para detectar la cara (float16)
│   └── mascota/           # Imágenes de la mascota por emoción
│       ├── asustado.png
│       ├── enojado.png
│       ├── feliz.png
│       ├── sorprendido.png
│       └── triste.png
└── templates/
    ├── index.html         # Menú principal
    ├── mimica.html        # Minijuego con cámara + IA
    └── interactuar.html   # Minijuego de interacción con el mouse
```

---

## 🚀 Instalación y ejecución

### Requisitos previos
- Python 3.12 (recomendado). TensorFlow 2.20 no es compatible con Python 3.13 ni 3.14.
- Una cámara web (para el minijuego de mímica)
- El archivo del modelo `modelo_affectnet_v1.h5` (se descarga desde Releases, ver paso 4).

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/lorkjhoan/ecoemociones.git
   cd ecoemociones
   ```

2. **Crear y activar un entorno virtual**
   ```bash
   # Windows
   py -3.12 -m venv .venv
   .venv\Scripts\activate
   # Linux / macOS
   python3.12 -m venv .venv
   source .venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```

4. **Descargar el modelo**

   El modelo pesa ~104 MB, por encima del límite de 100 MB por archivo de GitHub, así que no está en el repositorio. Descarga `modelo_affectnet_v1.h5` desde la sección [Releases](https://github.com/lorkjhoan/ecoemociones/releases) y colócalo en `modelo/modelo_affectnet_v1.h5` (crea la carpeta `modelo` en la raíz si no existe).

5. **Ejecutar la aplicación**
   ```bash
   python app.py
   ```
   Para desarrollar con recarga automática y mensajes de error detallados (modo debug):
   ```powershell
   # Windows (PowerShell)
   $env:FLASK_DEBUG="1"
   python app.py
   ```
   ```bash
   # Linux / macOS
   FLASK_DEBUG=1 python app.py
   ```
   Abre en el navegador: **http://127.0.0.1:5000**

> 💡 El navegador pedirá permiso para usar la cámara. Debe abrirse desde `localhost` / `127.0.0.1` (o HTTPS) para que el acceso a la cámara funcione.

---

## 🔌 Endpoints

| Método | Ruta | Descripción |
|---|---|---|
| GET | `/` | Menú principal |
| GET | `/mimica` | Minijuego de mímica con cámara |
| GET | `/interactuar` | Minijuego de interacción con la mascota |
| POST | `/predict` | Recibe `{ "image": "<base64 JPEG>" }`. Devuelve `status` (`ok`, `dudoso` o `sin_rostro`), y cuando aplica `emotion` y `confidence`. Responde 400 si la imagen falta o no es válida. |

---

## ⚠️ Limitaciones conocidas
- El modelo `.h5` debe descargarse aparte desde Releases; sin él la aplicación no inicia.
- La detección con Haar Cascade funciona mejor con el rostro de frente y buena iluminación.
- El servidor incluido en Flask es para desarrollo. El modo debug se activa con la variable de entorno `FLASK_DEBUG=1`.

---

## 👥 Autores
- **Gabriela Robles Bautista**
- **Jhoan Esteban Rodriguez** — [@lorkjhoan](https://github.com/lorkjhoan)

Proyecto desarrollado con inteligencia artificial y amor por el bienestar emocional 💚
