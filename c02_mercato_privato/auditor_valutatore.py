# auditor_valutatore.py
import os
import pandas as pd
from datetime import datetime
from cacciatore_privati import BUDGET_MAX, MQ_MIN, KEYWORDS_POSITIVE, KEYWORDS_NEGATIVE

class AuditorImmobiliare:
    def __init__(self):
        self.immobili_analizzati = 0
        self.immobili_scartati = 0
        
        # Percorso del Database Locale (La Memoria Storica)
        cartella_corrente = os.path.dirname(os.path.abspath(__file__))
        cartella_madre = os.path.dirname(cartella_corrente)
        self.percorso_db = os.path.join(cartella_madre, "c03_blacklist", "memoria_storica.csv")
        
        # Carica la memoria o la crea se non esiste
        self._carica_database()

    def _carica_database(self):
        """Carica il registro storico per controllare ID, prezzi e date."""
        if os.path.exists(self.percorso_db) and os.path.getsize(self.percorso_db) > 0:
            self.df_memoria = pd.read_csv(self.percorso_db)
        else:
            # Struttura della nostra Tabella di Audit
            colonne = ["ID_Univoco", "Link", "Titolo", "Prezzo_Ultimo", "Data_Scoperta", "Giorni_Mercato", "Stato_Umano", "Note_Lavori"]
            self.df_memoria = pd.DataFrame(columns=colonne)

    def salva_database(self):
        """Sigilla il faldone salvando i dati aggiornati su file."""
        self.df_memoria.to_csv(self.percorso_db, index=False)
        print("  [v] Memoria Storica aggiornata e salvata in c03_blacklist.")

    def valuta_annuncio(self, id_annuncio, link, titolo, descrizione, prezzo, metri_quadri):
        """Passa l'annuncio ai Raggi X. Applica i filtri e controlla la Memoria Storica."""
        testo_completo = (titolo + " " + descrizione).lower()
        oggi = datetime.now()

        # ---------------------------------------------------------
        # 1. CONTROLLO NELLA MEMORIA STORICA (Identità Intelligente)
        # ---------------------------------------------------------
        if id_annuncio in self.df_memoria["ID_Univoco"].values:
            riga = self.df_memoria[self.df_memoria["ID_Univoco"] == id_annuncio].iloc[0]
            prezzo_storico = float(riga["Prezzo_Ultimo"])
            stato_umano = str(riga["Stato_Umano"]).upper()
            data_scoperta = datetime.strptime(riga["Data_Scoperta"], "%Y-%m-%d")
            
            # Calcolo dei giorni sul mercato
            giorni_trascorsi = (oggi - data_scoperta).days
            
            # Se l'avevi scartato a mano e il prezzo non è sceso, viene polverizzato
            if stato_umano == "SCARTATO" and prezzo >= prezzo_storico:
                self.immobili_scartati += 1
                return False, "Scartato in precedenza (Prezzo invariato o aumentato)."
            
            # Se il prezzo è sceso, bypassa i filtri e alza l'allarme!
            if prezzo < prezzo_storico:
                sconto = prezzo_storico - prezzo
                # Aggiorniamo il prezzo nel database
                self.df_memoria.loc[self.df_memoria["ID_Univoco"] == id_annuncio, "Prezzo_Ultimo"] = prezzo
                self.df_memoria.loc[self.df_memoria["ID_Univoco"] == id_annuncio, "Stato_Umano"] = "DA_RIVALUTARE"
                
                self.immobili_analizzati += 1
                return True, f"🚨 RIBASSO RILEVATO! Sconto: €{sconto}. (Sul mercato da {giorni_trascorsi} gg)"

        # ---------------------------------------------------------
        # 2. FILTRI RIGIDI (Se è una casa nuova)
        # ---------------------------------------------------------
        if prezzo > BUDGET_MAX:
            self.immobili_scartati += 1
            return False, f"Scartato: Prezzo oltre limite."
        
        if metri_quadri > 0 and metri_quadri < MQ_MIN:
            self.immobili_scartati += 1
            return False, f"Scartato: Troppo piccolo."

        for parola in KEYWORDS_NEGATIVE:
            if parola in testo_completo:
                self.immobili_scartati += 1
                return False, f"Scartato: Trovata parola chiave negativa '{parola}'."

        ha_requisiti = any(parola in testo_completo for parola in KEYWORDS_POSITIVE)
        if not ha_requisiti:
            self.immobili_scartati += 1
            return False, "Scartato: Non indipendente."

        # ---------------------------------------------------------
        # 3. REGISTRAZIONE NUOVO BERSAGLIO
        # ---------------------------------------------------------
        if id_annuncio not in self.df_memoria["ID_Univoco"].values:
            nuova_riga = pd.DataFrame([{
                "ID_Univoco": id_annuncio, 
                "Link": link,
                "Titolo": titolo, 
                "Prezzo_Ultimo": prezzo, 
                "Data_Scoperta": oggi.strftime("%Y-%m-%d"), 
                "Giorni_Mercato": 0,
                "Stato_Umano": "DA_ANALIZZARE", 
                "Note_Lavori": ""
            }])
            self.df_memoria = pd.concat([self.df_memoria, nuova_riga], ignore_index=True)

        self.immobili_analizzati += 1
        return True, "Nuovo Bersaglio Acquisito."