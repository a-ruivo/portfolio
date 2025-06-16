import requests

url = "http://localhost:5678/webhook/0d8205fd-345d-4e28-aeca-ed557de86a22"

response = requests.get(url)

if response.status_code == 200:
    print("Resposta da API:")
    print(response.text)
else:
    print(f"Erro {response.status_code}: {response.reason}")
