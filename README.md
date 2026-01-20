# 📉 BtcBriefing iOS Assistant (V17.5)

Estado: 🟢 Producción | Licencia: MIT | Stack: Python + FastAPI + Google Cloud Run + iOS Shortcuts

Backend (API) diseñado para ser consumido por un Atajo de iOS. Cada mañana, recopila datos de BTC, ETH, Nasdaq y S&P500, genera un gráfico técnico con `mplfinance`, busca noticias en español, acorta los enlaces y devuelve un informe ejecutivo con imagen en Base64 para ser enviado por iMessage.

---

## 🏗️ Arquitectura del Sistema

1) 📱 iOS Shortcut solicita informe (GET /briefing).
2) ☁️ Cloud Run (Python):
   - Consulta APIs externas (Yahoo Finance, CryptoCompare).
   - Calcula indicadores (RSI, SMA 2Y, soportes).
   - Genera gráfico `.png` y lo codifica en Base64.
   - Busca noticias y acorta URLs con TinyURL.
3) 📱 iOS Shortcut recibe JSON, decodifica la imagen y envía el iMessage.

---

## 📁 Estructura del repositorio

Archivos principales:
- main.py
- requirements.txt
- Dockerfile
- test_local.py
- .gitignore
- README.md

---

## ✅ Requisitos Previos

- Python 3.9+ (recomendado 3.10+)
- pip
- (Opcional) Docker
- Google Cloud SDK instalado y autenticado

---

## 💻 Configuración y Pruebas Locales

### 1) Clonado y preparación

```bash
git clone https://github.com/gtrujillovdev-cyber/BtcBriefing_iOS_ShortCut.git
cd BtcBriefing_iOS_ShortCut
```

### 2) (Recomendado) Crear entorno virtual e instalar dependencias

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3) Test rápido del backend

```bash
python test_local.py
```

- Se crea `test_output_grafico.png` con el gráfico.
- En consola verás el texto del briefing.
- Corrige cualquier error antes de continuar.

### 4) Servidor local (opcional)

```bash
uvicorn main:app --reload
```

- Abre: http://127.0.0.1:8000/docs
- Prueba el endpoint `/briefing` desde Swagger UI.
- Debes recibir JSON con `mensaje` y `imagen_base64`.

---

## ☁️ Despliegue en Google Cloud

Esta guía cubre desde la preparación local hasta la publicación del servicio en Google Cloud Run.

### 1) Autenticación y proyecto

```bash
gcloud auth login
gcloud auth list
gcloud config set project [PROJECT_ID]   # Reemplaza por tu Project ID
```

### 2) (Opcional) Compilar imagen con Cloud Build

Valida que la imagen del contenedor construye correctamente con tu Dockerfile.

```bash
gcloud builds submit --tag gcr.io/[PROJECT_ID]/btcbriefing-test
```

- Compila la imagen con tu `Dockerfile`.
- Si hay fallos en dependencias o Python, se verán aquí.
- No despliega todavía; solo valida la imagen.

### 3) Despliegue en Cloud Run

```bash
gcloud run deploy brief-bot \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --clear-base-image
```

Resultado esperado:
- Se crea el servicio `brief-bot`.
- Obtendrás una URL pública, por ejemplo: `https://brief-bot-xxxxx.a.run.app`.

(Avanzado) Para probar sin exponer tráfico: añade `--no-traffic` y crea una revisión, luego cambia tráfico cuando confirmes.

### 4) Verificar API en producción

```bash
curl https://brief-bot-xxxxx.a.run.app/briefing
```

Respuesta esperada:

```json
{
  "mensaje": "Texto del briefing",
  "imagen_base64": "iVBORw0KGgoAAAANSUhEUgAA..."
}
```

Esto confirma que la API funciona para el Shortcut iOS.

---

## 📱 Configuración del Shortcut iOS

1) Obtener contenido de URL
   - URL: `https://[TU-SERVICIO].run.app/briefing`
   - Método: GET

2) Obtener valor del diccionario
   - Clave: `mensaje`
   - Clave: `imagen_base64`

3) Decodificar Base64 (entrada: `imagen_base64`).

4) Guardar archivo
   - Ruta: `temp_chart.png`
   - Preguntar: Off / Sobrescribir: On

5) Enviar mensaje
   - Contenido: Texto (`mensaje`) + Imagen (`temp_chart.png`).

---

## 🤝 Flujo de trabajo y buenas prácticas

1) Verifica build local con `python test_local.py`.
2) Verifica API local con `uvicorn main:app --reload`.
3) Verifica build con `gcloud builds submit` (opcional).
4) Despliega a Cloud Run (opcionalmente con `--no-traffic`).
5) Usa ramas y PRs:

```bash
git checkout -b feature/mi-mejora
git add .
git commit -m "Validate build and deploy pipeline"
git push origin feature/mi-mejora
```

6) Abre Pull Request para fusionar con `main`. La rama `main` debe permanecer estable.

---

## 📜 Licencia y mantenimiento

- Licencia: MIT
- Maintained by Gabriel Trujillo Vallejo (2026)
