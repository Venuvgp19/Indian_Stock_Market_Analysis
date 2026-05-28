"""
Indian Stock Market Research & Analyzer App V2
Enhanced with: Advanced Indicators, Backtesting, Portfolio Tracking, Enhanced ML
"""

from flask import Flask, render_template, jsonify, request
import json
import threading
import time
from datetime import datetime, timedelta
import sys
import os
import pandas as pd
import numpy as np

# Add modules directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher import StockDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.advanced_indicators import AdvancedIndicators
from modules.ml_predictor import MLPredictor
from modules.advanced_ml import AdvancedMLPredictor
from modules.news_validator import NewsValidator
from modules.stock_selector import StockSelector
from modules.backtester import Backtester
from modules.portfolio_tracker import PortfolioTracker

app = Flask(__name__)

# Initialize components
data_fetcher = StockDataFetcher()
technical_analyzer = TechnicalAnalyzer()
advanced_indicators = AdvancedIndicators()
ml_predictor = MLPredictor()
advanced_ml = AdvancedMLPredictor()
news_validator = NewsValidator()
stock_selector = StockSelector(data_fetcher, technical_analyzer, ml_predictor, news_validator)
backtester = Backtester()
portfolio_tracker = PortfolioTracker()

# Enhanced cache with TTL
cache = {
    'top_stocks': None,
    'last_updated': None,
    'cache_expiry': None,
    'individual_analysis': {},
    'backtest_results': {},
    'portfolio_summary': None
}

CACHE_DURATION = timedelta(minutes=5)  # Cache for 5 minutes

def is_cache_valid():
    """Check if cache is still valid"""
    if cache['cache_expiry'] is None:
        return False
    return datetime.now() < cache['cache_expiry']

