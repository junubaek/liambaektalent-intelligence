
import requests
url = 'https://docs.google.com/uc?export=download&id=1vZQrsftydP_DSFX3KnFWQxhkqsEmmXjU'
r = requests.get(url, stream=True)
print(f"Status: {r.status_code}")
print(f"Content-Length: {r.headers.get('Content-Length')}")
# If it's a small HTML file, it will show here
if r.headers.get('Content-Length') and int(r.headers.get('Content-Length')) < 10000:
    print(f"Content: {r.text[:500]}")
else:
    print("Content is large, likely the DB.")
