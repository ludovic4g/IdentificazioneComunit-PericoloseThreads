import os
import json
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from tqdm import tqdm
from bs4 import BeautifulSoup
from utils import randmized_sleep

# Funzione per configurare il driver di Chrome con le opzioni necessarie
def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")  # Avvia il browser in modalità incognito
    chrome_options.add_argument("--window-size=1920x1080")  # Imposta la dimensione della finestra del browser
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Funzione per effettuare il login su Instagram
def login_to_instagram(driver):
    url = "https://www.instagram.com/accounts/login/"
    driver.get(url)
    # Richiede all'utente di effettuare il login manualmente e di premere Enter una volta completato
    print("Effettuare il login manualmente e poi premere Enter...")
    input()

# Funzione per scorrere la pagina verso il basso fino a caricare tutti gli elementi
def scroll_to_load_all_elements(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        randmized_sleep(2)  # Pausa casuale per evitare rilevamenti di bot
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Funzione per ottenere i link dei post di un determinato hashtag
def get_posts_by_tag(driver, tag):
    url = f"https://www.instagram.com/explore/tags/{tag}/"
    driver.get(url)

    # Pausa per consentire il caricamento della pagina
    randmized_sleep(5)

    post_links = set()
    while True:
        print("Scorrimento per caricare più post...")
        scroll_to_load_all_elements(driver)

        # Attende che i post siano presenti sulla pagina
        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/p/')]"))
        )

        posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/p/')]")
        if not posts:
            break

        for post in posts:
            post_links.add(post.get_attribute("href"))

        prev_len = len(post_links)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        randmized_sleep(2)
        if len(post_links) == prev_len:
            break

    print(f"Post totali trovati: {len(post_links)}")
    return list(post_links)

# Funzione per ottenere i meta tag di un post specifico
def get_post_meta(driver, post_url):
    try:
        driver.get(post_url)
        randmized_sleep(2)  # Pausa per ridurre il rischio di rilevamento

        # Utilizza BeautifulSoup per estrarre i meta tag dalla sorgente della pagina
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        meta_tags = soup.find_all('meta')

        meta_contents = []
        for meta in meta_tags:
            if 'content' in meta.attrs:
                meta_contents.append({
                    "name": meta.attrs.get('name', ''),
                    "property": meta.attrs.get('property', ''),
                    "content": meta.attrs['content']
                })

        return {
            "url": post_url,
            "meta_contents": meta_contents
        }
    except Exception as e:
        print(f"Errore nel recupero dei meta tag del post {post_url}: {e}")
        return None

# Funzione per raccogliere i dati dei post di un determinato hashtag
def fetch_data(driver, tag):
    posts = get_posts_by_tag(driver, tag)
    data = []
    for post in tqdm(posts):
        details = get_post_meta(driver, post)
        if details:
            data.append(details)
            randmized_sleep(2)  # Pausa per ridurre il rischio di rilevamento
    return data

# Funzione per salvare i dati raccolti in un file JSON
def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

# Funzione principale che gestisce l'intero processo
def main():
    driver = setup_driver()  # Configura il driver
    login_to_instagram(driver)  # Effettua il login su Instagram
    randmized_sleep(5)  # Pausa dopo il login per ridurre il rischio di rilevamento

    tag = input("Inserire hashtag da cercare: ")  # Chiede all'utente di inserire un hashtag
    data = fetch_data(driver, tag)  # Raccoglie i dati dei post con quell'hashtag
    save_to_file(data, f"{tag}_data.json")  # Salva i dati in un file JSON
    print(f"Data saved to {tag}_data.json")

    driver.quit()  # Chiude il browser

if __name__ == "__main__":
    main()  # Avvia l'esecuzione del programma
