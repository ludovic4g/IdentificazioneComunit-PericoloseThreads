import requests
from bs4 import BeautifulSoup

# URL della pagina web
url = 'https://www.threads.net/@giorgiameloni?hl=it'

# Effettua la richiesta HTTP
response = requests.get(url)
if response.status_code == 200:
    # Analizza il contenuto HTML della pagina
    soup = BeautifulSoup(response.content, 'html.parser')

    # Trova tutti i meta tag
    meta_tags = soup.find_all('meta')

    # Itera e stampa ogni meta tag
    for meta in meta_tags:
        if 'content' in meta.attrs:
            print(f"Meta tag trovato: {meta.prettify()}")
            print(f"Contenuto: {meta.attrs['content']}")
else:
    print("Errore nella richiesta HTTP:", response.status_code)
