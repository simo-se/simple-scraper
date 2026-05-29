import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException
from bs4 import BeautifulSoup
import time
import random
import os

# File per salvare lo stato dello scraping e i risultati
LOG_FILE = "scraper_progress.txt"
OUTPUT_FILE = "found_urls.txt"

IS_HEADLESS_MODE = False
RITARDO_CHALLENGE = 30  # Tempo massimo per risolvere manualmente il CAPTCHA
RITARDO_SCRAPING = 2    # Attesa tra il caricamento di una pagina e l'altra

def load_page_index(default_start_page):
    """Carica l'ultimo indice di pagina elaborato."""
    if os.path.exists(LOG_FILE):
        try:
            with open(LOG_FILE, 'r') as f:
                last_page = int(f.read().strip())
                print(f"🔄 Riprendo lo scraping dall'indice di pagina: {last_page}")
                return last_page + 1
        except Exception:
            print("⚠️ Errore nella lettura del file di progresso. Inizio da capo.")
            return default_start_page
    return default_start_page

def save_page_index(page_num):
    """Salva l'indice della pagina corrente."""
    with open(LOG_FILE, 'w') as f:
        f.write(str(page_num))

def scrape_with_selenium(base_url, initial_start_page, end_page, search_string, delay_seconds):
    """Scansiona le pagine cercando una stringa specifica nel testo HTML."""
    start_page = load_page_index(initial_start_page) - 1  # Rielabora l'ultima pagina per sicurezza
    
    if start_page > end_page:
        print("✅ Scansione già completata fino all'ultima pagina richiesta.")
        return
    
    options = uc.ChromeOptions()
    if not IS_HEADLESS_MODE:
        print("Browser avviato in modalità visibile per consentire la risoluzione del CAPTCHA.")
    else:
        options.add_argument('--headless')
        print("Browser avviato in modalità headless.")

    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    driver = None
    try:
        import subprocess
        import re
        version_main = None
        # Rileva automaticamente la versione principale di Chrome/Chromium installata sul sistema
        for cmd in ["google-chrome", "chrome", "chromium", "/snap/bin/chromium"]:
            try:
                out = subprocess.check_output([cmd, "--version"], text=True)
                match = re.search(r"(\d+)\.", out)
                if match:
                    version_main = int(match.group(1))
                    break
            except Exception:
                continue
        
        if version_main:
            print(f"Rilevata versione di Chrome/Chromium: {version_main}. Avvio driver con version_main={version_main}")
            driver = uc.Chrome(options=options, version_main=version_main)
        else:
            driver = uc.Chrome(options=options)
    except Exception as e:
        print(f"❌ Errore durante l'inizializzazione del driver. Assicurati che Chrome sia installato. Errore: {e}")
        return

    print("Inizio la scansione...")
    
    for page_num in range(start_page, end_page + 1):
        url = f"{base_url}{page_num}/"
        
        try:
            print(f"Navigazione a: {url}")
            driver.get(url)
            
            # Gestione della challenge/CAPTCHA all'avvio o se richiesto
            wait_time = RITARDO_CHALLENGE
            if "Magazine" in driver.title:
                wait_time = RITARDO_SCRAPING
                print(f"Pagina caricata correttamente, attesa ridotta a {wait_time}s.")
            elif "Just a moment" in driver.title or "Ci siamo quasi" in driver.title:
                print(f"⚠️ Challenge rilevata. Hai {wait_time}s per risolvere il CAPTCHA...")
            
            wait = WebDriverWait(driver, wait_time)
            try:
                wait.until_not(EC.title_contains("Ci siamo quasi"))
                current_title = driver.title
                if "Magazine" in current_title:
                    print(f"✅ Titolo valido ('{current_title}') raggiunto. Proseguo.")
                else:
                    print(f"✅ Challenge superata, ma titolo inatteso ('{current_title}'). Proseguo.")
            except TimeoutException:
                if "Just a moment" in driver.title or "Ci siamo quasi" in driver.title:
                    print(f"❌ ERRORE: CAPTCHA non risolto entro {RITARDO_CHALLENGE}s. Interrompo lo scraping.")
                    driver.quit()
                    return

            # Applica il filtro lingua solo alla prima pagina caricata
            if page_num == start_page:
                try:
                    print("Applicazione del filtro 'Italian'...")
                    wait = WebDriverWait(driver, 10)
                    radio_button = wait.until(EC.element_to_be_clickable((By.ID, 'Italian')))
                    # Utilizziamo JS per bypassare eventuali overlay grafici che bloccano il click
                    driver.execute_script("arguments[0].click();", radio_button)
                    time.sleep(5)  # Attesa per ricaricamento pagina
                    print("Filtro 'Italian' applicato con successo.")
                except Exception as e:
                    print(f"❌ Errore durante l'applicazione del filtro 'Italian': {e}")

            # Analisi del contenuto
            html_content = driver.page_source
            soup = BeautifulSoup(html_content, 'html.parser')
            content_body = soup.find('body')
            
            if content_body:
                page_text = content_body.get_text()
                if search_string.lower() in page_text.lower():
                    print(f"\n🎉 Stringa trovata in: {url} 🎉")
                    with open(OUTPUT_FILE, 'a') as out_f:
                        out_f.write(f"{url}\n")
                else:
                    print(f"Stringa '{search_string}' non trovata in {url}.")

                save_page_index(page_num)
            else:
                print(f"⚠️ Nessun elemento 'body' trovato su {url}.")
            
        except WebDriverException as e:
            print(f"Errore critico del WebDriver: {e}")
            break
        except Exception as e:
            print(f"Si è verificato un errore: {e}")

        if page_num < end_page:
            time.sleep(RITARDO_SCRAPING + random.uniform(0.5, 1.5))

    print("\n--- Scansione completata ---")
    if driver:
        driver.quit()

# --- Configurazione ed esecuzione ---
STRINGA_DA_CERCARE = "RuoteClassiche"
RITARDO_IN_SECONDI = 5 

scrape_with_selenium(
    base_url='https://eurekaddl.art/magazines/page/',
    initial_start_page=3,
    end_page=143,
    search_string=STRINGA_DA_CERCARE,
    delay_seconds=RITARDO_IN_SECONDI
)
