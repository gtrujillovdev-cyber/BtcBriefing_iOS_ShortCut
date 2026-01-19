# 🛠️ Tutorial: Crea tu Propio Analista Financiero con Python y Cloud Run

¿Quieres aprender cómo se construyó este proyecto?
Esta guía documenta el proceso paso a paso para crear una API financiera en Python, contenedorizarla con Docker y desplegarla en Google Cloud para conectarla a tu iPhone.

**Nivel:** Intermedio | **Tiempo estimado:** 45 min

---

## 📋 Fase 1: Preparación del Entorno

Lo primero es organizar tu espacio de trabajo local.

1.  **Crea la carpeta del proyecto:**
    \`\`\`bash
    mkdir MiBotFinanciero
    cd MiBotFinanciero
    \`\`\`

2.  **Crea un entorno virtual (Buenas prácticas):**
    Aísla las librerías para no ensuciar tu sistema.
    \`\`\`bash
    python3 -m venv venv
    source venv/bin/activate  # En Mac/Linux
    \`\`\`

---

## 🐍 Fase 2: El Backend (Python + FastAPI)

Vamos a crear el cerebro del sistema. Usaremos **FastAPI** por su velocidad y **Matplotlib** para generar los gráficos.

### 1. Define las dependencias
Crea un archivo llamado `requirements.txt` con estas librerías clave:
\`\`\`text
fastapi
uvicorn
pandas
yfinance
mplfinance
requests
\`\`\`

### 2. Instálalas
\`\`\`bash
pip install -r requirements.txt
\`\`\`

### 3. El Código (main.py)
Crea el archivo `main.py`. Aquí es donde ocurre la magia.
*(Puedes ver el código completo en este repositorio, pero la lógica es esta):*

1.  **Imports:** Traemos `fastapi`, `yfinance` (datos de bolsa) y `mplfinance` (gráficos).
2.  **Endpoints:** Creamos una ruta `@app.get("/briefing")`.
3.  **Lógica:**
    * Descargamos datos de BTC y SP500.
    * Calculamos RSI y Medias Móviles (Matemática financiera).
    * Generamos una imagen PNG con `mplfinance`.
    * Convertimos esa imagen a Base64 (texto) para poder enviarla por internet.
4.  **Respuesta:** Devolvemos un JSON con el texto del resumen y la imagen codificada.

---

## 🐳 Fase 3: Dockerización (Haciéndolo Portable)

Para que esto funcione en la nube igual que en tu Mac, necesitamos meterlo en una "caja" (Contenedor).

Crea un archivo llamado `Dockerfile` (sin extensión) con este contenido exacto:

\`\`\`dockerfile
# Usamos una imagen ligera de Python
FROM python:3.9-slim

# Instalar dependencias de sistema para gráficos (Matplotlib)
RUN apt-get update && apt-get install -y libgl1-mesa-glx && rm -rf /var/lib/apt/lists/*

# Configurar carpeta de trabajo
WORKDIR /app

# Copiar archivos e instalar librerías
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .

# Comando de arranque (Lanza el servidor en el puerto 8080)
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
\`\`\`

---

## ☁️ Fase 4: Despliegue en Google Cloud Run

Aquí es donde subimos el bot a internet. Usaremos Cloud Run porque es "Serverless" (solo pagas cuando usas el bot, gratis si nadie lo llama).

1.  **Instala Google Cloud CLI** y loguéate:
    \`\`\`bash
    gcloud auth login
    \`\`\`

2.  **Despliega con un solo comando ("El Martillo"):**
    Este comando empaqueta tu código, lo sube, busca el Dockerfile, construye el contenedor y te da una URL pública HTTPS.

    \`\`\`bash
    gcloud run deploy mi-analista-bot \
      --source . \
      --platform managed \
      --region europe-west1 \
      --allow-unauthenticated \
      --memory 1Gi
    \`\`\`

3.  **Resultado:**
    La terminal te dará una URL parecida a:
    `https://mi-analista-bot-xyz.run.app`
    ¡Guarda esa URL! Es tu API.

---

## 📱 Fase 5: Conexión con iPhone (El Cliente)

Ahora actuamos como desarrolladores Frontend usando la app **Atajos (Shortcuts)** de iOS.

1.  Abre **Atajos** y crea uno nuevo.
2.  Añade la acción **"Obtener contenido de URL"**.
    * Pega tu URL de Google Cloud terminada en `/briefing`.
3.  Añade **"Obtener valor del diccionario"** (Clave: `mensaje`) para leer el texto.
4.  Añade **"Obtener valor del diccionario"** (Clave: `imagen_base64`) para leer el gráfico.
5.  Añade **"Descodificar Base64"** para transformar el texto en imagen.
6.  Añade **"Enviar Mensaje"**.
    * Arrastra la variable del texto y la imagen descodificada.

**¡Pruébalo!** Dale al Play ▶️ y verás cómo tu servidor en la nube procesa los datos y te envía el informe al móvil.

---

## 🤖 Fase 6: Automatización (El Toque Final)

Para que sea un verdadero asistente:
1.  Ve a la pestaña **Automatización** en Atajos.
2.  Crea una nueva: **"A las 08:00 AM, Diariamente"**.
3.  Acción: **"Ejecutar Atajo"** (Selecciona tu atajo).
4.  Desactiva "Solicitar Confirmación".

**Resultado:** Cada mañana, mientras desayunas, recibirás un análisis de mercado profesional creado por tu propio código. 🚀

---
*Tutorial creado por Gabriel Trujillo Vallejo.*
