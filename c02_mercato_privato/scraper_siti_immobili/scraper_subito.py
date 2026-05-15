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

# L'URL DI SUBITO.IT (Verona, Max 130k, Min 100mq)
URL_SUBITO = "https://www.subito.it/annunci-veneto/vendita/immobili/verona/?pe=130000&szs=100"

def esegui_scouting_subito():
    print("--- AVVIO SPECIALISTA: SUBITO.IT (V1 - DNA IMMOBILE) ---")
    auditor = AuditorImmobiliare()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            print("[*] Atterraggio iniziale sul target...")
            page.goto(URL_SUBITO)
            page.wait_for_timeout(3000)

            # CHIUSURA BANNER COOKIE SUBITO.IT
            try:
                bottone_cookie = page.locator("button:has-text('Accetta'), button:has-text('Accetto')").first
                if bottone_cookie.is_visible(timeout=2000):
                    bottone_cookie.click()
            except:
                pass

            pagina_corrente = 1

            while True:
                print(f"\n[>] Analisi Pagina {pagina_corrente} in corso...")
                page.wait_for_timeout(2500) 

                # Il locator basato sulla tua analisi HTML (L'ancora principale)
                annunci_web = page.locator("a[class*='index-module_link']")
                numero_annunci = annunci_web.count()
                
                indice_impronta = 2 if numero_annunci > 2 else 0
                impronta_corrente = annunci_web.nth(indice_impronta).inner_text() if numero_annunci > 0 else ""
                
                if numero_annunci == 0:
                    print("[-] Nessun annuncio trovato. L'archivio è vuoto o terminato.")
                    break
                    
                print(f"[*] Trovati {numero_annunci} annunci. Inizio Audit e generazione DNA...")
                
                for i in range(numero_annunci):
                    try:
                        nodo = annunci_web.nth(i)
                        link_completo = nodo.get_attribute("href")
                        
                        # Sicurezza Link
                        if not link_completo.startswith("http"):
                            link_completo = "https://www.subito.it" + link_completo

                        testo_card_intero = nodo.inner_text().lower()
                        
                        # Estrazione Titolo (Subito lo mette comodamente nell'aria-label del link!)
                        titolo_testo = nodo.get_attribute("aria-label")
                        if not titolo_testo:
                            titolo_testo = "Immobile Subito.it"

                        # ESTRAZIONE PREZZO (Subito usa il formato "120.000 €")
                        prezzo_pulito = 0.0
                        match_prezzo = re.search(r'([\d\.]+)\s*€', testo_card_intero)
                        if match_prezzo:
                            prezzo_pulito = float(match_prezzo.group(1).replace('.', ''))
                            
                        # ESTRAZIONE MQ (Subito usa il formato "170 mq")
                        mq_puliti = 0
                        match_mq = re.search(r'(\d+)\s*mq', testo_card_intero)
                        if match_mq:
                            mq_puliti = int(match_mq.group(1))

                        # --- LA MAGIA: IL DNA DELL'IMMOBILE ---
                        # Invece di un ID casuale, creiamo il codice fiscale della casa
                        id_annuncio = f"{int(prezzo_pulito)}_{mq_puliti}"

                        approvato, motivo = auditor.valuta_annuncio(id_annuncio, link_completo, titolo_testo, testo_card_intero, prezzo_pulito, mq_puliti)
                        
                        if approvato:
                            print(f"✅ {motivo} | {titolo_testo}")
                            print(f"   DNA: {id_annuncio} | Prezzo: € {prezzo_pulito} | {mq_puliti} m²")
                            print(f"   {'-'*40}")
                            
                    except Exception as e:
                        continue
                
                # --- IL SALTO PAGINA SU SUBITO.IT ---
                # Subito usa bottoni con la scritta "Successiva" o la freccia
                bottone_avanti = page.locator("button:has-text('Successiva'), a:has-text('Successiva'), a[aria-label*='successiva'], button[aria-label*='successiva']").first

                if bottone_avanti.is_visible():
                    bottone_avanti.click()
                    page.wait_for_timeout(3500) 
                    
                    nuova_impronta = page.locator("a[class*='index-module_link']").nth(indice_impronta).inner_text() if page.locator("a[class*='index-module_link']").count() > indice_impronta else ""
                    
                    if impronta_corrente == nuova_impronta:
                        print("  [X] Rilevato blocco pagina del server (Loop sull'impronta). Fine ricerca.")
                        break
                        
                    pagina_corrente += 1
                else:
                    print("\n[-] Nessun bottone 'Successiva' trovato. Ricerca completata.")
                    break

            # SALVATAGGIO
            print("\n" + "="*50)
            print("REPORT FINALE AUDIT (SUBITO.IT)")
            print("="*50)
            print(f"Totale annunci analizzati (anche i vecchi nel DB): {auditor.immobili_analizzati + auditor.immobili_scartati}")
            auditor.salva_database()
            browser.close()
            
    except Exception as e:
        print(f"\n[!] ERRORE DI ESECUZIONE: {str(e)}")

if __name__ == "__main__":
    esegui_scouting_subito()