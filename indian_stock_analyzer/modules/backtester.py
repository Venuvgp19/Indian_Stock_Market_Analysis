"""
Backtesting Module
Tests trading strategies on historical data
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta

class Backtester:
    def __init__(self):
        self.results = {}
    
    def run_strategy(self, data, strategy_name, **params):
        """Run a backtest strategy"""
        if strategy_name == 'sma_crossover':
            return self._sma_crossover(data, **params)
        elif strategy_name == 'rsi_strategy':
            return self._rsi_strategy(data, **params)
        elif strategy_name == 'macd_strategy':
            return self._macd_strategy(data, **params)
        elif strategy_name == 'bollinger_strategy':
            return self._bollinger_strategy(data, **params)
        elif strategy_name == 'combined':
            return self._combined_strategy(data, **params)
        elif strategy_name == 'adx_strategy':
            return self._adx_strategy(data, **params)
        elif strategy_name == 'supertrend_strategy':
            return self._supertrend_strategy(data, **params)
        elif strategy_name == 'ichimoku_strategy':
            return self._ichimoku_strategy(data, **params)
        elif strategy_name == 'breakout_strategy':
            return self._breakout_strategy(data, **params)
        elif strategy_name == 'mean_reversion':
            return self._mean_reversion_strategy(data, **params)
        elif strategy_name == 'momentum_strategy':
            return self._momentum_strategy(data, **params)
        elif strategy_name == 'multi_timeframe':
            return self._multi_timeframe_strategy(data, **params)
        else:
            return {'error': 'Unknown strategy'}
    
    def _sma_crossover(self, data, short_window=20, long_window=50):
        """SMA Crossover Strategy"""
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['short_mavg'] = data['Close'].rolling(window=short_window).mean()
        signals['long_mavg'] = data['Close'].rolling(window=long_window).mean()
        
        # Generate signals
        signals['signal'] = 0
        signals.loc[signals['short_mavg'] > signals['long_mavg'], 'signal'] = 1
        signals['positions'] = signals['signal'].diff()
        
        # Calculate returns
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'SMA Crossover')
    
    def _rsi_strategy(self, data, rsi_period=14, oversold=30, overbought=70):
        """RSI Strategy"""
        from modules.technical_analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        rsi = analyzer.calculate_rsi(data, rsi_period)
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['rsi'] = rsi
        signals['signal'] = 0
        
        # Buy when oversold, sell when overbought
        signals.loc[signals['rsi'] < oversold, 'signal'] = 1
        signals.loc[signals['rsi'] > overbought, 'signal'] = -1
        
        # Forward fill signals
        signals['signal'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'RSI Strategy')
    
    def _macd_strategy(self, data, fast=12, slow=26, signal=9):
        """MACD Strategy"""
        from modules.technical_analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        macd, signal_line, histogram = analyzer.calculate_macd(data, fast, slow, signal)
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['macd'] = macd
        signals['signal_line'] = signal_line
        signals['histogram'] = histogram
        signals['signal'] = 0
        
        # Buy when MACD crosses above signal line
        signals.loc[signals['macd'] > signals['signal_line'], 'signal'] = 1
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'MACD Strategy')
    
    def _bollinger_strategy(self, data, window=20, num_std=2):
        """Bollinger Bands Strategy"""
        from modules.technical_analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        upper, middle, lower = analyzer.calculate_bollinger_bands(data, window, num_std)
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['upper'] = upper
        signals['lower'] = lower
        signals['middle'] = middle
        signals['signal'] = 0
        
        # Buy when price touches lower band, sell when touches upper
        signals.loc[signals['price'] <= signals['lower'], 'signal'] = 1
        signals.loc[signals['price'] >= signals['upper'], 'signal'] = -1
        
        signals['signal'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'Bollinger Strategy')
    
    def _combined_strategy(self, data):
        """Combined strategy using multiple indicators"""
        from modules.technical_analyzer import TechnicalAnalyzer
        
        analyzer = TechnicalAnalyzer()
        
        # Get indicators
        sma_20 = data['Close'].rolling(window=20).mean()
        sma_50 = data['Close'].rolling(window=50).mean()
        rsi = analyzer.calculate_rsi(data)
        macd, signal_line, _ = analyzer.calculate_macd(data)
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['signal'] = 0
        
        # Combined conditions
        buy_condition = (
            (sma_20 > sma_50) &  # Bullish trend
            (rsi < 60) &         # Not overbought
            (macd > signal_line)  # MACD bullish
        )
        
        sell_condition = (
            (sma_20 < sma_50) &  # Bearish trend
            (rsi > 50) &         # Not oversold
            (macd < signal_line)  # MACD bearish
        )
        
        signals.loc[buy_condition, 'signal'] = 1
        signals.loc[sell_condition, 'signal'] = -1
        
        signals['signal'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'Combined Strategy')
    
    def _adx_strategy(self, data, period=14, adx_threshold=25):
        """ADX Trend Strength Strategy"""
        from modules.advanced_indicators import AdvancedIndicators
        
        adv = AdvancedIndicators()
        adx = adv.calculate_adx(data, period)
        plus_di, minus_di = adv.calculate_adx(data, period, return_di=True)
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['adx'] = adx
        signals['plus_di'] = plus_di
        signals['minus_di'] = minus_di
        signals['signal'] = 0
        
        # Buy when ADX > threshold and +DI > -DI
        buy_condition = (signals['adx'] > adx_threshold) & (signals['plus_di'] > signals['minus_di'])
        sell_condition = (signals['adx'] > adx_threshold) & (signals['plus_di'] < signals['minus_di'])
        
        signals.loc[buy_condition, 'signal'] = 1
        signals.loc[sell_condition, 'signal'] = -1
        signals['signal'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'ADX Strategy')
    
    def _supertrend_strategy(self, data, period=10, multiplier=3):
        """SuperTrend Strategy"""
        from modules.advanced_indicators import AdvancedIndicators
        
        adv = AdvancedIndicators()
        super_trend, direction = adv.calculate_super_trend(data, period, multiplier)
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['super_trend'] = super_trend
        signals['direction'] = direction
        signals['signal'] = 0
        
        # Buy when direction changes to bullish (1), sell when bearish (-1)
        signals.loc[signals['direction'] == 1, 'signal'] = 1
        signals.loc[signals['direction'] == -1, 'signal'] = -1
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'SuperTrend Strategy')
    
    def _ichimoku_strategy(self, data):
        """Ichimoku Cloud Strategy"""
        from modules.advanced_indicators import AdvancedIndicators
        
        adv = AdvancedIndicators()
        ichimoku = adv.calculate_ichimoku_cloud(data)
        
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['tenkan'] = ichimoku['tenkan_sen']
        signals['kijun'] = ichimoku['kijun_sen']
        signals['senkou_a'] = ichimoku['senkou_span_a']
        signals['senkou_b'] = ichimoku['senkou_span_b']
        signals['signal'] = 0
        
        # Buy: Price above cloud, Tenkan > Kijun
        buy_condition = (
            (signals['price'] > signals['senkou_a']) &
            (signals['price'] > signals['senkou_b']) &
            (signals['tenkan'] > signals['kijun'])
        )
        
        # Sell: Price below cloud, Tenkan < Kijun
        sell_condition = (
            (signals['price'] < signals['senkou_a']) &
            (signals['price'] < signals['senkou_b']) &
            (signals['tenkan'] < signals['kijun'])
        )
        
        signals.loc[buy_condition, 'signal'] = 1
        signals.loc[sell_condition, 'signal'] = -1
        signals['signal'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'Ichimoku Strategy')
    
    def _breakout_strategy(self, data, window=20):
        """Breakout Strategy"""
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['high_band'] = data['High'].rolling(window=window).max()
        signals['low_band'] = data['Low'].rolling(window=window).min()
        signals['signal'] = 0
        
        # Buy on upper breakout
        signals.loc[signals['price'] > signals['high_band'].shift(1), 'signal'] = 1
        # Sell on lower breakout
        signals.loc[signals['price'] < signals['low_band'].shift(1), 'signal'] = -1
        signals['signal'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'Breakout Strategy')
    
    def _mean_reversion_strategy(self, data, period=20, std_dev=2):
        """Mean Reversion Strategy"""
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['mean'] = data['Close'].rolling(window=period).mean()
        signals['std'] = data['Close'].rolling(window=period).std()
        signals['upper'] = signals['mean'] + (std_dev * signals['std'])
        signals['lower'] = signals['mean'] - (std_dev * signals['std'])
        signals['signal'] = 0
        
        # Buy when price hits lower band
        signals.loc[signals['price'] <= signals['lower'], 'signal'] = 1
        # Sell when price hits upper band
        signals.loc[signals['price'] >= signals['upper'], 'signal'] = -1
        signals['signal'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'Mean Reversion Strategy')
    
    def _momentum_strategy(self, data, short_period=12, long_period=26):
        """Momentum Strategy using ROC"""
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        signals['roc_short'] = ((data['Close'] - data['Close'].shift(short_period)) / 
                                data['Close'].shift(short_period)) * 100
        signals['roc_long'] = ((data['Close'] - data['Close'].shift(long_period)) / 
                               data['Close'].shift(long_period)) * 100
        signals['signal'] = 0
        
        # Buy when short ROC > long ROC
        signals.loc[signals['roc_short'] > signals['roc_long'], 'signal'] = 1
        signals.loc[signals['roc_short'] < signals['roc_long'], 'signal'] = -1
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'Momentum Strategy')
    
    def _multi_timeframe_strategy(self, data):
        """Multi-Timeframe Strategy"""
        signals = pd.DataFrame(index=data.index)
        signals['price'] = data['Close']
        
        # Multiple timeframe MAs
        signals['ema_5'] = data['Close'].ewm(span=5).mean()
        signals['ema_10'] = data['Close'].ewm(span=10).mean()
        signals['ema_20'] = data['Close'].ewm(span=20).mean()
        signals['sma_50'] = data['Close'].rolling(window=50).mean()
        signals['signal'] = 0
        
        # All MAs aligned bullish
        buy_condition = (
            (signals['ema_5'] > signals['ema_10']) &
            (signals['ema_10'] > signals['ema_20']) &
            (signals['ema_20'] > signals['sma_50'])
        )
        
        sell_condition = (
            (signals['ema_5'] < signals['ema_10']) &
            (signals['ema_10'] < signals['ema_20'])
        )
        
        signals.loc[buy_condition, 'signal'] = 1
        signals.loc[sell_condition, 'signal'] = -1
        signals['signal'] = signals['signal'].replace(0, np.nan).ffill().fillna(0)
        signals['positions'] = signals['signal'].diff()
        
        signals['returns'] = signals['price'].pct_change()
        signals['strategy_returns'] = signals['signal'].shift(1) * signals['returns']
        
        return self._calculate_metrics(signals, 'Multi-Timeframe Strategy')
    
    def _calculate_metrics(self, signals, strategy_name):
        """Calculate backtest metrics"""
        # Drop NaN values
        signals = signals.dropna()
        
        # Calculate cumulative returns
        signals['cumulative_market_returns'] = (1 + signals['returns']).cumprod()
        signals['cumulative_strategy_returns'] = (1 + signals['strategy_returns']).cumprod()
        
        # Metrics
        total_return = (signals['cumulative_strategy_returns'].iloc[-1] - 1) * 100
        market_return = (signals['cumulative_market_returns'].iloc[-1] - 1) * 100
        
        # Sharpe ratio (annualized)
        returns_std = signals['strategy_returns'].std()
        sharpe_ratio = (signals['strategy_returns'].mean() / returns_std) * np.sqrt(252) if returns_std != 0 else 0
        
        # Maximum drawdown
        cumulative = signals['cumulative_strategy_returns']
        running_max = cumulative.expanding().max()
        drawdown = (cumulative - running_max) / running_max
        max_drawdown = drawdown.min() * 100
        
        # Win rate
        trades = signals[signals['positions'] != 0]
        if len(trades) > 0:
            win_rate = (trades['strategy_returns'] > 0).mean() * 100
            total_trades = len(trades)
        else:
            win_rate = 0
            total_trades = 0
        
        # Buy and hold comparison
        buy_hold_return = (signals['price'].iloc[-1] / signals['price'].iloc[0] - 1) * 100
        
        return {
            'strategy_name': strategy_name,
            'total_return': round(total_return, 2),
            'market_return': round(market_return, 2),
            'buy_hold_return': round(buy_hold_return, 2),
            'sharpe_ratio': round(sharpe_ratio, 2),
            'max_drawdown': round(max_drawdown, 2),
            'win_rate': round(win_rate, 2),
            'total_trades': total_trades,
            'outperformance': round(total_return - buy_hold_return, 2)
        }
    
    def compare_strategies(self, data):
        """Compare all strategies"""
        strategies = [
            'sma_crossover', 'rsi_strategy', 'macd_strategy', 
            'bollinger_strategy', 'combined', 'adx_strategy',
            'supertrend_strategy', 'ichimoku_strategy', 'breakout_strategy',
            'mean_reversion', 'momentum_strategy', 'multi_timeframe'
        ]
        results = []
        
        for strategy in strategies:
            result = self.run_strategy(data, strategy)
            results.append(result)
        
        return results

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from modules.data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    data = fetcher.fetch_stock_data('RELIANCE.NS', '2y')
    
    if data is not None:
        backtester = Backtester()
        results = backtester.compare_strategies(data)
        
        print("Strategy Comparison:")
        for result in results:
            print(f"\n{result['strategy_name']}:")
            print(f"  Total Return: {result['total_return']}%")
            print(f"  Sharpe Ratio: {result['sharpe_ratio']}")
            print(f"  Max Drawdown: {result['max_drawdown']}%")
            print(f"  Win Rate: {result['win_rate']}%")
