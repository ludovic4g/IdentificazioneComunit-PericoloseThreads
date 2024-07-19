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

def initialize_driver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--window-size=1920x1080")
    driver = webdriver.Chrome(options=chrome_options)
    return driver

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

def fetch_posts_from_user(driver, username):
    url = f"https://www.threads.net/{username}"
    driver.get(url)
    randmized_sleep(5)

    post_links = set()
    posts = driver.find_elements(By.XPATH, "//a[contains(@href, '/post/')]")
    for post in posts:
        post_links.add(post.get_attribute("href"))
    print(f"Numero di post raccolti: {len(post_links)}")

    return list(post_links)

def extract_meta_data(driver, post_url):
    try:
        driver.get(post_url)
        randmized_sleep(random.uniform(5, 10))

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

def gather_data(driver, username):
    user_meta = fetch_user_page_meta(username)
    posts = fetch_posts_from_user(driver, username)
    data = []
    for post in tqdm(posts, desc="Fetching post metadata"):
        details = extract_meta_data(driver, post)
        if details:
            data.append(details)
            randmized_sleep(random.uniform(10, 15))
    return {"user_meta": user_meta, "posts": data}

def save_json_file(data, directory, filename):
    os.makedirs(directory, exist_ok=True)
    filepath = os.path.join(directory, filename)
    with open(filepath, 'w') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    print(f"Data saved to {filepath}")

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

def save_processed_data(input_file, output_directory):
    with open(input_file, 'r') as infile:
        data = json.load(infile)
        cleaned_data = process_data(data)

    os.makedirs(output_directory, exist_ok=True)
    output_file = os.path.join(output_directory, os.path.basename(input_file).replace(".json", "_processed.json"))
    with open(output_file, 'w') as outfile:
        json.dump(cleaned_data, outfile, ensure_ascii=False, indent=4)
    print(f"Cleaned data has been saved to {output_file}")

def main():
    driver = initialize_driver()
    randmized_sleep(5)

    username = input("Inserire il nome utente: ")
    data = gather_data(driver, username)
    raw_data_directory = "raw_data"
    processed_data_directory = "processed_data"
    raw_data_filename = f"{username}_data.json"

    save_json_file(data, raw_data_directory, raw_data_filename)

    raw_data_filepath = os.path.join(raw_data_directory, raw_data_filename)
    save_processed_data(raw_data_filepath, processed_data_directory)

    randmized_sleep(10)
    driver.quit()

if __name__ == "__main__":
    main()