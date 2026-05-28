# Run script for the Indian Stock Market Analyzer
import sys
import os

# Add the project directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app import app

if __name__ == '__main__':
    print("=" * 60)
    print("  Indian Stock Market Analyzer")
    print("=" * 60)
    print("  Features:")
    print("  - Technical Analysis (RSI, MACD, Bollinger Bands, etc.)")
    print("  - ML Predictions (Random Forest + Gradient Boosting)")
    print("  - News Sentiment Analysis")
    print("  - Top 10 Stock Recommendations")
    print("=" * 60)
    print("  Open your browser and go to: http://localhost:5000")
    print("=" * 60)
    
    app.run(host='0.0.0.0', port=5000, debug=True)
