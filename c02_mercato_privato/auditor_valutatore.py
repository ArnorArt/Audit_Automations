import os
import re
import pandas as pd
from datetime import datetime
from cacciatore_privati import BUDGET_MAX, MQ_MIN, KEYWORDS_POSITIVE, KEYWORDS_NEGATIVE, MATRICE_DISTANZE

class AuditorImmobiliare:
    def __init__(self):
        self.immobili_analizzati = 0
        self.immobili_scartati = 0
        
        cartella_corrente = os.path.dirname(os.path.abspath(__file__))
        cartella_madre = os.path.dirname(cartella_corrente)
        self.percorso_db = os.path.join(cartella_madre, "database_unico_scraper.xlsx")
        
        self._carica_database()

    def _carica_database(self):
        if os.path.exists(self.percorso_db):
            self.df_memoria = pd.read_excel(self.percorso_db)
            
            colonne_audit = ["Data_Scoperta", "Stato_Umano", "Note_Lavori"]
            for col in colonne_audit:
                if col not in self.df_memoria.columns:
                    self.df_memoria[col] = ""
        else:
            colonne = ["Sorgente", "DNA", "Comune", "Distanza_Km", "Prezzo", "Superficie_Mq", "Link", "Note", "Data_Scoperta", "Stato_Umano", "Note_Lavori"]
            self.df_memoria = pd.DataFrame(columns=colonne)

    def salva_database(self):
        self.df_memoria.to_excel(self.percorso_db, index=False)
        print("  [v] Database Unificato (Audit) aggiornato e salvato.")

    def valuta_annuncio(self, sorgente, link, titolo, descrizione, prezzo, metri_quadri):
        testo_completo = (titolo + " " + descrizione).lower()
        oggi = datetime.now()

        # ---------------------------------------------------------
        # 1. CONTROLLO DISTANZA (Spostato in alto per il nuovo DNA)
        # ---------------------------------------------------------
        minuti_distanza = 999
        comune_trovato = "Sconosciuto"
        
        for comune, dist in MATRICE_DISTANZE.items():
            if re.search(r'\b' + re.escape(comune.lower()) + r'\b', testo_completo):
                minuti_distanza = dist
                comune_trovato = comune
                break
                 
        if minuti_distanza > 25:
            self.immobili_scartati += 1
            return False, f"Scartato: Fuori raggio o Comune sconosciuto."

        # ---------------------------------------------------------
        # 2. GENERAZIONE NUOVO DNA (Comune + Prezzo + MQ)
        # ---------------------------------------------------------
        # Formattazione sicura del nome comune per il DNA (minuscolo, senza spazi)
        comune_safe = comune_trovato.lower().replace(" ", "")
        dna_annuncio = f"{comune_safe}_{int(prezzo)}_{metri_quadri}"

        # ---------------------------------------------------------
        # 3. CONTROLLO IDENTITÀ E GIUDIZIO UMANO
        # ---------------------------------------------------------
        if dna_annuncio in self.df_memoria["DNA"].values:
            riga = self.df_memoria[self.df_memoria["DNA"] == dna_annuncio].iloc[0]
            prezzo_storico = float(riga["Prezzo"])
            stato_umano = str(riga["Stato_Umano"]).upper().strip()
            
            if stato_umano in ["KO", "FALSE", "SCARTATO"] and prezzo >= prezzo_storico:
                self.immobili_scartati += 1
                return False, "Scartato dall'utente (KO)"
            
            if stato_umano in ["OK", "TRUE", "APPROVATO"]:
                if prezzo < prezzo_storico:
                    self.df_memoria.loc[self.df_memoria["DNA"] == dna_annuncio, "Prezzo"] = prezzo
                    self.df_memoria.loc[self.df_memoria["DNA"] == dna_annuncio, "Stato_Umano"] = "DA_RIVALUTARE"
                    self.immobili_analizzati += 1
                    return True, f"🚨 RIBASSO SU TARGET OK! (Sconto: €{prezzo_storico - prezzo})"
                
                self.immobili_scartati += 1
                return False, "Già in archivio come OK"

            if prezzo < prezzo_storico:
                self.df_memoria.loc[self.df_memoria["DNA"] == dna_annuncio, "Prezzo"] = prezzo
                self.df_memoria.loc[self.df_memoria["DNA"] == dna_annuncio, "Stato_Umano"] = "DA_RIVALUTARE"
                self.immobili_analizzati += 1
                return True, f"🚨 RIBASSO RILEVATO! Sconto: €{prezzo_storico - prezzo}"

        # ---------------------------------------------------------
        # 4. FILTRI RIGIDI E SEMANTICI
        # ---------------------------------------------------------
        if prezzo > BUDGET_MAX:
            self.immobili_scartati += 1
            return False, f"Scartato: Prezzo oltre limite (€{prezzo})."
        
        if metri_quadri > 0 and metri_quadri < MQ_MIN:
            self.immobili_scartati += 1
            return False, f"Scartato: Troppo piccolo ({metri_quadri}mq)."

        for parola in KEYWORDS_NEGATIVE:
            if parola in testo_completo:
                self.immobili_scartati += 1
                return False, f"Scartato: Trovata parola negativa '{parola}'."

        ha_requisiti = any(parola in testo_completo for parola in KEYWORDS_POSITIVE)
        if not ha_requisiti:
            self.immobili_scartati += 1
            return False, "Scartato: Nessuna keyword di indipendenza trovata."

        # ---------------------------------------------------------
        # 5. REGISTRAZIONE SUL FALDONE UNIFICATO
        # ---------------------------------------------------------
        if dna_annuncio not in self.df_memoria["DNA"].values:
            nuova_riga = pd.DataFrame([{
                "Sorgente": sorgente,
                "DNA": dna_annuncio, 
                "Comune": comune_trovato.capitalize(),
                "Distanza_Km": minuti_distanza,
                "Prezzo": prezzo,
                "Superficie_Mq": metri_quadri,
                "Link": link,
                "Note": titolo, 
                "Data_Scoperta": oggi.strftime("%Y-%m-%d"), 
                "Stato_Umano": "DA_ANALIZZARE", 
                "Note_Lavori": ""
             }])
            self.df_memoria = pd.concat([self.df_memoria, nuova_riga], ignore_index=True)

        self.immobili_analizzati += 1
        return True, f"Bersaglio Acquisito a {comune_trovato.capitalize()} ({minuti_distanza} min)"