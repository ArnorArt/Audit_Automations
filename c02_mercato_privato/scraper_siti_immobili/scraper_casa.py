import sys
import os
import re
from playwright.sync_api import sync_playwright, devices

# --- IL PONTE PER PYTHON ---
cartella_corrente = os.path.dirname(os.path.abspath(__file__))
cartella_superiore = os.path.dirname(cartella_corrente)
sys.path.append(cartella_superiore)

from auditor_valutatore import AuditorImmobiliare

# URL SEMPLIFICATO PER MOBILE
URL_TARGET = "https://www.casa.it/vendita/residenziale/verona-provincia/?priceMax=130000&mqMin=100"

def esegui_scouting_casa_it():
    print("--- AVVIO SPECIALISTA: CASA.IT (V11 - INFILTRATO iPHONE) ---")
    auditor = AuditorImmobiliare()
    
    try:
        with sync_playwright() as p:
            # Usiamo il profilo di un iPhone 13 per bypassare i blocchi desktop
            iphone = p.devices['iPhone 13']
            browser = p.chromium.launch(headless=False)
            context = browser.new_context(**iphone, locale="it-IT", timezone_id="Europe/Rome")
            page = context.new_page()

            print("[*] Accesso in modalità Mobile...")
            page.goto(URL_TARGET, wait_until="networkidle")
            page.wait_for_timeout(5000) 

            # COOKIE (Versione Mobile)
            try:
                page.locator("button:has-text('Accetta'), button:has-text('OK')").first.click(timeout=3000)
            except:
                pass

            pagina = 1
            while True:
                print(f"\n[>] Ispezione Pagina {pagina}...")
                
                # Scroll lento per caricare i dati (Lazy Load Mobile)
                page.mouse.wheel(0, 2000)
                page.wait_for_timeout(2000)

                # Usiamo i selettori estratti dal tuo file txt
                cards = page.locator("article, .csaSrpcard__cnt-card")
                count = cards.count()
                
                if count == 0:
                    print("[-] Nessun annuncio visibile. Tentativo di scroll extra...")
                    page.mouse.wheel(0, 3000)
                    page.wait_for_timeout(3000)
                    cards = page.locator("article, .csaSrpcard__cnt-card")
                    count = cards.count()
                    if count == 0: break

                print(f"[*] Rilevati {count} annunci. Analisi DNA...")
                
                for i in range(count):
                    try:
                        nodo = cards.nth(i)
                        testo = str(nodo.text_content()).lower()

                        if "€" not in testo: continue

                        # Link e Dati
                        link_el = nodo.locator("a").first
                        url = link_el.get_attribute("href")
                        if not url.startswith("http"): url = "https://www.casa.it" + url
                        
                        # Estrazione Prezzo e MQ chirurgica
                        p_match = re.search(r'€\s*([\d\.]+)', testo)
                        m_match = re.search(r'(\d+)\s*(?:m²|mq)', testo)
                        
                        if p_match and m_match:
                            prezzo = float(p_match.group(1).replace('.', ''))
                            mq = int(m_match.group(1))
                            id_dna = f"{int(prezzo)}_{mq}"
                            titolo = str(link_el.text_content()).strip() or "Annuncio"

                            approvato, motivo = auditor.valuta_annuncio(id_dna, url, titolo, testo, prezzo, mq)
                            if approvato:
                                print(f"✅ {motivo} | {titolo} (DNA: {id_dna})")
                    except:
                        continue

                # Tasto Avanti Mobile
                next_btn = page.locator("a[class*='next'], a:has-text('>')").first
                if next_btn.is_visible():
                    next_btn.click()
                    pagina += 1
                else:
                    break

            auditor.salva_database()
            browser.close()
            
    except Exception as e:
        print(f"[!] Errore critico: {e}")

if __name__ == "__main__":
    esegui_scouting_casa_it()