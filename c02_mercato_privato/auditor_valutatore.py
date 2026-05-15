# auditor_valutatore.py
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
        self.percorso_db = os.path.join(cartella_madre, "c03_blacklist", "memoria_storica.csv")
        
        self._carica_database()

    def _carica_database(self):
        if os.path.exists(self.percorso_db) and os.path.getsize(self.percorso_db) > 0:
            self.df_memoria = pd.read_csv(self.percorso_db)
        else:
            colonne = ["ID_Univoco", "Link", "Titolo", "Prezzo_Ultimo", "Data_Scoperta", "Giorni_Mercato", "Stato_Umano", "Note_Lavori"]
            self.df_memoria = pd.DataFrame(columns=colonne)

    def salva_database(self):
        self.df_memoria.to_csv(self.percorso_db, index=False)
        print("  [v] Memoria Storica aggiornata e salvata.")

    def valuta_annuncio(self, id_annuncio, link, titolo, descrizione, prezzo, metri_quadri):
        testo_completo = (titolo + " " + descrizione).lower()
        oggi = datetime.now()

        # ---------------------------------------------------------
        # 1. CONTROLLO IDENTITÀ E GIUDIZIO UMANO (Il DNA)
        # ---------------------------------------------------------
        if id_annuncio in self.df_memoria["ID_Univoco"].values:
            riga = self.df_memoria[self.df_memoria["ID_Univoco"] == id_annuncio].iloc[0]
            prezzo_storico = float(riga["Prezzo_Ultimo"])
            stato_umano = str(riga["Stato_Umano"]).upper().strip()
            
            # Se hai segnato KO, FALSE o SCARTATO e il prezzo non cala
            if stato_umano in ["KO", "FALSE", "SCARTATO"] and prezzo >= prezzo_storico:
                self.immobili_scartati += 1
                return False, "Scartato dall'utente (KO)"
            
            # Se hai segnato OK o TRUE
            if stato_umano in ["OK", "TRUE", "APPROVATO"]:
                if prezzo < prezzo_storico:
                    self.df_memoria.loc[self.df_memoria["ID_Univoco"] == id_annuncio, "Prezzo_Ultimo"] = prezzo
                    self.df_memoria.loc[self.df_memoria["ID_Univoco"] == id_annuncio, "Stato_Umano"] = "DA_RIVALUTARE"
                    self.immobili_analizzati += 1
                    return True, f"🚨 RIBASSO SU TARGET OK! (Sconto: €{prezzo_storico - prezzo})"
                
                # Se è già OK e il prezzo è uguale, lo ignoriamo nei log per non fare rumore
                self.immobili_scartati += 1
                return False, "Già in archivio come OK"

            # Se il prezzo è sceso su un annuncio ancora "DA_ANALIZZARE"
            if prezzo < prezzo_storico:
                self.df_memoria.loc[self.df_memoria["ID_Univoco"] == id_annuncio, "Prezzo_Ultimo"] = prezzo
                self.df_memoria.loc[self.df_memoria["ID_Univoco"] == id_annuncio, "Stato_Umano"] = "DA_RIVALUTARE"
                self.immobili_analizzati += 1
                return True, f"🚨 RIBASSO RILEVATO! Sconto: €{prezzo_storico - prezzo}"

        # ---------------------------------------------------------
        # 2. FILTRI RIGIDI: BUDGET E DIMENSIONI
        # ---------------------------------------------------------
        if prezzo > BUDGET_MAX:
            self.immobili_scartati += 1
            return False, f"Scartato: Prezzo oltre limite (€{prezzo})."
        
        if metri_quadri > 0 and metri_quadri < MQ_MIN:
            self.immobili_scartati += 1
            return False, f"Scartato: Troppo piccolo ({metri_quadri}mq)."

        # ---------------------------------------------------------
        # 3. CONTROLLO DISTANZA (Geolocalizzazione Semantica)
        # ---------------------------------------------------------
        minuti_distanza = 999
        comune_trovato = "Sconosciuto"
        
        for comune, dist in MATRICE_DISTANZE.items():
            # Cerca la parola esatta per evitare che "Mantova" combaci con "Borgo Mantovano"
            if re.search(r'\b' + re.escape(comune.lower()) + r'\b', testo_completo):
                minuti_distanza = dist
                comune_trovato = comune
                break
                
        if minuti_distanza > 25:
            self.immobili_scartati += 1
            return False, f"Scartato: Fuori raggio o Comune sconosciuto."

        # ---------------------------------------------------------
        # 4. FILTRO SEMANTICO (Keyword)
        # ---------------------------------------------------------
        for parola in KEYWORDS_NEGATIVE:
            if parola in testo_completo:
                self.immobili_scartati += 1
                return False, f"Scartato: Trovata parola negativa '{parola}'."

        ha_requisiti = any(parola in testo_completo for parola in KEYWORDS_POSITIVE)
        if not ha_requisiti:
            self.immobili_scartati += 1
            return False, "Scartato: Nessuna keyword di indipendenza trovata."

        # ---------------------------------------------------------
        # 5. REGISTRAZIONE SUL FALDONE
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
        return True, f"Bersaglio Acquisito a {comune_trovato} ({minuti_distanza} min)"