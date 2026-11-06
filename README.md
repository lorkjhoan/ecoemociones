# EcoEmociones 🐾

Aplicación web que usa **inteligencia artificial** para reconocer emociones en el rostro a través de la cámara y las refleja en una **mascota virtual**. Está pensada como una herramienta lúdica para trabajar el reconocimiento y la expresión de emociones mediante dos minijuegos.

---

## ✨ Funcionalidades

### 🎭 Mímica emocional (`/mimica`)
- Activa la cámara web del navegador.
- Cada **1,5 segundos** captura un fotograma y lo envía al servidor.
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
Navegador (cámara)  ──►  POST /predict (imagen en base64)
                              │
                              ▼
             OpenCV: detección de rostro (Haar Cascade)
                              │  se toma el rostro más grande
                              ▼
          Recorte → redimensión a 100×100 px → normalización (0–1)
                              │
                              ▼
          Modelo Keras/TensorFlow (modelo_affectnet_v1.h5)
                              │
                              ▼
          Respuesta JSON: { "emotion": "feliz" }
```

- Si no se detecta ningún rostro, se usa la imagen completa.
- El modelo clasifica **5 emociones**: `asustado`, `enojado`, `feliz`, `sorprendido` y `triste`.
- El nombre del modelo indica que fue entrenado a partir del dataset **AffectNet**.

---

## 🛠️ Tecnologías

| Capa | Herramientas |
|---|---|
| Backend | Python, Flask |
| IA / Visión | TensorFlow / Keras, OpenCV, NumPy, Pillow |
| Frontend | HTML, CSS, JavaScript (API `getUserMedia` y `fetch`), plantillas Jinja2 |

---

## 📁 Estructura del proyecto

```
ecoemociones/
├── app.py                 # Servidor Flask: rutas, preprocesamiento y predicción
├── requirements.txt       # Dependencias de Python
├── modelo/                # (no incluido en el repo) modelo_affectnet_v1.h5
├── static/
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
- Python 3.10 – 3.12 (compatible con TensorFlow 2.20)
- Una cámara web (para el minijuego de mímica)
- El archivo del modelo `modelo_affectnet_v1.h5`

### Pasos

1. **Clonar el repositorio**
   ```bash
   git clone https://github.com/lorkjhoan/ecoemociones.git
   cd ecoemociones
   ```

2. **Crear y activar un entorno virtual**
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # Linux / macOS
   source venv/bin/activate
   ```

3. **Instalar dependencias**
   ```bash
   pip install -r requirements.txt
   ```
   Si solo quieres lo indispensable para ejecutar la app:
   ```bash
   pip install flask tensorflow opencv-python numpy pillow
   ```

4. **Agregar el modelo**

   Por su tamaño, el modelo no se sube al repositorio (`modelo/*.h5` está en `.gitignore`). Crea la carpeta y coloca el archivo:
   ```
   modelo/modelo_affectnet_v1.h5
   ```

5. **Ejecutar la aplicación**
   ```bash
   python app.py
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
| POST | `/predict` | Recibe `{ "image": "<base64 JPEG>" }` y devuelve `{ "emotion": "<etiqueta>" }` |

---

## ⚠️ Limitaciones conocidas
- El modelo `.h5` debe obtenerse aparte; sin él la aplicación no inicia.
- La detección con Haar Cascade funciona mejor con el rostro de frente y buena iluminación.
- La app se ejecuta en modo `debug=True`, pensado para desarrollo y no para producción.

---

## 👥 Autores
- **Gabriela Robles Bautista**
- **Jhoan Esteban Rodriguez** — [@lorkjhoan](https://github.com/lorkjhoan)

Proyecto desarrollado con inteligencia artificial y amor por el bienestar emocional 💚
