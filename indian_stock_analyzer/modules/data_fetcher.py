"""
Indian Stock Data Fetcher Module
Fetches stock data using free APIs (Yahoo Finance for Indian stocks)
Now includes Nifty 50 + Nifty Next 50 + Midcap 100 = ~200 stocks
"""

import requests
import pandas as pd
import json
from datetime import datetime, timedelta
import time

class StockDataFetcher:
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
        
        # NIFTY 50 STOCKS (Large Cap)
        self.nifty50 = [
            'RELIANCE.NS', 'TCS.NS', 'INFY.NS', 'HDFCBANK.NS', 'ICICIBANK.NS',
            'HINDUNILVR.NS', 'ITC.NS', 'SBIN.NS', 'BHARTIARTL.NS', 'KOTAKBANK.NS',
            'BAJFINANCE.NS', 'LT.NS', 'AXISBANK.NS', 'ASIANPAINT.NS', 'MARUTI.NS',
            'SUNPHARMA.NS', 'TITAN.NS', 'ULTRACEMCO.NS', 'NESTLEIND.NS', 'WIPRO.NS',
            'M&M.NS', 'POWERGRID.NS', 'NTPC.NS', 'INDUSINDBK.NS', 'HDFC.NS',
            'BAJAJFINSV.NS', 'ADANIENT.NS', 'TATAMOTORS.NS', 'JSWSTEEL.NS', 'TECHM.NS',
            'HCLTECH.NS', 'ONGC.NS', 'COALINDIA.NS', 'BPCL.NS', 'IOC.NS',
            'GRASIM.NS', 'CIPLA.NS', 'DRREDDY.NS', 'EICHERMOT.NS', 'BRITANNIA.NS',
            'SHREECEM.NS', 'DIVISLAB.NS', 'TATASTEEL.NS', 'HEROMOTOCO.NS', 'APOLLOHOSP.NS',
            'UPL.NS', 'BAJAJ-AUTO.NS', 'TATACONSUM.NS', 'HINDALCO.NS', 'ADANIPORTS.NS',
            'DABUR.NS', 'PIDILITIND.NS', 'VEDL.NS', 'GODREJCP.NS', 'SIEMENS.NS'
        ]
        
        # NIFTY NEXT 50 STOCKS (Large-Mid Cap)
        self.nifty_next50 = [
            'ABB.NS', 'ACC.NS', 'APLAPOLLO.NS', 'AUBANK.NS', 'AMBUJACEM.NS',
            'ASHOKLEY.NS', 'ASTRAL.NS', 'AUROPHARMA.NS', 'BANDHANBNK.NS', 'BANKBARODA.NS',
            'BERGEPAINT.NS', 'BOSCHLTD.NS', 'CANBK.NS', 'CHOLAFIN.NS', 'COLPAL.NS',
            'CONCOR.NS', 'CUMMINSIND.NS', 'DLF.NS', 'DIXON.NS', 'ESCORTS.NS',
            'FEDERALBNK.NS', 'GAIL.NS', 'GLAND.NS', 'GODREJPROP.NS', 'HAL.NS',
            'HAVELLS.NS', 'HINDPETRO.NS', 'HONAUT.NS', 'IDFCFIRSTB.NS', 'INDIGO.NS',
            'IOCL.NS', 'IRCTC.NS', 'JINDALSTEL.NS', 'JUBLFOOD.NS', 'LICI.NS',
            'LUPIN.NS', 'MARICO.NS', 'MAXHEALTH.NS', 'MOTHERSON.NS', 'MPHASIS.NS',
            'MRF.NS', 'MUTHOOTFIN.NS', 'NAUKRI.NS', 'NMDC.NS', 'OFSS.NS',
            'PAGEIND.NS', 'PERSISTENT.NS', 'PETRONET.NS', 'POLYCAB.NS', 'SAMMAAN.NS'
        ]
        
        # NIFTY MIDCAP 100 STOCKS (Mid Cap - Selected popular ones)
        self.nifty_midcap = [
            'ABCAPITAL.NS', 'ABFRL.NS', 'ALKEM.NS', 'ALOKINDS.NS', 'ANGELONE.NS',
            'APARINDS.NS', 'ATGL.NS', 'BALKRISNA.NS', 'BATAINDIA.NS', 'BEL.NS',
            'BHARATFORG.NS', 'BLUEDART.NS', 'BSOFT.NS', 'CAMS.NS', 'CARBORUNIV.NS',
            'CDSL.NS', 'CENTRALBK.NS', 'CENTURYTEX.NS', 'CGPOWER.NS', 'CRISIL.NS',
            'CROMPTON.NS', 'CSBBANK.NS', 'DALBHARAT.NS', 'DEEPAKNTR.NS', 'DELHIVERY.NS',
            'DEVYANI.NS', 'EICHERMOT.NS', 'FORTIS.NS', 'GLENMARK.NS', 'GNFC.NS',
            'GPPL.NS', 'GUJGASLTD.NS', 'HDFCAMC.NS', 'HFCL.NS', 'HINDCOPPER.NS',
            'HUDCO.NS', 'IEX.NS', 'INDHOTEL.NS', 'INDIAMART.NS', 'INDIANB.NS',
            'IPCALAB.NS', 'ISEC.NS', 'JBCHEPHARM.NS', 'JKCEMENT.NS', 'JMFINANCIL.NS',
            'JSL.NS', 'KEI.NS', 'KIMS.NS', 'KPITTECH.NS', 'LALPATHLAB.NS',
            'LAURUSLABS.NS', 'LICHSGFIN.NS', 'LTIM.NS', 'M&MFIN.NS', 'MANAPPURAM.NS',
            'MCX.NS', 'METROBRAND.NS', 'MFSL.NS', 'MSUMI.NS', 'NAM-INDIA.NS',
            'NAVINFLUOR.NS', 'OBEROIRLTY.NS', 'PEL.NS', 'PFIZER.NS', 'PHOENIXLTD.NS',
            'PIIND.NS', 'PiramalEnterprises.NS', 'POONAWALLA.NS', 'PRAJIND.NS', 'PRESTIGE.NS',
            'RBLBANK.NS', 'SAIL.NS', 'SAREGAMA.NS', 'SBICARD.NS', 'SRF.NS',
            'STARHEALTH.NS', 'SUNTV.NS', 'SUPREMEIND.NS', 'SUZLON.NS', 'TANLA.NS',
            'TATACHEM.NS', 'TATACOMM.NS', 'TATAELXSI.NS', 'TIINDIA.NS', 'TORNTPHARM.NS',
            'TORNTPOWER.NS', 'TRENT.NS', 'TRIDENT.NS', 'TTKPRESTIG.NS', 'TVSMOTOR.NS',
            'UBL.NS', 'UNOMINDA.NS', 'VIJAYA.NS', 'VOLTAS.NS', 'YESBANK.NS',
            'ZFCVINDIA.NS', 'ZEEL.NS', 'ZYDUSWELL.NS'
        ]
        
        # All stocks combined
        self.all_stocks = self.nifty50 + self.nifty_next50 + self.nifty_midcap
        
        # Default for backward compatibility
        self.default_stocks = self.nifty50
        
        # Name mapping for all stocks
        self.name_map = self._build_name_map()
        
    def _build_name_map(self):
        """Build comprehensive name mapping"""
        name_map = {
            # Nifty 50
            'RELIANCE.NS': 'Reliance Industries',
            'TCS.NS': 'Tata Consultancy Services',
            'INFY.NS': 'Infosys',
            'HDFCBANK.NS': 'HDFC Bank',
            'ICICIBANK.NS': 'ICICI Bank',
            'HINDUNILVR.NS': 'Hindustan Unilever',
            'ITC.NS': 'ITC Limited',
            'SBIN.NS': 'State Bank of India',
            'BHARTIARTL.NS': 'Bharti Airtel',
            'KOTAKBANK.NS': 'Kotak Mahindra Bank',
            'BAJFINANCE.NS': 'Bajaj Finance',
            'LT.NS': 'Larsen & Toubro',
            'AXISBANK.NS': 'Axis Bank',
            'ASIANPAINT.NS': 'Asian Paints',
            'MARUTI.NS': 'Maruti Suzuki',
            'SUNPHARMA.NS': 'Sun Pharmaceutical',
            'TITAN.NS': 'Titan Company',
            'ULTRACEMCO.NS': 'UltraTech Cement',
            'NESTLEIND.NS': 'Nestle India',
            'WIPRO.NS': 'Wipro',
            'M&M.NS': 'Mahindra & Mahindra',
            'POWERGRID.NS': 'Power Grid Corporation',
            'NTPC.NS': 'NTPC Limited',
            'INDUSINDBK.NS': 'IndusInd Bank',
            'HDFC.NS': 'Housing Development Finance Corporation',
            'BAJAJFINSV.NS': 'Bajaj Finserv',
            'ADANIENT.NS': 'Adani Enterprises',
            'TATAMOTORS.NS': 'Tata Motors',
            'JSWSTEEL.NS': 'JSW Steel',
            'TECHM.NS': 'Tech Mahindra',
            'HCLTECH.NS': 'HCL Technologies',
            'ONGC.NS': 'Oil & Natural Gas Corporation',
            'COALINDIA.NS': 'Coal India',
            'BPCL.NS': 'Bharat Petroleum',
            'IOC.NS': 'Indian Oil Corporation',
            'GRASIM.NS': 'Grasim Industries',
            'CIPLA.NS': 'Cipla',
            'DRREDDY.NS': 'Dr. Reddy\'s Laboratories',
            'EICHERMOT.NS': 'Eicher Motors',
            'BRITANNIA.NS': 'Britannia Industries',
            'SHREECEM.NS': 'Shree Cement',
            'DIVISLAB.NS': 'Divi\'s Laboratories',
            'TATASTEEL.NS': 'Tata Steel',
            'HEROMOTOCO.NS': 'Hero MotoCorp',
            'APOLLOHOSP.NS': 'Apollo Hospitals',
            'UPL.NS': 'UPL Limited',
            'BAJAJ-AUTO.NS': 'Bajaj Auto',
            'TATACONSUM.NS': 'Tata Consumer Products',
            'HINDALCO.NS': 'Hindalco Industries',
            'ADANIPORTS.NS': 'Adani Ports',
            'DABUR.NS': 'Dabur India',
            'PIDILITIND.NS': 'Pidilite Industries',
            'VEDL.NS': 'Vedanta',
            'GODREJCP.NS': 'Godrej Consumer Products',
            'SIEMENS.NS': 'Siemens India',
            
            # Nifty Next 50
            'ABB.NS': 'ABB India',
            'ACC.NS': 'ACC Limited',
            'APLAPOLLO.NS': 'APL Apollo Tubes',
            'AUBANK.NS': 'AU Small Finance Bank',
            'AMBUJACEM.NS': 'Ambuja Cements',
            'ASHOKLEY.NS': 'Ashok Leyland',
            'ASTRAL.NS': 'Astral Limited',
            'AUROPHARMA.NS': 'Aurobindo Pharma',
            'BANDHANBNK.NS': 'Bandhan Bank',
            'BANKBARODA.NS': 'Bank of Baroda',
            'BERGEPAINT.NS': 'Berger Paints',
            'BOSCHLTD.NS': 'Bosch Limited',
            'CANBK.NS': 'Canara Bank',
            'CHOLAFIN.NS': 'Cholamandalam Investment',
            'COLPAL.NS': 'Colgate-Palmolive India',
            'CONCOR.NS': 'Container Corporation of India',
            'CUMMINSIND.NS': 'Cummins India',
            'DLF.NS': 'DLF Limited',
            'DIXON.NS': 'Dixon Technologies',
            'ESCORTS.NS': 'Escorts Limited',
            'FEDERALBNK.NS': 'Federal Bank',
            'GAIL.NS': 'GAIL India',
            'GLAND.NS': 'Gland Pharma',
            'GODREJPROP.NS': 'Godrej Properties',
            'HAL.NS': 'Hindustan Aeronautics',
            'HAVELLS.NS': 'Havells India',
            'HINDPETRO.NS': 'Hindustan Petroleum',
            'HONAUT.NS': 'Honeywell Automation',
            'IDFCFIRSTB.NS': 'IDFC First Bank',
            'INDIGO.NS': 'InterGlobe Aviation (IndiGo)',
            'IOCL.NS': 'Indian Oil Corporation',
            'IRCTC.NS': 'IRCTC',
            'JINDALSTEL.NS': 'Jindal Steel & Power',
            'JUBLFOOD.NS': 'Jubilant FoodWorks',
            'LICI.NS': 'LIC of India',
            'LUPIN.NS': 'Lupin Limited',
            'MARICO.NS': 'Marico Limited',
            'MAXHEALTH.NS': 'Max Healthcare',
            'MOTHERSON.NS': 'Motherson Sumi',
            'MPHASIS.NS': 'Mphasis Limited',
            'MRF.NS': 'MRF Limited',
            'MUTHOOTFIN.NS': 'Muthoot Finance',
            'NAUKRI.NS': 'Info Edge (Naukri)',
            'NMDC.NS': 'NMDC Limited',
            'OFSS.NS': 'Oracle Financial Services',
            'PAGEIND.NS': 'Page Industries',
            'PERSISTENT.NS': 'Persistent Systems',
            'PETRONET.NS': 'Petronet LNG',
            'POLYCAB.NS': 'Polycab India',
            'SAMMAAN.NS': 'Sammaan Capital',
            
            # Midcap 100
            'ABCAPITAL.NS': 'Aditya Birla Capital',
            'ABFRL.NS': 'Aditya Birla Fashion',
            'ALKEM.NS': 'Alkem Laboratories',
            'ALOKINDS.NS': 'Alok Industries',
            'ANGELONE.NS': 'Angel One',
            'APARINDS.NS': 'Apar Industries',
            'ATGL.NS': 'Adani Total Gas',
            'BALKRISNA.NS': 'Balkrishna Industries',
            'BATAINDIA.NS': 'Bata India',
            'BEL.NS': 'Bharat Electronics',
            'BHARATFORG.NS': 'Bharat Forge',
            'BLUEDART.NS': 'Blue Dart Express',
            'BSOFT.NS': 'Birlasoft',
            'CAMS.NS': 'Computer Age Management',
            'CARBORUNIV.NS': 'Carborundum Universal',
            'CDSL.NS': 'CDSL',
            'CENTRALBK.NS': 'Central Bank of India',
            'CENTURYTEX.NS': 'Century Textiles',
            'CGPOWER.NS': 'CG Power',
            'CRISIL.NS': 'CRISIL',
            'CROMPTON.NS': 'Crompton Greaves',
            'CSBBANK.NS': 'CSB Bank',
            'DALBHARAT.NS': 'Dalmia Bharat',
            'DEEPAKNTR.NS': 'Deepak Nitrite',
            'DELHIVERY.NS': 'Delhivery',
            'DEVYANI.NS': 'Devyani International',
            'FORTIS.NS': 'Fortis Healthcare',
            'GLENMARK.NS': 'Glenmark Pharma',
            'GNFC.NS': 'Gujarat Narmada Valley',
            'GUJGASLTD.NS': 'Gujarat Gas',
            'HDFCAMC.NS': 'HDFC AMC',
            'HFCL.NS': 'HFCL Limited',
            'HINDCOPPER.NS': 'Hindustan Copper',
            'HUDCO.NS': 'HUDCO',
            'IEX.NS': 'Indian Energy Exchange',
            'INDHOTEL.NS': 'Indian Hotels',
            'INDIAMART.NS': 'IndiaMART',
            'INDIANB.NS': 'Indian Bank',
            'IPCALAB.NS': 'Ipca Laboratories',
            'ISEC.NS': 'ICICI Securities',
            'JBCHEPHARM.NS': 'JB Chemicals',
            'JKCEMENT.NS': 'JK Cement',
            'JMFINANCIL.NS': 'JM Financial',
            'JSL.NS': 'Jindal Stainless',
            'KEI.NS': 'KEI Industries',
            'KIMS.NS': 'KIMS Hospitals',
            'KPITTECH.NS': 'KPIT Technologies',
            'LALPATHLAB.NS': 'Dr. Lal PathLabs',
            'LAURUSLABS.NS': 'Laurus Labs',
            'LICHSGFIN.NS': 'LIC Housing Finance',
            'LTIM.NS': 'LTIMindtree',
            'M&MFIN.NS': 'Mahindra Finance',
            'MANAPPURAM.NS': 'Manappuram Finance',
            'MCX.NS': 'MCX India',
            'METROBRAND.NS': 'Metro Brands',
            'MFSL.NS': 'Max Financial Services',
            'MSUMI.NS': 'Motherson Sumi Wiring',
            'NAM-INDIA.NS': 'Nippon Life India',
            'NAVINFLUOR.NS': 'Navin Fluorine',
            'OBEROIRLTY.NS': 'Oberoi Realty',
            'PEL.NS': 'Piramal Enterprises',
            'PFIZER.NS': 'Pfizer India',
            'PHOENIXLTD.NS': 'Phoenix Mills',
            'PIIND.NS': 'PI Industries',
            'PiramalEnterprises.NS': 'Piramal Enterprises Ltd',
            'POONAWALLA.NS': 'Poonawalla Fincorp',
            'PRAJIND.NS': 'Praj Industries',
            'PRESTIGE.NS': 'Prestige Estates',
            'RBLBANK.NS': 'RBL Bank',
            'SAIL.NS': 'Steel Authority of India',
            'SAREGAMA.NS': 'Saregama India',
            'SBICARD.NS': 'SBI Cards',
            'SRF.NS': 'SRF Limited',
            'STARHEALTH.NS': 'Star Health Insurance',
            'SUNTV.NS': 'Sun TV Network',
            'SUPREMEIND.NS': 'Supreme Industries',
            'SUZLON.NS': 'Suzlon Energy',
            'TANLA.NS': 'Tanla Platforms',
            'TATACHEM.NS': 'Tata Chemicals',
            'TATACOMM.NS': 'Tata Communications',
            'TATAELXSI.NS': 'Tata Elxsi',
            'TIINDIA.NS': 'Tube Investments',
            'TORNTPHARM.NS': 'Torrent Pharmaceuticals',
            'TORNTPOWER.NS': 'Torrent Power',
            'TRENT.NS': 'Trent Limited',
            'TRIDENT.NS': 'Trident Limited',
            'TTKPRESTIG.NS': 'TTK Prestige',
            'TVSMOTOR.NS': 'TVS Motor Company',
            'UBL.NS': 'United Breweries',
            'UNOMINDA.NS': 'Uno Minda',
            'VIJAYA.NS': 'Vijaya Diagnostic',
            'VOLTAS.NS': 'Voltas Limited',
            'YESBANK.NS': 'Yes Bank',
            'ZFCVINDIA.NS': 'ZF Commercial Vehicle',
            'ZEEL.NS': 'Zee Entertainment',
            'ZYDUSWELL.NS': 'Zydus Wellness'
        }
        return name_map
        
    def fetch_stock_data(self, symbol, period="1y"):
        """Fetch historical stock data from Yahoo Finance"""
        try:
            # Yahoo Finance API endpoint
            end_date = int(datetime.now().timestamp())
            if period == "1mo":
                start_date = int((datetime.now() - timedelta(days=30)).timestamp())
            elif period == "3mo":
                start_date = int((datetime.now() - timedelta(days=90)).timestamp())
            elif period == "6mo":
                start_date = int((datetime.now() - timedelta(days=180)).timestamp())
            elif period == "1y":
                start_date = int((datetime.now() - timedelta(days=365)).timestamp())
            elif period == "2y":
                start_date = int((datetime.now() - timedelta(days=730)).timestamp())
            else:
                start_date = int((datetime.now() - timedelta(days=365)).timestamp())
            
            url = f"https://query1.finance.yahoo.com/v8/finance/chart/{symbol}"
            params = {
                'period1': start_date,
                'period2': end_date,
                'interval': '1d',
                'events': 'history'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'chart' not in data or 'result' not in data['chart'] or not data['chart']['result']:
                print(f"No data found for {symbol}")
                return None
            
            result = data['chart']['result'][0]
            timestamps = result['timestamp']
            quote = result['indicators']['quote'][0]
            
            df = pd.DataFrame({
                'Date': [datetime.fromtimestamp(ts).strftime('%Y-%m-%d') for ts in timestamps],
                'Open': quote['open'],
                'High': quote['high'],
                'Low': quote['low'],
                'Close': quote['close'],
                'Volume': quote['volume']
            })
            
            df['Date'] = pd.to_datetime(df['Date'])
            df = df.dropna()
            
            return df
            
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return None
    
    def fetch_multiple_stocks(self, symbols=None, period="1y"):
        """Fetch data for multiple stocks"""
        if symbols is None:
            symbols = self.default_stocks
        
        stock_data = {}
        for symbol in symbols:
            data = self.fetch_stock_data(symbol, period)
            if data is not None:
                stock_data[symbol] = data
            time.sleep(0.3)  # Rate limiting
        
        return stock_data
    
    def get_stock_info(self, symbol):
        """Get stock info (name, sector, etc.)"""
        try:
            url = f"https://query1.finance.yahoo.com/v10/finance/quoteSummary/{symbol}"
            params = {'modules': 'summaryProfile,price,summaryDetail'}
            response = self.session.get(url, params=params, timeout=10)
            data = response.json()
            
            if 'quoteSummary' in data and 'result' in data['quoteSummary'] and data['quoteSummary']['result']:
                result = data['quoteSummary']['result'][0]
                info = {}
                
                if 'price' in result:
                    price_data = result['price']
                    info['name'] = price_data.get('longName', '')
                    info['symbol'] = price_data.get('symbol', '')
                    info['currency'] = price_data.get('currency', '')
                    info['current_price'] = price_data.get('regularMarketPrice', {}).get('raw', 0)
                    info['market_cap'] = price_data.get('marketCap', {}).get('raw', 0)
                
                if 'summaryProfile' in result:
                    profile = result['summaryProfile']
                    info['sector'] = profile.get('sector', '')
                    info['industry'] = profile.get('industry', '')
                    info['website'] = profile.get('website', '')
                    info['description'] = profile.get('longBusinessSummary', '')
                
                return info
            return None
            
        except Exception as e:
            print(f"Error fetching info for {symbol}: {e}")
            return None
    
    def get_nifty50_list(self):
        """Return list of Nifty 50 stocks"""
        return self.nifty50
    
    def get_nifty_next50_list(self):
        """Return list of Nifty Next 50 stocks"""
        return self.nifty_next50
    
    def get_midcap_list(self):
        """Return list of Midcap stocks"""
        return self.nifty_midcap
    
    def get_all_stocks_list(self):
        """Return all stocks (Nifty 50 + Next 50 + Midcap)"""
        return self.all_stocks
    
    def get_stock_name(self, symbol):
        """Extract stock name from symbol"""
        return self.name_map.get(symbol, symbol.replace('.NS', ''))
    
    def get_stock_category(self, symbol):
        """Get category of stock (Nifty50, NiftyNext50, Midcap)"""
        if symbol in self.nifty50:
            return 'Nifty 50 (Large Cap)'
        elif symbol in self.nifty_next50:
            return 'Nifty Next 50 (Large-Mid Cap)'
        elif symbol in self.nifty_midcap:
            return 'Nifty Midcap 100'
        else:
            return 'Other'

if __name__ == "__main__":
    fetcher = StockDataFetcher()
    print(f"Total stocks: {len(fetcher.all_stocks)}")
    print(f"Nifty 50: {len(fetcher.nifty50)}")
    print(f"Nifty Next 50: {len(fetcher.nifty_next50)}")
    print(f"Midcap 100: {len(fetcher.nifty_midcap)}")
