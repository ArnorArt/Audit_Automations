# auditor_valutatore.py
from cacciatore_privati import BUDGET_MAX, MQ_MIN, KEYWORDS_POSITIVE, KEYWORDS_NEGATIVE

class AuditorImmobiliare:
    def __init__(self):
        # Qui in futuro collegheremo il nostro file Excel (La Memoria/Blacklist)
        self.immobili_analizzati = 0
        self.immobili_scartati = 0

    def valuta_annuncio(self, titolo, descrizione, prezzo, metri_quadri):
        """Passa l'annuncio ai Raggi X. Se fallisce un parametro, viene scartato subito."""
        testo_completo = (titolo + " " + descrizione).lower()

        # 1. Filtro Finanziario e Dimensionale
        if prezzo > BUDGET_MAX:
            self.immobili_scartati += 1
            return False, f"Scartato: Prezzo ({prezzo}€) oltre limite."
        
        if metri_quadri > 0 and metri_quadri < MQ_MIN:
            self.immobili_scartati += 1
            return False, f"Scartato: Troppo piccolo ({metri_quadri} mq)."

        # 2. Filtro Anti-Rudere (La Blacklist Linguistica)
        for parola in KEYWORDS_NEGATIVE:
            if parola in testo_completo:
                self.immobili_scartati += 1
                return False, f"Scartato: Trovata parola chiave negativa '{parola}'."

        # 3. Filtro Tipologia (Deve avere almeno un match positivo)
        ha_requisiti = any(parola in testo_completo for parola in KEYWORDS_POSITIVE)
        if not ha_requisiti:
            self.immobili_scartati += 1
            return False, "Scartato: Non è indipendente/villino/loghino."

        # Se sopravvive a tutto:
        self.immobili_analizzati += 1
        return True, "APPROVATO: Pronto per la Vetrina."