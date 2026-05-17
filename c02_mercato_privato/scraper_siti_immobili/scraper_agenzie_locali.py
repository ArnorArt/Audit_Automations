import sys
import os
import re
import csv
import time
import logging
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

# --- IL PONTE PER PYTHON ---
cartella_corrente = os.path.dirname(os.path.abspath(__file__))
cartella_superiore = os.path.dirname(cartella_corrente)
sys.path.append(cartella_superiore)

# Importiamo il Cervello e le nuove regole dal Manuale
try:
    from auditor_valutatore import AuditorImmobiliare
    from cacciatore_privati import KEYWORD_LINK_UTILI, KEYWORD_LINK_SPAZZATURA
except ImportError as e:
    logging.error(f"ATTENZIONE: Moduli base non trovati. Dettaglio: {e}")
    sys.exit()

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

PORTALI_VIETATI = ['idealista', 'casa.it', 'immobiliare.it', 'trovacasa.it']
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
}

def leggi_elenco_certo(percorso_file: str) -> list:
    agenzie_valide = []
    if not os.path.exists(percorso_file):
        logging.error(f"File CSV non trovato: {percorso_file}")
        return agenzie_valide

    try:
        with open(percorso_file, mode='r', encoding='utf-8-sig') as file:
            reader = csv.DictReader(file, delimiter=';')
            for row in reader:
                nome = row.get('Agenzia', '').strip()
                url = row.get('Link', '').strip()
                if not url or any(vietato in url.lower() for vietato in PORTALI_VIETATI):
                    continue
                agenzie_valide.append({'nome': nome, 'url': url})
    except Exception as e:
        logging.error(f"Errore lettura CSV: {e}")
    return agenzie_valide

def estrai_link_potenziali(html_pagina: str, url_base: str) -> list:
    """Il Ragno: Trova i link alle schede immobile usando le regole del Cacciatore."""
    soup = BeautifulSoup(html_pagina, 'html.parser')
    link_trovati = set()
    dominio_base = urlparse(url_base).netloc

    for tag_a in soup.find_all('a', href=True):
        href = tag_a['href'].lower()
        url_completo = urljoin(url_base, href)

        if dominio_base in url_completo:
            if not any(bad in href for bad in KEYWORD_LINK_SPAZZATURA):
                if any(good in href for good in KEYWORD_LINK_UTILI) or re.search(r'\d{3,}', href):
                    link_trovati.add(url_completo)

    return list(link_trovati)[:10]

def analizza_scheda_immobile(html_scheda: str, url_scheda: str, nome_agenzia: str, auditor):
    """Il Bisturi Regex: Estrae Prezzo e MQ e invia all'Auditor."""
    soup = BeautifulSoup(html_scheda, 'html.parser')
    testo_grezzo = soup.get_text(separator=' ', strip=True).lower()
    titolo_pagina = soup.title.string.strip() if soup.title and soup.title.string else f"Annuncio {nome_agenzia}"
    
    match_prezzo = re.search(r'(?:€|euro)\s*([\d\.]+)', testo_grezzo)
    prezzo_estratto = 0.0
    if match_prezzo:
        try:
            prezzo_estratto = float(match_prezzo.group(1).replace('.', ''))
        except ValueError:
            pass

    match_mq = re.search(r'([\d\.]+)\s*(?:mq|m2|metri\s*quadri)', testo_grezzo)
    mq_estratti = 0
    if match_mq:
        try:
            mq_estratti = int(float(match_mq.group(1).replace('.', '')))
        except ValueError:
            pass

    if prezzo_estratto <= 0:
        logging.info(f"  [!] SCARTATO (Nessun prezzo dalla Regex) -> {url_scheda}")
        return False

    esito, messaggio = auditor.valuta_annuncio(
        sorgente=nome_agenzia,
        link=url_scheda,
        titolo=titolo_pagina,
        descrizione=testo_grezzo,
        prezzo=prezzo_estratto,
        metri_quadri=mq_estratti
    )
    
    if esito:
        logging.info(f"  ✅ [BERSAGLIO APPROVATO] {messaggio}")
        logging.info(f"     -> {url_scheda}")
    else:
        logging.info(f"  ❌ [SCARTATO] {messaggio} -> {url_scheda}")
        
    return esito

def main():
    logging.info("--- AVVIO SCRAPER AGENZIE LOCALI (FASE DI CACCIA) ---")
    auditor = AuditorImmobiliare()
    percorso_csv = os.path.join(cartella_superiore, "elenco_agenzie.csv")
    lista_agenzie = leggi_elenco_certo(percorso_csv)

    for agenzia in lista_agenzie:
        nome = agenzia['nome']
        url = agenzia['url']
        logging.info(f"\n> Agenzia: {nome}")
        
        try:
            response = requests.get(url, headers=HEADERS, timeout=15)
            if response.status_code == 200:
                link_da_visitare = estrai_link_potenziali(response.text, url)
                logging.info(f"  Trovati {len(link_da_visitare)} link potenziali. Inizio ispezione schede...")
                
                for link_scheda in link_da_visitare:
                    try:
                        time.sleep(1)
                        resp_scheda = requests.get(link_scheda, headers=HEADERS, timeout=10)
                        if resp_scheda.status_code == 200:
                            analizza_scheda_immobile(resp_scheda.text, link_scheda, nome, auditor)
                    except Exception:
                        pass
                        
            else:
                logging.warning(f"  [!] Rifiuto connessione (Codice {response.status_code})")
        except requests.exceptions.RequestException:
             logging.error(f"  [!] Sito irraggiungibile.")

    auditor.salva_database()

if __name__ == "__main__":
    main()