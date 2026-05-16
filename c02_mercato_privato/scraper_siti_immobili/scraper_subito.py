import time
import re
import os
import pandas as pd
from playwright.sync_api import sync_playwright

# --- CONFIGURAZIONE CHIRURGICA ---
BUDGET_MAX = 130000
DB_PATH = "../database_unico.xlsx"
KEYWORDS_NEGATIVE = ["bar", "negozio", "ufficio", "quota indivisa", "nuda proprieta"]

URLS_TARGET = [
    "https://www.subito.it/annunci-veneto/vendita/appartamenti/verona/?price_end=130000",
    "https://www.subito.it/annunci-lombardia/vendita/immobili/mantova/?price_end=130000",
    "https://www.subito.it/annunci-veneto/vendita/immobili/rovigo/?price_end=130000"
]

MATRICE_DISTANZE = {
    "nogara": 0, "gazzo veronese": 5, "sanguinetto": 7, "villimpenta": 8,
    "salizzole": 9, "sorga": 10, "concamarise": 11, "isola della scala": 12,
    "bovolone": 12, "castel d'ario": 13, "casaleone": 13, "erbe": 14,
    "cerea": 15, "serravalle a po": 16, "trevenzuolo": 16, "ostiglia": 17,
    "sustinente": 17, "roncoferraro": 18, "oppeano": 19
}

def pulisci_prezzo(testo):
    match = re.search(r'[\d\.]+', testo)
    return float(match.group(0).replace(".", "")) if match else 0.0

def pulisci_mq(testo):
    match = re.search(r'(\d+)\s*mq', testo, re.IGNORECASE)
    return int(match.group(1)) if match else 0

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

def analizza_subito():
    with sync_playwright() as p:
        print("--- AVVIO AUTOMAZIONE: SUBITO.IT (MULTI-PROVINCIA) ---")
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()
        
        annunci_salvati = []

        for url_target in URLS_TARGET:
            print(f"\n[*] Navigazione su: {url_target}")
            page.goto(url_target)
            page.wait_for_load_state("networkidle")
            time.sleep(2)
            
            try:
                page.locator("button:has-text('Accetta')").first.click(timeout=3000)
            except:
                pass

            cards = page.locator("div[class*='Container-module_card']")
            count = cards.count()
            print(f"[*] Rilevati {count} potenziali annunci in questa provincia.")

            for i in range(count):
                try:
                    card = cards.nth(i)
                    testo_completo = card.inner_text().lower()
                    
                    if any(x in testo_completo for x in KEYWORDS_NEGATIVE):
                        continue
                    
                    titolo = card.locator("h2[class*='ItemTitle']").inner_text()
                    info_prezzo = card.locator("p[class*='price']").inner_text()
                    
                    prezzo = pulisci_prezzo(info_prezzo)
                    mq = pulisci_mq(testo_completo)
                    
                    if prezzo == 0 or prezzo > BUDGET_MAX:
                        continue
                    
                    comune_trovato = "Sconosciuto"
                    distanza = 999
                    for comune, km in MATRICE_DISTANZE.items():
                        if comune in testo_completo:
                            comune_trovato = comune
                            distanza = km
                            break
                    
                    if distanza > 25:
                        continue
                    
                    dna = f"{int(prezzo)}_{mq}"
                    link = card.locator("a").first.get_attribute("href")
                    
                    annunci_salvati.append({
                        "Sorgente": "SUBITO_PRIVATO",
                        "DNA": dna,
                        "Comune": comune_trovato.capitalize(),
                        "Distanza_Km": distanza,
                        "Prezzo": prezzo,
                        "Superficie_Mq": mq,
                        "Link": link,
                        "Note": titolo
                    })
                    print(f" -> Bersaglio ID [DNA: {dna}] Acquisito a {comune_trovato.capitalize()}")
                    
                except Exception:
                    continue
        
        browser.close()
        if annunci_salvati:
            salva_su_database_unico(annunci_salvati)

if __name__ == "__main__":
    analizza_subito()