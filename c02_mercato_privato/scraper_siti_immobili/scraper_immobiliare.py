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

# L'URL GIGANTE
URL_IMMOBILIARE = (
    "https://www.immobiliare.it/search-list/?idContratto=1&idCategoria=1&prezzoMassimo=130000"
    "&superficieMinima=90&__lang=it&vrt=45.199129%2C10.911345%3B45.18544%2C10.897053%3B45.169386"
    "%2C10.830781%3B45.164974%2C10.833893%3B45.160635%2C10.836845%3B45.154153%2C10.83881%3B"
    "45.149466%2C10.841124%3B45.143592%2C10.846065%3B45.140149%2C10.846672%3B45.132208%2C10.845697"
    "%3B45.119028%2C10.859638%3B45.113083%2C10.880196%3B45.113768%2C10.898872%3B45.083525%2C10.954134"
    "%3B45.069329%2C10.990396%3B45.057589%2C11.027952%3B45.041739%2C11.07912%3B45.056975%2C11.1175"
    "%3B45.065609%2C11.118986%3B45.068469%2C11.124869%3B45.064948%2C11.129646%3B45.060517%2C11.132598"
    "%3B45.058527%2C11.133329%3B45.056207%2C11.13489%3B45.04441%2C11.151832%3B45.044743%2C11.159172"
    "%3B45.045871%2C11.171638%3B45.058138%2C11.193085%3B45.059165%2C11.20578%3B45.058309%2C11.210742"
    "%3B45.044948%2C11.233846%3B45.042452%2C11.239754%3B45.044267%2C11.24808%3B45.05271%2C11.257131"
    "%3B45.055688%2C11.264968%3B45.053902%2C11.26891%3B45.049607%2C11.271142%3B45.045978%2C11.270393"
    "%3B45.042707%2C11.269343%3B45.040659%2C11.268196%3B45.038665%2C11.266896%3B45.031763%2C11.263389"
    "%3B45.025231%2C11.262068%3B45.019192%2C11.263735%3B45.013812%2C11.295497%3B45.009768%2C11.315536"
    "%3B45.012874%2C11.320073%3B45.018064%2C11.324778%3B45.023615%2C11.324094%3B45.027048%2C11.320482"
    "%3B45.042042%2C11.31676%3B45.095757%2C11.311346%3B45.144881%2C11.283942%3B45.174381%2C11.258"
    "%3B45.183113%2C11.241047%3B45.190345%2C11.242852%3B45.19344%2C11.226883%3B45.203129%2C11.216166"
    "%3B45.210286%2C11.198376%3B45.223678%2C11.184554%3B45.254439%2C11.138498%3B45.258984%2C11.140974"
    "%3B45.266205%2C11.135285%3B45.269397%2C11.12304%3B45.253881%2C11.102827%3B45.247566%2C11.082871"
    "%3B45.243381%2C11.079541%3B45.230904%2C11.056273%3B45.236767%2C11.02286%3B45.23389%2C11.006629"
    "%3B45.239551%2C10.98725%3B45.247606%2C10.980125%3B45.245134%2C10.968279%3B45.240712%2C10.962771"
    "%3B45.199129%2C10.911345&pag=1&idTipologia%5B%5D=7&idTipologia%5B%5D=11&idTipologia%5B%5D=12"
    "&idTipologia%5B%5D=13#geohash-u0pb8np8"
)

