import requests
# Broad search
url = "https://newsapi.org/v2/everything"
params = {
    "q": "Drosera Network",
    "apiKey": "493e3ae3babf4c11852bf7b13653a54e",
    "pageSize": 5
}
res = requests.get(url, params=params)
print(res.json().get("totalResults", 0))
if res.status_code == 200:
    for a in res.json().get("articles", []):
        print(f"- {a['title']}")
