import sys
sys.path.append('.')

from app_v2 import app
import json

# Create test client
client = app.test_client()

# Test /api/stocks
print('Testing /api/stocks...')
response = client.get('/api/stocks')
print('Status:', response.status_code)
if response.status_code == 200:
    data = json.loads(response.data)
    print('Count:', len(data))
    print('First:', data[0])
else:
    print('Error:', response.data)

# Test /api/analyze/INFY.NS
print('\nTesting /api/analyze/INFY.NS...')
response = client.get('/api/analyze/INFY.NS')
print('Status:', response.status_code)
if response.status_code == 200:
    data = json.loads(response.data)
    print('Symbol:', data.get('symbol'))
    print('Has advanced_indicators:', 'advanced_indicators' in data)
    print('Has support_resistance:', 'support_resistance' in data)
else:
    print('Error:', response.data[:500])

# Test /api/backtest/RELIANCE.NS
print('\nTesting /api/backtest/RELIANCE.NS...')
response = client.get('/api/backtest/RELIANCE.NS?strategy=combined')
print('Status:', response.status_code)
if response.status_code == 200:
    data = json.loads(response.data)
    print('Strategy:', data.get('strategy_name'))
    print('Total Return:', data.get('total_return'))
else:
    print('Error:', response.data[:500])

# Test /api/portfolio/summary
print('\nTesting /api/portfolio/summary...')
response = client.get('/api/portfolio/summary')
print('Status:', response.status_code)
if response.status_code == 200:
    data = json.loads(response.data)
    print('Total Invested:', data.get('total_invested'))
else:
    print('Error:', response.data[:500])

print('\nDone!')
