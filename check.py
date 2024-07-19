import requests

url = 'http://198.211.106.68/products/main_category/'

response = requests.get(url)

if response.status_code == 200:
    print(response.text)  # or response.content for binary data
else:
    print(f"Failed to retrieve data: {response.status_code}")
