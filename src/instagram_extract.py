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

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_instagram(driver):
    url = "https://www.instagram.com/accounts/login/"
    driver.get(url)
    # Log-in manuale
    print("Effettuare il login manualmente e poi premere Enter...")
    input()

def scroll_to_load_all_elements(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        randmized_sleep(2)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

def get_posts_by_tag(driver, tag):
    url = f"https://www.instagram.com/explore/tags/{tag}/"
    driver.get(url)

    # Aggiungere una pausa per consentire il caricamento della pagina
    randmized_sleep(5)

    post_links = set()
    while True:
        print("Scorrimento per caricare più post...")
        scroll_to_load_all_elements(driver)

        # Attendere che i post siano presenti sulla pagina
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

    print(f"Total posts found: {len(post_links)}")
    return list(post_links)

def get_post_meta(driver, post_url):
    try:
        driver.get(post_url)
        randmized_sleep(2)  # Aggiungere una pausa per ridurre il rischio di rilevamento

        # Utilizza BeautifulSoup per estrarre i meta tag
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

def fetch_data(driver, tag):
    posts = get_posts_by_tag(driver, tag)
    data = []
    for post in tqdm(posts):
        details = get_post_meta(driver, post)
        if details:
            data.append(details)
            randmized_sleep(2)  # Aggiungere una pausa per ridurre il rischio di rilevamento
    return data

def save_to_file(data, filename):
    with open(filename, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def main():
    driver = setup_driver()
    login_to_instagram(driver)
    randmized_sleep(5)  # Aggiungere una pausa dopo il login per ridurre il rischio di rilevamento

    tag = input("Enter the hashtag to search: ")
    data = fetch_data(driver, tag)
    save_to_file(data, f"{tag}_data.json")
    print(f"Data saved to {tag}_data.json")

    driver.quit()

if __name__ == "__main__":
    main()
