# 📉 Financial Briefing Bot (iOS + Python Cloud Run)

**Versión Actual:** V17.5 (Spanish Edition + TinyURL Support)
**Autor:** Gabriel Trujillo Vallejo
**Estado:** Producción 🟢

Este proyecto es un **Analista Financiero Personal** automatizado. Consiste en una API REST desarrollada en Python (FastAPI) que recopila datos de mercado en tiempo real, genera gráficos técnicos al vuelo y entrega un "Briefing" matutino directamente a iMessage mediante un Atajo de iOS.

---

## 🚀 Funcionalidades (V17.5)

* **Multi-Activo:** Monitorización en tiempo real de **Bitcoin (BTC)**, **Ethereum (ETH)**, **S&P 500**, **Nasdaq 100** y **Oro**.
* **Análisis Cuantitativo:** Cálculo automático de indicadores técnicos:
    * **RSI (14):** Detección de Sobrecompra/Sobreventa.
    * **SMA (2Y):** Tendencia estructural a largo plazo.
    * **Soportes:** Detección de mínimos locales.
* **Motor Gráfico:** Generación de velas japonesas (Candlestick) con `mplfinance`, incluyendo medias móviles y zonas de soporte, renderizado en el servidor.
* **Noticias Inteligentes:** Scraper de **Google News España** con filtrado de relevancia.
    * *Novedad V17.5:* Integración con **TinyURL API** para convertir enlaces kilométricos en links cortos y clickables en iMessage.
* **Anti-Bloqueo:** Headers personalizados para evadir restricciones 403 en Yahoo Finance y Google.

---

## 🛠️ Stack Tecnológico

* **Lenguaje:** Python 3.9+
* **Framework:** FastAPI + Uvicorn
* **Análisis de Datos:** Pandas, Numpy
* **Finanzas:** `yfinance` (Stocks), `cryptocompare` (Crypto)
* **Visualización:** `mplfinance`, `matplotlib`
* **Infraestructura:** Google Cloud Run (Serverless Docker Container)

---

## 🤝 Cómo Colaborar (Workflow)

Este proyecto sigue un flujo de trabajo estándar de Git. Si quieres añadir un indicador nuevo o mejorar el gráfico, **NO hagas push a `main` directamente**.

1.  **Clona el repositorio:**
    \`\`\`bash
    git clone https://github.com/gtrujillovdev-cyber/DevOps.git
    \`\`\`
2.  **Crea una rama (Branch) para tu mejora:**
    \`\`\`bash
    git checkout -b feature/nuevo-indicador-macd
    \`\`\`
3.  **Realiza tus cambios y haz commit:**
    \`\`\`bash
    git add .
    git commit -m "Feat: Añadido MACD al gráfico"
    \`\`\`
4.  **Sube tu rama:**
    \`\`\`bash
    git push origin feature/nuevo-indicador-macd
    \`\`\`
5.  **Abre un Pull Request (PR)** en GitHub para fusionar tus cambios con `main`.

---

## ☁️ Guía de Despliegue (DevOps)

Para actualizar el bot en producción (Google Cloud Run), ejecuta el siguiente comando desde la carpeta del proyecto:

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

## 📱 Guía de Configuración: Atajo de iOS (Frontend)

El "cliente" es un Atajo nativo de Apple. Sigue estos pasos para construirlo desde cero:

### 1. Configurar la Petición
1.  Acción: **Obtener contenido de URL**
    * **URL:** `https://[TU-URL-DE-CLOUD-RUN].run.app/briefing`
    * **Método:** GET

### 2. Procesar la Respuesta (JSON)
2.  Acción: **Obtener valor del diccionario**
    * Clave: `mensaje`
    * Entrada: *Contenido de URL* (Guárdalo en variable `TextoInforme`).
3.  Acción: **Obtener valor del diccionario**
    * Clave: `imagen_base64`
    * Entrada: *Contenido de URL*.

### 3. Decodificar el Gráfico
4.  Acción: **Descodificar Base64**
    * Entrada: Valor del paso anterior.
5.  Acción: **Guardar archivo** (Vital para evitar errores de memoria)
    * **Preguntar al guardar:** 🔴 Desactivado.
    * **Ruta:** `grafico_temp.png`
    * **Sobrescribir:** 🟢 Activado.

### 4. Enviar el Briefing
6.  Acción: **Enviar mensaje**
    * **Destinatario:** Tú mismo (o grupo).
    * **Mensaje:** Variable `TextoInforme`.
    * **Adjunto:** Selecciona el archivo guardado en el paso 5.

---
*Developed by Gabriel Trujillo Vallejo (2026).*
