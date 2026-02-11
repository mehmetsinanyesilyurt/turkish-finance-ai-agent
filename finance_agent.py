import logging
import yfinance as yf
import pandas as pd
import numpy as np

# Günlükleme ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinanceAgent")

def get_stock_data(symbol: str, period: str = "6mo"):
    """
    Veriyi indirir, temizler ve teknik analiz göstergelerini hesaplar.
    """
    try:
        logger.info(f"📥 {symbol} için veriler çekiliyor...")
        # auto_adjust=True fiyat bölünmelerini otomatik düzeltir
        df = yf.download(symbol, period=period, interval="1d", auto_adjust=True, progress=False)
        
        if df.empty:
            raise ValueError(f"'{symbol}' için veri bulunamadı.")

        # Yfinance Multi-Index sütun hatasını gider
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        # --- TEKNİK HESAPLAMALAR ---
        # 1. Hareketli Ortalamalar
        df['SMA20'] = df['Close'].rolling(window=20).mean()
        df['SMA50'] = df['Close'].rolling(window=50).mean()

        # 2. RSI (Göreceli Güç Endeksi)
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))

        # 3. Volatilite (Yıllıklandırılmış)
        df['Returns'] = df['Close'].pct_change()
        volatility = df['Returns'].std() * np.sqrt(252) * 100

        return df, volatility

    except Exception as e:
        logger.error(f"❌ Veri çekme hatası: {e}")
        return None, 0

def advanced_analysis(df, vol):
    """
    Finance Agent'ın karar verme motoru. 
    Verileri yorumlar ve strateji üretir.
    """
    if df is None or len(df) < 50:
        return {"decision": "VERİ YETERSİZ", "comment": "Analiz için en az 50 günlük veri gerekli.", "risk": "Yüksek"}

    last_close = float(df['Close'].iloc[-1])
    first_close = float(df['Close'].iloc[0])
    rsi = float(df['RSI'].iloc[-1])
    sma20 = float(df['SMA20'].iloc[-1])
    sma50 = float(df['SMA50'].iloc[-1])
    
    change_pct = ((last_close - first_close) / first_close) * 100
    
    # --- KARAR MANTIĞI ---
    decision = "TUT / İZLE"
    comment = "Piyasada net bir yön yok. Bekle-gör stratejisi uygun."
    risk = "Orta"

    if rsi < 32:
        decision = "GÜÇLÜ AL"
        comment = "Fiyat aşırı satım bölgesinde ve tepki alımları bekleniyor. Teknik dip oluşumu var."
    elif rsi > 68:
        decision = "GÜÇLÜ SAT"
        comment = "Fiyat aşırı alım bölgesinde yorgunluk belirtileri gösteriyor. Kar realizasyonu yapılabilir."
        risk = "Yüksek"
    elif last_close > sma20 and sma20 > sma50:
        decision = "KADEMELİ AL"
        comment = "Trend yukarı yönlü güçleniyor (Altın Kesişim yaklaşıyor). İvme pozitif."
    elif last_close < sma20:
        decision = "ZAYIF GÖRÜNÜM"
        comment = "Fiyat kısa vadeli ortalamanın altına sarktı. Satış baskısı artabilir."
        risk = "Yüksek"

    return {
        "symbol_name": "Varlık Analizi",
        "last_price": last_close,
        "change_pct": change_pct,
        "rsi": rsi,
        "volatility": vol,
        "decision": decision,
        "comment": comment,
        "risk_level": risk
    }
