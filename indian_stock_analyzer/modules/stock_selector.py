"""
Stock Selector Module
Combines technical analysis, ML predictions, and news sentiment to recommend top stocks
"""

import pandas as pd
import numpy as np
from datetime import datetime
import time

class StockSelector:
    def __init__(self, data_fetcher, technical_analyzer, ml_predictor, news_validator):
        self.data_fetcher = data_fetcher
        self.technical_analyzer = technical_analyzer
        self.ml_predictor = ml_predictor
        self.news_validator = news_validator
        
    def analyze_stock(self, symbol):
        """Analyze a single stock comprehensively"""
        try:
            print(f"Analyzing {symbol}...")
            
            # Fetch historical data
            data = self.data_fetcher.fetch_stock_data(symbol, '2y')
            if data is None or len(data) < 50:
                return None
            
            # Technical Analysis Score
            tech_score, tech_details = self.technical_analyzer.score_stock(data)
            
            # ML Prediction
            ml_result = self.ml_predictor.predict(symbol, data)
            
            # News Sentiment
            news_result = self.news_validator.validate_stock(symbol)
            
            # Current price
            current_price = data['Close'].iloc[-1]
            price_change = ((current_price - data['Close'].iloc[-2]) / data['Close'].iloc[-2]) * 100
            
            # Calculate composite score with dynamic weights based on indicator strength
            # Stronger indicators get more weight
            
            # Technical score (0-100)
            tech_score_final = tech_score
            
            # ML confidence (0-100) - only bullish predictions get high scores
            if ml_result['prediction'] == 'BULLISH':
                ml_confidence = ml_result['confidence']
            elif ml_result['prediction'] == 'BEARISH':
                ml_confidence = 100 - ml_result['confidence']  # Invert for bearish
            else:
                ml_confidence = 50  # Neutral gets middle score
            
            # News sentiment (0-100)
            news_score = news_result['sentiment_score']
            
            # Calculate signal strength for each component
            tech_strength = abs(tech_score - 50) * 2  # How far from neutral (50)
            ml_strength = abs(ml_confidence - 50) * 2
            news_strength = abs(news_score - 50) * 2
            
            # Dynamic weights - stronger signals get more weight
            total_strength = tech_strength + ml_strength + news_strength
            if total_strength > 0:
                tech_weight = 0.2 + (tech_strength / total_strength) * 0.3
                ml_weight = 0.2 + (ml_strength / total_strength) * 0.3
                news_weight = 0.2 + (news_strength / total_strength) * 0.3
            else:
                tech_weight = ml_weight = news_weight = 0.333
            
            # Normalize weights to sum to 1
            total_weight = tech_weight + ml_weight + news_weight
            tech_weight /= total_weight
            ml_weight /= total_weight
            news_weight /= total_weight
            
            # Calculate weighted composite score
            composite_score = (
                (tech_score_final * tech_weight) +
                (ml_confidence * ml_weight) +
                (news_score * news_weight)
            )
            
            # Base score is now calculated
            # Apply adjustments based on LSTM and conditions
            
            # Apply trend adjustments
            # If LSTM and ML agree on direction, boost confidence
            if 'lstm' in ml_result and ml_result['lstm']:
                lstm_pred = ml_result['lstm'].get('lstm_prediction', 'NEUTRAL')
                # Only apply disagreement penalty if NOT oversold with LSTM bullish
                # (oversold + LSTM bullish is a buy signal, not a disagreement)
                is_oversold_lstm_bullish = (tech_score <= 35 and 
                                            lstm_pred == 'BULLISH' and 
                                            ml_result['lstm'].get('lstm_confidence', 0) > 60)
                
                if lstm_pred == ml_result['prediction'] and lstm_pred != 'NEUTRAL':
                    # Agreement boost
                    composite_score *= 1.15
                elif lstm_pred != ml_result['prediction'] and lstm_pred != 'NEUTRAL' and not is_oversold_lstm_bullish:
                    # Disagreement penalty (skip if oversold + LSTM bullish)
                    composite_score *= 0.85
            
            # If technical score is very low (oversold), consider it a potential buy
            if tech_score <= 35 and ml_result['prediction'] == 'BULLISH':
                composite_score *= 1.2  # Oversold + bullish ML = potential reversal
            
            # Also consider LSTM for oversold reversals
            if tech_score <= 35 and 'lstm' in ml_result and ml_result['lstm']:
                lstm_pred = ml_result['lstm'].get('lstm_prediction', 'NEUTRAL')
                lstm_conf = ml_result['lstm'].get('lstm_confidence', 0)
                if lstm_pred == 'BULLISH' and lstm_conf > 60:
                    composite_score *= 1.35  # Strong oversold + LSTM bullish = potential reversal
                    # Override ML neutral if LSTM is strongly bullish on oversold stock
                    if ml_result['prediction'] == 'NEUTRAL':
                        composite_score *= 1.2
            
            # If technical is very high (overbought), consider taking profits
            if tech_score > 80 and ml_result['prediction'] == 'BEARISH':
                composite_score *= 0.8  # Overbought + bearish ML = potential pullback
            
            # News sentiment penalty/boost
            if news_score < 30:
                composite_score *= 0.85  # Bad news penalty
            elif news_score > 70:
                composite_score *= 1.1  # Good news boost
            
            composite_score = min(100, max(0, composite_score))
            
            return {
                'symbol': symbol,
                'company_name': self.data_fetcher.get_stock_name(symbol),
                'current_price': round(current_price, 2),
                'price_change': round(price_change, 2),
                'tech_score': tech_score,
                'tech_details': tech_details,
                'ml_prediction': ml_result['prediction'],
                'ml_confidence': ml_result['confidence'],
                'ml_prob_up': ml_result.get('prob_up', 0.5),
                'lstm': ml_result.get('lstm', {}),
                'news_sentiment': news_result['sentiment_score'],
                'news_label': news_result['sentiment_label'],
                'news_recommendation': news_result['recommendation'],
                'composite_score': round(composite_score, 2),
                'recommendation': self._get_final_recommendation({
                    'composite_score': composite_score,
                    'tech_score': tech_score,
                    'ml_prediction': ml_result['prediction'],
                    'ml_confidence': ml_result['confidence'],
                    'news_sentiment': news_result['sentiment_score']
                }),
                'articles': news_result['articles'][:3]
            }
            
        except Exception as e:
            print(f"Error analyzing {symbol}: {e}")
            return None
    
    def get_top_stocks(self, symbols=None, top_n=10):
        """Get top N stocks based on composite analysis"""
        if symbols is None:
            symbols = self.data_fetcher.get_nifty50_list()
        
        results = []
        
        for symbol in symbols:
            analysis = self.analyze_stock(symbol)
            if analysis is not None:
                results.append(analysis)
            time.sleep(1)  # Rate limiting between stocks
        
        # Sort by composite score (descending)
        results.sort(key=lambda x: x['composite_score'], reverse=True)
        
        return results[:top_n]
    
    def generate_report(self, top_stocks):
        """Generate detailed report for top stocks"""
        report = {
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_stocks_analyzed': len(top_stocks),
            'recommendations': []
        }
        
        for stock in top_stocks:
            recommendation = {
                'rank': top_stocks.index(stock) + 1,
                'symbol': stock['symbol'],
                'company_name': stock['company_name'],
                'current_price': stock['current_price'],
                'price_change_pct': stock['price_change'],
                'composite_score': stock['composite_score'],
                'technical_score': stock['tech_score'],
                'ml_prediction': stock['ml_prediction'],
                'ml_confidence': stock['ml_confidence'],
                'news_sentiment': stock['news_sentiment'],
                'news_label': stock['news_label'],
                'recommendation': self._get_final_recommendation(stock),
                'key_reasons': stock['tech_details'].get('reasons', [])[:3]
            }
            report['recommendations'].append(recommendation)
        
        return report
    
    def _get_final_recommendation(self, stock):
        """Generate final buy/sell recommendation based on composite score and signals"""
        score = stock.get('composite_score', 0)
        
        # Consider all signals
        tech_score = stock.get('tech_score', 50)
        ml_pred = stock.get('ml_prediction', 'NEUTRAL')
        ml_conf = stock.get('ml_confidence', 50)
        news_sentiment = stock.get('news_sentiment', 50)
        
        # Strong buy signals:
        # - Oversold (RSI < 30) + Bullish ML + Good news
        if tech_score < 35 and ml_pred == 'BULLISH' and ml_conf > 60:
            if news_sentiment > 50:
                return 'STRONG BUY (Oversold Reversal)'
            else:
                return 'BUY (Potential Reversal)'
        
        # Oversold with LSTM bullish (even if ML neutral)
        if tech_score < 35 and 'lstm' in stock and stock['lstm']:
            lstm_pred = stock['lstm'].get('lstm_prediction', 'NEUTRAL')
            lstm_conf = stock['lstm'].get('lstm_confidence', 0)
            if lstm_pred == 'BULLISH' and lstm_conf > 60:
                return 'BUY (LSTM Oversold Reversal)'
        
        # Strong sell signals:
        # - Overbought (RSI > 70) + Bearish ML + Bad news
        if tech_score > 70 and ml_pred == 'BEARISH' and ml_conf > 60:
            if news_sentiment < 50:
                return 'STRONG SELL (Overbought Pullback)'
            else:
                return 'SELL (Potential Pullback)'
        
        # Standard scoring
        if score >= 75:
            return 'STRONG BUY'
        elif score >= 60:
            return 'BUY'
        elif score >= 50:
            return 'HOLD'
        elif score >= 40:
            return 'WEAK HOLD / REDUCE'
        elif score >= 30:
            return 'SELL'
        else:
            return 'STRONG SELL'
    
    def get_sector_analysis(self, stocks):
        """Analyze stocks by sector"""
        # This would require sector data from an API
        # For now, return a simplified version
        sectors = {}
        for stock in stocks:
            sector = 'Unknown'  # Would be populated from stock info API
            if sector not in sectors:
                sectors[sector] = []
            sectors[sector].append(stock)
        
        return sectors

if __name__ == "__main__":
    import sys
    sys.path.append('..')
    from modules.data_fetcher import StockDataFetcher
    from modules.technical_analyzer import TechnicalAnalyzer
    from modules.ml_predictor import MLPredictor
    from modules.news_validator import NewsValidator
    
    fetcher = StockDataFetcher()
    analyzer = TechnicalAnalyzer()
    predictor = MLPredictor()
    validator = NewsValidator()
    
    selector = StockSelector(fetcher, analyzer, predictor, validator)
    
    # Test with a few stocks
    test_stocks = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
    top = selector.get_top_stocks(test_stocks, top_n=3)
    
    report = selector.generate_report(top)
    print(json.dumps(report, indent=2))
