# BtcBriefing_iOS_ShortCut – Explicación del Código

## Resumen funcional

- Servicio HTTP con FastAPI que expone el endpoint GET `/briefing`.
- Devuelve un JSON con:
  - `mensaje`: informe en texto (español) con situación del mercado y titulares.
  - `imagen_base64`: gráfico PNG (codificado en Base64) con velas de BTC, SMA y soporte.

## Configuración (CONFIG)

- `api`
  - `crypto_url`: endpoint de CryptoCompare para histórico diario de BTC.
  - `news_url`: RSS de Google News (ES) para obtener titulares.
  - `shortener_api`: servicio is.gd para acortar enlaces (sustituye a TinyURL por estabilidad).
  - `headers`: User-Agent de navegador para evitar bloqueos.
- `tickers`: símbolos consultados vía yfinance (ETH-USD, MSTR, ^GSPC, ^NDX, GC=F) mapeados a nombres amigables.
- `params`
  - `sma_period`: periodo de SMA de largo plazo (p.ej. 730 días).
  - `rsi_period`: periodo de RSI (p.ej. 14 días).
  - `support_range_days`: rango temporal para calcular soporte (mínimo reciente).
  - `plot_range_days`: días que se muestran en el gráfico.
- `chart`
  - `style`, `colors`, `grid`: estilo y colores de mplfinance.
  - `sma_color`, `support_color`: colores de overlays/soportes.

## Flujo del endpoint `/briefing`

1. Obtiene datos de BTC (OHLCV) y calcula indicadores (SMA y RSI).
2. Obtiene precios/variaciones de activos clave (ETH, MSTR, índices, oro).
3. Obtiene y formatea 3 titulares de Google News, acortando URLs.
4. Redacta un análisis corto (tendencia por SMA y lectura de RSI) y compone el mensaje final.
5. Genera un gráfico de velas con SMA y una línea de soporte.
6. Responde con `mensaje` e `imagen_base64`.

## Detalle de funciones

### 1) `make_tiny(url: str) -> str`
- Llama a la API de is.gd para acortar la URL de forma resiliente. Si falla, retorna la original.

### 2) `get_crypto_data() -> tuple[pd.DataFrame, dict[str, float]]`
- Descarga histórico diario de BTC (CryptoCompare) y construye un DataFrame con columnas: Open, High, Low, Close, Volume.
- Convierte a `float`, calcula:
  - `SMA`: media simple de largo plazo (`sma_period`).
  - `RSI`: cálculo clásico con protección para evitar división por cero.
- Devuelve:
  - DataFrame con columnas adicionales `SMA` y `RSI`.
  - Diccionario con métricas: `price`, `chg` (% diario), `ath_dist` (% vs ATH), `rsi`, `sma_2y`, `range_low` (mínimo reciente para soporte).

### 3) `get_market_data() -> dict[str, tuple[float, float]]`
- Usa `yfinance.Tickers` para obtener `fast_info` de los tickers configurados.
- Para cada activo calcula `(precio, variación % diaria)` y retorna un diccionario por nombre amigable.

### 4) `get_clean_news() -> str`
- Lee el RSS de Google News, toma 3 ítems, extrae título y enlace.
- Acorta con `make_tiny` y formatea viñetas listas para insertar en el informe.

### 5) `get_analysis(rsi: float, price: float, sma: float) -> str`
- Redacta análisis corto:
  - Tendencia de fondo: ALCISTA si `price > sma`, si no BAJISTA.
  - Señal de RSI: sobrecompra (>70), sobreventa (<30) o neutral.

### 6) `format_briefing_message(date, analisis, btc, mk, news) -> str`
- Compone el mensaje final (texto en ES) con secciones:
  - Situación y análisis.
  - Activos clave (BTC, ETH, MSTR, S&P 500, Nasdaq 100, Oro).
  - Técnico BTC: RSI, media, soporte.
  - Titulares.

### 7) `generate_briefing_chart(df, btc_data, date) -> str`
- Genera un gráfico con `mplfinance`:
  - Velas (`type='candle'`), estilo y colores de `CONFIG`.
  - Overlays: `SMA` si existe, línea horizontal de soporte (`range_low`).
  - Leyenda personalizada con `matplotlib`.
  - Guarda a PNG en memoria (`BytesIO`) y retorna en Base64.

### 8) `briefing() -> BriefResponse`
- Orquestador del endpoint.
- Maneja errores y retorna mensaje y gráfico (o solo mensaje en caso de fallo).

## Consideraciones técnicas

- Matplotlib usa backend `Agg` y `MPLCONFIGDIR=/tmp/matplotlib` para entornos sin GUI (servidor/containers).
- Manejo de errores envolviendo las llamadas externas para garantizar respuesta estable.
- Tipado de retorno con Pydantic (`BriefResponse`) y `TypedDict` para la configuración.
- Librerías externas: `requests`, `pandas`, `yfinance`, `mplfinance`, `matplotlib`, `fastapi`.

## Cómo ejecutar localmente

- Arrancar servidor:
  - `uvicorn main:app --reload`
- Probar endpoint:
  - `curl http://127.0.0.1:8000/briefing`
- Respuesta: JSON con `mensaje` (texto del informe) e `imagen_base64` (PNG codificado).
