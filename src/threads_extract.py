import os
import json
import random
import time
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

# Funzione per effettuare il login su Threads manualmente
def login_to_threads(driver):
    url = "https://www.threads.net/"
    driver.get(url)
    # Richiede all'utente di effettuare il login manualmente e di premere Enter una volta completato
    print("Effettuare il login manualmente e poi premere Enter...")
    input()

# Funzione per scorrere la pagina verso il basso fino a caricare tutti gli elementi e raccogliere i link dei post
def scroll_to_load_all_elements(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    post_links = set()

    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        randmized_sleep(random.uniform(3, 7))  # Pausa casuale per evitare rilevamenti di bot

        # Attesa per vedere se ci sono altri contenuti da caricare
        time.sleep(20)

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            time.sleep(5)
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                print("Raggiunta la fine della pagina")
                break
        last_height = new_height

        # Trova tutti i link dei post nella pagina
        posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/post/')]")
        for post in posts:
            post_links.add(post.get_attribute("href"))
        print(f"Numero di post raccolti finora: {len(post_links)}")
        randmized_sleep(random.uniform(3, 7))  # Pausa casuale per evitare rilevamenti di bot

    return list(post_links)

# Funzione per ottenere i link dei post di un determinato hashtag
def get_posts_by_tag(driver, tag):
    url = f"https://www.threads.net/search?q={tag}&serp_type=default"
    driver.get(url)

    randmized_sleep(5)  # Pausa per consentire il caricamento della pagina

    print("Scorrimento per caricare più post...")
    post_links = scroll_to_load_all_elements(driver)

    print(f"Total posts found: {len(post_links)}")
    return post_links

# Funzione per ottenere i meta tag di un post specifico
def get_post_meta(driver, post_url):
    try:
        driver.get(post_url)
        randmized_sleep(random.uniform(5, 10))  # Pausa casuale per ridurre il rischio di rilevamento

        # Utilizza BeautifulSoup per estrarre i meta tag dalla sorgente della pagina
        soup = BeautifulSoup(driver.page_source, 'html.parser')
        meta_tags = soup.find_all('meta')

        meta_contents = []
        for meta in meta_tags:
            if 'content' in meta.attrs:
                # Struttura dei dati nel JSON
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
            randmized_sleep(random.uniform(10, 15))  # Pausa casuale per ridurre il rischio di rilevamento
    return data

# Funzione per salvare i dati raccolti in un file JSON
def save_to_file(data, directory, filename):
    os.makedirs(directory, exist_ok=True)  # Crea la directory se non esiste
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filepath}")

# Funzione per pulire i dati estratti, mantenendo solo le informazioni rilevanti
def clean_data(data):
    cleaned_data = []
    for entry in data:
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
        cleaned_data.append(cleaned_entry)
    return cleaned_data

# Funzione per salvare i dati puliti in un file JSON
def save_cleaned_data(input_file, output_directory):
    with open(input_file, 'r') as infile:
        data = json.load(infile)
        cleaned_data = clean_data(data)

    os.makedirs(output_directory, exist_ok=True)  # Crea la directory se non esiste
    output_file = os.path.join(output_directory, os.path.basename(input_file).replace(".json", "_cleaned.json"))
    with open(output_file, 'w') as outfile:
        json.dump(cleaned_data, outfile, ensure_ascii=False, indent=4)
    print(f"Dati ripuliti salvati in {output_file}")

# Funzione principale che gestisce l'intero processo
def main():
    driver = setup_driver()  # Configura il driver
    login_to_threads(driver)  # Effettua il login su Threads
    randmized_sleep(5)  # Pausa dopo il login per ridurre il rischio di rilevamento

    tag = input("Inserire hashtag da cercare: ")  # Chiede all'utente di inserire un hashtag
    data = fetch_data(driver, tag)  # Raccoglie i dati dei post con quell'hashtag
    raw_data_directory = "raw_data"
    cleaned_data_directory = "cleaned_data"
    raw_data_filename = f"{tag}_data.json"

    save_to_file(data, raw_data_directory, raw_data_filename)  # Salva i dati raccolti in un file JSON

    raw_data_filepath = os.path.join(raw_data_directory, raw_data_filename)
    save_cleaned_data(raw_data_filepath, cleaned_data_directory)  # Pulisce e salva i dati in un nuovo file JSON

    randmized_sleep(10)  # Pausa finale per ridurre il rischio di rilevamento
    driver.quit()  # Chiude il browser

if __name__ == "__main__":
    main()  # Avvia l'esecuzione del programma
