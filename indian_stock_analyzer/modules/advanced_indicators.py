"""
Advanced Technical Indicators Module
Additional indicators for better analysis
"""

import pandas as pd
import numpy as np

class AdvancedIndicators:
    def __init__(self):
        pass
    
    def calculate_vwap(self, data):
        """Volume Weighted Average Price"""
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        vwap = (typical_price * data['Volume']).cumsum() / data['Volume'].cumsum()
        return vwap
    
    def calculate_fibonacci_retracement(self, data, period=100):
        """Fibonacci Retracement Levels"""
        high = data['High'].rolling(window=period).max()
        low = data['Low'].rolling(window=period).min()
        diff = high - low
        
        levels = pd.DataFrame(index=data.index)
        levels['Fib_0'] = high
        levels['Fib_23.6'] = high - (diff * 0.236)
        levels['Fib_38.2'] = high - (diff * 0.382)
        levels['Fib_50'] = high - (diff * 0.5)
        levels['Fib_61.8'] = high - (diff * 0.618)
        levels['Fib_78.6'] = high - (diff * 0.786)
        levels['Fib_100'] = low
        
        return levels
    
    def calculate_super_trend(self, data, period=10, multiplier=3):
        """SuperTrend Indicator"""
        hl2 = (data['High'] + data['Low']) / 2
        atr = self._calculate_atr(data, period)
        
        upper_band = hl2 + (multiplier * atr)
        lower_band = hl2 - (multiplier * atr)
        
        super_trend = pd.Series(index=data.index)
        direction = pd.Series(index=data.index)
        
        for i in range(len(data)):
            if i == 0:
                super_trend.iloc[i] = upper_band.iloc[i]
                direction.iloc[i] = 1  # 1 = bullish, -1 = bearish
            else:
                if data['Close'].iloc[i] > super_trend.iloc[i-1]:
                    direction.iloc[i] = 1
                    super_trend.iloc[i] = max(lower_band.iloc[i], super_trend.iloc[i-1])
                else:
                    direction.iloc[i] = -1
                    super_trend.iloc[i] = min(upper_band.iloc[i], super_trend.iloc[i-1])
        
        return super_trend, direction
    
    def _calculate_atr(self, data, period=14):
        """Average True Range"""
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr
    
    def calculate_ichimoku_cloud(self, data):
        """Ichimoku Cloud"""
        # Tenkan-sen (Conversion Line): (9-period high + 9-period low)/2
        period9_high = data['High'].rolling(window=9).max()
        period9_low = data['Low'].rolling(window=9).min()
        tenkan_sen = (period9_high + period9_low) / 2
        
        # Kijun-sen (Base Line): (26-period high + 26-period low)/2
        period26_high = data['High'].rolling(window=26).max()
        period26_low = data['Low'].rolling(window=26).min()
        kijun_sen = (period26_high + period26_low) / 2
        
        # Senkou Span A (Leading Span A): (Conversion Line + Base Line)/2
        senkou_span_a = ((tenkan_sen + kijun_sen) / 2).shift(26)
        
        # Senkou Span B (Leading Span B): (52-period high + 52-period low)/2
        period52_high = data['High'].rolling(window=52).max()
        period52_low = data['Low'].rolling(window=52).min()
        senkou_span_b = ((period52_high + period52_low) / 2).shift(26)
        
        # Chikou Span (Lagging Span): Close shifted back 26 periods
        chikou_span = data['Close'].shift(-26)
        
        return {
            'tenkan_sen': tenkan_sen,
            'kijun_sen': kijun_sen,
            'senkou_span_a': senkou_span_a,
            'senkou_span_b': senkou_span_b,
            'chikou_span': chikou_span
        }
    
    def calculate_pivot_points(self, data):
        """Pivot Points (Classic)"""
        pivot = (data['High'] + data['Low'] + data['Close']) / 3
        
        r1 = (2 * pivot) - data['Low']
        r2 = pivot + (data['High'] - data['Low'])
        r3 = r2 + (data['High'] - data['Low'])
        
        s1 = (2 * pivot) - data['High']
        s2 = pivot - (data['High'] - data['Low'])
        s3 = s2 - (data['High'] - data['Low'])
        
        return {
            'pivot': pivot,
            'r1': r1, 'r2': r2, 'r3': r3,
            's1': s1, 's2': s2, 's3': s3
        }
    
    def calculate_williams_r(self, data, period=14):
        """Williams %R"""
        highest_high = data['High'].rolling(window=period).max()
        lowest_low = data['Low'].rolling(window=period).min()
        
        williams_r = -100 * ((highest_high - data['Close']) / (highest_high - lowest_low))
        return williams_r
    
    def calculate_mfi(self, data, period=14):
        """Money Flow Index"""
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        raw_money_flow = typical_price * data['Volume']
        
        money_flow_sign = np.where(typical_price > typical_price.shift(1), 1, -1)
        signed_money_flow = raw_money_flow * money_flow_sign
        
        positive_flow = pd.Series(signed_money_flow).rolling(window=period).apply(
            lambda x: x[x > 0].sum(), raw=True
        )
        negative_flow = pd.Series(signed_money_flow).rolling(window=period).apply(
            lambda x: abs(x[x < 0].sum()), raw=True
        )
        
        money_ratio = positive_flow / negative_flow
        mfi = 100 - (100 / (1 + money_ratio))
        
        return mfi
    
    def calculate_cmo(self, data, period=14):
        """Chande Momentum Oscillator"""
        diff = data['Close'].diff()
        sum_gains = diff.where(diff > 0, 0).rolling(window=period).sum()
        sum_losses = abs(diff.where(diff < 0, 0).rolling(window=period).sum())
        
        cmo = 100 * ((sum_gains - sum_losses) / (sum_gains + sum_losses))
        return cmo
    
    def calculate_all_advanced(self, data):
        """Calculate all advanced indicators"""
        indicators = pd.DataFrame(index=data.index)
        indicators['Date'] = data.index
        indicators['Close'] = data['Close']
        
        # VWAP
        indicators['VWAP'] = self.calculate_vwap(data)
        
        # SuperTrend
        indicators['SuperTrend'], indicators['SuperTrend_Direction'] = self.calculate_super_trend(data)
        
        # Fibonacci
        fib_levels = self.calculate_fibonacci_retracement(data)
        for col in fib_levels.columns:
            indicators[f'Fib_{col}'] = fib_levels[col]
        
        # Ichimoku
        ichimoku = self.calculate_ichimoku_cloud(data)
        for key, value in ichimoku.items():
            indicators[key] = value
        
        # Pivot Points
        pivot = self.calculate_pivot_points(data)
        for key, value in pivot.items():
            indicators[f'Pivot_{key}'] = value
        
        # Williams %R
        indicators['Williams_R'] = self.calculate_williams_r(data)
        
        # MFI
        indicators['MFI'] = self.calculate_mfi(data)
        
        # CMO
        indicators['CMO'] = self.calculate_cmo(data)
        
        # NEW INDICATORS
        # ADX (Average Directional Index)
        indicators['ADX'] = self.calculate_adx(data)
        indicators['ADX_Plus_DI'] = self.calculate_adx(data, return_di=True)[0]
        indicators['ADX_Minus_DI'] = self.calculate_adx(data, return_di=True)[1]
        
        # OBV (On-Balance Volume)
        indicators['OBV'] = self.calculate_obv(data)
        
        # Stochastic Oscillator
        indicators['Stochastic_K'], indicators['Stochastic_D'] = self.calculate_stochastic(data)
        
        # CCI (Commodity Channel Index)
        indicators['CCI'] = self.calculate_cci(data)
        
        # ATR (Average True Range)
        indicators['ATR'] = self._calculate_atr(data)
        
        # EMA Crossovers
        indicators['EMA_12'] = data['Close'].ewm(span=12).mean()
        indicators['EMA_26'] = data['Close'].ewm(span=26).mean()
        indicators['EMA_50'] = data['Close'].ewm(span=50).mean()
        indicators['EMA_200'] = data['Close'].ewm(span=200).mean()
        
        # Parabolic SAR
        indicators['Parabolic_SAR'] = self.calculate_parabolic_sar(data)
        
        # Donchian Channels
        indicators['Donchian_Upper'], indicators['Donchian_Lower'], indicators['Donchian_Middle'] = self.calculate_donchian_channels(data)
        
        # Rate of Change
        indicators['ROC_10'] = ((data['Close'] - data['Close'].shift(10)) / data['Close'].shift(10)) * 100
        indicators['ROC_20'] = ((data['Close'] - data['Close'].shift(20)) / data['Close'].shift(20)) * 100
        
        # TRIX
        indicators['TRIX'] = self.calculate_trix(data)
        
        # Keltner Channels
        indicators['Keltner_Upper'], indicators['Keltner_Middle'], indicators['Keltner_Lower'] = self.calculate_keltner_channels(data)
        
        return indicators
    
    def get_support_resistance(self, data, window=20):
        """Find support and resistance levels"""
        recent_data = data.tail(window)
        
        # Local minima and maxima
        lows = recent_data['Low'].nsmallest(3)
        highs = recent_data['High'].nlargest(3)
        
        support = lows.mean()
        resistance = highs.mean()
        
        return {
            'support': round(support, 2),
            'resistance': round(resistance, 2),
            'support_levels': lows.tolist(),
            'resistance_levels': highs.tolist()
        }
    
    def calculate_adx(self, data, period=14, return_di=False):
        """Average Directional Index"""
        high = data['High']
        low = data['Low']
        close = data['Close']
        
        plus_dm = high.diff()
        minus_dm = -low.diff()
        
        plus_dm = plus_dm.where((plus_dm > minus_dm) & (plus_dm > 0), 0)
        minus_dm = minus_dm.where((minus_dm > plus_dm) & (minus_dm > 0), 0)
        
        tr = pd.concat([
            high - low,
            abs(high - close.shift()),
            abs(low - close.shift())
        ], axis=1).max(axis=1)
        
        atr = tr.rolling(window=period).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=period).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=period).mean() / atr)
        
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.rolling(window=period).mean()
        
        if return_di:
            return plus_di, minus_di
        return adx
    
    def calculate_obv(self, data):
        """On-Balance Volume"""
        obv = pd.Series(index=data.index)
        obv.iloc[0] = data['Volume'].iloc[0]
        
        for i in range(1, len(data)):
            if data['Close'].iloc[i] > data['Close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] + data['Volume'].iloc[i]
            elif data['Close'].iloc[i] < data['Close'].iloc[i-1]:
                obv.iloc[i] = obv.iloc[i-1] - data['Volume'].iloc[i]
            else:
                obv.iloc[i] = obv.iloc[i-1]
        
        return obv
    
    def calculate_stochastic(self, data, k_period=14, d_period=3):
        """Stochastic Oscillator"""
        lowest_low = data['Low'].rolling(window=k_period).min()
        highest_high = data['High'].rolling(window=k_period).max()
        
        k = 100 * ((data['Close'] - lowest_low) / (highest_high - lowest_low))
        d = k.rolling(window=d_period).mean()
        
        return k, d
    
    def calculate_cci(self, data, period=20):
        """Commodity Channel Index"""
        tp = (data['High'] + data['Low'] + data['Close']) / 3
        sma_tp = tp.rolling(window=period).mean()
        mean_dev = tp.rolling(window=period).apply(lambda x: abs(x - x.mean()).mean())
        cci = (tp - sma_tp) / (0.015 * mean_dev)
        return cci
    
    def calculate_parabolic_sar(self, data, af=0.02, max_af=0.2):
        """Parabolic SAR"""
        high = data['High']
        low = data['Low']
        
        psar = data['Close'].copy()
        psar_af = pd.Series(index=data.index).fillna(af)
        psar_ep = high.copy()
        psar_trend = pd.Series(index=data.index).fillna(1)
        
        for i in range(1, len(data)):
            if psar_trend.iloc[i-1] == 1:  # Uptrend
                psar.iloc[i] = psar.iloc[i-1] + psar_af.iloc[i-1] * (psar_ep.iloc[i-1] - psar.iloc[i-1])
                if low.iloc[i] < psar.iloc[i]:
                    psar_trend.iloc[i] = -1
                    psar.iloc[i] = psar_ep.iloc[i-1]
                    psar_ep.iloc[i] = low.iloc[i]
                    psar_af.iloc[i] = af
                else:
                    psar_trend.iloc[i] = 1
                    if high.iloc[i] > psar_ep.iloc[i-1]:
                        psar_ep.iloc[i] = high.iloc[i]
                        psar_af.iloc[i] = min(psar_af.iloc[i-1] + af, max_af)
                    else:
                        psar_ep.iloc[i] = psar_ep.iloc[i-1]
                        psar_af.iloc[i] = psar_af.iloc[i-1]
            else:  # Downtrend
                psar.iloc[i] = psar.iloc[i-1] + psar_af.iloc[i-1] * (psar_ep.iloc[i-1] - psar.iloc[i-1])
                if high.iloc[i] > psar.iloc[i]:
                    psar_trend.iloc[i] = 1
                    psar.iloc[i] = psar_ep.iloc[i-1]
                    psar_ep.iloc[i] = high.iloc[i]
                    psar_af.iloc[i] = af
                else:
                    psar_trend.iloc[i] = -1
                    if low.iloc[i] < psar_ep.iloc[i-1]:
                        psar_ep.iloc[i] = low.iloc[i]
                        psar_af.iloc[i] = min(psar_af.iloc[i-1] + af, max_af)
                    else:
                        psar_ep.iloc[i] = psar_ep.iloc[i-1]
                        psar_af.iloc[i] = psar_af.iloc[i-1]
        
        return psar
    
    def calculate_donchian_channels(self, data, period=20):
        """Donchian Channels"""
        upper = data['High'].rolling(window=period).max()
        lower = data['Low'].rolling(window=period).min()
        middle = (upper + lower) / 2
        return upper, lower, middle
    
    def calculate_trix(self, data, period=15):
        """TRIX - Triple Exponential Moving Average"""
        ema1 = data['Close'].ewm(span=period).mean()
        ema2 = ema1.ewm(span=period).mean()
        ema3 = ema2.ewm(span=period).mean()
        trix = (ema3 - ema3.shift(1)) / ema3.shift(1) * 100
        return trix
    
    def calculate_keltner_channels(self, data, period=20, atr_multiplier=2):
        """Keltner Channels"""
        typical_price = (data['High'] + data['Low'] + data['Close']) / 3
        middle = typical_price.rolling(window=period).mean()
        atr = self._calculate_atr(data, period)
        upper = middle + (atr_multiplier * atr)
        lower = middle - (atr_multiplier * atr)
        return upper, middle, lower
    
    def calculate_momentum(self, data, period=10):
        """Momentum Indicator"""
        return data['Close'] - data['Close'].shift(period)
    
    def calculate_awesome_oscillator(self, data):
        """Awesome Oscillator"""
        median_price = (data['High'] + data['Low']) / 2
        sma5 = median_price.rolling(window=5).mean()
        sma34 = median_price.rolling(window=34).mean()
        return sma5 - sma34

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from modules.data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    data = fetcher.fetch_stock_data('RELIANCE.NS', '3mo')
    
    if data is not None:
        adv = AdvancedIndicators()
        indicators = adv.calculate_all_advanced(data)
        print("Advanced Indicators:")
        print(indicators.tail())
        
        sr = adv.get_support_resistance(data)
        print("\nSupport/Resistance:")
        print(sr)
