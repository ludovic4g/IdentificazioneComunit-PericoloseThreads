import os
import json
import random
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


def login_to_threads(driver):
    url = "https://www.threads.net/"
    driver.get(url)
    # Log-in manuale
    print("Effettuare il login manualmente e poi premere Enter...")
    input()


def scroll_to_load_all_elements(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        randmized_sleep(random.uniform(2, 5))  # Randomize sleep time between 2 to 5 seconds

        # Attendere che i post siano presenti sulla pagina
        WebDriverWait(driver, 20).until(
            EC.presence_of_element_located((By.XPATH, "//a[contains(@href, '/post/')]"))
        )

        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height
        randmized_sleep(random.uniform(2, 5))  # Additional random sleep during scrolling


def get_posts_by_tag(driver, tag):
    url = f"https://www.threads.net/search?q={tag}&serp_type=default"
    driver.get(url)

    # Aggiungere una pausa per consentire il caricamento della pagina
    randmized_sleep(5)

    post_links = set()
    while True:
        print("Scorrimento per caricare più post...")
        scroll_to_load_all_elements(driver)

        posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/post/')]")
        if not posts:
            break

        for post in posts:
            post_links.add(post.get_attribute("href"))

        prev_len = len(post_links)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        randmized_sleep(random.uniform(2, 5))  # Randomize sleep time between 2 to 5 seconds
        if len(post_links) == prev_len:
            break

    print(f"Total posts found: {len(post_links)}")
    return list(post_links)


def get_post_meta(driver, post_url):
    try:
        driver.get(post_url)
        randmized_sleep(random.uniform(5, 10))  # Aggiungere una pausa per ridurre il rischio di rilevamento

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
            randmized_sleep(random.uniform(10, 15))  # Randomize sleep time between 10 to 15 seconds
    return data


def save_to_file(data, directory, filename):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filepath}")


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


def save_cleaned_data(input_file, output_directory):
    with open(input_file, 'r') as infile:
        data = json.load(infile)
        cleaned_data = clean_data(data)

    os.makedirs(output_directory, exist_ok=True)
    output_file = os.path.join(output_directory, os.path.basename(input_file).replace(".json", "_cleaned.json"))
    with open(output_file, 'w') as outfile:
        json.dump(cleaned_data, outfile, ensure_ascii=False, indent=4)
    print(f"Cleaned data has been saved to {output_file}")


def main():
    driver = setup_driver()
    login_to_threads(driver)
    randmized_sleep(5)  # Aggiungere una pausa dopo il login per ridurre il rischio di rilevamento

    tag = input("Enter the hashtag to search: ")
    data = fetch_data(driver, tag)
    raw_data_directory = "raw_data"
    cleaned_data_directory = "cleaned_data"
    raw_data_filename = f"{tag}_data.json"

    save_to_file(data, raw_data_directory, raw_data_filename)

    raw_data_filepath = os.path.join(raw_data_directory, raw_data_filename)
    save_cleaned_data(raw_data_filepath, cleaned_data_directory)

    randmized_sleep(10)  # Attendere un po' prima di chiudere per sembrare più umano
    driver.quit()


if __name__ == "__main__":
    main()
