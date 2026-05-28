import requests

print('Fetching top stock recommendations...')
r = requests.get('http://localhost:5000/api/top-stocks')
print('Status:', r.status_code)
data = r.json()
print('Last Updated:', data.get('last_updated'))
print('Number of stocks:', len(data.get('stocks', [])))
for i, stock in enumerate(data.get('stocks', [])[:5]):
    print(f"{i+1}. {stock['symbol']} - Score: {stock['composite_score']} - {stock['ml_prediction']} - {stock.get('recommendation', 'HOLD')}")
