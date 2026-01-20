
from typing import Mapping, TypedDict, Any, cast
from fastapi import FastAPI
from pydantic import BaseModel
import io
import base64
from datetime import datetime
import requests
import os
os.environ['MPLCONFIGDIR'] = '/tmp/matplotlib'
import matplotlib
matplotlib.use('Agg')
import mplfinance as mpf  # type: ignore
import pandas as pd
import yfinance as yf  # type: ignore
from xml.etree import ElementTree
from matplotlib.lines import Line2D
from matplotlib.figure import Figure
from matplotlib.axes import Axes

app = FastAPI()

class BriefResponse(BaseModel):
    mensaje: str
    imagen_base64: str

class ApiConfig(TypedDict):
    crypto_url: str
    news_url: str
    tinyurl_api: str
    headers: dict[str, str]

class ChartConfig(TypedDict):
    style: str
    colors: dict[str, str | bool]
    grid: str
    sma_color: str
    support_color: str

class AppConfig(TypedDict):
    api: ApiConfig
    tickers: dict[str, str]
    params: dict[str, int]
    chart: ChartConfig

# --- CONFIGURACIÓN CENTRALIZADA ---
CONFIG: AppConfig = {
    "api": {
        "crypto_url": "https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=800",
        "news_url": "https://news.google.com/rss/search?q=Bitcoin+OR+Criptomonedas+OR+Mercados&hl=es&gl=ES&ceid=ES:es",
        "tinyurl_api": "http://tinyurl.com/api-create.php?url={url}",
        "headers": {
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
    },
    "tickers": {
        "ETH-USD": "Ethereum",
        "MSTR": "MicroStrategy",
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq 100",
        "GC=F": "Oro (Gold)"
    },
    "params": {
        "sma_period": 730,
        "rsi_period": 14,
        "support_range_days": 60,
        "plot_range_days": 150
    },
    "chart": {
        "style": "nightclouds",
        "colors": {'up': '#00ff00', 'down': '#ff3333', 'inherit': True},
        "grid": ":",
        "sma_color": "orange",
        "support_color": "cyan"
    }
}

# --- HERRAMIENTA EXTRA: ACORTADOR DE URLS ---

def make_tiny(url: str) -> str:
    try:
        # Usamos la API pública de TinyURL para limpiar el enlace
        api_url = CONFIG['api']['tinyurl_api'].format(url=url)
        r = requests.get(api_url, timeout=2)
        return r.text
    except Exception:
        # Si falla el acortador, devolvemos el enlace original aunque sea largo
        return url


# --- 1. MOTOR CRYPTO ---

def get_crypto_data() -> tuple[pd.DataFrame, dict[str, float]]:
    try:
        url = CONFIG['api']['crypto_url']
        r = requests.get(url, headers=CONFIG['api']['headers'], timeout=10)
        data = r.json()

        df: pd.DataFrame = pd.DataFrame(data['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index('time')
        df = df[['open', 'high', 'low', 'close', 'volumefrom']]
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        for col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').astype(float)  # type: ignore

        current: float = float(df['Close'].iloc[-1])
        ath: float = float(df['High'].max())

        # Medias y RSI
        df['SMA'] = df['Close'].rolling(CONFIG['params']['sma_period']).mean()

        delta: pd.Series = df['Close'].diff()
        gain: pd.Series = delta.clip(lower=0).rolling(CONFIG['params']['rsi_period']).mean()
        loss: pd.Series = (-delta).clip(lower=0).rolling(CONFIG['params']['rsi_period']).mean()

        # Evitamos la división por cero en el cálculo de RSI añadiendo un pequeño epsilon
        loss_safe: pd.Series = loss.copy()
        loss_safe[loss_safe == 0] = 1e-10
        rs: pd.Series = gain / loss_safe
        df['RSI'] = 100 - (100 / (1 + rs))

        return df, {
            "price": current,
            "chg": ((current - float(df['Close'].iloc[-2])) / float(df['Close'].iloc[-2])) * 100,
            "ath_dist": ((current - ath) / ath) * 100,
            "rsi": float(df['RSI'].iloc[-1]),
            "sma_2y": float(df['SMA'].iloc[-1]),
            "range_low": float(df['Low'].tail(CONFIG['params']['support_range_days']).min()),
        }
    except Exception as e:
        print(f"Error in get_crypto_data: {e}")
        return pd.DataFrame(), {}


# --- 2. MOTOR STOCKS ---

def get_market_data() -> dict[str, tuple[float, float]]:
    tickers: dict[str, str] = CONFIG['tickers']
    results: dict[str, tuple[float, float]] = {}
    try:
        data = yf.Tickers(" ".join(tickers.keys()))
        for symbol, name in tickers.items():
            try:
                info = data.tickers[symbol].fast_info  # type: ignore[attr-defined]
                price = float(info['last_price'])
                prev = float(info['previous_close'])
                chg = ((price - prev) / prev) * 100
                results[name] = (price, chg)
            except Exception as e:
                print(f"Error fetching {name}: {e}")
                results[name] = (0.0, 0.0)
        return results
    except Exception as e:
        print(f"Error in get_market_data: {e}")
        return {k: (0.0, 0.0) for k in tickers.values()}


# --- 3. NOTICIAS (ESPAÑOL + TINYURL) ---

def get_clean_news() -> str:
    try:
        url = CONFIG['api']['news_url']
        r = requests.get(url, headers=CONFIG['api']['headers'], timeout=5)
        root = ElementTree.fromstring(r.content)
        items = root.findall('./channel/item')[:3]  # Limitamos a 3 para no saturar

        formatted: list[str] = []
        for item in items:
            title_element = item.find('title')
            title = title_element.text.split(' - ')[0] if title_element is not None and title_element.text else ""
            link_element = item.find('link')
            long_link = link_element.text if link_element is not None and link_element.text else ""

            # ¡MAGIA! Acortamos el enlace
            short_link = make_tiny(long_link)
            formatted.append(f"🔹 {title}\n   👉 {short_link}")

        if not formatted:
            return "Sin noticias."
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error news: {str(e)}"

# --- 4. REDACTOR ---

def get_analysis(rsi: float, price: float, sma: float) -> str:
    trend = "ALCISTA 🐂" if price > sma else "BAJISTA 🐻"
    if rsi > 70:
        sent = "⚠️ SOBRECOMPRA: Riesgo de corrección a corto plazo."
    elif rsi < 30:
        sent = "💎 OPORTUNIDAD: Zona de rebote técnico."
    else:
        sent = "⚖️ NEUTRAL: Mercado consolidando niveles."
    return f"{sent} Tendencia de fondo ({CONFIG['params']['sma_period']}d): {trend}"

def format_briefing_message(date: str, analisis: str, btc: dict[str, float], mk: Mapping[str, tuple[float, float]], news: str) -> str:
    return f"""
🇪🇸 *INFORME V17.5 – {date}*

1️⃣ *SITUACIÓN*

{analisis}

2️⃣ *ACTIVOS CLAVE*

• ₿ BTC: ${btc['price']:,.0f} ({btc['chg']:+.2f}%)
• Ξ ETH: ${mk['Ethereum'][0]:,.0f} ({mk['Ethereum'][1]:+.2f}%)
• 🏢 MSTR: ${mk['MicroStrategy'][0]:.2f} ({mk['MicroStrategy'][1]:+.2f}%)
• 🏛 SP500: {mk['S&P 500'][0]:,.0f} ({mk['S&P 500'][1]:+.2f}%)
• 💻 NDX: {mk['Nasdaq 100'][0]:,.0f} ({mk['Nasdaq 100'][1]:+.2f}%)
• 🥇 ORO: ${mk['Oro (Gold)'][0]:,.0f}

3️⃣ *TÉCNICO BTC*

• RSI (14d): {btc['rsi']:.1f}
• Media ({CONFIG['params']['sma_period']}d): ${btc['sma_2y']:,.0f}
• Soporte ({CONFIG['params']['support_range_days']}d): ${btc['range_low']:,.0f}

4️⃣ *TITULARES*

{news}
"""

def generate_briefing_chart(df: pd.DataFrame, btc_data: dict[str, float], date: str) -> str:
    try:
        buf = io.BytesIO()
        plot_df = df.tail(CONFIG['params']['plot_range_days'])

        chart_config = CONFIG['chart']
        mc: Any = mpf.make_marketcolors(  # type: ignore
            up=chart_config['colors']['up'],
            down=chart_config['colors']['down'],
            inherit=chart_config['colors']['inherit'],
        )
        s: Any = mpf.make_mpf_style(  # type: ignore
            base_mpf_style=chart_config['style'],
            marketcolors=mc,
            gridstyle=chart_config['grid'],
        )

        ap: list[dict[str, Any]] = []
        if not plot_df['SMA'].isnull().all():
            ap.append(cast(dict[str, Any], mpf.make_addplot(plot_df['SMA'], color=chart_config['sma_color'], width=2)))  # type: ignore

        fig: Figure
        axlist: list[Axes]
        fig, axlist = cast(
            tuple[Figure, list[Axes]],
            mpf.plot(  # type: ignore
                plot_df,
                type='candle',
                style=s,
                mav=(20),
                volume=True,
                addplot=ap,
                hlines=dict(hlines=[btc_data['range_low']], colors=[chart_config['support_color']], linestyle='--'),
                title=f"BTC/USD | {date}",
                panel_ratios=(4, 1),
                returnfig=True,
            ),
        )

        ax: Axes = axlist[0]
        handles = [
            Line2D([0], [0], color=chart_config['sma_color'], lw=2, label=f"SMA {CONFIG['params']['sma_period']}d"),
            Line2D([0], [0], color=chart_config['support_color'], lw=1.5, linestyle='--', label=f"Soporte {CONFIG['params']['support_range_days']}d"),
            Line2D([0], [0], color='white', lw=1, label='SMA 20d'),
        ]
        ax.legend(handles=handles, loc='upper left', fontsize='x-small', facecolor='#333333', labelcolor='white')  # type: ignore

        fig.savefig(buf, format='png', bbox_inches='tight', dpi=100)  # type: ignore
        buf.seek(0)
        return base64.b64encode(buf.read()).decode('utf-8')
    except Exception as e:
        print(f"Error generating chart: {e}")
        return ""

@app.get("/briefing", response_model=BriefResponse)
def briefing() -> BriefResponse:
    try:
        # 1. Recopilación de Datos
        df, btc_data = get_crypto_data()
        if df.empty:
            return BriefResponse(mensaje="Error al obtener datos de BTC.", imagen_base64="")

        market_data = get_market_data()
        news = get_clean_news()

        # 2. Análisis y Formateo
        analysis = get_analysis(btc_data['rsi'], btc_data['price'], btc_data['sma_2y'])
        date_str = datetime.now().strftime('%d %b')
        message = format_briefing_message(date_str, analysis, btc_data, market_data, news)

        # 3. Generación de Gráfico
        img_b64 = generate_briefing_chart(df, btc_data, date_str)
        if not img_b64:
            return BriefResponse(mensaje="Error al generar el gráfico. El informe de texto está disponible.", imagen_base64="")

        return BriefResponse(mensaje=message, imagen_base64=img_b64)

    except Exception as e:
        # Error general catastrófico
        return BriefResponse(mensaje=f"Error V17.5: {str(e)}", imagen_base64="")
