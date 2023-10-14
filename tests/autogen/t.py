import requests

def search(query):
    endpoint = "https://ddg-api.herokuapp.com/search"
    params = {
        'query': query,
        'limit': 5
    }
    res = requests.get(endpoint, params=params)
    if res.status_code == 200:
        results = res.json()
        return results
    else:
        return (f"Didn't get any results")

print(search('UDP-GlcA'))

