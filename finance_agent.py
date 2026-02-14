import logging
from dataclasses import dataclass
from typing import Dict, Optional, Tuple

import numpy as np
import pandas as pd
import yfinance as yf

# Günlükleme ayarı
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("FinanceAgent")


@dataclass
class AnalysisConfig:
    rsi_period: int = 14
    short_sma: int = 20
    long_sma: int = 50
    ema_fast: int = 12
    ema_slow: int = 26
    ema_signal: int = 9


def _safe_float(value: Optional[float], default: float = 0.0) -> float:
    if value is None or pd.isna(value):
        return default
    return float(value)


def get_stock_data(symbol: str, period: str = "6mo", config: AnalysisConfig = AnalysisConfig()) -> Tuple[Optional[pd.DataFrame], float]:
    """
    Veriyi indirir, temizler ve teknik analiz göstergelerini hesaplar.
    """
    try:
        logger.info("📥 %s için veriler çekiliyor...", symbol)
        df = yf.download(symbol, period=period, interval="1d", auto_adjust=True, progress=False)

        if df.empty:
            raise ValueError(f"'{symbol}' için veri bulunamadı.")

        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)

        df = df.dropna(subset=["Open", "High", "Low", "Close"]).copy()

        # Hareketli Ortalamalar
        df["SMA20"] = df["Close"].rolling(window=config.short_sma, min_periods=config.short_sma).mean()
        df["SMA50"] = df["Close"].rolling(window=config.long_sma, min_periods=config.long_sma).mean()

        # RSI
        delta = df["Close"].diff()
        gain = delta.where(delta > 0, 0.0)
        loss = -delta.where(delta < 0, 0.0)
        avg_gain = gain.ewm(alpha=1 / config.rsi_period, min_periods=config.rsi_period, adjust=False).mean()
        avg_loss = loss.ewm(alpha=1 / config.rsi_period, min_periods=config.rsi_period, adjust=False).mean()
        rs = avg_gain / avg_loss.replace(0, np.nan)
        df["RSI"] = 100 - (100 / (1 + rs))
        df["RSI"] = df["RSI"].fillna(50)

        # MACD
        ema_fast = df["Close"].ewm(span=config.ema_fast, adjust=False).mean()
        ema_slow = df["Close"].ewm(span=config.ema_slow, adjust=False).mean()
        df["MACD"] = ema_fast - ema_slow
        df["MACD_SIGNAL"] = df["MACD"].ewm(span=config.ema_signal, adjust=False).mean()
        df["MACD_HIST"] = df["MACD"] - df["MACD_SIGNAL"]

        # Volatilite
        df["Returns"] = df["Close"].pct_change()
        volatility = _safe_float(df["Returns"].std() * np.sqrt(252) * 100)

        return df, volatility

    except Exception as e:
        logger.error("❌ Veri çekme hatası: %s", e)
        return None, 0.0


def advanced_analysis(df: Optional[pd.DataFrame], vol: float) -> Dict[str, float | str]:
    """
    Finance Agent'ın karar verme motoru.
    Verileri yorumlar ve strateji üretir.
    """
    if df is None or len(df) < 50:
        return {
            "symbol_name": "Varlık Analizi",
            "last_price": 0.0,
            "change_pct": 0.0,
            "rsi": 50.0,
            "volatility": vol,
            "decision": "VERİ YETERSİZ",
            "comment": "Analiz için en az 50 günlük veri gerekli.",
            "risk_level": "Yüksek",
            "trend_strength": "Zayıf",
        }

    last_close = _safe_float(df["Close"].iloc[-1])
    first_close = _safe_float(df["Close"].iloc[0], last_close)
    rsi = _safe_float(df["RSI"].iloc[-1], 50)
    sma20 = _safe_float(df["SMA20"].iloc[-1], last_close)
    sma50 = _safe_float(df["SMA50"].iloc[-1], last_close)
    macd = _safe_float(df["MACD"].iloc[-1])
    macd_signal = _safe_float(df["MACD_SIGNAL"].iloc[-1])

    change_pct = 0.0 if first_close == 0 else ((last_close - first_close) / first_close) * 100

    decision = "TUT / İZLE"
    comment = "Piyasada net bir yön yok. Bekle-gör stratejisi uygun."
    risk = "Orta"
    trend_strength = "Nötr"

    bullish_macd = macd > macd_signal

    if rsi < 30 and bullish_macd:
        decision = "GÜÇLÜ AL"
        comment = "Aşırı satım bölgesinden dönüş sinyali var. Kademeli toplama değerlendirilebilir."
        trend_strength = "Orta"
    elif rsi > 70 and not bullish_macd:
        decision = "GÜÇLÜ SAT"
        comment = "Aşırı alım + zayıflayan momentum birlikte görülüyor. Kar realizasyonu düşünülebilir."
        risk = "Yüksek"
        trend_strength = "Zayıflıyor"
    elif last_close > sma20 and sma20 > sma50 and bullish_macd:
        decision = "KADEMELİ AL"
        comment = "Kısa ve orta vadede yükseliş yapısı korunuyor, momentum pozitif."
        trend_strength = "Güçlü"
    elif last_close < sma20 and sma20 < sma50:
        decision = "ZAYIF GÖRÜNÜM"
        comment = "Fiyat ortalamaların altında. Düşüş trendinde temkinli kalınmalı."
        risk = "Yüksek"
        trend_strength = "Zayıf"

    return {
        "symbol_name": "Varlık Analizi",
        "last_price": last_close,
        "change_pct": change_pct,
        "rsi": rsi,
        "volatility": _safe_float(vol),
        "decision": decision,
        "comment": comment,
        "risk_level": risk,
        "trend_strength": trend_strength,
    }
