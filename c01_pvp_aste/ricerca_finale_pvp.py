import time
import re
import os
import pandas as pd
from playwright.sync_api import sync_playwright
from cacciatore_aste import MATRICE_DISTANZE, KEYWORDS_POSITIVE

TRIBUNALI = ["Verona", "Mantova", "Rovigo"]
BUDGET_MAX = 130000
ANNO_TARGET = "2025"
DB_PATH = "../database_unico.xlsx"

def salva_su_database_unico(nuovi_annunci):
    df_nuovi = pd.DataFrame(nuovi_annunci)
    if os.path.exists(DB_PATH):
        df_esistente = pd.read_excel(DB_PATH)
        df_combinato = pd.concat([df_esistente, df_nuovi], ignore_index=True)
        df_final = df_combinato.drop_duplicates(subset=["DNA"], keep="first")
    else:
        df_final = df_nuovi
    df_final.to_excel(DB_PATH, index=False)
    print(f"\n[v] Database Unificato aggiornato. Record totali: {len(df_final)}")

def esegui_caccia_professionale():
    risultati_finali = []

    with sync_playwright() as p:
        print("--- AVVIO SISTEMA DI AUDIT AUTOMATICO (ASTE PVP) ---")
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        for tribunale in TRIBUNALI:
            print(f"\n{'-'*50}\n> Analisi Target: Tribunale di {tribunale}\n{'-'*50}")
            page.goto("https://pvp.giustizia.it/pvp/")
            page.wait_for_load_state("networkidle")
            
            page.locator("text='Affina la ricerca'").click()
            time.sleep(2)
            
            page.locator("text='Categoria'").first.click(force=True)
            page.keyboard.type("Residenziale", delay=200)
            time.sleep(1)
            page.keyboard.press("ArrowDown")
            time.sleep(0.5)
            page.keyboard.press("Enter")
            
            page.get_by_placeholder("Anno procedura", exact=True).fill(ANNO_TARGET)
            time.sleep(0.5)
            page.get_by_placeholder("a", exact=True).fill(str(BUDGET_MAX))
            time.sleep(0.5)
            
            campo_tribunale = page.locator("text='Seleziona Tribunale'").first
            campo_tribunale.click(force=True)
            page.keyboard.type(tribunale, delay=200)
            time.sleep(1.5)
            page.locator(f"text='Tribunale di {tribunale.upper()}'").first.click(force=True)
            time.sleep(1)
            
            page.locator("button:has-text('Cerca')").last.click()
            page.wait_for_timeout(4000)
            
            pagina_corrente = 1
            
            while True:
                print(f"  [Scansione Pagina {pagina_corrente}] Attendere...")
                page.wait_for_timeout(3000)
                annunci = page.locator("app-annuncio-card")
                numero_annunci = annunci.count()
                
                impronta_corrente = annunci.first.inner_text() if numero_annunci > 0 else ""
                
                for i in range(numero_annunci):
                    try:
                        annuncio = annunci.nth(i)
                        testo_intero = annuncio.inner_text()
                        testo_low = testo_intero.lower()
                        righe = testo_intero.split('\n')
                        
                        prezzo_asta = 0.0
                        try:
                            testo_prezzo = annuncio.locator(".gui-card-price").inner_text()
                            match = re.search(r'[\d\.,]+', testo_prezzo.split("€")[-1] if "€" in testo_prezzo else testo_prezzo)
                            if match:
                                p_str = match.group(0) 
                                p_pulito = p_str.replace(".", "").replace(",", ".")
                                prezzo_asta = float(p_pulito)
                        except Exception:
                            pass 

                        data_asta = "Data N.D."
                        for riga in righe:
                            if "/" in riga and ":" in riga: 
                                data_asta = riga.strip()
                                break

                        distanza = 999
                        paese_trovato = "Sconosciuto"
                        for paese, km in MATRICE_DISTANZE.items():
                            if paese.lower() in testo_low:
                                distanza = km
                                paese_trovato = paese
                                break
                        
                        if distanza > 30:
                            continue

                        is_indipendente = any(parola in testo_low for parola in KEYWORDS_POSITIVE)

                        if is_indipendente:
                            url_parziale = annuncio.locator("a").first.get_attribute("href")
                            link_completo = url_parziale if url_parziale.startswith("http") else f"https://pvp.giustizia.it{url_parziale}"
                            
                            dna = f"{int(prezzo_asta)}_0"
                            descrizione = testo_intero.replace('\n', ' ')[:100] + "..."
                            print(f"    [!] TARGET: {paese_trovato} ({distanza}km) | {prezzo_asta}€ | {data_asta}")
                            
                            risultati_finali.append({
                                "Sorgente": "ASTA_PVP",
                                "DNA": dna,
                                "Comune": paese_trovato.capitalize(),
                                "Distanza_Km": distanza,
                                "Prezzo": prezzo_asta,
                                "Superficie_Mq": 0,
                                "Link": link_completo,
                                "Note": descrizione
                            })
                    except Exception:
                        continue

                bottone_succ = page.locator("text='Successiva'").last
                if bottone_succ.is_visible():
                    is_disabled = bottone_succ.evaluate("el => el.classList.contains('disabled') || el.parentElement.classList.contains('disabled')")
                    if is_disabled: 
                        break
                    
                    bottone_succ.evaluate("el => el.click()")
                    pagina_corrente += 1
                    page.wait_for_timeout(4000)
                    
                    nuova_impronta = page.locator("app-annuncio-card").first.inner_text() if page.locator("app-annuncio-card").count() > 0 else ""
                    if impronta_corrente == nuova_impronta:
                        break
                else:
                    break

        browser.close()

    if risultati_finali:
        salva_su_database_unico(risultati_finali)
    else:
        print("\n[!] Nessun immobile residenziale trovato sotto i target.")

if __name__ == "__main__":
    esegui_caccia_professionale()