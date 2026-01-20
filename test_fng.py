
import requests

def get_fear_greed():
    try:
        r = requests.get("https://api.alternative.me/fng/", timeout=5)
        data = r.json()
        val = data['data'][0]['value']
        cls = data['data'][0]['value_classification']
        return val, cls
    except Exception as e:
        return None, str(e)

val, cls = get_fear_greed()
print(f"Value: {val}, Class: {cls}")
