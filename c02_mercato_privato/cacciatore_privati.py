# cacciatore_privati.py
# Modulo Dati: Parametri di Audit per il Mercato Privato

# 1. PARAMETRI FINANZIARI E DIMENSIONALI
BUDGET_MAX = 130000
MQ_MIN = 100

# 2. LA MATRICE GEOGRAFICA (Max 25 min da Nogara 37054)
MATRICE_DISTANZE = {
    "Nogara": 0, "Gazzo Veronese": 5, "Sanguinetto": 7, "Villimpenta": 8,
    "Salizzole": 9, "Sorgà": 10, "Concamarise": 11, "Isola della Scala": 12,
    "Bovolone": 12, "Castel d'Ario": 13, "Casaleone": 13, "Erbè": 14,
    "Cerea": 15, "Serravalle a Po": 16, "Trevenzuolo": 16, "Ostiglia": 17,
    "Sustinente": 17, "Roncoferraro": 18, "Oppeano": 19, "Palù": 19,
    "San Pietro di Morubio": 20, "Melara": 21, "Vigasio": 22, 
    "Isola Rizza": 22, "Buttapietra": 22, "Borgo Mantovano": 23,
    "Legnago": 24, "Roverchiara": 24, "Nogarole Rocca": 24
}

# 3. IL SETACCIO LINGUISTICO (Filtri Testuali)
KEYWORDS_POSITIVE = [
    "indipendente", "giardino", "corte esclusiva", "area scoperta", 
    "scoperto esclusivo", "cielo terra", "bifamiliare", "plirifamiliare", "unifamiliare", 
    "villa", "villino", "loghino", "saldo e stralcio", "affitto a riscatto", 
    "rent to buy", "rent-to-buy"
]

# 4. FILTRO ANTI-RUDERE E TITOLO NON PIENO
KEYWORDS_NEGATIVE = [
    "rudere", "da demolire", "inagibile", "privo di impianti", 
    "completamente da ristrutturare", "nuda proprietà"
]