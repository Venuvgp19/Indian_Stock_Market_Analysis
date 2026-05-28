"""
Indian Stock Market Research & Analyzer App
Main Flask Application - Now with 200+ stocks and Stock Research Page
"""

from flask import Flask, render_template, jsonify, request
import json
import threading
import time
from datetime import datetime
import sys
import os
import pandas as pd
import numpy as np

# Add modules directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from modules.data_fetcher import StockDataFetcher
from modules.technical_analyzer import TechnicalAnalyzer
from modules.ml_predictor import MLPredictor
from modules.news_validator import NewsValidator
from modules.stock_selector import StockSelector
from modules.backtester import Backtester
from modules.advanced_indicators import AdvancedIndicators
from modules.portfolio_tracker import PortfolioTracker
from modules.strategy_evaluator import StrategyEvaluator

app = Flask(__name__)

# Initialize components
data_fetcher = StockDataFetcher()
technical_analyzer = TechnicalAnalyzer()
ml_predictor = MLPredictor()
news_validator = NewsValidator()
stock_selector = StockSelector(data_fetcher, technical_analyzer, ml_predictor, news_validator)
backtester = Backtester()
advanced_indicators = AdvancedIndicators()
portfolio_tracker = PortfolioTracker()
strategy_evaluator = StrategyEvaluator()

# Cache for analysis results
cache = {
    'top_stocks': None,
    'last_updated': None,
    'individual_analysis': {}
}

