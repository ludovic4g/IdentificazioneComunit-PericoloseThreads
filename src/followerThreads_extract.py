from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import os
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
    url = "https://www.threads.net"
    driver.get(url)
    # Richiede all'utente di effettuare il login manualmente e di premere Enter una volta completato
    print("Effettuare il login manualmente e poi premere Enter...")
    input()

# Funzione per scorrere la pagina verso il basso fino a caricare tutti gli elementi
def scroll_to_load_all_elements(driver):
    last_height = driver.execute_script("return document.body.scrollHeight")
    while True:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(2)  # Pausa per consentire il caricamento dei contenuti
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

# Funzione per raccogliere i follower di un determinato utente
def collect_followers(driver, username):
    url = f"https://www.threads.net/{username}"
    driver.get(url)
    time.sleep(5)  # Attesa per il caricamento della pagina

    try:
        # Attendere che il pulsante dei follower sia visibile e cliccabile
        followers_button = WebDriverWait(driver, 20).until(
            EC.element_to_be_clickable((By.XPATH, "//span[contains(text(), 'Follower') and contains(@class, 'x1lliihq')]"))
        )
        followers_button.click()
        time.sleep(5)  # Attesa per il caricamento della lista dei follower

        # Scorrere per caricare tutti i follower
        scroll_to_load_all_elements(driver)

        # Estrarre i nomi utente dei follower
        followers = set()  # Usare un set per evitare duplicati
        follower_elements = driver.find_elements(By.XPATH, "//a[contains(@class, 'x1i10hfl')]")
        for elem in follower_elements:
            username = elem.get_attribute("href").split("/")[-1]
            if username not in followers:
                followers.add(username)
        return list(followers)

    except Exception as e:
        print(f"Errore nella raccolta dei follower: {e}")
        return []

# Funzione per salvare i dati in un file
def save_to_file(data, filename):
    os.makedirs('followers_extracted', exist_ok=True)  # Crea la directory se non esiste
    file_path = os.path.join('followers_extracted', filename)
    with open(file_path, 'w', encoding='utf-8') as file:
        for item in data:
            file.write(f"{item}\n")

# Funzione principale che gestisce l'intero processo
def main():
    driver = setup_driver()  # Configura il driver
    login_to_threads(driver)  # Effettua il login su Threads
    randmized_sleep(5)  # Pausa dopo il login per ridurre il rischio di rilevamento
    username = input("Inserire il nome utente di partenza: ")  # Chiede all'utente di inserire un nome utente
    followers = collect_followers(driver, username)  # Raccoglie i follower di quell'utente

    if followers:
        output_filename = f"{username}_followers.txt"
        save_to_file(followers, output_filename)  # Salva i follower in un file
        print(f"Follower salvati in {output_filename}")
    else:
        print("Nessun follower trovato.")

    driver.quit()  # Chiude il browser

if __name__ == "__main__":
    main()  # Avvia l'esecuzione del programma
