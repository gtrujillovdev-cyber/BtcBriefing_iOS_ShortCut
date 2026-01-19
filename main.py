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
import mplfinance as mpf
import pandas as pd
import yfinance as yf
from xml.etree import ElementTree
from matplotlib.lines import Line2D

app = FastAPI()

class BriefResponse(BaseModel):
    mensaje: str
    imagen_base64: str

# --- HEADERS ---
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

# --- HERRAMIENTA EXTRA: ACORTADOR DE URLS ---
def make_tiny(url):
    try:
        # Usamos la API pública de TinyURL para limpiar el enlace
        api_url = f"http://tinyurl.com/api-create.php?url={url}"
        r = requests.get(api_url, timeout=2)
        return r.text
    except:
        # Si falla el acortador, devolvemos el enlace original aunque sea largo
        return url

# --- 1. MOTOR CRYPTO ---
def get_crypto_data():
    try:
        url = "https://min-api.cryptocompare.com/data/v2/histoday?fsym=BTC&tsym=USD&limit=800"
        r = requests.get(url, headers=HEADERS, timeout=10)
        data = r.json()
        df = pd.DataFrame(data['Data']['Data'])
        df['time'] = pd.to_datetime(df['time'], unit='s')
        df = df.set_index('time')
        df = df[['open', 'high', 'low', 'close', 'volumefrom']]
        df.columns = ['Open', 'High', 'Low', 'Close', 'Volume']
        
        current = df['Close'].iloc[-1]
        ath = df['High'].max()
        df['SMA_730'] = df['Close'].rolling(730).mean()
        
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        return df, {
            "price": current,
            "chg": ((current - df['Close'].iloc[-2]) / df['Close'].iloc[-2]) * 100,
            "ath_dist": ((current - ath) / ath) * 100,
            "rsi": df['RSI'].iloc[-1],
            "sma_2y": df['SMA_730'].iloc[-1],
            "range_low": df['Low'].tail(60).min()
        }
    except:
        return pd.DataFrame(), {}

# --- 2. MOTOR STOCKS ---
def get_market_data():
    tickers = {
        "ETH-USD": "Ethereum",
        "MSTR": "MicroStrategy",
        "^GSPC": "S&P 500",
        "^NDX": "Nasdaq 100",
        "GC=F": "Oro (Gold)" 
    }
    results = {}
    try:
        data = yf.Tickers(" ".join(tickers.keys()))
        for symbol, name in tickers.items():
            try:
                info = data.tickers[symbol].fast_info
                price = info['last_price']
                prev = info['previous_close']
                chg = ((price - prev) / prev) * 100
                results[name] = (price, chg)
            except:
                results[name] = (0, 0)
        return results
    except:
        return {k: (0,0) for k in tickers.values()}

# --- 3. NOTICIAS (ESPAÑOL + TINYURL) ---
def get_clean_news():
    try:
        url = "https://news.google.com/rss/search?q=Bitcoin+OR+Criptomonedas+OR+Mercados&hl=es&gl=ES&ceid=ES:es"
        r = requests.get(url, headers=HEADERS, timeout=5)
        root = ElementTree.fromstring(r.content)
        items = root.findall('./channel/item')[:3] # Limitamos a 3 para no saturar
        
        formatted = []
        for item in items:
            title = item.find('title').text.split(' - ')[0]
            long_link = item.find('link').text
            
            # ¡MAGIA! Acortamos el enlace
            short_link = make_tiny(long_link)
            
            formatted.append(f"🔹 {title}\n   👉 {short_link}")
        
        if not formatted: return "Sin noticias."
        return "\n\n".join(formatted)
    except Exception as e:
        return f"Error news: {str(e)}"

# --- 4. REDACTOR ---
def get_analysis(rsi, price, sma):
    trend = "ALCISTA 🐂" if price > sma else "BAJISTA 🐻"
    if rsi > 70: sent = "⚠️ SOBRECOMPRA: Riesgo de corrección a corto plazo."
    elif rsi < 30: sent = "💎 OPORTUNIDAD: Zona de rebote técnico."
    else: sent = "⚖️ NEUTRAL: Mercado consolidando niveles."
    return f"{sent} Tendencia de fondo (2Y): {trend}"

@app.get("/briefing", response_model=BriefResponse)
def briefing():
    try:
        df, btc = get_crypto_data()
        if df.empty: return BriefResponse(mensaje="Error Datos", imagen_base64="")
        
        mk = get_market_data()
        news = get_clean_news()
        analisis = get_analysis(btc['rsi'], btc['price'], btc['sma_2y'])
        date = datetime.now().strftime('%d %b')

        msg = f"""
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

• RSI (14): {btc['rsi']:.1f}
• Media 2A: ${btc['sma_2y']:,.0f}
• Soporte: ${btc['range_low']:,.0f}

4️⃣ *TITULARES*

{news}
"""
        buf = io.BytesIO()
        plot_df = df.tail(150)
        
        mc = mpf.make_marketcolors(up='#00ff00', down='#ff3333', inherit=True)
        s = mpf.make_mpf_style(base_mpf_style='nightclouds', marketcolors=mc, gridstyle=':') 
        
        ap = []
        if not plot_df['SMA_730'].isnull().all():
            ap.append(mpf.make_addplot(plot_df['SMA_730'], color='orange', width=2))
            
        fig, axlist = mpf.plot(plot_df, type='candle', style=s, mav=(20), volume=True,
                addplot=ap,
                hlines=dict(hlines=[btc['range_low']], colors=['cyan'], linestyle='--'),
                title=f"BTC/USD | {date}",
                panel_ratios=(4,1), returnfig=True,
                savefig=dict(fname=buf, dpi=100, bbox_inches='tight'))
        
        ax = axlist[0]
        handles = [
            Line2D([0], [0], color='orange', lw=2, label='SMA 2Y'),
            Line2D([0], [0], color='cyan', lw=1.5, linestyle='--', label='Soporte'),
            Line2D([0], [0], color='white', lw=1, label='SMA 20')
        ]
        ax.legend(handles=handles, loc='upper left', fontsize='x-small', facecolor='#333333', labelcolor='white')
        
        fig.savefig(buf, bbox_inches='tight')
        buf.seek(0)
        img_b64 = base64.b64encode(buf.read()).decode('utf-8')

        return BriefResponse(mensaje=msg, imagen_base64=img_b64)

    except Exception as e:
        return BriefResponse(mensaje=f"Error V17.5: {str(e)}", imagen_base64="")