# Pre-populate cache with demo data on startup
def initialize_cache():
    """Initialize cache with demo data so the home page loads instantly"""
    global cache
    
    # Demo stock data for initial load
    demo_stocks = [
        {
            'symbol': 'RELIANCE.NS',
            'company_name': 'Reliance Industries',
            'current_price': 1354.30,
            'price_change': 2.39,
            'tech_score': 35,
            'tech_details': {'rsi': 31.9, 'macd': -9.84, 'adx': 27.57, 'score': 35},
            'ml_prediction': 'BULLISH',
            'ml_confidence': 63,
            'ml_prob_up': 0.638,
            'news_sentiment': 46.2,
            'news_label': 'NEUTRAL',
            'news_recommendation': 'HOLD',
            'composite_score': 48.16,
            'recommendation': 'HOLD',
            'articles': []
        },
        {
            'symbol': 'TCS.NS',
            'company_name': 'Tata Consultancy Services',
            'current_price': 3245.50,
            'price_change': 1.85,
            'tech_score': 58,
            'tech_details': {'rsi': 52.3, 'macd': 2.15, 'adx': 22.1, 'score': 58},
            'ml_prediction': 'BULLISH',
            'ml_confidence': 72,
            'ml_prob_up': 0.72,
            'news_sentiment': 62.5,
            'news_label': 'POSITIVE',
            'news_recommendation': 'BUY',
            'composite_score': 64.33,
            'recommendation': 'BUY',
            'articles': []
        },
        {
            'symbol': 'HDFCBANK.NS',
            'company_name': 'HDFC Bank',
            'current_price': 1420.80,
            'price_change': -0.45,
            'tech_score': 62,
            'tech_details': {'rsi': 48.7, 'macd': 1.23, 'adx': 25.8, 'score': 62},
            'ml_prediction': 'BULLISH',
            'ml_confidence': 68,
            'ml_prob_up': 0.68,
            'news_sentiment': 55.3,
            'news_label': 'POSITIVE',
            'news_recommendation': 'BUY',
            'composite_score': 61.80,
            'recommendation': 'BUY',
            'articles': []
        },
        {
            'symbol': 'INFY.NS',
            'company_name': 'Infosys',
            'current_price': 1450.25,
            'price_change': 1.12,
            'tech_score': 55,
            'tech_details': {'rsi': 50.1, 'macd': 0.85, 'adx': 20.5, 'score': 55},
            'ml_prediction': 'NEUTRAL',
            'ml_confidence': 52,
            'ml_prob_up': 0.52,
            'news_sentiment': 58.7,
            'news_label': 'POSITIVE',
            'news_recommendation': 'BUY',
            'composite_score': 55.26,
            'recommendation': 'BUY',
            'articles': []
        },
        {
            'symbol': 'ICICIBANK.NS',
            'company_name': 'ICICI Bank',
            'current_price': 875.60,
            'price_change': 0.95,
            'tech_score': 65,
            'tech_details': {'rsi': 55.2, 'macd': 3.12, 'adx': 28.5, 'score': 65},
            'ml_prediction': 'BULLISH',
            'ml_confidence': 75,
            'ml_prob_up': 0.75,
            'news_sentiment': 48.3,
            'news_label': 'NEUTRAL',
            'news_recommendation': 'HOLD',
            'composite_score': 62.85,
            'recommendation': 'BUY',
            'articles': []
        },
        {
            'symbol': 'HINDUNILVR.NS',
            'company_name': 'Hindustan Unilever',
            'current_price': 2180.40,
            'price_change': -1.25,
            'tech_score': 48,
            'tech_details': {'rsi': 45.8, 'macd': -1.25, 'adx': 18.2, 'score': 48},
            'ml_prediction': 'NEUTRAL',
            'ml_confidence': 48,
            'ml_prob_up': 0.48,
            'news_sentiment': 42.1,
            'news_label': 'NEUTRAL',
            'news_recommendation': 'HOLD',
            'composite_score': 45.57,
            'recommendation': 'HOLD',
            'articles': []
        },
        {
            'symbol': 'ITC.NS',
            'company_name': 'ITC',
            'current_price': 395.80,
            'price_change': 0.65,
            'tech_score': 52,
            'tech_details': {'rsi': 49.3, 'macd': 0.45, 'adx': 21.8, 'score': 52},
            'ml_prediction': 'BULLISH',
            'ml_confidence': 58,
            'ml_prob_up': 0.58,
            'news_sentiment': 51.4,
            'news_label': 'POSITIVE',
            'news_recommendation': 'BUY',
            'composite_score': 53.52,
            'recommendation': 'BUY',
            'articles': []
        },
        {
            'symbol': 'SBIN.NS',
            'company_name': 'State Bank of India',
            'current_price': 575.20,
            'price_change': 1.85,
            'tech_score': 58,
            'tech_details': {'rsi': 53.7, 'macd': 2.35, 'adx': 24.6, 'score': 58},
            'ml_prediction': 'BULLISH',
            'ml_confidence': 65,
            'ml_prob_up': 0.65,
            'news_sentiment': 55.8,
            'news_label': 'POSITIVE',
            'news_recommendation': 'BUY',
            'composite_score': 59.43,
            'recommendation': 'BUY',
            'articles': []
        },
        {
            'symbol': 'BHARTIARTL.NS',
            'company_name': 'Bharti Airtel',
            'current_price': 875.50,
            'price_change': -0.35,
            'tech_score': 50,
            'tech_details': {'rsi': 47.2, 'macd': 0.15, 'adx': 19.8, 'score': 50},
            'ml_prediction': 'NEUTRAL',
            'ml_confidence': 52,
            'ml_prob_up': 0.52,
            'news_sentiment': 49.2,
            'news_label': 'NEUTRAL',
            'news_recommendation': 'HOLD',
            'composite_score': 50.34,
            'recommendation': 'HOLD',
            'articles': []
        },
        {
            'symbol': 'BAJFINANCE.NS',
            'company_name': 'Bajaj Finance',
            'current_price': 6820.75,
            'price_change': 2.15,
            'tech_score': 70,
            'tech_details': {'rsi': 58.5, 'macd': 5.25, 'adx': 32.1, 'score': 70},
            'ml_prediction': 'BULLISH',
            'ml_confidence': 78,
            'ml_prob_up': 0.78,
            'news_sentiment': 61.3,
            'news_label': 'POSITIVE',
            'news_recommendation': 'STRONG_BUY',
            'composite_score': 70.15,
            'recommendation': 'STRONG_BUY',
            'articles': []
        }
    ]
    
    cache['top_stocks'] = demo_stocks
    cache['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    print("[OK] Cache initialized with {} demo stocks".format(len(demo_stocks)))

# Initialize cache on startup
initialize_cache()

@app.route('/')
def index():
    """Home page"""
    return render_template('index.html')

@app.route('/research')
def research():
    """Dedicated stock research page"""
    return render_template('research.html')

@app.route('/api/stocks')
def get_stocks():
    """Get list of ALL available stocks"""
    stocks = []
    for symbol in data_fetcher.get_all_stocks_list():
        stocks.append({
            'symbol': symbol,
            'name': data_fetcher.get_stock_name(symbol),
            'category': data_fetcher.get_stock_category(symbol)
        })
    return jsonify(stocks)

@app.route('/portfolio')
def portfolio_page():
    """Portfolio Dashboard Page"""
    return render_template('portfolio.html')

@app.route('/backtest')
def backtest_page():
    """Backtesting Strategy Page"""
    return render_template('backtest.html')

@app.route('/api/stocks/by-category')
def get_stocks_by_category():
    """Get stocks grouped by category"""
    return jsonify({
        'nifty50': [
            {'symbol': s, 'name': data_fetcher.get_stock_name(s)} 
            for s in data_fetcher.get_nifty50_list()
        ],
        'nifty_next50': [
            {'symbol': s, 'name': data_fetcher.get_stock_name(s)} 
            for s in data_fetcher.get_nifty_next50_list()
        ],
        'midcap': [
            {'symbol': s, 'name': data_fetcher.get_stock_name(s)} 
            for s in data_fetcher.get_midcap_list()
        ]
    })

@app.route('/api/analyze/<symbol>')
def analyze_stock(symbol):
    """Analyze a specific stock"""
    try:
        # Check cache first
        if symbol in cache['individual_analysis']:
            cached = cache['individual_analysis'][symbol]
            if time.time() - cached['timestamp'] < 300:  # 5 min cache
                return jsonify(cached['data'])
        
        result = stock_selector.analyze_stock(symbol)
        if result:
            cache['individual_analysis'][symbol] = {
                'data': result,
                'timestamp': time.time()
            }
            return jsonify(result)
        else:
            return jsonify({'error': 'Failed to analyze stock'}), 500
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/top-stocks')
def get_top_stocks():
    """Get top 10 stock recommendations"""
    try:
        # Return cached data if available
        if cache['top_stocks'] is not None:
            return jsonify({
                'stocks': cache['top_stocks'],
                'last_updated': cache['last_updated']
            })
        
        # Otherwise, do live analysis (slower)
        symbols = data_fetcher.get_nifty50_list()[:15]
        results = stock_selector.get_top_stocks(symbols, top_n=10)
        
        return jsonify({
            'stocks': results,
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/refresh-analysis')
def refresh_analysis():
    """Force refresh of analysis"""
    try:
        cache['top_stocks'] = None
        cache['individual_analysis'] = {}
        
        symbols = data_fetcher.get_nifty50_list()[:15]
        results = stock_selector.get_top_stocks(symbols, top_n=10)
        
        cache['top_stocks'] = results
        cache['last_updated'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        return jsonify({
            'stocks': results,
            'last_updated': cache['last_updated']
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/strategy-evaluation/<symbol>')
def get_strategy_evaluation(symbol):
    """Get real-time strategy evaluation for a stock"""
    try:
        stock_data = data_fetcher.fetch_stock_data(symbol, '6mo')
        if stock_data is None:
            return jsonify({'error': 'No data available'}), 404
        
        # Get ML prediction
        analysis = stock_selector.analyze_stock(symbol)
        ml_pred = analysis.get('ml_prediction', 'NEUTRAL') if analysis else 'NEUTRAL'
        ml_conf = analysis.get('ml_confidence', 50) if analysis else 50
        tech_details = analysis.get('tech_details', {}) if analysis else {}
        
        result = strategy_evaluator.evaluate_strategies(stock_data, tech_details, ml_pred, ml_conf)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/stock-data/<symbol>')
def get_stock_data(symbol):
    """Get historical stock data for charts"""
    try:
        period = request.args.get('period', '1y')
        data = data_fetcher.fetch_stock_data(symbol, period)
        
        if data is not None:
            # Convert to list of dicts for JSON serialization
            records = data.to_dict('records')
            for record in records:
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
            
            return jsonify({
                'symbol': symbol,
                'data': records
            })
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
            
            # Convert to list of dicts
            records = indicators.tail(30).to_dict('records')
            for record in records:
                if isinstance(record['Date'], datetime):
                    record['Date'] = record['Date'].strftime('%Y-%m-%d')
            
            return jsonify({
                'symbol': symbol,
                'indicators': records
            })
        else:
            return jsonify({'error': 'No data available'}), 404
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/search')
def search_stocks():
    """Search for stocks across all categories"""
    query = request.args.get('q', '').lower()
    
    if not query:
        return jsonify([])
    
    results = []
    for symbol in data_fetcher.get_all_stocks_list():
        name = data_fetcher.get_stock_name(symbol).lower()
        if query in symbol.lower() or query in name:
            results.append({
                'symbol': symbol,
                'name': data_fetcher.get_stock_name(symbol),
                'category': data_fetcher.get_stock_category(symbol)
            })
    
    return jsonify(results[:20])

# Portfolio Management Endpoints
@app.route('/api/portfolio/add', methods=['POST'])
def add_to_portfolio():
    """Add stock to portfolio"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        shares = data.get('shares')
        buy_price = data.get('buy_price')
        
        if not all([symbol, shares, buy_price]):
            return jsonify({'error': 'Missing required fields'}), 400
        
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
        shares = data.get('shares')
        sell_price = data.get('sell_price')
        
        if not all([symbol, shares, sell_price]):
            return jsonify({'error': 'Missing required fields'}), 400
        
        result = portfolio_tracker.remove_stock(symbol, shares, sell_price)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/watchlist')
def get_watchlist():
    """Get watchlist"""
    try:
        watchlist = portfolio_tracker.get_watchlist()
        return jsonify({'watchlist': watchlist})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """Add stock to watchlist"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        
        if not symbol:
            return jsonify({'error': 'Symbol required'}), 400
        
        result = portfolio_tracker.add_to_watchlist(symbol)
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/transactions')
def get_transactions():
    """Get transaction history"""
    try:
        transactions = portfolio_tracker.get_transaction_history()
        return jsonify({'transactions': transactions})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# NEW ENDPOINTS FOR ENHANCED FEATURES

@app.route('/api/backtest/<symbol>', methods=['GET','POST'])
def backtest_stock(symbol):
    """Run backtest on a stock with specified strategy"""
    try:
        if request.method == 'POST':
            data = request.get_json()
            strategy = data.get('strategy', 'combined')
            period = data.get('period', '2y')
        else:
            strategy = request.args.get('strategy', 'combined')
            period = request.args.get('period', '2y')
        
        stock_data = data_fetcher.fetch_stock_data(symbol, period)
        if stock_data is None:
            return jsonify({'error': 'No data available'}), 404
        
        result = backtester.run_strategy(stock_data, strategy)
        return jsonify(result)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/backtest/compare/<symbol>')
def compare_strategies(symbol):
    """Compare all backtest strategies"""
    try:
        period = request.args.get('period', '2y')
        stock_data = data_fetcher.fetch_stock_data(symbol, period)
        
        if stock_data is None:
            return jsonify({'error': 'No data available'}), 404
        
        results = backtester.compare_strategies(stock_data)
        return jsonify({
            'symbol': symbol,
            'strategies': results
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/lstm-predict/<symbol>')
def lstm_predict(symbol):
    """Get LSTM prediction for a stock"""
    try:
        stock_data = data_fetcher.fetch_stock_data(symbol, '2y')
        if stock_data is None:
            return jsonify({'error': 'No data available'}), 404
        
        # Try to get LSTM prediction
        lstm_result = ml_predictor.predict_lstm(symbol, stock_data)
        
        if lstm_result:
            return jsonify({
                'symbol': symbol,
                'lstm_prediction': lstm_result
            })
        else:
            return jsonify({
                'symbol': symbol,
                'message': 'LSTM model not available (TensorFlow may not be installed)',
                'lstm_prediction': None
            })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/ml-details/<symbol>')
def ml_details(symbol):
    """Get detailed ML analysis with individual model predictions"""
    try:
        stock_data = data_fetcher.fetch_stock_data(symbol, '1y')
        if stock_data is None:
            return jsonify({'error': 'No data available'}), 404
        
        # Get ML prediction (the new version takes just symbol and data)
        ml_result = ml_predictor.predict(symbol, stock_data)
        
        # Get latest technical values for reference
        from modules.technical_analyzer import TechnicalAnalyzer
        analyzer = TechnicalAnalyzer()
        indicators = analyzer.calculate_all_indicators(stock_data)
        
        return jsonify({
            'symbol': symbol,
            'ml_prediction': ml_result,
            'technical_summary': {
                'close': indicators['Close'].iloc[-1],
                'sma_20': indicators['SMA_20'].iloc[-1],
                'sma_50': indicators['SMA_50'].iloc[-1],
                'rsi': indicators['RSI'].iloc[-1],
                'macd': indicators['MACD'].iloc[-1]
            }
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/advanced-indicators/<symbol>')
def get_advanced_indicators(symbol):
    """Get advanced technical indicators"""
    try:
        stock_data = data_fetcher.fetch_stock_data(symbol, '1y')
        if stock_data is None:
            return jsonify({'error': 'No data available'}), 404
        
        indicators = advanced_indicators.calculate_all_advanced(stock_data)
        
        # Convert to list of dicts for JSON
        records = indicators.tail(30).to_dict('records')
        for record in records:
            if isinstance(record.get('Date'), datetime):
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
            elif isinstance(record.get('Date'), pd.Timestamp):
                record['Date'] = record['Date'].strftime('%Y-%m-%d')
        
        return jsonify({
            'symbol': symbol,
            'indicators': records
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/summary')
def portfolio_summary():
    """Get portfolio summary"""
    try:
        summary = portfolio_tracker.get_portfolio_summary()
        return jsonify(summary)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/portfolio/holdings')
def portfolio_holdings():
    """Get portfolio holdings"""
    try:
        holdings = portfolio_tracker.get_holdings()
        return jsonify(holdings)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/market-overview')
def market_overview():
    """Get market overview"""
    try:
        # Get major indices
        indices = {
            'NIFTY_50': data_fetcher.fetch_stock_data('^NSEI', '5d'),
            'SENSEX': data_fetcher.fetch_stock_data('^BSESN', '5d'),
            'NIFTY_BANK': data_fetcher.fetch_stock_data('^NSEBANK', '5d'),
            'NIFTY_IT': data_fetcher.fetch_stock_data('^CNXIT', '5d')
        }
        
        overview = {}
        for name, data in indices.items():
            if data is not None and len(data) > 0:
                latest = data['Close'].iloc[-1]
                prev = data['Close'].iloc[-2] if len(data) > 1 else latest
                change = ((latest - prev) / prev) * 100 if prev != 0 else 0
                
                overview[name] = {
                    'value': round(latest, 2),
                    'change': round(change, 2),
                    'change_pct': round(change, 2)
                }
        
        return jsonify(overview)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/stock/<symbol>')
def stock_detail_page(symbol):
    """Stock detail page"""
    return render_template('stock_detail.html', symbol=symbol)

@app.route('/api/stock-detail/<symbol>')
def get_stock_detail(symbol):
    """Get comprehensive stock detail with all strategy metrics"""
    try:
        # 1. Basic stock analysis
        analysis = stock_selector.analyze_stock(symbol)
        if not analysis:
            return jsonify({'error': 'Failed to analyze stock'}), 500

        # 2. Historical data for charts
        stock_data = data_fetcher.fetch_stock_data(symbol, '1y')
        chart_data = []
        if stock_data is not None:
            records = stock_data.to_dict('records')
            for record in records:
                chart_data.append({
                    'date': record['Date'].strftime('%Y-%m-%d') if hasattr(record['Date'], 'strftime') else str(record['Date']),
                    'open': round(record['Open'], 2),
                    'high': round(record['High'], 2),
                    'low': round(record['Low'], 2),
                    'close': round(record['Close'], 2),
                    'volume': int(record['Volume'])
                })

        # 3. Technical indicators history
        tech_history = []
        if stock_data is not None:
            indicators = technical_analyzer.calculate_all_indicators(stock_data)
            records = indicators.tail(60).to_dict('records')
            for record in records:
                tech_history.append({
                    'date': record['Date'].strftime('%Y-%m-%d') if hasattr(record['Date'], 'strftime') else str(record['Date']),
                    'sma_20': round(record.get('SMA_20', 0), 2) if pd.notna(record.get('SMA_20')) else None,
                    'sma_50': round(record.get('SMA_50', 0), 2) if pd.notna(record.get('SMA_50')) else None,
                    'sma_200': round(record.get('SMA_200', 0), 2) if pd.notna(record.get('SMA_200')) else None,
                    'rsi': round(record.get('RSI', 0), 2) if pd.notna(record.get('RSI')) else None,
                    'macd': round(record.get('MACD', 0), 2) if pd.notna(record.get('MACD')) else None,
                    'macd_signal': round(record.get('MACD_Signal', 0), 2) if pd.notna(record.get('MACD_Signal')) else None,
                    'bb_upper': round(record.get('BB_Upper', 0), 2) if pd.notna(record.get('BB_Upper')) else None,
                    'bb_lower': round(record.get('BB_Lower', 0), 2) if pd.notna(record.get('BB_Lower')) else None,
                    'adx': round(record.get('ADX', 0), 2) if pd.notna(record.get('ADX')) else None
                })

        # 4. Advanced indicators
        adv_indicators = {}
        if stock_data is not None:
            try:
                adv_df = advanced_indicators.calculate_all_advanced(stock_data)
                if adv_df is not None and not adv_df.empty:
                    latest_adv = adv_df.iloc[-1]
                    adv_indicators = {
                        'vwap': round(float(latest_adv.get('VWAP', 0)), 2) if pd.notna(latest_adv.get('VWAP')) else None,
                        'super_trend': round(float(latest_adv.get('SuperTrend', 0)), 2) if pd.notna(latest_adv.get('SuperTrend')) else None,
                        'super_trend_direction': int(latest_adv.get('SuperTrend_Direction', 0)) if pd.notna(latest_adv.get('SuperTrend_Direction')) else None,
                        'williams_r': round(float(latest_adv.get('Williams_R', 0)), 2) if pd.notna(latest_adv.get('Williams_R')) else None,
                        'mfi': round(float(latest_adv.get('MFI', 0)), 2) if pd.notna(latest_adv.get('MFI')) else None,
                        'cmo': round(float(latest_adv.get('CMO', 0)), 2) if pd.notna(latest_adv.get('CMO')) else None,
                        'stochastic_k': round(float(latest_adv.get('Stochastic_K', 0)), 2) if pd.notna(latest_adv.get('Stochastic_K')) else None,
                        'stochastic_d': round(float(latest_adv.get('Stochastic_D', 0)), 2) if pd.notna(latest_adv.get('Stochastic_D')) else None,
                        'cci': round(float(latest_adv.get('CCI', 0)), 2) if pd.notna(latest_adv.get('CCI')) else None,
                        'atr': round(float(latest_adv.get('ATR', 0)), 2) if pd.notna(latest_adv.get('ATR')) else None,
                        'obv': int(latest_adv.get('OBV', 0)) if pd.notna(latest_adv.get('OBV')) else None,
                        'parabolic_sar': round(float(latest_adv.get('Parabolic_SAR', 0)), 2) if pd.notna(latest_adv.get('Parabolic_SAR')) else None,
                        'donchian_upper': round(float(latest_adv.get('Donchian_Upper', 0)), 2) if pd.notna(latest_adv.get('Donchian_Upper')) else None,
                        'donchian_lower': round(float(latest_adv.get('Donchian_Lower', 0)), 2) if pd.notna(latest_adv.get('Donchian_Lower')) else None,
                        'roc_10': round(float(latest_adv.get('ROC_10', 0)), 2) if pd.notna(latest_adv.get('ROC_10')) else None,
                        'roc_20': round(float(latest_adv.get('ROC_20', 0)), 2) if pd.notna(latest_adv.get('ROC_20')) else None,
                        'trix': round(float(latest_adv.get('TRIX', 0)), 2) if pd.notna(latest_adv.get('TRIX')) else None,
                        'keltner_upper': round(float(latest_adv.get('Keltner_Upper', 0)), 2) if pd.notna(latest_adv.get('Keltner_Upper')) else None,
                        'keltner_lower': round(float(latest_adv.get('Keltner_Lower', 0)), 2) if pd.notna(latest_adv.get('Keltner_Lower')) else None,
                        'ema_12': round(float(latest_adv.get('EMA_12', 0)), 2) if pd.notna(latest_adv.get('EMA_12')) else None,
                        'ema_26': round(float(latest_adv.get('EMA_26', 0)), 2) if pd.notna(latest_adv.get('EMA_26')) else None,
                        'ichimoku_tenkan': round(float(latest_adv.get('tenkan_sen', 0)), 2) if pd.notna(latest_adv.get('tenkan_sen')) else None,
                        'ichimoku_kijun': round(float(latest_adv.get('kijun_sen', 0)), 2) if pd.notna(latest_adv.get('kijun_sen')) else None,
                    }
                    # Fibonacci levels
                    fib_keys = ['Fib_Fib_0', 'Fib_Fib_23.6', 'Fib_Fib_38.2', 'Fib_Fib_50', 'Fib_Fib_61.8', 'Fib_Fib_78.6', 'Fib_Fib_100']
                    fib_present = {}
                    for fk in fib_keys:
                        if fk in latest_adv.index and pd.notna(latest_adv.get(fk)):
                            clean_key = fk.replace('Fib_Fib_', 'fib_').replace('.', '_')
                            fib_present[clean_key] = round(float(latest_adv.get(fk)), 2)
                    if fib_present:
                        adv_indicators['fibonacci_levels'] = fib_present
                    # Pivot points
                    pivot_keys = {'Pivot_pivot': 'pivot', 'Pivot_r1': 'r1', 'Pivot_r2': 'r2', 'Pivot_r3': 'r3', 'Pivot_s1': 's1', 'Pivot_s2': 's2', 'Pivot_s3': 's3'}
                    pivot_present = {}
                    for pk, clean in pivot_keys.items():
                        if pk in latest_adv.index and pd.notna(latest_adv.get(pk)):
                            pivot_present[clean] = round(float(latest_adv.get(pk)), 2)
                    if pivot_present:
                        adv_indicators['pivot_points'] = pivot_present
                    # Support/Resistance
                    try:
                        sr = advanced_indicators.get_support_resistance(stock_data)
                        adv_indicators['support_resistance'] = sr
                    except Exception:
                        pass
            except Exception as e:
                adv_indicators = {'error': str(e)}
        # 5. Backtest strategies
        backtest_results = {}
        if stock_data is not None:
            try:
                strategies = ['sma_crossover', 'rsi_strategy', 'macd_strategy', 'bollinger_strategy', 'combined']
                for strategy in strategies:
                    result = backtester.run_strategy(stock_data, strategy)
                    backtest_results[strategy] = {
                        'total_return': result.get('total_return', 0),
                        'buy_hold_return': result.get('buy_hold_return', 0),
                        'sharpe_ratio': result.get('sharpe_ratio', 0),
                        'max_drawdown': result.get('max_drawdown', 0),
                        'total_trades': result.get('total_trades', 0),
                        'win_rate': result.get('win_rate', 0),
                        'outperformance': result.get('outperformance', 0)
                    }
            except Exception as e:
                backtest_results = {'error': str(e)}
        # 6. LSTM prediction
        lstm_data = {}
        try:
            if stock_data is not None:
                lstm_result = ml_predictor.predict_lstm(symbol, stock_data)
                if lstm_result:
                    lstm_data = lstm_result
                else:
                    lstm_data = {'message': 'LSTM prediction not available'}
            else:
                lstm_data = {'message': 'No historical data for LSTM'}
        except Exception as e:
            lstm_data = {'message': f'LSTM error: {str(e)}'}

        # 7. Strategy Evaluation - determine which strategies are currently favorable
        strategy_evaluation = {}
        try:
            if stock_data is not None:
                tech_details = analysis.get('tech_details', {})
                ml_pred = analysis.get('ml_prediction', 'NEUTRAL')
                ml_conf = analysis.get('ml_confidence', 50)
                strategy_evaluation = strategy_evaluator.evaluate_strategies(stock_data, tech_details, ml_pred, ml_conf)
        except Exception as e:
            strategy_evaluation = {'error': str(e)}

        # 8. ML model details
        ml_details_data = {}

        # Compile all data
        detail = {
            'symbol': symbol,
            'company_name': analysis.get('company_name', symbol),
            'current_price': analysis.get('current_price', 0),
            'price_change': analysis.get('price_change', 0),
            'last_updated': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            
            # Technical Analysis
            'technical': {
                'score': analysis.get('tech_score', 0),
                'details': analysis.get('tech_details', {})
            },
            
            # ML Analysis
            'ml': {
                'prediction': analysis.get('ml_prediction', 'N/A'),
                'confidence': analysis.get('ml_confidence', 0),
                'prob_up': analysis.get('ml_prob_up', 0),
                'details': ml_details_data,
                'lstm': lstm_data
            },
            
            # News Sentiment
            'news': {
                'sentiment_score': analysis.get('news_sentiment', 0),
                'label': analysis.get('news_label', 'N/A'),
                'recommendation': analysis.get('news_recommendation', 'N/A'),
                'articles': analysis.get('articles', [])
            },
            
            # Composite
            'composite': {
                'score': analysis.get('composite_score', 0),
                'recommendation': analysis.get('recommendation', 'N/A')
            },
            
            # LSTM (direct from predictor)
            'lstm': lstm_data,
            
            # Advanced Indicators
            'advanced_indicators': adv_indicators,
            
            # Chart Data
            'chart_data': chart_data,
            'tech_history': tech_history,
            
            # Backtest Results
            'backtest': backtest_results,
            
            # Strategy Evaluation
            'strategy_evaluation': strategy_evaluation
        }

        return jsonify(detail)

    except Exception as e:
        return jsonify({'error': str(e)}), 500

import threading
from datetime import datetime

# Global store for MiroFish jobs
mirofish_jobs = {}
mirofish_job_counter = 0
mirofish_lock = threading.Lock()

def run_mirofish_agent_sync(miro, agent, stock_data):
    """Run a single agent synchronously and return result (uses kimi-k2.6:cloud)"""
    try:
        prompt = miro._build_stock_prompt(agent, stock_data or {})
        # Log which model is being used for this agent call
        model_name = getattr(miro.llm, 'model', 'unknown')
        print(f"  [Agent {agent['name']}] Calling model: {model_name}")
        response = miro.llm.chat([
            {"role": "system", "content": f"You are {agent['name']}, {agent['type']}"},
            {"role": "user", "content": prompt}
        ], timeout=60)
        print(f"  [Agent {agent['name']}] Response received (len={len(str(response))})")
        return {"perspective": response, "type": agent['type'], "done": True, "error": False}
    except Exception as e:
        print(f"  [Agent {agent['name']}] ERROR: {str(e)}")
        return {"perspective": f"[ERROR: {str(e)}]", "type": agent['type'], "done": True, "error": True}

@app.route('/mirofish/<symbol>')
def mirofish_page(symbol):
    """MiroFish AI multi-agent stock analysis page"""
    return render_template('mirofish.html', symbol=symbol)

@app.route('/api/mirofish-run/<symbol>', methods=['POST'])
def mirofish_run_with_data(symbol):
    """Start MiroFish using ALREADY COLLECTED data from the detail page (no extra fetch)"""
    global mirofish_job_counter
    try:
        import sys
        sys.path.append(r'C:\Users\praneeth\.openclaw\workspace\mirofish\backend')
        from realtime_mirofish_framework import RealTimeMiroFish

        # Read already-collected data sent from the detail page
        payload = request.get_json(force=True, silent=True) or {}
        stock_data = payload if payload else None

        # Create job
        with mirofish_lock:
            mirofish_job_counter += 1
            job_id = mirofish_job_counter

        miro = RealTimeMiroFish(f"Stock: {symbol}", num_agents=5)
        miro.stock_symbol = symbol
        # Force model to kimi-k2.6:cloud explicitly (NOT qwen)
        miro.llm.model = "kimi-k2.6:cloud"
        # CRITICAL: create stock agents so miro.agents is populated
        miro.create_stock_agents(symbol)
        print(f"  [MiroFish-inline] Initialized. Model set to: {miro.llm.model}. Agents: {len(miro.agents)}")

        # Build agent-to-agent message graph (same as standalone page)
        agent_names = [a['name'] for a in miro.agents]
        graph = {}
        for i, agent in enumerate(miro.agents):
            others = [n for n in agent_names if n != agent['name']]
            if agent['type'] == 'Technical Analyst':
                graph[agent['name']] = [n for n in others if 'Fundamental' in n or 'ML' in n]
            elif agent['type'] == 'Fundamental Analyst':
                graph[agent['name']] = [n for n in others if 'Risk' in n or 'Portfolio' in n]
            elif agent['type'] == 'ML/Quant Strategist':
                graph[agent['name']] = [n for n in others if 'Technical' in n or 'Risk' in n]
            elif agent['type'] == 'Risk Manager':
                graph[agent['name']] = [n for n in others if 'Portfolio' in n]
            elif agent['type'] == 'Portfolio Manager':
                graph[agent['name']] = [n for n in others if 'Fundamental' in n or 'ML' in n]
            else:
                graph[agent['name']] = []

        with mirofish_lock:
            mirofish_jobs[job_id] = {
                'job_id': job_id,
                'symbol': symbol,
                'company_name': stock_data.get('company_name', symbol) if stock_data else symbol,
                'current_price': stock_data.get('current_price', 'N/A') if stock_data else 'N/A',
                'status': 'running',
                'perspectives': {},
                'report': None,
                'completed_agents': 0,
                'total_agents': len(miro.agents),
                'agents': miro.agents,
                'miro': miro,
                'stock_data': stock_data,
                'graph': graph
            }

        # Run agents SEQUENTIALLY in a single background thread
        def run_all_agents():
            start_time = datetime.now()
            for i, agent in enumerate(miro.agents):
                agent_start = datetime.now()
                print(f"  [MiroFish-inline] Agent {i+1}/{len(miro.agents)}: {agent['name']} starting...")
                result = run_mirofish_agent_sync(miro, agent, stock_data)
                agent_elapsed = (datetime.now() - agent_start).total_seconds()
                print(f"  [MiroFish-inline] Agent {agent['name']} completed in {agent_elapsed:.1f}s")
                with mirofish_lock:
                    if job_id in mirofish_jobs:
                        mirofish_jobs[job_id]['perspectives'][agent['name']] = result
                        mirofish_jobs[job_id]['completed_agents'] += 1
            total_elapsed = (datetime.now() - start_time).total_seconds()
            print(f"  [MiroFish-inline] All {len(miro.agents)} agents done in {total_elapsed:.1f}s. Generating report...")
            # After all agents done, generate report
            with mirofish_lock:
                if job_id in mirofish_jobs:
                    mirofish_jobs[job_id]['status'] = 'generating_report'
            try:
                report = miro.generate_report(mirofish_jobs[job_id]['perspectives'], graph)
                with mirofish_lock:
                    if job_id in mirofish_jobs:
                        mirofish_jobs[job_id]['report'] = report
                        mirofish_jobs[job_id]['status'] = 'complete'
            except Exception as e:
                with mirofish_lock:
                    if job_id in mirofish_jobs:
                        mirofish_jobs[job_id]['report'] = f"Report error: {str(e)}"
                        mirofish_jobs[job_id]['status'] = 'complete'

        t = threading.Thread(target=run_all_agents)
        t.daemon = True
        t.start()

        return jsonify({
            'job_id': job_id,
            'symbol': symbol,
            'company_name': stock_data.get('company_name', symbol) if stock_data else symbol,
            'current_price': stock_data.get('current_price', 'N/A') if stock_data else 'N/A',
            'status': 'started',
            'total_agents': len(miro.agents),
            'source': 'client_data'
        })

    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mirofish-start/<symbol>')
def mirofish_start(symbol):
    """Start MiroFish analysis SEQUENTIALLY, return job ID immediately"""
    global mirofish_job_counter
    try:
        import sys
        sys.path.append(r'C:\Users\praneeth\.openclaw\workspace\mirofish\backend')
        from realtime_mirofish_framework import RealTimeMiroFish
        
        # Create job
        with mirofish_lock:
            mirofish_job_counter += 1
            job_id = mirofish_job_counter
            
        # Initialize with kimi-k2.6:cloud explicitly (fast, smart)
        miro = RealTimeMiroFish(f"Stock: {symbol}", num_agents=5)
        miro.stock_symbol = symbol
        # Force model to kimi-k2.6:cloud (not qwen)
        miro.llm.model = "kimi-k2.6:cloud"
        # CRITICAL: create stock agents so miro.agents is populated
        miro.create_stock_agents(symbol)
        print(f"  [MiroFish] Initialized. Model set to: {miro.llm.model}. Agents: {len(miro.agents)}")
        
        # Fetch stock data DIRECTLY using internal data_fetcher (no HTTP self-request!)
        stock_data = None
        try:
            # Use the existing data_fetcher from app.py directly
            stock_info = data_fetcher.get_stock_data(symbol)
            stock_data = {
                'symbol': symbol,
                'company_name': stock_info.get('company_name', symbol),
                'current_price': stock_info.get('current_price', 'N/A'),
                'price_change': stock_info.get('price_change_pct', 'N/A'),
                'technical': {},
                'ml': {},
                'news': {},
                'composite': {},
                'advanced_indicators': {},
                'strategy_evaluation': {}
            }
            # Try to enrich with full detail data
            try:
                detail = get_stock_detail(symbol)
                if hasattr(detail, 'json'):
                    detail_data = detail.json
                elif hasattr(detail, 'get_json'):
                    detail_data = detail.get_json()
                else:
                    detail_data = {}
                if isinstance(detail_data, dict) and 'symbol' in detail_data:
                    stock_data = detail_data
            except:
                pass
        except Exception as e:
            print(f"[MiroFish] Data fetch warning: {e}")
            stock_data = {
                'symbol': symbol,
                'company_name': symbol,
                'current_price': 'N/A'
            }
        
        if stock_data:
            miro.kg_builder.add_data("stock_analyzer_comprehensive", stock_data)
        
        miro.create_stock_agents(symbol)
        graph = miro.build_knowledge_graph()
        
        # Store job
        with mirofish_lock:
            mirofish_jobs[job_id] = {
                'symbol': symbol,
                'company_name': stock_data.get('company_name', symbol) if stock_data else symbol,
                'current_price': stock_data.get('current_price', 'N/A') if stock_data else 'N/A',
                'status': 'running',
                'started_at': datetime.now().isoformat(),
                'agents': miro.agents,
                'perspectives': {},
                'completed_agents': 0,
                'total_agents': len(miro.agents),
                'report': None,
                'miro': miro,
                'stock_data': stock_data,
                'graph': graph
            }
        
        # Run agents SEQUENTIALLY in a single background thread (avoids deadlock)
        def run_all_agents():
            start_time = datetime.now()
            for i, agent in enumerate(miro.agents):
                agent_start = datetime.now()
                print(f"  [MiroFish] Agent {i+1}/{len(miro.agents)}: {agent['name']} starting...")
                result = run_mirofish_agent_sync(miro, agent, stock_data)
                agent_elapsed = (datetime.now() - agent_start).total_seconds()
                print(f"  [MiroFish] Agent {agent['name']} completed in {agent_elapsed:.1f}s")
                with mirofish_lock:
                    if job_id in mirofish_jobs:
                        mirofish_jobs[job_id]['perspectives'][agent['name']] = result
                        mirofish_jobs[job_id]['completed_agents'] += 1
            total_elapsed = (datetime.now() - start_time).total_seconds()
            print(f"  [MiroFish] All {len(miro.agents)} agents done in {total_elapsed:.1f}s. Generating report...")
            # After all agents done, generate report
            with mirofish_lock:
                if job_id in mirofish_jobs:
                    mirofish_jobs[job_id]['status'] = 'generating_report'
            try:
                report = miro.generate_report(mirofish_jobs[job_id]['perspectives'], graph)
                with mirofish_lock:
                    if job_id in mirofish_jobs:
                        mirofish_jobs[job_id]['report'] = report
                        mirofish_jobs[job_id]['status'] = 'complete'
            except Exception as e:
                with mirofish_lock:
                    if job_id in mirofish_jobs:
                        mirofish_jobs[job_id]['report'] = f"Report error: {str(e)}"
                        mirofish_jobs[job_id]['status'] = 'complete'
        
        t = threading.Thread(target=run_all_agents)
        t.daemon = True
        t.start()
        
        return jsonify({
            'job_id': job_id,
            'symbol': symbol,
            'company_name': stock_data.get('company_name', symbol) if stock_data else symbol,
            'current_price': stock_data.get('current_price', 'N/A') if stock_data else 'N/A',
            'status': 'started',
            'total_agents': len(miro.agents)
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/api/mirofish-status/<int:job_id>')
def mirofish_status(job_id):
    """Poll for agent completion status"""
    with mirofish_lock:
        job = mirofish_jobs.get(job_id)
        if not job:
            return jsonify({'error': 'Job not found'}), 404
        
        # Check if all agents done and report not yet generated
        if job['completed_agents'] >= job['total_agents'] and job['report'] is None and job['status'] == 'running':
            job['status'] = 'generating_report'
            # Generate report in background
            def generate_report_async():
                try:
                    report = job['miro'].generate_report(job['perspectives'], job['graph'])
                    with mirofish_lock:
                        job['report'] = report
                        job['status'] = 'complete'
                except Exception as e:
                    with mirofish_lock:
                        job['report'] = f"Report generation error: {str(e)}"
                        job['status'] = 'complete'
            t = threading.Thread(target=generate_report_async)
            t.daemon = True
            t.start()
        
        return jsonify({
            'job_id': job_id,
            'symbol': job['symbol'],
            'company_name': job['company_name'],
            'current_price': job['current_price'],
            'status': job['status'],
            'completed_agents': job['completed_agents'],
            'total_agents': job['total_agents'],
            'agents': job['agents'],
            'perspectives': job['perspectives'],
            'report': job['report']
        })

@app.route('/api/mirofish-analyze/<symbol>')
def mirofish_analyze_legacy(symbol):
    """Legacy synchronous endpoint - kept for compatibility"""
    try:
        import sys
        sys.path.append(r'C:\Users\praneeth\.openclaw\workspace\mirofish\backend')
        from realtime_mirofish_framework import RealTimeMiroFish
        
        miro = RealTimeMiroFish(f"Stock: {symbol}", num_agents=5)
        miro.stock_symbol = symbol
        
        stock_data = miro.data_fetcher.fetch_stock_analyzer_data(symbol, 
            base_url=request.url_root.rstrip('/'))
        if stock_data:
            miro.kg_builder.add_data("stock_analyzer_comprehensive", stock_data)
        
        miro.create_stock_agents(symbol)
        graph = miro.build_knowledge_graph()
        
        perspectives = {}
        for agent in miro.agents:
            prompt = miro._build_stock_prompt(agent, stock_data or {})
            response = miro.llm.chat([
                {"role": "system", "content": f"You are {agent['name']}, {agent['type']}"},
                {"role": "user", "content": prompt}
            ])
            perspectives[agent['name']] = {
                "type": agent['type'],
                "perspective": response
            }
        
        report = miro.generate_report(perspectives, graph)
        
        return jsonify({
            'symbol': symbol,
            'company_name': stock_data.get('company_name', symbol) if stock_data else symbol,
            'current_price': stock_data.get('current_price', 'N/A') if stock_data else 'N/A',
            'agents': miro.agents,
            'perspectives': perspectives,
            'report': report,
            'timestamp': datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/market-overview')
def market_overview_page():
    """Market overview page"""
    return render_template('market_overview.html')

@app.route('/api/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat(),
        'version': '2.0.0',
        'features': [
            'technical_analysis',
            'ml_predictions',
            'news_sentiment',
            'backtesting',
            'advanced_indicators',
            'portfolio_tracking',
            'strategy_evaluation'
        ]
    })

if __name__ == '__main__':
    print("=" * 60)
    print("  Indian Stock Market Analyzer")
    print("=" * 60)
    print(f"  Total Stocks: {len(data_fetcher.get_all_stocks_list())}")
    print("    - Nifty 50: {}".format(len(data_fetcher.get_nifty50_list())))
    print("    - Nifty Next 50: {}".format(len(data_fetcher.get_nifty_next50_list())))
    print("    - Midcap 100: {}".format(len(data_fetcher.get_midcap_list())))
    print("=" * 60)
    print("  Starting Flask server...")
    print("  Access the app at: http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=8080, debug=True, threaded=True)

# Note: The /mirofish/<symbol> route is already defined above in the file (around line 1000).
