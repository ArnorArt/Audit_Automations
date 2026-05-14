# ricerca_finale_privati.py
from playwright.sync_api import sync_playwright
from auditor_valutatore import AuditorImmobiliare
import time

def avvia_motore_a(url_partenza):
    print("--- AVVIO MOTORE A: RICERCA PORTALI PRIVATI ---")
    
    # 1. Assumiamo l'Auditor (Il nostro "Stampo")
    auditor = AuditorImmobiliare()
    immobili_approvati = []

    with sync_playwright() as p:
        # Apriamo il browser in modalità visibile per simulare un umano
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("[*] Accesso al portale in corso...")
        page.goto(url_partenza)
        page.wait_for_load_state("networkidle")
        time.sleep(3) # Pausa umana

        # TODO: Qui inseriremo la logica per cliccare "Accetta Cookie"
        # TODO: Qui inseriremo il ciclo per leggere le schede degli immobili

        """
        --- ESEMPIO DELLA LOGICA DEL SILENZIATORE CHE HAI RICHIESTO ---
        
        Per ogni immobile trovato sulla pagina:
            # Estraiamo titolo, desc, prezzo, mq...
            
            # Passiamo i dati all'Auditor
            approvato, motivo = auditor.valuta_annuncio(titolo, desc, prezzo, mq)
            
            if approvato:
                # STAMPA SOLO I TRUE (Segnale puro)
                print(f"[!] BERSAGLIO ACQUISITO: {titolo} | Prezzo: {prezzo}€")
                immobili_approvati.append(url_immobile)
            else:
                # NESSUN PRINT (Silenzio assoluto sui False)
                pass 
        """

        print("\n" + "="*50)
        print(f"REPORT FINALE AUDIT (MOTORE A)")
        print("="*50)
        print(f"Totale annunci analizzati (anche i respinti in silenzio): {auditor.immobili_analizzati + auditor.immobili_scartati}")
        print(f"Totale annunci APPROVATI e in target: {auditor.immobili_analizzati}")

        browser.close()

if __name__ == "__main__":
    # URL di test vuoto per ora
    URL_TEST = "https://www.immobiliare.it/"
    avvia_motore_a(URL_TEST)