def update_cache(data):
    """Update cache with new data"""
    cache['top_stocks'] = data
    cache['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    cache['cache_expiry'] = datetime.now() + CACHE_DURATION

def initialize_cache():
    """Initialize cache with demo data"""
    demo_stocks = [
        {
            'symbol': 'INFY.NS', 'company_name': 'Infosys',
            'current_price': 1191.80, 'price_change': 0.95,
            'tech_score': 65, 'ml_prediction': 'BULLISH',
            'ml_confidence': 93, 'news_sentiment': 50.3,
            'composite_score': 70.39, 'recommendation': 'STRONG BUY'
        },
        {
            'symbol': 'KOTAKBANK.NS', 'company_name': 'Kotak Mahindra Bank',
            'current_price': 1756.00, 'price_change': -0.45,
            'tech_score': 62, 'ml_prediction': 'BULLISH',
            'ml_confidence': 88, 'news_sentiment': 48.2,
            'composite_score': 68.80, 'recommendation': 'BUY'
        },
        {
            'symbol': 'BHARTIARTL.NS', 'company_name': 'Bharti Airtel',
            'current_price': 1988.50, 'price_change': 1.25,
            'tech_score': 58, 'ml_prediction': 'BULLISH',
            'ml_confidence': 85, 'news_sentiment': 52.1,
            'composite_score': 65.56, 'recommendation': 'BUY'
        }
    ]
    update_cache(demo_stocks)

# Initialize on startup
initialize_cache()

@app.route('/')
def index():
    """Main dashboard page"""
    return render_template('index.html')

@app.route('/research')
def research():
    """Stock research page"""
    return render_template('research.html')

@app.route('/portfolio')
def portfolio():
    """Portfolio tracking page"""
    return render_template('portfolio.html')

@app.route('/backtest')
def backtest_page():
    """Backtesting page"""
    return render_template('backtest.html')

@app.route('/api/stocks')
def get_stocks():
    """Get list of all available stocks"""
    stocks = data_fetcher.get_all_stocks_list()
    stock_list = []
    for symbol in stocks:
        stock_list.append({
            'symbol': symbol,
            'name': data_fetcher.get_stock_name(symbol)
        })
    return jsonify(stock_list)

@app.route('/api/stocks/by-category')
def get_stocks_by_category():
    """Get stocks organized by category"""
    return jsonify(data_fetcher.get_stocks_by_category())

@app.route('/api/analyze/<symbol>')
def analyze_stock(symbol):
    """Analyze a specific stock with ALL indicators"""
    try:
        # Check individual cache first
        if symbol in cache['individual_analysis']:
            cached = cache['individual_analysis'][symbol]
            if cached.get('expiry', datetime.min) > datetime.now():
                return jsonify(cached['data'])

        # Fetch data
        data = data_fetcher.fetch_stock_data(symbol, '2y')
        if data is None:
            return jsonify({'error': 'No data available'}), 404

        current_price = data['Close'].iloc[-1]
        prev_price = data['Close'].iloc[-2]
        price_change = ((current_price - prev_price) / prev_price) * 100

        # Technical Analysis
        tech_score, tech_details = technical_analyzer.score_stock(data)

        # Advanced Indicators
        adv_indicators = advanced_indicators.calculate_all_advanced(data)
        latest_adv = adv_indicators.iloc[-1]

        # Support/Resistance
        sr_levels = advanced_indicators.get_support_resistance(data)

        # ML Predictions (both basic and advanced)
        ml_result = ml_predictor.predict(symbol, data)
        adv_ml_result = advanced_ml.get_ml_signals(data)

        # News
        news_result = news_validator.validate_stock(symbol)

        # Composite Score
        tech_weight = 0.35
        ml_weight = 0.35
        news_weight = 0.30

        ml_score = ml_result['confidence'] if ml_result['prediction'] == 'UP' else (100 - ml_result['confidence'])
        news_score = news_result['sentiment_score']

        composite_score = (tech_score * tech_weight) + (ml_score * ml_weight) + (news_score * news_weight)

        # Recommendation
        if composite_score >= 75:
            recommendation = 'STRONG BUY'
        elif composite_score >= 60:
            recommendation = 'BUY'
        elif composite_score >= 40:
            recommendation = 'HOLD'
        elif composite_score >= 25:
            recommendation = 'SELL'
        else:
            recommendation = 'STRONG SELL'

        result = {
            'symbol': symbol,
            'company_name': data_fetcher.get_stock_name(symbol),
            'current_price': round(current_price, 2),
            'price_change': round(price_change, 2),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),

            # Technical Analysis
            'tech_score': tech_score,
            'tech_details': tech_details,

            # Advanced Indicators
            'advanced_indicators': {
                'vwap': round(latest_adv.get('VWAP', 0), 2),
                'super_trend': round(latest_adv.get('SuperTrend', 0), 2),
                'super_trend_direction': 'Bullish' if latest_adv.get('SuperTrend_Direction', -1) == 1 else 'Bearish',
                'williams_r': round(latest_adv.get('Williams_R', 0), 2),
                'mfi': round(latest_adv.get('MFI', 0), 2),
                'cmo': round(latest_adv.get('CMO', 0), 2),
                'pivot': round(latest_adv.get('Pivot_pivot', 0), 2),
                'r1': round(latest_adv.get('Pivot_r1', 0), 2),
                's1': round(latest_adv.get('Pivot_s1', 0), 2),
            },

            # Support/Resistance
            'support_resistance': sr_levels,

            # ML Predictions
            'ml_prediction': ml_result['prediction'],
            'ml_confidence': ml_result['confidence'],
            'ml_probability': ml_result.get('prob_up', ml_result.get('probability', 0)),
            'advanced_ml': adv_ml_result,

            # News
            'news_sentiment': news_result['sentiment_score'],
            'news_label': news_result['sentiment_label'],
            'news_recommendation': news_result['recommendation'],
            'articles': news_result.get('articles', []),

            # Overall
            'composite_score': round(composite_score, 2),
            'recommendation': recommendation
        }

        # Cache result
        cache['individual_analysis'][symbol] = {
            'data': result,
            'expiry': datetime.now() + timedelta(minutes=10)
        }

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-stocks')
def get_top_stocks():
    """Get top stock recommendations - with caching"""
    try:
        # Return cached data if valid
        if is_cache_valid() and cache['top_stocks'] is not None:
            return jsonify({
                'stocks': cache['top_stocks'],
                'last_updated': cache['last_updated'],
                'cached': True
            })

        # Quick analysis for top stocks (limit to first 10 for speed)
        symbols = data_fetcher.get_nifty50_list()[:10]
        results = []

        for symbol in symbols:
            try:
                data = data_fetcher.fetch_stock_data(symbol, '6mo')
                if data is None:
                    continue

                current_price = data['Close'].iloc[-1]
                tech_score, _ = technical_analyzer.score_stock(data)

                # Simplified ML
                ml_result = ml_predictor.predict(data)
                ml_score = ml_result['confidence'] if ml_result['prediction'] == 'UP' else (100 - ml_result['confidence'])

                # Simplified news
                news_result = news_validator.validate_stock(symbol)
                news_score = news_result['sentiment_score']

                composite_score = (tech_score * 0.35) + (ml_score * 0.35) + (news_score * 0.30)

                if composite_score >= 60:
                    recommendation = 'BUY' if composite_score >= 75 else 'STRONG BUY'
                elif composite_score >= 40:
                    recommendation = 'HOLD'
                else:
                    recommendation = 'SELL'

                results.append({
                    'symbol': symbol,
                    'company_name': data_fetcher.get_stock_name(symbol),
                    'current_price': round(current_price, 2),
                    'tech_score': tech_score,
                    'ml_prediction': ml_result['prediction'],
                    'ml_confidence': ml_result['confidence'],
                    'news_sentiment': news_score,
                    'composite_score': round(composite_score, 2),
                    'recommendation': recommendation
                })

            except:
                continue

        # Sort by composite score
        results.sort(key=lambda x: x['composite_score'], reverse=True)
        top_10 = results[:10]

        update_cache(top_10)

        return jsonify({
            'stocks': top_10,
            'last_updated': cache['last_updated'],
            'cached': False
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh-analysis')
def refresh_analysis():
    """Force refresh of analysis"""
    cache['top_stocks'] = None
    cache['individual_analysis'] = {}
    cache['cache_expiry'] = None
    return get_top_stocks()

@app.route('/api/stock-data/<symbol>')
def get_stock_data(symbol):
    """Get historical stock data for charts"""
    try:
        period = request.args.get('period', '1y')
        data = data_fetcher.fetch_stock_data(symbol, period)

        if data is not None:
            records = data.to_dict('records')
            for record in records:
                record['Date'] = record['Date'].strftime('%Y-%m-%d')

            return jsonify({'symbol': symbol, 'data': records})
        else:
            return jsonify({'error': 'No data available'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/news/<symbol>')
def get_news(symbol):
    """Get news for a specific stock"""
    try:
        result = news_validator.validate_stock(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/indicators/<symbol>')
def get_technical_indicators(symbol):
    """Get technical indicators for a stock"""
    try:
        data = data_fetcher.fetch_stock_data(symbol, '1y')
        if data is not None:
            indicators = technical_analyzer.calculate_all_indicators(data)
            records = indicators.tail(30).to_dict('records')
            for record in records:
                if isinstance(record['Date'], datetime):
                    record['Date'] = record['Date'].strftime('%Y-%m-%d')

            return jsonify({'symbol': symbol, 'indicators': records})
        else:
            return jsonify({'error': 'No data available'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced-indicators/<symbol>')
def get_advanced_indicators(symbol):
    """Get advanced indicators for a stock"""
    try:
        data = data_fetcher.fetch_stock_data(symbol, '1y')
        if data is not None:
            indicators = advanced_indicators.calculate_all_advanced(data)
            records = indicators.tail(30).to_dict('records')
            for record in records:
                if isinstance(record['Date'], datetime):
                    record['Date'] = record['Date'].strftime('%Y-%m-%d')

            # Get support/resistance
            sr = advanced_indicators.get_support_resistance(data)

            return jsonify({
                'symbol': symbol,
                'indicators': records,
                'support_resistance': sr
            })
        else:
            return jsonify({'error': 'No data available'}), 404

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_stocks():
    """Search for stocks"""
    query = request.args.get('q', '').upper()
    if not query:
        return jsonify([])

    all_stocks = data_fetcher.get_all_stocks()
    results = [s for s in all_stocks if query in s['symbol'] or query in s['name'].upper()]
    return jsonify(results[:10])

# Portfolio APIs
@app.route('/api/portfolio/summary')
def get_portfolio_summary():
    """Get portfolio summary"""
    try:
        # Get current prices for holdings
        holdings = portfolio_tracker.portfolio.get('holdings', {})
        current_prices = {}

        for symbol in holdings.keys():
            try:
                data = data_fetcher.fetch_stock_data(symbol, '5d')
                if data is not None and len(data) > 0:
                    current_prices[symbol] = data['Close'].iloc[-1]
                else:
                    # Fallback: use buy price if fetch fails
                    current_prices[symbol] = holdings[symbol]['avg_buy_price']
            except Exception as e:
                print(f"Error fetching {symbol}: {e}")
                # Fallback: use buy price
                current_prices[symbol] = holdings[symbol]['avg_buy_price']
                continue

        summary = portfolio_tracker.get_portfolio_summary(current_prices)
        return jsonify(summary)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/add', methods=['POST'])
def add_to_portfolio():
    """Add stock to portfolio"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        shares = data.get('shares', 0)
        buy_price = data.get('buy_price', 0)

        result = portfolio_tracker.add_stock(symbol, shares, buy_price)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/remove', methods=['POST'])
def remove_from_portfolio():
    """Remove stock from portfolio"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        shares = data.get('shares', 0)
        sell_price = data.get('sell_price', 0)

        result = portfolio_tracker.remove_stock(symbol, shares, sell_price)
        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/transactions')
def get_transactions():
    """Get transaction history"""
    try:
        transactions = portfolio_tracker.get_transaction_history()
        return jsonify(transactions)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Backtesting APIs
@app.route('/api/backtest/<symbol>')
def run_backtest(symbol):
    """Run backtest for a symbol"""
    try:
        strategy = request.args.get('strategy', 'combined')
        period = request.args.get('period', '2y')

        data = data_fetcher.fetch_stock_data(symbol, period)
        if data is None:
            return jsonify({'error': 'No data available'}), 404

        result = backtester.run_strategy(data, strategy)

        # Cache result
        cache['backtest_results'][f"{symbol}_{strategy}"] = result

        return jsonify(result)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest/compare/<symbol>')
def compare_strategies(symbol):
    """Compare all strategies"""
    try:
        period = request.args.get('period', '2y')

        data = data_fetcher.fetch_stock_data(symbol, period)
        if data is None:
            return jsonify({'error': 'No data available'}), 404

        results = backtester.compare_strategies(data)
        return jsonify(results)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("=" * 60)
    print("  Indian Stock Market Analyzer V2")
    print("=" * 60)
    print("  Features:")
    print("  - Advanced Technical Indicators")
    print("  - Enhanced ML Predictions")
    print("  - Backtesting")
    print("  - Portfolio Tracking")
    print("  - News Sentiment Analysis")
    print("=" * 60)
    print("  Open: http://localhost:8080")
    print("=" * 60)
    app.run(host='0.0.0.0', port=8080, debug=False)
