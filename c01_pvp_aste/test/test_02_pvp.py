# Importiamo lo strumento Playwright
from playwright.sync_api import sync_playwright

def esplora_pvp_stealth():
    """
    Funzione di test avanzata: Simula un utente umano per superare i blocchi WAF.
    """
    print("1. Accensione del motore Playwright in modalità stealth...")
    
    with sync_playwright() as p:
        
        print("2. Creazione della finta identità browser...")
        # args: rimuove il cartello "Sono un bot" dal motore del browser
        browser = p.chromium.launch(
            headless=True,
            args=["--disable-blink-features=AutomationControlled"]
        )
        
        # Creiamo il Contesto (l'impronta digitale dell'utente)
        contesto = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            viewport={"width": 1920, "height": 1080},
            locale="it-IT",
            timezone_id="Europe/Rome"
        )
        
        pagina = contesto.new_page()
        
        # Iniezione Javascript: Cancella la variabile interna che rivela i bot
        pagina.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url_target = "https://pvp.giustizia.it/pvp/"
        print(f"3. Navigazione verso: {url_target}")
        
        # Andiamo sul sito
        pagina.goto(url_target, wait_until="domcontentloaded")
        
        # Estraiamo il titolo
        titolo_estratto = pagina.title()
        
        print("-" * 40)
        print(f"ESITO POSITIVO. Firewall bypassato.")
        print(f"TITOLO LETTO: '{titolo_estratto}'")
        print("-" * 40)
        
        browser.close()

if __name__ == "__main__":
    esplora_pvp_stealth()