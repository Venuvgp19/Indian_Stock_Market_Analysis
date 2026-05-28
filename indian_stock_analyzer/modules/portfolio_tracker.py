"""
Portfolio Tracking Module
Tracks user's stock portfolio performance with sector allocation and analytics
"""

import json
import os
from datetime import datetime
import pandas as pd
import numpy as np

class PortfolioTracker:
    def __init__(self, portfolio_file='data/portfolio.json'):
        self.portfolio_file = portfolio_file
        self.portfolio = self._load_portfolio()
        
        # Stock sector mapping
        self.sectors = {
            'RELIANCE.NS': 'Energy',
            'TCS.NS': 'IT',
            'INFY.NS': 'IT',
            'HDFCBANK.NS': 'Banking',
            'ICICIBANK.NS': 'Banking',
            'HINDUNILVR.NS': 'FMCG',
            'ITC.NS': 'FMCG',
            'SBIN.NS': 'Banking',
            'BHARTIARTL.NS': 'Telecom',
            'KOTAKBANK.NS': 'Banking',
            'BAJFINANCE.NS': 'Finance',
            'LT.NS': 'Infrastructure',
            'AXISBANK.NS': 'Banking',
            'ASIANPAINT.NS': 'Consumer Goods',
            'MARUTI.NS': 'Automobile',
            'SUNPHARMA.NS': 'Pharma',
            'TITAN.NS': 'Consumer Goods',
            'ULTRACEMCO.NS': 'Cement',
            'NESTLEIND.NS': 'FMCG',
            'WIPRO.NS': 'IT',
            'M&M.NS': 'Automobile',
            'POWERGRID.NS': 'Power',
            'NTPC.NS': 'Power',
            'HDFC.NS': 'Finance',
            'BAJAJFINSV.NS': 'Finance',
            'ADANIENT.NS': 'Conglomerate',
            'TATAMOTORS.NS': 'Automobile',
            'JSWSTEEL.NS': 'Metals',
            'TECHM.NS': 'IT',
            'HCLTECH.NS': 'IT',
            'ONGC.NS': 'Energy',
            'COALINDIA.NS': 'Energy',
            'BPCL.NS': 'Energy',
            'IOC.NS': 'Energy',
            'GRASIM.NS': 'Diversified',
            'CIPLA.NS': 'Pharma',
            'DRREDDY.NS': 'Pharma',
            'EICHERMOT.NS': 'Automobile',
            'BRITANNIA.NS': 'FMCG',
            'TATASTEEL.NS': 'Metals',
            'HINDALCO.NS': 'Metals',
            'ADANIPORTS.NS': 'Infrastructure'
        }
        
    def _load_portfolio(self):
        """Load portfolio from file"""
        if os.path.exists(self.portfolio_file):
            try:
                with open(self.portfolio_file, 'r') as f:
                    return json.load(f)
            except:
                return {'holdings': {}, 'transactions': [], 'watchlist': []}
        return {'holdings': {}, 'transactions': [], 'watchlist': []}
    
    def _save_portfolio(self):
        """Save portfolio to file"""
        os.makedirs(os.path.dirname(self.portfolio_file), exist_ok=True)
        with open(self.portfolio_file, 'w') as f:
            json.dump(self.portfolio, f, indent=2)
    
    def add_stock(self, symbol, shares, buy_price, buy_date=None):
        """Add stock to portfolio"""
        if buy_date is None:
            buy_date = datetime.now().strftime('%Y-%m-%d')
        
        transaction = {
            'symbol': symbol,
            'shares': shares,
            'buy_price': buy_price,
            'buy_date': buy_date,
            'type': 'BUY'
        }
        
        self.portfolio['transactions'].append(transaction)
        
        if symbol in self.portfolio['holdings']:
            # Update existing holding
            holding = self.portfolio['holdings'][symbol]
            total_shares = holding['shares'] + shares
            avg_price = ((holding['shares'] * holding['avg_buy_price']) + (shares * buy_price)) / total_shares
            holding['shares'] = total_shares
            holding['avg_buy_price'] = round(avg_price, 2)
        else:
            # New holding
            self.portfolio['holdings'][symbol] = {
                'shares': shares,
                'avg_buy_price': buy_price,
                'buy_date': buy_date
            }
        
        self._save_portfolio()
        return {'status': 'success', 'message': f'Added {shares} shares of {symbol}'}
    
    def remove_stock(self, symbol, shares, sell_price, sell_date=None):
        """Remove stock from portfolio (sell)"""
        if sell_date is None:
            sell_date = datetime.now().strftime('%Y-%m-%d')
        
        if symbol not in self.portfolio['holdings']:
            return {'status': 'error', 'message': f'Stock {symbol} not in portfolio'}
        
        holding = self.portfolio['holdings'][symbol]
        
        if holding['shares'] < shares:
            return {'status': 'error', 'message': f'Not enough shares. Have {holding["shares"]}, trying to sell {shares}'}
        
        transaction = {
            'symbol': symbol,
            'shares': shares,
            'sell_price': sell_price,
            'sell_date': sell_date,
            'type': 'SELL'
        }
        
        self.portfolio['transactions'].append(transaction)
        
        holding['shares'] -= shares
        if holding['shares'] == 0:
            del self.portfolio['holdings'][symbol]
        
        self._save_portfolio()
        return {'status': 'success', 'message': f'Sold {shares} shares of {symbol}'}
    
    def get_portfolio_summary(self, current_prices=None):
        """Get portfolio summary with current values"""
        holdings = self.portfolio['holdings']
        
        if not holdings:
            return {
                'total_invested': 0,
                'current_value': 0,
                'total_pnl': 0,
                'total_pnl_percent': 0,
                'holdings': [],
                'sector_allocation': {},
                'risk_metrics': {}
            }
        
        total_invested = 0
        current_value = 0
        holdings_list = []
        
        for symbol, holding in holdings.items():
            invested = holding['shares'] * holding['avg_buy_price']
            total_invested += invested
            
            if current_prices and symbol in current_prices:
                current_price = current_prices[symbol]
            else:
                current_price = holding['avg_buy_price']  # Fallback
            
            value = holding['shares'] * current_price
            current_value += value
            
            pnl = value - invested
            pnl_percent = ((current_price - holding['avg_buy_price']) / holding['avg_buy_price']) * 100
            
            holdings_list.append({
                'symbol': symbol,
                'shares': holding['shares'],
                'avg_buy_price': holding['avg_buy_price'],
                'current_price': current_price,
                'invested': round(invested, 2),
                'current_value': round(value, 2),
                'pnl': round(pnl, 2),
                'pnl_percent': round(pnl_percent, 2),
                'sector': self.sectors.get(symbol, 'Unknown'),
                'weight': 0  # Will be calculated below
            })
        
        # Calculate weights
        for h in holdings_list:
            h['weight'] = round((h['current_value'] / current_value) * 100, 2) if current_value > 0 else 0
        
        # Sector allocation
        sector_allocation = {}
        for h in holdings_list:
            sector = h['sector']
            if sector not in sector_allocation:
                sector_allocation[sector] = {'value': 0, 'weight': 0}
            sector_allocation[sector]['value'] += h['current_value']
            sector_allocation[sector]['weight'] += h['weight']
        
        # Calculate risk metrics
        returns_list = [h['pnl_percent'] for h in holdings_list]
        if returns_list:
            avg_return = np.mean(returns_list)
            volatility = np.std(returns_list)
            sharpe = avg_return / volatility if volatility > 0 else 0
            
            # Concentration risk (max single stock weight)
            max_weight = max(h['weight'] for h in holdings_list)
        else:
            avg_return = volatility = sharpe = max_weight = 0
        
        total_pnl = current_value - total_invested
        total_pnl_percent = (total_pnl / total_invested) * 100 if total_invested > 0 else 0
        
        return {
            'total_invested': round(total_invested, 2),
            'current_value': round(current_value, 2),
            'total_pnl': round(total_pnl, 2),
            'total_pnl_percent': round(total_pnl_percent, 2),
            'holdings': sorted(holdings_list, key=lambda x: x['current_value'], reverse=True),
            'sector_allocation': {k: {'value': round(v['value'], 2), 'weight': round(v['weight'], 2)} 
                                for k, v in sector_allocation.items()},
            'risk_metrics': {
                'volatility': round(volatility, 2),
                'sharpe_ratio': round(sharpe, 2),
                'concentration_risk': round(max_weight, 2),
                'diversification_score': round(100 - max_weight, 2)
            }
        }
    
    def get_transaction_history(self):
        """Get all transactions"""
        return self.portfolio['transactions']
    
    def add_to_watchlist(self, symbol):
        """Add stock to watchlist"""
        if symbol not in self.portfolio['watchlist']:
            self.portfolio['watchlist'].append(symbol)
            self._save_portfolio()
        return {'status': 'success', 'message': f'Added {symbol} to watchlist'}
    
    def remove_from_watchlist(self, symbol):
        """Remove stock from watchlist"""
        if symbol in self.portfolio['watchlist']:
            self.portfolio['watchlist'].remove(symbol)
            self._save_portfolio()
        return {'status': 'success', 'message': f'Removed {symbol} from watchlist'}
    
    def get_watchlist(self):
        """Get watchlist"""
        return self.portfolio['watchlist']
    
    def clear_portfolio(self):
        """Clear all portfolio data"""
        self.portfolio = {'holdings': {}, 'transactions': [], 'watchlist': []}
        self._save_portfolio()
        return {'status': 'success', 'message': 'Portfolio cleared'}

if __name__ == "__main__":
    tracker = PortfolioTracker()
    
    # Example usage
    print("Adding stocks...")
    tracker.add_stock('RELIANCE.NS', 10, 2400.50)
    tracker.add_stock('TCS.NS', 5, 3200.00)
    
    print("\nPortfolio Summary:")
    summary = tracker.get_portfolio_summary({'RELIANCE.NS': 2500.00, 'TCS.NS': 3300.00})
    print(json.dumps(summary, indent=2))
