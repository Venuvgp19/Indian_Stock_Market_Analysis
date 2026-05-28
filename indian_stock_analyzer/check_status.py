import requests
import json

try:
    # Check server status
    r = requests.get('http://localhost:8080/api/top-stocks', timeout=10)
    if r.status_code == 200:
        data = r.json()
        stocks = data.get('stocks', [])
        print("SERVER: UP")
        print("Updated:", data.get('last_updated'))
        print("Top 3 Picks:")
        for i, s in enumerate(stocks[:3]):
            print(f"  {i+1}. {s['symbol']} | Score: {s['composite_score']} | {s['recommendation']}")
    else:
        print("SERVER: ERROR - Status", r.status_code)
except Exception as e:
    print("SERVER: DOWN -", str(e))
