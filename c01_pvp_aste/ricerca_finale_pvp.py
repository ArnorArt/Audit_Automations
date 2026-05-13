from playwright.sync_api import sync_playwright
import time
import re  # IL NUOVO BISTURI
from cacciatore_aste import MATRICE_DISTANZE, KEYWORDS_POSITIVE

TRIBUNALI = ["Verona", "Mantova", "Rovigo"]
BUDGET_MAX = 130000
ANNO_TARGET = "2025"

def esegui_caccia_professionale():
    risultati_finali = []

    with sync_playwright() as p:
        print("--- AVVIO SISTEMA DI AUDIT AUTOMATICO (V 3.3 CHIRURGICA) ---")
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        for tribunale in TRIBUNALI:
            print(f"\n{'-'*50}\n> Analisi Target: Tribunale di {tribunale}\n{'-'*50}")
            page.goto("https://pvp.giustizia.it/pvp/")
            page.wait_for_load_state("networkidle")
            
            # --- FILTRI DI INPUT ---
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
            
            # --- PAGINAZIONE E AUDIT ---
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
                        
                        # 1. ESTRAZIONE PREZZO (Metodo Regex Infallibile)
                        prezzo_asta = 0.0
                        try:
                            # Miriamo al contenitore esatto del prezzo
                            testo_prezzo = annuncio.locator(".gui-card-price").inner_text()
                            # Tagliamo via "Prezzo base d'asta" e teniamo i numeri
                            match = re.search(r'[\d\.,]+', testo_prezzo.split("€")[-1] if "€" in testo_prezzo else testo_prezzo)
                            if match:
                                p_str = match.group(0) # Es. "130.000,00"
                                # Convertiamo per Python
                                p_pulito = p_str.replace(".", "").replace(",", ".")
                                prezzo_asta = float(p_pulito)
                        except Exception:
                            pass # Se la card è difettosa, salta silenziosamente

                        # 2. ESTRAZIONE DATA
                        data_asta = "Data N.D."
                        for riga in righe:
                            if "/" in riga and ":" in riga: 
                                data_asta = riga.strip()
                                break

                        # 3. GEOMAPPATURA
                        distanza = 999
                        paese_trovato = "Sconosciuto"
                        for paese, km in MATRICE_DISTANZE.items():
                            if paese.lower() in testo_low:
                                distanza = km
                                paese_trovato = paese
                                break
                        
                        if distanza > 30:
                            continue

                        # 4. VERIFICA TIPOLOGIA E STAMPA
                        is_indipendente = any(parola in testo_low for parola in KEYWORDS_POSITIVE)

                        if is_indipendente:
                            url_parziale = annuncio.locator("a").first.get_attribute("href")
                            # Controllo doppio HTTP
                            if url_parziale.startswith("http"):
                                link_completo = url_parziale
                            else:
                                link_completo = f"https://pvp.giustizia.it{url_parziale}"
                            
                            print(f"    [!] TARGET: {paese_trovato} ({distanza}km) | {prezzo_asta}€ | {data_asta}")
                            
                            risultati_finali.append({
                                "paese": paese_trovato,
                                "data": data_asta,
                                "asta": prezzo_asta,
                                "km": distanza,
                                "link": link_completo,
                                "desc": testo_intero.replace('\n', ' ')[:100] + "..."
                            })
                    except Exception:
                        continue

                # --- CONTROLLO SUCCESSIVA E ANTI-LOOP ---
                bottone_succ = page.locator("text='Successiva'").last
                if bottone_succ.is_visible():
                    is_disabled = bottone_succ.evaluate("el => el.classList.contains('disabled') || el.parentElement.classList.contains('disabled')")
                    if is_disabled: 
                        print("  - Archivio terminato per questo tribunale.")
                        break
                    
                    bottone_succ.evaluate("el => el.click()")
                    pagina_corrente += 1
                    page.wait_for_timeout(4000)
                    
                    nuova_impronta = page.locator("app-annuncio-card").first.inner_text() if page.locator("app-annuncio-card").count() > 0 else ""
                    if impronta_corrente == nuova_impronta:
                        print("  [X] Rilevato blocco pagina del server (Loop). Passo al tribunale successivo.")
                        break
                else:
                    break

        browser.close()

    # --- REPORT FINALE ---
    if not risultati_finali:
        print("\n[!] Nessun immobile residenziale indipendente trovato sotto i 130k.")
        return

    print("\n" + "="*85)
    print(f"REPORT FINALE AUDIT - OBIETTIVI {ANNO_TARGET} (TARGET: INDIPENDENTI < {BUDGET_MAX}€)")
    print("="*85)
    
    # Pulizia finalissima dei duplicati basata sul link unico
    report_pulito = {r['link']: r for r in risultati_finali}.values()
    report_ordinato = sorted(report_pulito, key=lambda x: (x['km'], x['asta']))
    
    for r in report_ordinato:
        print(f"[{r['paese']} - {r['km']} km] Prezzo: {r['asta']}€ | Data Asta: {r['data']}")
        print(f"Dettaglio: {r['desc']}")
        print(f"LINK: {r['link']}\n")

if __name__ == "__main__":
    esegui_caccia_professionale()