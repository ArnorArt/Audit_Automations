import pandas as pd

# 1. LA MATRICE GEOGRAFICA AGGIORNATA (KM da Nogara 37054)
MATRICE_DISTANZE = {
    "Nogara": 0,
    "Gazzo Veronese": 5,
    "Sanguinetto": 7,
    "Villimpenta": 8,
    "Salizzole": 9,
    "Sorgà": 10,
    "Concamarise": 11,
    "Isola della Scala": 12,
    "Bovolone": 12,
    "Castel d'Ario": 13,
    "Casaleone": 13,
    "Erbè": 14,
    "Cerea": 15,
    "Serravalle a Po": 16,
    "Trevenzuolo": 16,
    "Ostiglia": 17,
    "Sustinente": 17,
    "Roncoferraro": 18,
    "Oppeano": 19,
    "Palù": 19,
    "San Pietro di Morubio": 20,
    "Melara": 21,
    "Vigasio": 22,
    "Isola Rizza": 22,
    "Buttapietra": 22,
    "Borgo Mantovano": 23,
    "Legnago": 24,
    "Roverchiara": 24,
    "Nogarole Rocca": 24
}

# 2. IL SETACCIO LINGUISTICO
# Parole che devono essere presenti nella descrizione per identificare una casa indipendente
KEYWORDS_POSITIVE = [
    "indipendente", "giardino", "corte esclusiva", 
    "area scoperta", "scoperto esclusivo", "cielo terra", 
    "bifamiliare", "unifamiliare", "villa", "villino", "loghino"
]

# 3. PARAMETRI DI AUDIT
BUDGET_MAX = 130000
TRIBUNALI = ["Verona", "Mantova", "Rovigo"]

def analizza_descrizione(testo):
    """
    Usa la logica booleana per vedere se la descrizione 
    corrisponde ai criteri di 'Casa Indipendente'.
    """
    testo_low = testo.lower()
    # Verifichiamo se almeno una delle parole chiave è presente
    riscontro = any(parola in testo_low for parola in KEYWORDS_POSITIVE)
    return riscontro

def calcola_convenienza(prezzo_perizia, prezzo_asta):
    """
    Calcola il Delta percentuale tra perizia e asta.
    """
    if prezzo_perizia <= 0: return 0
    sconto = ((prezzo_perizia - prezzo_asta) / prezzo_perizia) * 100
    return round(sconto, 2)

# TEST LOGICO
if __name__ == "__main__":
    print("--- TEST MATRICE DI INTELLIGENCE ---")
    
    # Simuliamo un dato estratto dal PVP
    test_annuncio = {
        "paese": "Gazzo Veronese",
        "descrizione": "Abitazione indipendente con ampio giardino e garage.",
        "perizia": 150000,
        "offerta_minima": 95000
    }
    
    # Esecuzione controlli
    esito_filtro = analizza_descrizione(test_annuncio["descrizione"])
    sconto = calcola_convenienza(test_annuncio["perizia"], test_annuncio["offerta_minima"])
    minuti = MATRICE_DISTANZE.get(test_annuncio["paese"], 999) # 999 se non in lista
    
    print(f"Paese: {test_annuncio['paese']} ({minuti} min da Nogara)")
    print(f"Sconto su perizia: {sconto}%")
    print(f"Corrisponde ai criteri: {'SI' if esito_filtro else 'NO'}")