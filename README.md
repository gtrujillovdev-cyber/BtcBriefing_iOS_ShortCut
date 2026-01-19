# 📉 BtcBriefing iOS Assistant (V17.5)

**Estado:** 🟢 Producción | **Licencia:** MIT | **Stack:** Python + Google Cloud Run + iOS Shortcuts

Este proyecto es un **Analista Financiero Cuantitativo Personal**.
Es un backend (API) diseñado para ser consumido por un Atajo de iOS. Cada mañana, recopila datos de BTC, ETH, Nasdaq y S&P500, genera un gráfico técnico con `mplfinance`, busca noticias en español, acorta los enlaces y envía un informe ejecutivo vía iMessage.

---

## 🏗️ Arquitectura del Sistema

El flujo de datos funciona así:

1.  📱 **iOS Shortcut:** Despierta y pide informe (`GET /briefing`).
2.  ☁️ **Cloud Run (Python):**
    * Consulta APIs externas (Yahoo Finance, CryptoCompare).
    * Calcula indicadores (RSI, SMA 2Y, Soportes).
    * Genera gráfico `.png` y lo codifica en Base64.
    * Busca noticias y acorta URLs con TinyURL.
3.  📱 **iOS Shortcut:** Recibe JSON, decodifica la imagen y envía el iMessage.

---

## 💻 Guía para Desarrolladores (Local Setup)

Si quieres colaborar o probar cambios sin gastar dinero en la nube, sigue estos pasos:

### 1. Clonar y Preparar
\`\`\`bash
git clone https://github.com/gtrujillovdev-cyber/BtcBriefing_iOS_ShortCut.git
cd BtcBriefing_iOS_ShortCut

# Crear entorno virtual (Opcional pero recomendado)
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt
\`\`\`

### 2. 🧪 Realizar Pruebas Locales (Test Script)
Hemos incluido un script que simula ser el iPhone. Ejecútalo para verificar que tu código genera el gráfico y el texto correctamente:

\`\`\`bash
python test_local.py
\`\`\`

* **Éxito:** Se creará un archivo `test_output_grafico.png` en tu carpeta. Ábrelo para verificar el diseño.
* **Logs:** Verás el texto del informe impreso en la terminal.

### 3. Servidor de Desarrollo
Si prefieres probar la API en el navegador:
\`\`\`bash
uvicorn main:app --reload
\`\`\`
Abre [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) para ver la documentación interactiva (Swagger UI).

---

## ☁️ Guía de Despliegue (Google Cloud)

Para subir tu propia versión a producción:

1.  Instala el [Google Cloud SDK](https://cloud.google.com/sdk/docs/install).
2.  Ejecuta el deploy:

\`\`\`bash
gcloud run deploy brief-bot \
  --source . \
  --platform managed \
  --region europe-west1 \
  --allow-unauthenticated \
  --memory 1Gi \
  --clear-base-image
\`\`\`

---

## 📱 Configuración del Cliente (iPhone)

El usuario final debe crear un Atajo (Shortcut) nativo en iOS con estos bloques exactos:

| Paso | Acción | Configuración |
| :--- | :--- | :--- |
| **1** | **Obtener contenido de URL** | **URL:** `https://[TU-URL].run.app/briefing`<br>**Método:** GET |
| **2** | **Obtener valor del diccionario** | **Clave:** `mensaje`<br>**Entrada:** Resultado del Paso 1 |
| **3** | **Obtener valor del diccionario** | **Clave:** `imagen_base64`<br>**Entrada:** Resultado del Paso 1 |
| **4** | **Descodificar Base64** | **Entrada:** Resultado del Paso 3 |
| **5** | **Guardar archivo** | **Entrada:** Imagen del Paso 4<br>**Ruta:** `temp_chart.png`<br>**Preguntar:** 🔴 Off \| **Sobrescribir:** 🟢 On |
| **6** | **Enviar mensaje** | **Contenido:** Variable Texto (Paso 2) + Variable Archivo (Paso 5) |

---

## 🤝 Cómo Colaborar (Contributing)

Este proyecto sigue un flujo de trabajo estricto para proteger la estabilidad.

1.  **NO hagas push a `main`:** La rama principal está protegida.
2.  **Crea una rama:** `git checkout -b feature/mi-mejora`
3.  **Haz tus cambios y prueba:** Usa `python test_local.py`.
4.  **Sube tu rama:** `git push origin feature/mi-mejora`.
5.  **Abre un Pull Request (PR):** En GitHub, solicita fusionar tu rama con `main`.

---
*Maintained by Gabriel Trujillo Vallejo (2026).*
