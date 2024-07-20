import os
import json
import random
import time
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from bs4 import BeautifulSoup
import requests
from tqdm import tqdm
from utils import randmized_sleep

# Funzione per inizializzare il driver di Chrome con le opzioni necessarie
def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")  # Avvia il browser in modalità incognito
    chrome_options.add_argument("--window-size=1920x1080")  # Imposta la dimensione della finestra del browser
    driver = webdriver.Chrome(options=chrome_options)
    return driver

# Funzione per ottenere i meta tag della pagina utente
def fetch_user_page_meta(username):
    url = f"https://www.threads.net/{username}"
    response = requests.get(url)
    if response.status_code == 200:
        soup = BeautifulSoup(response.content, 'html.parser')
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
            "url": url,
            "meta_contents": meta_contents
        }
    else:
        print(f"Errore nella richiesta HTTP: {response.status_code}")
        return None

# Funzione per ottenere i link dei post di un utente
def fetch_posts_from_user(driver, username):
    url = f"https://www.threads.net/{username}"
    driver.get(url)
    randmized_sleep(5)  # Pausa per consentire il caricamento della pagina

    post_links = set()
    # Trova tutti i link dei post nella pagina
    posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/post/')]")
    for post in posts:
        post_links.add(post.get_attribute("href"))
    print(f"Numero di post raccolti: {len(post_links)}")

    return list(post_links)

# Funzione per ottenere i meta tag di un post specifico
def extract_meta_data(driver, post_url):
    try:
        driver.get(post_url)
        randmized_sleep(random.uniform(5, 10))  # Pausa casuale per ridurre il rischio di rilevamento

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

# Funzione per raccogliere i dati di un utente e dei suoi post
def gather_data(driver, username):
    user_meta = fetch_user_page_meta(username)  # Ottiene i meta tag della pagina utente
    posts = fetch_posts_from_user(driver, username)  # Ottiene i link dei post dell'utente
    data = []
    for post in tqdm(posts, desc="Fetching post metadata"):
        details = extract_meta_data(driver, post)  # Estrae i meta tag di ciascun post
        if details:
            data.append(details)
            randmized_sleep(random.uniform(10, 15))  # Pausa casuale per ridurre il rischio di rilevamento
    return {"user_meta": user_meta, "posts": data}

# Funzione per salvare i dati in un file JSON
def save_json_file(data, directory, filename):
    os.makedirs(directory, exist_ok=True)  # Crea la directory se non esiste
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filepath}")

# Funzione per pulire i meta tag della pagina utente
def clean_user_meta(user_meta):
    cleaned_meta = {
        "url": user_meta.get("url"),
        "title": "",
        "description": "",
        "image": ""
    }
    for meta in user_meta.get("meta_contents", []):
        if meta.get("property") == "og:title":
            cleaned_meta["title"] = meta.get("content")
        elif meta.get("property") == "og:description":
            cleaned_meta["description"] = meta.get("content")
        elif meta.get("property") == "og:image":
            cleaned_meta["image"] = meta.get("content")
    return cleaned_meta

# Funzione per pulire i dati dei post e della pagina utente
def process_data(data):
    cleaned_data = {
        "user_meta": clean_user_meta(data.get("user_meta", {})),
        "posts": []
    }
    for entry in data.get("posts", []):
        cleaned_entry = {
            "url": entry.get("url"),
            "title": "",
            "description": "",
            "image": ""
        }
        for meta in entry.get("meta_contents", []):
            if meta.get("property") == "og:title":
                cleaned_entry["title"] = meta.get("content")
            elif meta.get("property") == "og:description":
                cleaned_entry["description"] = meta.get("content")
            elif meta.get("property") == "og:image":
                cleaned_entry["image"] = meta.get("content")
        cleaned_data["posts"].append(cleaned_entry)
    return cleaned_data

# Funzione per salvare i dati puliti in un file JSON
def save_processed_data(input_file, output_directory):
    with open(input_file, 'r') as infile:
        data = json.load(infile)
        cleaned_data = process_data(data)

    os.makedirs(output_directory, exist_ok=True)  # Crea la directory se non esiste
    output_file = os.path.join(output_directory, os.path.basename(input_file).replace(".json", "_processed.json"))
    with open(output_file, 'w') as outfile:
        json.dump(cleaned_data, outfile, ensure_ascii=False, indent=4)
    print(f"Dati ripuliti salvati in {output_file}")

# Funzione principale che gestisce l'intero processo
def main():
    driver = initialize_driver()  # Inizializza il driver
    randmized_sleep(5)  # Pausa per ridurre il rischio di rilevamento

    username = input("Inserire il nome utente: ")  # Chiede all'utente di inserire un nome utente
    data = gather_data(driver, username)  # Raccoglie i dati dell'utente e dei suoi post
    raw_data_directory = "raw_data"
    processed_data_directory = "processed_data"
    raw_data_filename = f"{username}_data.json"

    save_json_file(data, raw_data_directory, raw_data_filename)  # Salva i dati raccolti in un file JSON

    raw_data_filepath = os.path.join(raw_data_directory, raw_data_filename)
    save_processed_data(raw_data_filepath, processed_data_directory)  # Pulisce e salva i dati in un nuovo file JSON

    randmized_sleep(10)  # Pausa finale per ridurre il rischio di rilevamento
    driver.quit()  # Chiude il browser

if __name__ == "__main__":
    main()  # Avvia l'esecuzione del programma
