import csv
import logging
from pathlib import Path

# Configurazione logging per monitoraggio chirurgico delle operazioni
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [%(module)s] %(message)s'
)

def leggi_elenco_certo(percorso_file: str) -> list[dict]:
    """
    Legge il file CSV dell'Elenco Certo e filtra solo le agenzie attive.
    Restituisce una lista di dizionari con i parametri di scraping.
    """
    agenzie_valide = []
    file_path = Path(percorso_file)

    if not file_path.exists():
        logging.error(f"File non trovato: {percorso_file}. Creare il file CSV prima di procedere.")
        return agenzie_valide

    try:
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                # Ignora le righe dove il flag 'attivo' è 0
                if row.get('attivo', '1') == '1':
                    agenzie_valide.append(row)
        
        logging.info(f"Caricate {len(agenzie_valide)} agenzie attive dall'Elenco Certo.")
    except Exception as e:
        logging.error(f"Errore durante la lettura del file CSV: {e}")

    return agenzie_valide


def main():
    # File di input
    file_elenco = "elenco_agenzie.csv"

    # 1. Estrazione dati di partenza
    lista_agenzie = leggi_elenco_certo(file_elenco)

    if not lista_agenzie:
        logging.warning("Elenco vuoto o file mancante. Interruzione script.")
        return

    # 2. Ciclo di elaborazione base (Struttura per step futuri)
    for agenzia in lista_agenzie:
        nome = agenzia.get('nome_agenzia', 'Sconosciuta')
        url = agenzia.get('url_base', '')
        
        logging.info(f"> Inizio scansione: {nome} | URL: {url}")

        # [TODO] Blocco 1: Richiesta HTTP con gestione timeout e regola "Semaforo Rosso" (Max 2 errori).
        # [TODO] Blocco 2: Parsing HTML ed estrazione dati generali.
        # [TODO] Blocco 3: Filtro specifico / ricerca integrata per la keyword "riscatto".
        # [TODO] Blocco 4: Generazione hash 'DNA' per ogni annuncio e salvataggio in database_unico.xlsx.

if __name__ == "__main__":
    main()