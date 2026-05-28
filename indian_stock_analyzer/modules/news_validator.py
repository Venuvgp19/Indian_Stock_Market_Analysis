"""
News Validator Module
Fetches and analyzes news sentiment for stocks
"""

import requests
import json
import time
from datetime import datetime, timedelta
from textblob import TextBlob
import re

class NewsValidator:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # Stock to company name mapping for better news search
        self.stock_names = {
            'RELIANCE.NS': 'Reliance Industries',
            'TCS.NS': 'Tata Consultancy Services',
            'INFY.NS': 'Infosys',
            'HDFCBANK.NS': 'HDFC Bank',
            'ICICIBANK.NS': 'ICICI Bank',
            'HINDUNILVR.NS': 'Hindustan Unilever',
            'ITC.NS': 'ITC',
            'SBIN.NS': 'State Bank of India',
            'BHARTIARTL.NS': 'Bharti Airtel',
            'KOTAKBANK.NS': 'Kotak Mahindra Bank',
            'BAJFINANCE.NS': 'Bajaj Finance',
            'LT.NS': 'Larsen Toubro',
            'AXISBANK.NS': 'Axis Bank',
            'ASIANPAINT.NS': 'Asian Paints',
            'MARUTI.NS': 'Maruti Suzuki',
            'SUNPHARMA.NS': 'Sun Pharmaceutical',
            'TITAN.NS': 'Titan',
            'ULTRACEMCO.NS': 'UltraTech Cement',
            'NESTLEIND.NS': 'Nestle India',
            'WIPRO.NS': 'Wipro',
            'M&M.NS': 'Mahindra Mahindra',
            'POWERGRID.NS': 'Power Grid',
            'NTPC.NS': 'NTPC',
            'INDUSINDBK.NS': 'IndusInd Bank',
            'HDFC.NS': 'HDFC',
            'BAJAJFINSV.NS': 'Bajaj Finserv',
            'ADANIENT.NS': 'Adani Enterprises',
            'TATAMOTORS.NS': 'Tata Motors',
            'JSWSTEEL.NS': 'JSW Steel',
            'TECHM.NS': 'Tech Mahindra',
            'HCLTECH.NS': 'HCL Technologies',
            'ONGC.NS': 'ONGC',
            'COALINDIA.NS': 'Coal India',
            'BPCL.NS': 'Bharat Petroleum',
            'IOC.NS': 'Indian Oil',
            'GRASIM.NS': 'Grasim',
            'CIPLA.NS': 'Cipla',
            'DRREDDY.NS': 'Dr Reddy',
            'EICHERMOT.NS': 'Eicher Motors',
            'BRITANNIA.NS': 'Britannia',
            'SHREECEM.NS': 'Shree Cement',
            'DIVISLAB.NS': 'Divis Laboratories',
            'TATASTEEL.NS': 'Tata Steel',
            'HEROMOTOCO.NS': 'Hero MotoCorp',
            'APOLLOHOSP.NS': 'Apollo Hospitals',
            'UPL.NS': 'UPL',
            'BAJAJ-AUTO.NS': 'Bajaj Auto',
            'TATACONSUM.NS': 'Tata Consumer',
            'HINDALCO.NS': 'Hindalco',
            'ADANIPORTS.NS': 'Adani Ports',
            'DABUR.NS': 'Dabur',
            'PIDILITIND.NS': 'Pidilite',
            'VEDL.NS': 'Vedanta',
            'GODREJCP.NS': 'Godrej Consumer',
            'SIEMENS.NS': 'Siemens India'
        }
        
        # Additional news sources
        self.rss_feeds = {
            'moneycontrol': 'https://www.moneycontrol.com/rss/business.xml',
            'economic_times': 'https://economictimes.indiatimes.com/markets/rssfeeds/1977021501.cms',
            'business_standard': 'https://www.business-standard.com/rss/markets-106.rss',
            'financial_express': 'https://www.financialexpress.com/market/feed/',
            'livemint': 'https://www.livemint.com/rss/markets',
            'marketwatch': 'https://www.marketwatch.com/rss/marketwatch'
        }
        
        # API Keys (optional - for enhanced sources)
        self.newsapi_key = None  # Can be set from environment
        self.gnews_available = False
        
        try:
            from gnews import GNews
            self.gnews_available = True
        except ImportError:
            pass
        self.positive_keywords = [
            'profit', 'growth', 'surge', 'rally', 'boom', 'outperform', 'upgrade',
            'beat', 'strong', 'excellent', 'positive', 'gain', 'rise', 'high',
            'bullish', 'buy', 'outlook', 'momentum', 'breakthrough', 'expansion',
            'dividend', 'bonus', 'record', 'all-time high', 'ATH', 'target raised'
        ]
        
        self.negative_keywords = [
            'loss', 'decline', 'crash', 'plunge', 'underperform', 'downgrade',
            'miss', 'weak', 'poor', 'negative', 'fall', 'drop', 'low',
            'bearish', 'sell', 'concern', 'risk', 'investigation', 'probe',
            'debt', 'default', 'bankruptcy', 'fraud', 'scandal', 'target cut'
        ]
    
    def fetch_news_gnews(self, symbol, days=7):
        """Fetch news using GNews API (free tier)"""
        try:
            if not self.gnews_available:
                return []
            
            company_name = self.stock_names.get(symbol, symbol.replace('.NS', ''))
            
            # Use GNews API (free tier: 100 requests/day)
            from gnews import GNews
            
            google_news = GNews(language='en', country='IN', max_results=10)
            news = google_news.get_news(f"{company_name} stock India")
            
            articles = []
            for article in news:
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('description', ''),
                    'url': article.get('url', ''),
                    'published_date': article.get('published date', ''),
                    'source': article.get('publisher', {}).get('title', 'Unknown')
                })
            
            return articles
            
        except Exception as e:
            print(f"Error fetching GNews for {symbol}: {e}")
            return []
    
    def fetch_news_newsapi(self, symbol, days=7):
        """Fetch news using NewsAPI (free tier: 100 requests/day)"""
        try:
            if not self.newsapi_key:
                # Try to get from environment
                import os
                self.newsapi_key = os.getenv('NEWSAPI_KEY')
                
            if not self.newsapi_key:
                return []
            
            company_name = self.stock_names.get(symbol, symbol.replace('.NS', ''))
            
            url = 'https://newsapi.org/v2/everything'
            params = {
                'q': f'{company_name} stock India',
                'from': (datetime.now() - timedelta(days=days)).strftime('%Y-%m-%d'),
                'to': datetime.now().strftime('%Y-%m-%d'),
                'language': 'en',
                'sortBy': 'relevancy',
                'pageSize': 10,
                'apiKey': self.newsapi_key
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                articles = []
                
                for article in data.get('articles', []):
                    articles.append({
                        'title': article.get('title', ''),
                        'description': article.get('description', ''),
                        'url': article.get('url', ''),
                        'published_date': article.get('publishedAt', ''),
                        'source': article.get('source', {}).get('name', 'Unknown')
                    })
                
                return articles
            
            return []
            
        except Exception as e:
            print(f"Error fetching NewsAPI for {symbol}: {e}")
            return []
    
    def fetch_news_rss(self, symbol):
        """Fetch news from RSS feeds"""
        try:
            import feedparser
            
            company_name = self.stock_names.get(symbol, symbol.replace('.NS', ''))
            articles = []
            
            for source_name, feed_url in self.rss_feeds.items():
                try:
                    feed = feedparser.parse(feed_url)
                    
                    for entry in feed.entries[:5]:  # Top 5 from each source
                        title = entry.get('title', '')
                        summary = entry.get('summary', '')
                        
                        # Check if article mentions the company
                        if company_name.lower() in title.lower() or company_name.lower() in summary.lower():
                            articles.append({
                                'title': title,
                                'description': summary[:300] + '...' if len(summary) > 300 else summary,
                                'url': entry.get('link', ''),
                                'published_date': entry.get('published', ''),
                                'source': source_name
                            })
                except Exception as e:
                    continue
            
            return articles
            
        except ImportError:
            print("feedparser not available, skipping RSS")
            return []
        except Exception as e:
            print(f"Error fetching RSS for {symbol}: {e}")
            return []
    
    def fetch_news_yahoo(self, symbol):
        """Fetch news from Yahoo Finance"""
        try:
            import yfinance as yf
            
            ticker = yf.Ticker(symbol)
            news = ticker.news
            
            articles = []
            for article in news[:10]:
                articles.append({
                    'title': article.get('title', ''),
                    'description': article.get('summary', ''),
                    'url': article.get('link', ''),
                    'published_date': article.get('publisher', '')
                })
            
            return articles
            
        except Exception as e:
            print(f"Error fetching Yahoo news for {symbol}: {e}")
            return []
    
    def fetch_news_fallback(self, symbol):
        """Fallback news fetching using Google News RSS"""
        try:
            import feedparser
            
            company_name = self.stock_names.get(symbol, symbol.replace('.NS', ''))
            query = company_name.replace(' ', '+')
            
            # Use Google News RSS
            rss_url = f"https://news.google.com/rss/search?q={query}+stock+India&hl=en-IN&gl=IN&ceid=IN:en"
            
            feed = feedparser.parse(rss_url)
            
            articles = []
            for entry in feed.entries[:10]:
                articles.append({
                    'title': entry.get('title', ''),
                    'description': entry.get('summary', ''),
                    'url': entry.get('link', ''),
                    'published_date': entry.get('published', ''),
                    'source': entry.get('source', {}).get('title', 'Unknown') if isinstance(entry.get('source'), dict) else 'Unknown'
                })
            
            return articles
            
        except Exception as e:
            print(f"Error in fallback news for {symbol}: {e}")
            return []
    
    def analyze_sentiment(self, text):
        """Analyze sentiment of text"""
        try:
            # TextBlob sentiment
            blob = TextBlob(text)
            textblob_sentiment = blob.sentiment.polarity  # -1 to 1
            
            # Keyword-based sentiment
            text_lower = text.lower()
            pos_count = sum(1 for word in self.positive_keywords if word in text_lower)
            neg_count = sum(1 for word in self.negative_keywords if word in text_lower)
            
            # Combine scores
            keyword_sentiment = (pos_count - neg_count) / max(1, pos_count + neg_count)
            
            # Weighted average
            final_sentiment = (textblob_sentiment * 0.3) + (keyword_sentiment * 0.7)
            
            # Normalize to 0-100 scale (50 is neutral)
            sentiment_score = int((final_sentiment + 1) * 50)
            sentiment_score = max(0, min(100, sentiment_score))
            
            # Determine sentiment label
            if sentiment_score >= 60:
                label = 'POSITIVE'
            elif sentiment_score <= 40:
                label = 'NEGATIVE'
            else:
                label = 'NEUTRAL'
            
            return {
                'score': sentiment_score,
                'label': label,
                'textblob_score': round(textblob_sentiment, 3),
                'keyword_score': round(keyword_sentiment, 3)
            }
            
        except Exception as e:
            print(f"Error analyzing sentiment: {e}")
            return {'score': 50, 'label': 'NEUTRAL', 'textblob_score': 0, 'keyword_score': 0}
    
    def validate_stock(self, symbol):
        """Validate a stock based on news sentiment"""
        try:
            # Fetch news
            articles = self.fetch_news_gnews(symbol)
            
            # Fallback to RSS if no articles
            if not articles:
                articles = self.fetch_news_fallback(symbol)
            
            if not articles:
                return {
                    'symbol': symbol,
                    'company_name': self.stock_names.get(symbol, symbol),
                    'sentiment_score': 50,
                    'sentiment_label': 'NEUTRAL',
                    'articles_count': 0,
                    'articles': [],
                    'recommendation': 'HOLD'
                }
            
            # Analyze sentiment for each article
            analyzed_articles = []
            total_sentiment = 0
            
            for article in articles:
                text = f"{article['title']} {article['description']}"
                sentiment = self.analyze_sentiment(text)
                
                analyzed_articles.append({
                    'title': article['title'],
                    'description': article['description'][:200] + '...' if len(article['description']) > 200 else article['description'],
                    'url': article['url'],
                    'published_date': article['published_date'],
                    'source': article['source'],
                    'sentiment': sentiment
                })
                
                total_sentiment += sentiment['score']
            
            # Calculate average sentiment
            avg_sentiment = total_sentiment / len(analyzed_articles) if analyzed_articles else 50
            
            # Determine recommendation
            if avg_sentiment >= 65:
                recommendation = 'STRONG_BUY'
            elif avg_sentiment >= 55:
                recommendation = 'BUY'
            elif avg_sentiment >= 45:
                recommendation = 'HOLD'
            elif avg_sentiment >= 35:
                recommendation = 'SELL'
            else:
                recommendation = 'STRONG_SELL'
            
            return {
                'symbol': symbol,
                'company_name': self.stock_names.get(symbol, symbol),
                'sentiment_score': round(avg_sentiment, 1),
                'sentiment_label': self._get_sentiment_label(avg_sentiment),
                'articles_count': len(analyzed_articles),
                'articles': analyzed_articles[:5],  # Top 5 articles
                'recommendation': recommendation,
                'positive_articles': sum(1 for a in analyzed_articles if a['sentiment']['label'] == 'POSITIVE'),
                'negative_articles': sum(1 for a in analyzed_articles if a['sentiment']['label'] == 'NEGATIVE'),
                'neutral_articles': sum(1 for a in analyzed_articles if a['sentiment']['label'] == 'NEUTRAL')
            }
            
        except Exception as e:
            print(f"Error validating stock {symbol}: {e}")
            return {
                'symbol': symbol,
                'company_name': self.stock_names.get(symbol, symbol),
                'sentiment_score': 50,
                'sentiment_label': 'NEUTRAL',
                'articles_count': 0,
                'articles': [],
                'recommendation': 'HOLD'
            }
    
    def _get_sentiment_label(self, score):
        """Convert sentiment score to label"""
        if score >= 60:
            return 'POSITIVE'
        elif score <= 40:
            return 'NEGATIVE'
        else:
            return 'NEUTRAL'

if __name__ == "__main__":
    validator = NewsValidator()
    result = validator.validate_stock('RELIANCE.NS')
    print(f"Sentiment Score: {result['sentiment_score']}")
    print(f"Recommendation: {result['recommendation']}")
    print(f"Articles: {result['articles_count']}")
    for article in result['articles'][:3]:
        print(f"  - {article['title']} [{article['sentiment']['label']}]")
