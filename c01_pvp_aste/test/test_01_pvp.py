# Importiamo SOLO lo strumento specifico che ci serve dalla libreria playwright
from playwright.sync_api import sync_playwright

def esplora_pvp():
    """
    Funzione di test: Apre un browser invisibile, naviga sul PVP ed estrae il titolo.
    """
    print("1. Accensione del motore Playwright...")
    
    # Il blocco 'with' è una misura di sicurezza: garantisce che il browser
    # venga chiuso in automatico alla fine, anche se lo script va in crash.
    with sync_playwright() as p:
        
        print("2. Lancio del browser fantasma (Chromium)...")
        # headless=True significa che non vedrai finestre aprirsi. Lavora nella RAM.
        browser = p.chromium.launch(headless=True) 
        pagina = browser.new_page()
        
        url_target = "https://pvp.giustizia.it/pvp/"
        print(f"3. Navigazione verso: {url_target}")
        
        # Diciamo al bot di andare all'URL e aspettare che la rete si stabilizzi
        pagina.goto(url_target, wait_until="domcontentloaded")
        
        # Estraiamo l'elemento HTML <title>
        titolo_estratto = pagina.title()
        
        print("-" * 40)
        print(f"ESITO POSITIVO. Il server ha risposto.")
        print(f"TITOLO LETTO: '{titolo_estratto}'")
        print("-" * 40)
        
        # Chiudiamo la porta
        browser.close()

# Questa è la "Firma del Professionista". Evita che lo script parta da solo 
# se in futuro lo importiamo in un altro file.
if __name__ == "__main__":
    esplora_pvp()