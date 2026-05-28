"""
Technical Analysis Module
Calculates technical indicators and scores stocks
"""

import pandas as pd
import numpy as np

class TechnicalAnalyzer:
    def __init__(self):
        pass
    
    def calculate_sma(self, data, window):
        """Simple Moving Average"""
        return data['Close'].rolling(window=window).mean()
    
    def calculate_ema(self, data, window):
        """Exponential Moving Average"""
        return data['Close'].ewm(span=window, adjust=False).mean()
    
    def calculate_rsi(self, data, window=14):
        """Relative Strength Index"""
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        return rsi
    
    def calculate_macd(self, data, fast=12, slow=26, signal=9):
        """MACD (Moving Average Convergence Divergence)"""
        ema_fast = self.calculate_ema(data, fast)
        ema_slow = self.calculate_ema(data, slow)
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal, adjust=False).mean()
        histogram = macd_line - signal_line
        return macd_line, signal_line, histogram
    
    def calculate_bollinger_bands(self, data, window=20, num_std=2):
        """Bollinger Bands"""
        sma = self.calculate_sma(data, window)
        std = data['Close'].rolling(window=window).std()
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        return upper_band, sma, lower_band
    
    def calculate_stochastic(self, data, k_window=14, d_window=3):
        """Stochastic Oscillator"""
        low_min = data['Low'].rolling(window=k_window).min()
        high_max = data['High'].rolling(window=k_window).max()
        k_percent = 100 * ((data['Close'] - low_min) / (high_max - low_min))
        d_percent = k_percent.rolling(window=d_window).mean()
        return k_percent, d_percent
    
    def calculate_adx(self, data, window=14):
        """Average Directional Index"""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = pd.DataFrame(high - low)
        tr2 = pd.DataFrame(abs(high - close.shift(1)))
        tr3 = pd.DataFrame(abs(low - close.shift(1)))
        
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=window).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=window).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=window).mean() / atr)
        
        dx = (abs(plus_di - minus_di) / (plus_di + minus_di)) * 100
        adx = dx.rolling(window=window).mean()
        
        return adx, plus_di, minus_di
    
    def calculate_volume_indicators(self, data):
        """Volume-based indicators"""
        # Volume Moving Average
        vol_sma = data['Volume'].rolling(window=20).mean()
        
        # On-Balance Volume (OBV)
        obv = pd.Series(index=data.index)
        obv.iloc[0] = data['Volume'].iloc[0]
        
        for i in range(1, len(data)):
            if data['Close'].iloc[i] > data['Close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + data['Volume'].iloc[i]
            elif data['Close'].iloc[i] < data['Close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - data['Volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return vol_sma, obv
    
    def calculate_all_indicators(self, data):
        """Calculate all technical indicators"""
        indicators = pd.DataFrame(index=data.index)
        indicators['Date'] = data['Date']
        indicators['Close'] = data['Close']
        
        # Moving Averages
        indicators['SMA_20'] = self.calculate_sma(data, 20)
        indicators['SMA_50'] = self.calculate_sma(data, 50)
        indicators['SMA_200'] = self.calculate_sma(data, 200)
        indicators['EMA_12'] = self.calculate_ema(data, 12)
        indicators['EMA_26'] = self.calculate_ema(data, 26)
        
        # RSI
        indicators['RSI'] = self.calculate_rsi(data)
        
        # MACD
        macd, signal, histogram = self.calculate_macd(data)
        indicators['MACD'] = macd
        indicators['MACD_Signal'] = signal
        indicators['MACD_Histogram'] = histogram
        
        # Bollinger Bands
        upper, middle, lower = self.calculate_bollinger_bands(data)
        indicators['BB_Upper'] = upper
        indicators['BB_Middle'] = middle
        indicators['BB_Lower'] = lower
        
        # Stochastic
        k, d = self.calculate_stochastic(data)
        indicators['Stochastic_K'] = k
        indicators['Stochastic_D'] = d
        
        # ADX
        adx, plus_di, minus_di = self.calculate_adx(data)
        indicators['ADX'] = adx
        indicators['Plus_DI'] = plus_di
        indicators['Minus_DI'] = minus_di
        
        # Volume indicators
        vol_sma, obv = self.calculate_volume_indicators(data)
        indicators['Volume_SMA'] = vol_sma
        indicators['OBV'] = obv
        
        return indicators
    
    def score_stock(self, data):
        """Score a stock based on technical indicators (0-100)"""
        if len(data) < 50:
            return 50, {}  # Not enough data
        
        indicators = self.calculate_all_indicators(data)
        latest = indicators.iloc[-1]
        
        score = 0
        reasons = []
        
        # Trend Analysis (30 points)
        # Price above SMA 20, 50, 200
        trend_score = 0
        if latest['Close'] > latest['SMA_20']:
            trend_score += 10
            reasons.append("Price above SMA 20 (bullish)")
        if latest['Close'] > latest['SMA_50']:
            trend_score += 10
            reasons.append("Price above SMA 50 (bullish)")
        if latest['Close'] > latest['SMA_200']:
            trend_score += 10
            reasons.append("Price above SMA 200 (bullish)")
        score += trend_score
        
        # RSI Analysis (20 points)
        rsi = latest['RSI']
        if pd.isna(rsi):
            rsi = 50
        if 40 <= rsi <= 60:
            score += 15
            reasons.append(f"RSI neutral ({rsi:.1f}) - good entry zone")
        elif 60 < rsi <= 70:
            score += 20
            reasons.append(f"RSI bullish ({rsi:.1f})")
        elif rsi > 70:
            score += 10
            reasons.append(f"RSI overbought ({rsi:.1f}) - caution")
        elif 30 <= rsi < 40:
            score += 10
            reasons.append(f"RSI oversold recovery ({rsi:.1f})")
        else:
            score += 5
            reasons.append(f"RSI deeply oversold ({rsi:.1f})")
        
        # MACD Analysis (20 points)
        macd = latest['MACD']
        macd_signal = latest['MACD_Signal']
        macd_hist = latest['MACD_Histogram']
        
        if pd.notna(macd) and pd.notna(macd_signal):
            if macd > macd_signal:
                score += 15
                reasons.append("MACD above signal line (bullish)")
                if pd.notna(macd_hist) and macd_hist > 0:
                    score += 5
                    reasons.append("MACD histogram positive")
            else:
                score += 5
                reasons.append("MACD below signal line (bearish)")
        
        # Bollinger Bands (15 points)
        bb_upper = latest['BB_Upper']
        bb_lower = latest['BB_Lower']
        close = latest['Close']
        
        if pd.notna(bb_upper) and pd.notna(bb_lower):
            bb_position = (close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
            if 0.2 <= bb_position <= 0.8:
                score += 15
                reasons.append("Price in Bollinger middle zone (healthy)")
            elif bb_position < 0.2:
                score += 10
                reasons.append("Price near lower Bollinger band (oversold)")
            else:
                score += 5
                reasons.append("Price near upper Bollinger band (overbought)")
        
        # Volume Analysis (15 points)
        if 'Volume' in data.columns and 'Volume_SMA' in latest.index:
            latest_vol = data['Volume'].iloc[-1]
            vol_sma = latest['Volume_SMA']
            if pd.notna(vol_sma) and vol_sma > 0:
                vol_ratio = latest_vol / vol_sma
                if vol_ratio > 1.5:
                    score += 15
                    reasons.append(f"High volume ({vol_ratio:.1f}x average)")
                elif vol_ratio > 1.0:
                    score += 10
                    reasons.append(f"Above average volume ({vol_ratio:.1f}x)")
                else:
                    score += 5
                    reasons.append(f"Below average volume ({vol_ratio:.1f}x)")
        
        # Ensure score is between 0-100
        score = max(0, min(100, score))
        
        return score, {
            'score': score,
            'rsi': round(rsi, 2) if pd.notna(rsi) else None,
            'macd': round(macd, 4) if pd.notna(macd) else None,
            'macd_signal': round(macd_signal, 4) if pd.notna(macd_signal) else None,
            'sma_20': round(latest['SMA_20'], 2) if pd.notna(latest['SMA_20']) else None,
            'sma_50': round(latest['SMA_50'], 2) if pd.notna(latest['SMA_50']) else None,
            'sma_200': round(latest['SMA_200'], 2) if pd.notna(latest['SMA_200']) else None,
            'adx': round(latest['ADX'], 2) if pd.notna(latest['ADX']) else None,
            'bb_position': round(bb_position, 2) if 'bb_position' in locals() else None,
            'reasons': reasons
        }

if __name__ == "__main__":
    # Test with sample data
    import sys
    sys.path.append('..')
    from modules.data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    data = fetcher.fetch_stock_data('RELIANCE.NS', '1y')
    
    if data is not None:
        analyzer = TechnicalAnalyzer()
        score, details = analyzer.score_stock(data)
        print(f"Score: {score}")
        print(f"Details: {details}")
