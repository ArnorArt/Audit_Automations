# cacciatore_privati.py
import re

# 1. LA MATRICE GEOGRAFICA AGGIORNATA (KM da Nogara 37054)
MATRICE_DISTANZE = {
    "Nogara": 0, "Gazzo Veronese": 5, "Sanguinetto": 7, "Villimpenta": 8,
    "Salizzole": 9, "Sorgà": 10, "Concamarise": 11, "Isola della Scala": 12,
    "Bovolone": 12, "Castel d'Ario": 13, "Casaleone": 13, "Erbè": 14,
    "Cerea": 15, "Serravalle a Po": 16, "Trevenzuolo": 16, "Ostiglia": 17,
    "Sustinente": 17, "Roncoferraro": 18, "San Pietro di Morubio": 20, 
    "Melara": 21, "Buttapietra": 22, "Borgo Mantovano": 23, "Legnago": 24
}

# 2. IL SETACCIO LINGUISTICO
KEYWORDS_POSITIVE = [
    "indipendente", "giardino", "corte esclusiva", "area scoperta", 
    "scoperto esclusivo", "cielo terra", "bifamiliare", "plurifamiliare", 
    "unifamiliare", "villa", "villino", "loghino", "saldo e stralcio",
    "saldo stralcio", "affitto a riscatto", "rent to buy", "riscatto"
    "singola", "schiera", "rustico"
]

KEYWORDS_NEGATIVE = [
    "rudere", "da demolire", "inagibile", "privo di impianti", 
    "completamente da ristrutturare", "nuda proprietà", "bar ", "ristorante",
    "uffici", "negozio", "attività commerciale", "capannone"
    "bar", "ufficio", "quota indivisa", "nuda proprieta",
    "commerciale", "laboratorio", "terreno", "garage", "box"
]

# 3. Per il Ragno (Spider)
KEYWORD_LINK_UTILI = ['immobile', 'vendita', 'dettaglio', 'annuncio', 'appartamento', 'casa', 'residenziale', 'scheda', 'rif', 'affitto a riscatto', 'rent-to-buy', 'rent to buy']
KEYWORD_LINK_SPAZZATURA = ['contatti', 'chi-siamo', 'privacy', 'cookie', 'servizi', 'facebook', 'instagram', 'mailto:', 'tel:', 'agenzia', 'valuta', 'riservata']

# 4. PARAMETRI DI AUDIT FISSI
BUDGET_MAX = 130000
MQ_MIN = 100