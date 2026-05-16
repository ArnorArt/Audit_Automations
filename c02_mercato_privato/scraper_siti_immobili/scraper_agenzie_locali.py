import re
import logging
from bs4 import BeautifulSoup
import requests

# Assumiamo che il file del tuo cervello si chiami 'auditor_valuatore.py'
# e si trovi nella stessa cartella (o in una accessibile dal path).
try:
    from auditor_valuatore import AuditorImmobiliare
except ImportError:
    logging.error("ATTENZIONE: File 'auditor_valuatore.py' non trovato. Assicurati che il nome sia corretto.")

# Configurazione chirurgica del logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

def analizza_scheda_immobile(html_scheda: str, url_scheda: str, nome_agenzia: str, auditor):
    """
    Estrae i testi, usa le Regex per isolare i numeri (Prezzo, Mq) 
    e innesca la validazione dell'Auditor.
    """
    soup = BeautifulSoup(html_scheda, 'html.parser')
    
    # 1. Estrazione brutale di tutto il testo visibile e conversione in minuscolo
    testo_grezzo = soup.get_text(separator=' ', strip=True).lower()
    titolo_pagina = soup.title.string.strip() if soup.title and soup.title.string else f"Annuncio {nome_agenzia}"
    
    # 2. Regex per il PREZZO (intercetta € 120.000, 120000 euro, ecc.)
    match_prezzo = re.search(r'(?:€|euro)\s*([\d\.]+)', testo_grezzo)
    prezzo_estratto = 0.0
    if match_prezzo:
        try:
            prezzo_pulito = match_prezzo.group(1).replace('.', '')
            prezzo_estratto = float(prezzo_pulito)
        except ValueError:
            pass

    # 3. Regex per i METRI QUADRI (intercetta 120 mq, 120 m2, ecc.)
    match_mq = re.search(r'([\d\.]+)\s*(?:mq|m2|metri\s*quadri)', testo_grezzo)
    mq_estratti = 0
    if match_mq:
        try:
            mq_pulito = match_mq.group(1).replace('.', '')
            mq_estratti = int(float(mq_pulito))
        except ValueError:
            pass

    # Se non trova il prezzo, scarta a priori per non far impazzire l'Auditor
    if prezzo_estratto <= 0:
         logging.debug(f"[SCARTATO - MANCA PREZZO] {url_scheda}")
         return False

    # 4. Passaggio dati al Cervello Centrale
    esito, messaggio = auditor.valuta_annuncio(
        sorgente=nome_agenzia,
        link=url_scheda,
        titolo=titolo_pagina,
        descrizione=testo_grezzo,
        prezzo=prezzo_estratto,
        metri_quadri=mq_estratti
    )
    
    if esito:
        logging.info(f"✅ [BERSAGLIO APPROVATO] {messaggio} -> {url_scheda}")
    else:
        logging.info(f"❌ [SCARTATO DALL'AUDITOR] {messaggio} -> {url_scheda}")
        
    return esito

def main():
    logging.info("Avvio Scraper Agenzie Locali...")
    
    # Inizializziamo il Cervello
    try:
        auditor = AuditorImmobiliare()
    except NameError:
        logging.error("Interruzione: AuditorImmobiliare non caricato.")
        return

    # [QUI IN FUTURO ANDRÀ IL CICLO CHE LEGGE IL CSV E FA LE RICHIESTE HTTP]
    
    # TEST: Simuliamo una pagina web letta per verificare che l'integrazione funzioni
    html_finto = """
    <html>
        <head><title>Trilocale a Sanguinetto</title></head>
        <body>
            Bellissimo appartamento indipendente in vendita a Sanguinetto.
            Il prezzo richiesto è di € 105.000. 
            La superficie commerciale è di 110 mq. Dispone di giardino privato e formula rent to buy.
        </body>
    </html>
    """
    
    logging.info("Esecuzione Test a secco con pagina HTML simulata...")
    analizza_scheda_immobile(
        html_scheda=html_finto, 
        url_scheda="http://www.agenziatest.it/immobile-1", 
        nome_agenzia="Agenzia Test", 
        auditor=auditor
    )
    
    # Salvataggio finale del database
    auditor.salva_database()

if __name__ == "__main__":
    main()