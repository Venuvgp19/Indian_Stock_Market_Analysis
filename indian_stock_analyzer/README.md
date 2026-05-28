# Indian Stock Market Analysis

A comprehensive stock analysis and portfolio management web application for the Indian stock market. Built with Flask, featuring real-time data, technical indicators, ML predictions, backtesting, and an AI-powered expert panel.

---

## Features

### 1. Stock Analysis
- **Real-time stock data** from Yahoo Finance
- **Technical indicators**: RSI, MACD, Bollinger Bands, Moving Averages
- **Interactive price charts** with candlestick and volume analysis
- **Fundamental data**: P/E, EPS, market cap, dividend yield
- **News sentiment analysis** for informed decisions

### 2. Portfolio Management
- Track your stock holdings with real-time P&L
- Sector allocation visualization
- Risk metrics and diversification analysis

### 3. Backtesting Engine
- Test trading strategies on historical data
- Supports SMA Crossover, RSI Strategy, Bollinger Bands, MACD Signal
- Performance metrics: returns, Sharpe ratio, max drawdown

### 4. Research & Screening
- Screen stocks by technical and fundamental criteria
- Top picks based on momentum and value metrics
- Market overview with sector performance

### 5. MiroFish AI Deep Analysis
The flagship feature — an AI-powered expert panel that analyzes stocks using 5 specialized agents:

| Agent | Role | Focus |
|-------|------|-------|
| Technical Analyst | Chart & pattern expert | Indicators, trends, support/resistance |
| Fundamental Analyst | Value investor | Financials, ratios, growth metrics |
| ML Strategist | Quant researcher | ML models, statistical signals |
| Risk Manager | Risk officer | Volatility, drawdown, position sizing |
| Portfolio Manager | Allocation strategist | Entry timing, portfolio fit |

**How it works:**
1. Navigate to any stock's detail page
2. Click **"Run MiroFish Deep Analysis"**
3. 5 AI agents analyze the stock sequentially using the `kimi-k2.6:cloud` model
4. Watch real-time progress as each agent completes
5. Receive a final investment verdict with confidence score

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Flask (Python) |
| Frontend | HTML5, CSS3, vanilla JS |
| Data Source | Yahoo Finance API |
| AI Model | Ollama (kimi-k2.6:cloud) |
| Charts | Chart.js |
| Styling | Custom CSS with CSS variables |

---

## Quick Start

### Prerequisites
- Python 3.10+
- Ollama running locally with `kimi-k2.6:cloud` model

### Installation

```bash
# Clone the repo
git clone https://github.com/Venuvgp19/Indian_Stock_Market_Analysis.git
cd Indian_Stock_Market_Analysis

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # Linux/Mac

# Install dependencies
pip install -r requirements.txt

# Start Ollama (in separate terminal)
ollama run kimi-k2.6:cloud

# Run the app
python app.py
```

The app will be available at `http://localhost:5000`

---

## Project Structure

```
indian_stock_analyzer/
├── app.py                      # Main Flask application
├── app_v2.py                   # Alternative entry point
├── run.py                      # Simple runner
├── start.bat                   # Windows batch starter
├── requirements.txt            # Python dependencies
├── ENHANCEMENTS.md             # Feature roadmap
├── modules/                    # Core business logic
│   ├── data_fetcher.py         # Yahoo Finance integration
│   ├── technical_analyzer.py   # Indicator calculations
│   ├── ml_predictor.py         # ML models for prediction
│   ├── backtester.py           # Strategy backtesting
│   ├── portfolio_tracker.py    # Portfolio management
│   ├── stock_selector.py       # Stock screening
│   ├── news_validator.py       # News & sentiment
│   ├── advanced_indicators.py  # Advanced technical tools
│   ├── advanced_ml.py          # Advanced ML models
│   └── strategy_evaluator.py   # Strategy analysis
├── templates/                  # HTML templates
│   ├── index.html              # Home page
│   ├── stock_detail.html       # Stock analysis + MiroFish
│   ├── portfolio.html          # Portfolio dashboard
│   ├── backtest.html           # Backtesting UI
│   ├── research.html           # Stock screener
│   ├── market_overview.html    # Market summary
│   └── mirofish.html           # Standalone MiroFish
└── data/
    └── portfolio.json          # Sample portfolio data
```

---

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | Home page with market overview |
| `/stock/<symbol>` | GET | Stock detail page |
| `/api/stock-detail/<symbol>` | GET | Full stock data JSON |
| `/api/mirofish-run/<symbol>` | POST | Start MiroFish analysis |
| `/api/mirofish-status/<job_id>` | GET | Poll analysis progress |
| `/portfolio` | GET | Portfolio page |
| `/backtest` | GET | Backtesting page |
| `/research` | GET | Stock screener |
| `/market-overview` | GET | Market summary data |

---

## MiroFish AI Architecture

The MiroFish system uses a multi-agent architecture:

1. **Data Collection** — Stock data is fetched from Yahoo Finance
2. **Knowledge Graph** — Data is structured into a knowledge graph for AI context
3. **Sequential Agent Execution** — Each of 5 agents runs one at a time to avoid resource contention
4. **Real-time Polling** — Frontend polls every 2 seconds for progress updates
5. **Report Generation** — A final synthesis combines all 5 perspectives into an actionable verdict

**Model Configuration:**
- Primary: `kimi-k2.6:cloud` (1T parameters, ~15-25s per agent)
- Timeout per agent: 100 seconds
- Total analysis time: ~2-3 minutes for all 5 agents

---

## Screenshots

### Stock Detail Page with MiroFish
![Stock Detail](https://via.placeholder.com/800x400?text=Stock+Detail+Page)

### MiroFish Analysis in Progress
![MiroFish](https://via.placeholder.com/800x400?text=MiroFish+AI+Analysis)

### Portfolio Dashboard
![Portfolio](https://via.placeholder.com/800x400?text=Portfolio+Dashboard)

---

## Contributing

This is a personal project. Feel free to fork and adapt for your own use.

---

## License

MIT License — use freely with attribution.

---

## Acknowledgments

- Data powered by [Yahoo Finance](https://finance.yahoo.com)
- AI analysis powered by [Ollama](https://ollama.com) and the `kimi-k2.6:cloud` model
- Charts by [Chart.js](https://chartjs.org)

---

*Built with passion for the Indian stock market.*
