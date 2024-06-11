from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
import time

def setup_driver():
    chrome_options = Options()
    chrome_options.add_argument("--incognito")
    chrome_options.add_argument("--window-size=1920x1080")
   
    driver = webdriver.Chrome(options=chrome_options)
    return driver

def login_to_threads(driver):
    url = "https://www.threads.net"
    driver.get(url)

    # Log-in manuale
    print("Effettuare il login manualmente e poi premere Enter...")
    input()

def collect_user_data(driver, username):
    url = f"https://www.threads.net/{username}"
    driver.get(url)
    time.sleep(5)  # Attesa per il caricamento della pagina

    # Raccolta dati utente specifico
    user_data = {
        "username": username,
        "followers": [],
        "following": [],
        "posts": []
    }

    # Esempio di raccolta follower
    followers_button = driver.find_element(By.XPATH, '//a[contains(@href, "/followers")]')
    followers_button.click()
    time.sleep(5)
    followers = driver.find_elements(By.CSS_SELECTOR, 'div.follower')  # Sostituire con il selettore corretto
    for follower in followers:
        user_data["followers"].append(follower.text)

    # Tornare alla pagina principale dell'utente
    driver.back()
    time.sleep(5)

    # Esempio di raccolta following
    following_button = driver.find_element(By.XPATH, '//a[contains(@href, "/following")]')
    following_button.click()
    time.sleep(5)
    followings = driver.find_elements(By.CSS_SELECTOR, 'div.following')  # Sostituire con il selettore corretto
    for following in followings:
        user_data["following"].append(following.text)

    # Tornare alla pagina principale dell'utente
    driver.back()
    time.sleep(5)

    # Esempio di raccolta post
    posts = driver.find_elements(By.CSS_SELECTOR, 'div.post')  # Sostituire con il selettore corretto
    for post in posts:
        content = post.find_element(By.CSS_SELECTOR, 'div.content').text
        likes = post.find_element(By.CSS_SELECTOR, 'span.likes').text
        comments = post.find_elements(By.CSS_SELECTOR, 'div.comment')
        post_data = {
            "content": content,
            "likes": likes,
            "comments": [comment.text for comment in comments]
        }
        user_data["posts"].append(post_data)

    return user_data

def main():
    driver = setup_driver()
    login_to_threads(driver)
    
    username = input("Inserire il nome utente di partenza: ")
    user_data = collect_user_data(driver, username)

    print(user_data)

    driver.quit()

if __name__ == "__main__":
    main()
