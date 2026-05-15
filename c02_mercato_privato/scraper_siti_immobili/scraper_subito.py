import sys
import os
import time
import re
from playwright.sync_api import sync_playwright

# --- IL PONTE PER PYTHON ---
cartella_corrente = os.path.dirname(os.path.abspath(__file__))
cartella_superiore = os.path.dirname(cartella_corrente)
sys.path.append(cartella_superiore)

from auditor_valutatore import AuditorImmobiliare

# LA FLOTTA DELLE PROVINCE (Legge 80/20: niente click, andiamo diretti al bersaglio)
URL_SUBITO_LISTA = [
    "https://www.subito.it/annunci-veneto/vendita/immobili/verona/?pe=130000&szs=100",
    "https://www.subito.it/annunci-lombardia/vendita/immobili/mantova/?pe=130000&szs=100",
    "https://www.subito.it/annunci-veneto/vendita/immobili/rovigo/?pe=130000&szs=100"
]

def esegui_scouting_subito():
    print("--- AVVIO SPECIALISTA: SUBITO.IT (V2 - MULTI-PROVINCIA & DNA) ---")
    auditor = AuditorImmobiliare()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            # Il bot esegue la ricerca per ogni provincia nell'elenco
            for url_target in URL_SUBITO_LISTA:
                provincia_nome = url_target.split('/')[-2].upper()
                print(f"\n[*] Cambio rotta. Atterraggio sulla provincia: {provincia_nome}")
                page.goto(url_target)
                page.wait_for_timeout(3500)

                # Chiusura Cookie aggressiva
                try:
                    bottone_cookie = page.locator("button:has-text('Accetta'), button:has-text('Accetto')").first
                    if bottone_cookie.is_visible(timeout=2000):
                        bottone_cookie.click()
                except:
                    pass

                pagina_corrente = 1

                while True:
                    print(f"  [>] Analisi Pagina {pagina_corrente} in corso...")
                    page.wait_for_timeout(2500) 

                    # TRACCIAMENTO TERMICO: Puntiamo al recinto dei dettagli
                    sezioni_web = page.locator("section[class*='index-module_details']")
                    numero_annunci = sezioni_web.count()
                    
                    if numero_annunci == 0:
                        print("  [-] Nessun annuncio organico trovato in questa pagina.")
                        break
                        
                    print(f"  [*] Trovati {numero_annunci} annunci. Estrazione e calcolo DNA...")
                    
                    for i in range(numero_annunci):
                        try:
                            # 1. Cattura della Sezione
                            sezione = sezioni_web.nth(i)
                            
                            # 2. Passo indietro per trovare il Link
                            padre = sezione.locator("xpath=..")
                            nodo_link = padre.locator("a[href*='.htm']").first
                            
                            if not nodo_link.is_visible():
                                continue
                                
                            link_completo = nodo_link.get_attribute("href")
                            if not link_completo.startswith("http"):
                                link_completo = "https://www.subito.it" + link_completo

                            # 3. Estrazione Titolo (dal link o dal tag h3 interno)
                            titolo_testo = nodo_link.get_attribute("aria-label")
                            if not titolo_testo:
                                titolo_testo = sezione.locator("h3").first.inner_text()

                            # 4. Estrazione Dati per il DNA
                            testo_card_intero = sezione.inner_text().lower()
                            
                            prezzo_pulito = 0.0
                            match_prezzo = re.search(r'([\d\.]+)\s*€', testo_card_intero)
                            if match_prezzo:
                                prezzo_pulito = float(match_prezzo.group(1).replace('.', ''))
                                
                            mq_puliti = 0
                            match_mq = re.search(r'(\d+)\s*mq', testo_card_intero)
                            if match_mq:
                                mq_puliti = int(match_mq.group(1))

                            # LA CHIAVE: Creazione del DNA Univoco (Es. 120000_170)
                            id_annuncio = f"{int(prezzo_pulito)}_{mq_puliti}"

                            # INVIO AL CERVELLO
                            approvato, motivo = auditor.valuta_annuncio(id_annuncio, link_completo, titolo_testo, testo_card_intero, prezzo_pulito, mq_puliti)
                            
                            if approvato:
                                print(f"  ✅ {motivo} | {titolo_testo}")
                                print(f"     DNA: {id_annuncio} | Prezzo: € {prezzo_pulito} | {mq_puliti} m²")
                                print(f"     {'-'*40}")
                                
                        except Exception as e:
                            continue
                    
                    # SALTO PAGINA SUBITO.IT
                    bottone_avanti = page.locator("button:has-text('Successiva'), a:has-text('Successiva'), a[aria-label*='successiva'], button[aria-label*='successiva']").first
                    
                    if bottone_avanti.is_visible():
                        bottone_avanti.click()
                        page.wait_for_timeout(3500) 
                        pagina_corrente += 1
                    else:
                        print(f"  [-] Fine delle pagine per la provincia di {provincia_nome}.")
                        break

            # CHIUSURA DEI LAVORI
            print("\n" + "="*50)
            print("REPORT FINALE AUDIT (SUBITO.IT - 3 PROVINCE)")
            print("="*50)
            print(f"Totale annunci processati e inviati a memoria: {auditor.immobili_analizzati + auditor.immobili_scartati}")
            auditor.salva_database()
            browser.close()
            
    except Exception as e:
        print(f"\n[!] ERRORE DI ESECUZIONE: {str(e)}")

if __name__ == "__main__":
    esegui_scouting_subito()