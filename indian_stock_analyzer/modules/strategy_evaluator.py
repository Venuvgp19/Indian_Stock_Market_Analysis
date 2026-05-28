"""
Strategy Evaluator Module
Determines which trading strategies are currently favorable for a stock
based on current market conditions and technical indicators.
"""

import pandas as pd
import numpy as np

class StrategyEvaluator:
    def __init__(self):
        self.strategies = {
            'sma_crossover': {
                'name': 'SMA Crossover',
                'description': 'Uses 20-day and 50-day SMA crossovers for trend following',
                'best_for': 'Trending markets',
                'timeframe': 'Medium-term',
                'risk_level': 'Moderate'
            },
            'rsi_strategy': {
                'name': 'RSI Strategy',
                'description': 'Buy when oversold (RSI < 30), sell when overbought (RSI > 70)',
                'best_for': 'Range-bound markets',
                'timeframe': 'Short to medium-term',
                'risk_level': 'Moderate'
            },
            'macd_strategy': {
                'name': 'MACD Strategy',
                'description': 'Follows MACD line crossovers with signal line for momentum trades',
                'best_for': 'Momentum markets',
                'timeframe': 'Medium-term',
                'risk_level': 'Moderate'
            },
            'bollinger_strategy': {
                'name': 'Bollinger Bands',
                'description': 'Buy at lower band, sell at upper band - mean reversion approach',
                'best_for': 'Volatile range-bound markets',
                'timeframe': 'Short-term',
                'risk_level': 'Moderate'
            },
            'combined': {
                'name': 'Combined Strategy',
                'description': 'Uses multiple indicators (SMA, RSI, MACD) together for confirmation',
                'best_for': 'All market conditions',
                'timeframe': 'Medium-term',
                'risk_level': 'Lower (more confirmation)'
            },
            'adx_strategy': {
                'name': 'ADX Trend Strength',
                'description': 'Trades based on trend strength with directional movement',
                'best_for': 'Strong trending markets',
                'timeframe': 'Medium to long-term',
                'risk_level': 'Moderate'
            },
            'supertrend_strategy': {
                'name': 'SuperTrend',
                'description': 'Follows ATR-based trailing stop for trend following',
                'best_for': 'Trending markets with clear direction',
                'timeframe': 'Medium-term',
                'risk_level': 'Moderate'
            },
            'ichimoku_strategy': {
                'name': 'Ichimoku Cloud',
                'description': 'Comprehensive Japanese indicator for trend, support/resistance, momentum',
                'best_for': 'Trending markets',
                'timeframe': 'Medium to long-term',
                'risk_level': 'Moderate'
            },
            'breakout_strategy': {
                'name': 'Breakout Strategy',
                'description': 'Buys on resistance breakout, sells on support breakdown',
                'best_for': 'Consolidation breakouts',
                'timeframe': 'Short to medium-term',
                'risk_level': 'Higher'
            },
            'mean_reversion': {
                'name': 'Mean Reversion',
                'description': 'Trades price extremes back to statistical mean',
                'best_for': 'Range-bound markets',
                'timeframe': 'Short-term',
                'risk_level': 'Moderate'
            },
            'momentum_strategy': {
                'name': 'Momentum Strategy',
                'description': 'Follows rate of change momentum for trend continuation',
                'best_for': 'Strong momentum markets',
                'timeframe': 'Short to medium-term',
                'risk_level': 'Higher'
            },
            'multi_timeframe': {
                'name': 'Multi-Timeframe',
                'description': 'Uses aligned EMAs across multiple timeframes for strong trend confirmation',
                'best_for': 'Strong sustained trends',
                'timeframe': 'Long-term',
                'risk_level': 'Lower'
            }
        }
    
    def evaluate_strategies(self, data, technical_details, ml_prediction='NEUTRAL', ml_confidence=50):
        """
        Evaluate which strategies are currently favorable based on:
        1. Current technical indicator values
        2. Market conditions (trending/ranging/volatile)
        3. ML prediction direction
        
        Returns dict with strategy names as keys and evaluation results as values
        """
        if data is None or len(data) < 50:
            return {'error': 'Insufficient data'}
        
        # Get latest indicator values
        latest = data.iloc[-1]
        close = latest['Close']
        
        # Calculate indicators
        sma_20 = data['Close'].rolling(window=20).mean().iloc[-1]
        sma_50 = data['Close'].rolling(window=50).mean().iloc[-1]
        sma_200 = data['Close'].rolling(window=200).mean().iloc[-1]
        
        # RSI
        delta = data['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
        rs = gain / loss
        rsi = (100 - (100 / (1 + rs))).iloc[-1]
        
        # MACD
        ema_12 = data['Close'].ewm(span=12).mean()
        ema_26 = data['Close'].ewm(span=26).mean()
        macd_line = ema_12 - ema_26
        signal_line = macd_line.ewm(span=9).mean()
        macd = macd_line.iloc[-1]
        macd_sig = signal_line.iloc[-1]
        
        # Bollinger Bands
        bb_sma = data['Close'].rolling(window=20).mean()
        bb_std = data['Close'].rolling(window=20).std()
        bb_upper = (bb_sma + (bb_std * 2)).iloc[-1]
        bb_lower = (bb_sma - (bb_std * 2)).iloc[-1]
        bb_position = (close - bb_lower) / (bb_upper - bb_lower) if (bb_upper - bb_lower) != 0 else 0.5
        
        # ATR for volatility
        high_low = data['High'] - data['Low']
        high_close = abs(data['High'] - data['Close'].shift())
        low_close = abs(data['Low'] - data['Close'].shift())
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean().iloc[-1]
        atr_pct = (atr / close) * 100
        
        # ADX
        from modules.advanced_indicators import AdvancedIndicators
        adv = AdvancedIndicators()
        adx_value = adv.calculate_adx(data).iloc[-1]
        plus_di, minus_di = adv.calculate_adx(data, return_di=True)
        plus_di_val = plus_di.iloc[-1]
        minus_di_val = minus_di.iloc[-1]
        
        # Determine market condition
        is_trending = adx_value > 25 if not pd.isna(adx_value) else False
        is_strong_trend = adx_value > 40 if not pd.isna(adx_value) else False
        is_ranging = adx_value < 20 if not pd.isna(adx_value) else True
        is_volatile = atr_pct > 3
        
        # Trend direction
        is_bullish_trend = close > sma_50 > sma_200 if not pd.isna(sma_200) else close > sma_50
        is_bearish_trend = close < sma_50 < sma_200 if not pd.isna(sma_200) else close < sma_50
        
        # ML direction
        is_ml_bullish = ml_prediction == 'BULLISH' and ml_confidence > 60
        is_ml_bearish = ml_prediction == 'BEARISH' and ml_confidence > 60
        
        evaluations = {}
        
        # 1. SMA Crossover
        sma_score = 0
        sma_reasons = []
        if close > sma_20 > sma_50:
            sma_score += 40
            sma_reasons.append("Price above SMA 20 and 50 - bullish alignment")
        if is_bullish_trend:
            sma_score += 30
            sma_reasons.append("Strong bullish trend structure")
        if is_trending:
            sma_score += 20
            sma_reasons.append("Trending market favors SMA strategy")
        if is_ml_bullish:
            sma_score += 10
            sma_reasons.append("ML prediction confirms bullish direction")
        evaluations['sma_crossover'] = {
            'favorable': bool(sma_score >= 50),
            'score': int(sma_score),
            'max_score': 100,
            'reasons': sma_reasons if sma_reasons else ["Current conditions not ideal for SMA crossover"]
        }
        
        # 2. RSI Strategy
        rsi_score = 0
        rsi_reasons = []
        if 30 <= rsi <= 70:
            rsi_score += 30
            rsi_reasons.append(f"RSI at {rsi:.1f} - in tradable range")
        if rsi < 35:
            rsi_score += 40
            rsi_reasons.append(f"RSI oversold at {rsi:.1f} - potential buy zone")
        elif rsi > 65:
            rsi_score += 40
            rsi_reasons.append(f"RSI overbought at {rsi:.1f} - potential sell zone")
        if is_ranging:
            rsi_score += 20
            rsi_reasons.append("Range-bound market ideal for RSI")
        if not is_strong_trend:
            rsi_score += 10
            rsi_reasons.append("No extreme trend - mean reversion possible")
        evaluations['rsi_strategy'] = {
            'favorable': bool(rsi_score >= 50),
            'score': int(rsi_score),
            'max_score': 100,
            'reasons': rsi_reasons if rsi_reasons else ["Current conditions not ideal for RSI strategy"]
        }
        
        # 3. MACD Strategy
        macd_score = 0
        macd_reasons = []
        if macd > macd_sig:
            macd_score += 40
            macd_reasons.append("MACD above signal line - bullish momentum")
        else:
            macd_score += 20
            macd_reasons.append("MACD below signal - watch for crossover")
        if is_trending:
            macd_score += 30
            macd_reasons.append("Trending market - MACD effective")
        if abs(macd - macd_sig) > abs(macd * 0.1):
            macd_score += 20
            macd_reasons.append("MACD divergence significant")
        if is_ml_bullish and macd > macd_sig:
            macd_score += 10
            macd_reasons.append("ML bullish + MACD bullish alignment")
        evaluations['macd_strategy'] = {
            'favorable': bool(macd_score >= 50),
            'score': int(macd_score),
            'max_score': 100,
            'reasons': macd_reasons if macd_reasons else ["Current conditions not ideal for MACD strategy"]
        }
        
        # 4. Bollinger Bands
        bb_score = 0
        bb_reasons = []
        if bb_position < 0.2:
            bb_score += 45
            bb_reasons.append("Price near lower band - potential bounce")
        elif bb_position > 0.8:
            bb_score += 45
            bb_reasons.append("Price near upper band - potential reversal")
        else:
            bb_score += 20
            bb_reasons.append("Price in middle zone")
        if is_ranging or not is_strong_trend:
            bb_score += 30
            bb_reasons.append("Range-bound conditions favor Bollinger mean reversion")
        if is_volatile:
            bb_score += 15
            bb_reasons.append("Higher volatility increases band width")
        if not is_trending:
            bb_score += 10
            bb_reasons.append("Non-trending market ideal for band trading")
        evaluations['bollinger_strategy'] = {
            'favorable': bool(bb_score >= 50),
            'score': int(bb_score),
            'max_score': 100,
            'reasons': bb_reasons if bb_reasons else ["Current conditions not ideal for Bollinger strategy"]
        }
        
        # 5. Combined Strategy
        combined_score = 0
        combined_reasons = []
        favorable_count = sum(1 for s in ['sma_crossover', 'rsi_strategy', 'macd_strategy'] 
                             if evaluations[s]['favorable'])
        if favorable_count >= 2:
            combined_score += 50
            combined_reasons.append(f"{favorable_count}/3 component strategies favorable")
        if close > sma_20 and rsi > 40 and macd > macd_sig:
            combined_score += 30
            combined_reasons.append("All key indicators aligned bullish")
        elif close < sma_20 and rsi < 60 and macd < macd_sig:
            combined_score += 30
            combined_reasons.append("All key indicators aligned bearish")
        if is_trending:
            combined_score += 20
            combined_reasons.append("Trending market - multiple confirmations work well")
        if is_ml_bullish or is_ml_bearish:
            combined_score += 10
            combined_reasons.append("ML provides directional confirmation")
        evaluations['combined'] = {
            'favorable': bool(combined_score >= 50 or favorable_count >= 2),
            'score': int(combined_score),
            'max_score': 100,
            'reasons': combined_reasons if combined_reasons else ["Multiple confirmations not yet aligned"]
        }
        
        # 6. ADX Strategy
        adx_score = 0
        adx_reasons = []
        if not pd.isna(adx_value):
            if adx_value > 25:
                adx_score += 40
                adx_reasons.append(f"ADX at {adx_value:.1f} - strong trend detected")
            if adx_value > 35:
                adx_score += 20
                adx_reasons.append("Very strong trend - ADX highly effective")
            if plus_di_val > minus_di_val:
                adx_score += 30
                adx_reasons.append("+DI > -DI - bullish directional movement")
            elif minus_di_val > plus_di_val:
                adx_score += 30
                adx_reasons.append("-DI > +DI - bearish directional movement")
            if is_trending:
                adx_score += 10
                adx_reasons.append("Trending market confirms ADX signals")
        evaluations['adx_strategy'] = {
            'favorable': bool(adx_score >= 50),
            'score': int(adx_score),
            'max_score': 100,
            'reasons': adx_reasons if adx_reasons else ["ADX not showing strong trend - strategy less effective"]
        }
        
        # 7. SuperTrend
        st_score = 0
        st_reasons = []
        # Simple SuperTrend approximation using ATR bands
        hl2 = (latest['High'] + latest['Low']) / 2
        upper_band = hl2 + (3 * atr)
        lower_band = hl2 - (3 * atr)
        is_bullish_st = close > lower_band
        
        if is_bullish_st and close > sma_50:
            st_score += 45
            st_reasons.append("Price above SuperTrend support - bullish")
        elif not is_bullish_st and close < sma_50:
            st_score += 45
            st_reasons.append("Price below SuperTrend resistance - bearish")
        if is_trending:
            st_score += 35
            st_reasons.append("Trending market - SuperTrend effective")
        if not is_ranging:
            st_score += 20
            st_reasons.append("Clear direction favors trailing stop approach")
        evaluations['supertrend_strategy'] = {
            'favorable': bool(st_score >= 50),
            'score': int(st_score),
            'max_score': 100,
            'reasons': st_reasons if st_reasons else ["Unclear trend - SuperTrend may give false signals"]
        }
        
        # 8. Ichimoku Cloud
        ichimoku_score = 0
        ichimoku_reasons = []
        try:
            ichimoku = adv.calculate_ichimoku_cloud(data)
            tenkan = ichimoku['tenkan_sen'].iloc[-1]
            kijun = ichimoku['kijun_sen'].iloc[-1]
            senkou_a = ichimoku['senkou_span_a'].iloc[-1]
            senkou_b = ichimoku['senkou_span_b'].iloc[-1]
            
            if close > senkou_a and close > senkou_b:
                ichimoku_score += 35
                ichimoku_reasons.append("Price above cloud - bullish Ichimoku signal")
            elif close < senkou_a and close < senkou_b:
                ichimoku_score += 35
                ichimoku_reasons.append("Price below cloud - bearish Ichimoku signal")
            if tenkan > kijun:
                ichimoku_score += 30
                ichimoku_reasons.append("Tenkan > Kijun - bullish conversion")
            elif tenkan < kijun:
                ichimoku_score += 30
                ichimoku_reasons.append("Tenkan < Kijun - bearish conversion")
            if is_trending:
                ichimoku_score += 25
                ichimoku_reasons.append("Trending market - Ichimoku cloud effective")
            if is_ml_bullish and close > senkou_a:
                ichimoku_score += 10
                ichimoku_reasons.append("ML bullish + above cloud")
        except:
            ichimoku_reasons.append("Ichimoku data insufficient")
        evaluations['ichimoku_strategy'] = {
            'favorable': bool(ichimoku_score >= 50),
            'score': int(ichimoku_score),
            'max_score': 100,
            'reasons': ichimoku_reasons if ichimoku_reasons else ["Ichimoku signals unclear"]
        }
        
        # 9. Breakout Strategy
        breakout_score = 0
        breakout_reasons = []
        recent_high = data['High'].tail(20).max()
        recent_low = data['Low'].tail(20).min()
        range_pct = ((recent_high - recent_low) / recent_low) * 100
        
        if range_pct < 10:
            breakout_score += 35
            breakout_reasons.append(f"Tight consolidation ({range_pct:.1f}% range) - breakout likely")
        elif range_pct < 20:
            breakout_score += 20
            breakout_reasons.append("Moderate consolidation - watch for breakout")
        if close > recent_high * 0.98:
            breakout_score += 40
            breakout_reasons.append("Price near recent highs - breakout setup")
        elif close < recent_low * 1.02:
            breakout_score += 40
            breakout_reasons.append("Price near recent lows - breakdown setup")
        if is_volatile:
            breakout_score += 15
            breakout_reasons.append("Volatility supports breakout moves")
        if volume_spike(data):
            breakout_score += 10
            breakout_reasons.append("Volume spike detected - confirms breakout potential")
        evaluations['breakout_strategy'] = {
            'favorable': bool(breakout_score >= 50),
            'score': int(breakout_score),
            'max_score': 100,
            'reasons': breakout_reasons if breakout_reasons else ["No clear consolidation pattern for breakout"]
        }
        
        # 10. Mean Reversion
        mr_score = 0
        mr_reasons = []
        if is_ranging or adx_value < 20:
            mr_score += 40
            mr_reasons.append("Range-bound market ideal for mean reversion")
        if bb_position < 0.15 or bb_position > 0.85:
            mr_score += 35
            mr_reasons.append("Price at Bollinger extremes - reversion likely")
        if rsi < 30 or rsi > 70:
            mr_score += 25
            mr_reasons.append(f"RSI extreme at {rsi:.1f} - mean reversion setup")
        if not is_trending:
            mr_score += 15
            mr_reasons.append("Non-trending supports mean reversion")
        if is_volatile:
            mr_score += 10
            mr_reasons.append("Volatility creates reversion opportunities")
        evaluations['mean_reversion'] = {
            'favorable': bool(mr_score >= 50),
            'score': int(mr_score),
            'max_score': 100,
            'reasons': mr_reasons if mr_reasons else ["Trending market - mean reversion risky"]
        }
        
        # 11. Momentum Strategy
        mom_score = 0
        mom_reasons = []
        roc_10 = ((close - data['Close'].iloc[-10]) / data['Close'].iloc[-10]) * 100
        roc_20 = ((close - data['Close'].iloc[-20]) / data['Close'].iloc[-20]) * 100
        
        if roc_10 > roc_20:
            mom_score += 40
            mom_reasons.append(f"Short-term ROC ({roc_10:.1f}%) > Long-term ({roc_20:.1f}%) - momentum building")
        if abs(roc_10) > 5:
            mom_score += 30
            mom_reasons.append(f"Strong {roc_10:.1f}% recent momentum")
        if is_trending:
            mom_score += 20
            mom_reasons.append("Trending market - momentum strategies effective")
        if is_ml_bullish and roc_10 > 0:
            mom_score += 10
            mom_reasons.append("ML bullish + positive momentum")
        evaluations['momentum_strategy'] = {
            'favorable': bool(mom_score >= 50),
            'score': int(mom_score),
            'max_score': 100,
            'reasons': mom_reasons if mom_reasons else ["Momentum not clearly established"]
        }
        
        # 12. Multi-Timeframe
        mtf_score = 0
        mtf_reasons = []
        ema_5 = data['Close'].ewm(span=5).mean().iloc[-1]
        ema_10 = data['Close'].ewm(span=10).mean().iloc[-1]
        ema_20 = data['Close'].ewm(span=20).mean().iloc[-1]
        
        if ema_5 > ema_10 > ema_20 > sma_50:
            mtf_score += 50
            mtf_reasons.append("All EMAs aligned bullish - strong trend")
        elif ema_5 < ema_10 < ema_20 < sma_50:
            mtf_score += 50
            mtf_reasons.append("All EMAs aligned bearish - strong downtrend")
        else:
            mtf_score += 20
            mtf_reasons.append("Mixed EMA alignment")
        if is_strong_trend:
            mtf_score += 35
            mtf_reasons.append("Strong trend - multi-timeframe very effective")
        if is_trending:
            mtf_score += 15
            mtf_reasons.append("Trending market supports timeframe alignment")
        evaluations['multi_timeframe'] = {
            'favorable': bool(mtf_score >= 50),
            'score': int(mtf_score),
            'max_score': 100,
            'reasons': mtf_reasons if mtf_reasons else ["EMAs not aligned - strategy less effective"]
        }
        
        # Determine top recommendation
        favorable_strategies = [k for k, v in evaluations.items() if v['favorable']]
        
        # Add strategy info to each evaluation
        for key in evaluations:
            if key in self.strategies:
                evaluations[key]['info'] = self.strategies[key]
        
        return {
            'evaluations': evaluations,
            'favorable_count': int(len(favorable_strategies)),
            'total_strategies': int(len(self.strategies)),
            'favorable_strategies': favorable_strategies,
            'market_condition': {
                'is_trending': bool(is_trending),
                'is_strong_trend': bool(is_strong_trend),
                'is_ranging': bool(is_ranging),
                'is_volatile': bool(is_volatile),
                'is_bullish_trend': bool(is_bullish_trend),
                'is_bearish_trend': bool(is_bearish_trend),
                'adx': round(float(adx_value), 2) if not pd.isna(adx_value) else None,
                'rsi': round(float(rsi), 2) if not pd.isna(rsi) else None,
                'atr_pct': round(float(atr_pct), 2) if not pd.isna(atr_pct) else None
            }
        }
    
    def get_strategy_recommendation(self, evaluations):
        """Get overall strategy recommendation"""
        favorable = [k for k, v in evaluations.items() if v.get('favorable', False)]
        
        if not favorable:
            return "No strategy is strongly favorable right now. Consider waiting for clearer signals."
        
        if 'combined' in favorable:
            return "Combined Strategy is favorable - use multiple confirmations for safer trades."
        
        if len(favorable) == 1:
            return f"{evaluations[favorable[0]]['info']['name']} is favorable."
        
        return f"Multiple strategies favorable ({len(favorable)}). {evaluations[favorable[0]]['info']['name']} scores highest."


def volume_spike(data, period=20, threshold=1.5):
    """Check if there's a volume spike"""
    if 'Volume' not in data.columns or len(data) < period + 1:
        return False
    avg_volume = data['Volume'].tail(period).mean()
    latest_volume = data['Volume'].iloc[-1]
    return latest_volume > (avg_volume * threshold)


if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from modules.data_fetcher import StockDataFetcher
    
    fetcher = StockDataFetcher()
    data = fetcher.fetch_stock_data('RELIANCE.NS', '6mo')
    
    if data is not None:
        evaluator = StrategyEvaluator()
        result = evaluator.evaluate_strategies(data, {}, 'BULLISH', 65)
        
        print("Strategy Evaluation Results:")
        print("=" * 60)
        for strategy, eval_result in result['evaluations'].items():
            status = "✓ FAVORABLE" if eval_result['favorable'] else "✗ Not Favorable"
            print(f"\n{strategy}: {status} (Score: {eval_result['score']}/{eval_result['max_score']})")
            for reason in eval_result['reasons']:
                print(f"  - {reason}")
        
        print("\n" + "=" * 60)
        print(f"Market Condition: {'Trending' if result['market_condition']['is_trending'] else 'Ranging'}")
        print(f"Favorable Strategies: {result['favorable_count']}/{result['total_strategies']}")
