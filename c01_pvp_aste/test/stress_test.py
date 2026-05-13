from playwright.sync_api import sync_playwright
import time

def esegui_stress_test():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("\n--- AVVIO STRESS TEST (SENZA FILTRI) ---")
        tribunale = "Verona" # Testiamo solo su uno per fare in fretta
        
        page.goto("https://pvp.giustizia.it/pvp/")
        page.wait_for_load_state("networkidle")
        
        page.locator("text='Affina la ricerca'").click()
        time.sleep(2) 
        
        campo_tribunale = page.locator("text='Seleziona Tribunale'").first
        campo_tribunale.click(force=True)
        page.keyboard.type(tribunale, delay=150)
        time.sleep(1.5)
        page.keyboard.press("ArrowDown")
        time.sleep(0.5)
        page.keyboard.press("Enter")
        
        print("  - Bottoni premuti. Clicco Cerca e attendo...")
        page.locator("button:has-text('Cerca')").last.click()
        
        # Aspettiamo 5 secondi interi per assicurarci che la pagina carichi
        time.sleep(5) 

        # --- DIAGNOSTICA VISIVA ---
        annunci = page.query_selector_all(".risultato-ricerca")
        print(f"\n[!] DIAGNOSTICA: Il bot vede {len(annunci)} blocchi annuncio nella pagina.")

        if len(annunci) > 0:
            print("\n--- PRIMI 5 RISULTATI GREZZI (Nessun filtro applicato) ---")
            for i, annuncio in enumerate(annunci[:5]):
                try:
                    descrizione = annuncio.query_selector(".descrizione-annuncio").inner_text().strip()
                    localita = annuncio.query_selector(".localita-annuncio").inner_text().strip()
                    prezzo = annuncio.query_selector(".prezzo-annuncio").inner_text().strip()
                    
                    print(f"{i+1}. LOC: {localita} | PRZ: {prezzo}")
                    print(f"   DESC: {descrizione[:80]}...")
                except Exception as e:
                    print(f"   [Errore lettura annuncio {i+1}: Dati mancanti]")
        else:
            print("\n[X] Niente da fare. Il bot non vede la classe '.risultato-ricerca'. Il Ministero ha cambiato il codice del sito.")

        browser.close()

if __name__ == "__main__":
    esegui_stress_test()