def esegui_scouting_organico():
    print("--- AVVIO SPECIALISTA: IMMOBILIARE.IT E MEMORIA STORICA (V7 - BYPASS VETRINA) ---")
    auditor = AuditorImmobiliare()
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
            context = browser.new_context(viewport={"width": 1920, "height": 1080})
            page = context.new_page()

            print("[*] Atterraggio iniziale sul target...")
            page.goto(URL_IMMOBILIARE)
            page.wait_for_timeout(3000)

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

                titoli_web = page.locator("a[class*='Title_title']")
                numero_annunci = titoli_web.count()
                
                # BISTURI ANTI-LOOP POTENZIATO: Legge il 5° annuncio per saltare gli sponsorizzati
                indice_impronta = 4 if numero_annunci > 4 else 0
                impronta_corrente = titoli_web.nth(indice_impronta).inner_text() if numero_annunci > 0 else ""
                
                if numero_annunci == 0:
                    print("[-] Nessun annuncio trovato. L'archivio è vuoto o terminato.")
                    break
                    
                print(f"[*] Trovati {numero_annunci} annunci. Inizio Audit e registrazione CSV...")
                
                for i in range(numero_annunci):
                    try:
                        nodo_titolo = titoli_web.nth(i)
                        titolo_testo = nodo_titolo.inner_text()
                        link_relativo = nodo_titolo.get_attribute("href")
                        link_completo = link_relativo if link_relativo.startswith("http") else f"https://www.immobiliare.it{link_relativo}"

                        match_id = re.search(r'/annunci/(\d+)/', link_completo)
                        id_annuncio = match_id.group(1) if match_id else f"ERR-{int(time.time()*1000)}"

                        card = nodo_titolo.locator("xpath=ancestor::li | ancestor::div[contains(@class, 'nd-mediaObject')]").first
                        testo_card_intero = card.inner_text().lower()
                        
                        prezzo_pulito = 0.0
                        match_prezzo = re.search(r'€\s*([\d\.]+)', testo_card_intero)
                        if match_prezzo:
                            prezzo_pulito = float(match_prezzo.group(1).replace('.', ''))
                            
                        mq_puliti = 0
                        match_mq = re.search(r'(\d+)\s*(m²|m2|mq|m\n)', testo_card_intero)
                        if not match_mq:
                            html_card = card.inner_html()
                            match_mq = re.search(r'aria-label="(\d+)\s*m²"', html_card)

                        if match_mq:
                            mq_puliti = int(match_mq.group(1))

                        approvato, motivo = auditor.valuta_annuncio(id_annuncio, link_completo, titolo_testo, testo_card_intero, prezzo_pulito, mq_puliti)
                        
                        if approvato:
                            print(f"✅ {motivo} | {titolo_testo}")
                            print(f"   ID: {id_annuncio} | Prezzo: € {prezzo_pulito} | {mq_puliti} m²")
                            print(f"   {'-'*40}")
                            
                    except Exception as e:
                        continue
                
                pagina_successiva = pagina_corrente + 1
                selettore_link_successivo = f"a[href*='pag={pagina_successiva}']"
                link_successivo_locator = page.locator(selettore_link_successivo).first

                if link_successivo_locator.count() > 0:
                    url_prossima_pagina = link_successivo_locator.get_attribute("href")
                    if not url_prossima_pagina.startswith("http"):
                        url_prossima_pagina = "https://www.immobiliare.it" + url_prossima_pagina
                        
                    page.goto(url_prossima_pagina)
                    page.wait_for_timeout(3500) 
                    
                    # Rilevamento loop aggiornato per la nuova pagina
                    nuova_impronta = page.locator("a[class*='Title_title']").nth(indice_impronta).inner_text() if page.locator("a[class*='Title_title']").count() > indice_impronta else ""
                    
                    if impronta_corrente == nuova_impronta:
                        print("  [X] Rilevato blocco pagina del server (Loop sull'impronta). Fine ricerca.")
                        break
                        
                    pagina_corrente += 1
                else:
                    print("\n[-] Nessun collegamento alla pagina successiva trovato. Ricerca completata.")
                    break

            print("\n" + "="*50)
            print("REPORT FINALE AUDIT (IMMOBILIARE.IT)")
            print("="*50)
            print(f"Totale annunci analizzati (anche i vecchi nel DB): {auditor.immobili_analizzati + auditor.immobili_scartati}")
            print(f"Totale approvati (o ribassati): {auditor.immobili_analizzati}")
            
            auditor.salva_database()
            browser.close()
            
    except Exception as e:
        print(f"\n[!] ERRORE DI ESECUZIONE: {str(e)}")

if __name__ == "__main__":
    esegui_scouting_organico()