# 🏢 Ecosistema di Automazione per Audit Immobiliare

Questo repository contiene l'infrastruttura tecnica e i bot di scouting progettati per automatizzare la ricerca, il filtraggio e l'analisi finanziaria di asset immobiliari. 

L'obiettivo è eliminare il "rumore" del mercato (annunci fuori target, prezzi gonfiati) e applicare un metodo di indagine rigoroso per valutare opportunità sia sul mercato privato che nelle aste giudiziarie.

## ⚙️ Architettura del Sistema

Il flusso di lavoro è progettato per compartimenti stagni:

1. **Estrazione Dati (Python):** Script di web scraping interrogano i principali portali immobiliari e i siti dei tribunali per estrarre i parametri chiave degli immobili.
2. **Filtro e Pulizia (Excel - Blacklist):** I dati grezzi vengono confrontati localmente con un database storico (Blacklist) per scartare automaticamente gli immobili già analizzati o non conformi ai parametri di rendimento.
3. **Visualizzazione (Notion):** Gli asset che superano l'audit vengono inviati a una dashboard su Notion, che funge da "Vetrina" operativa per la valutazione finale (Lavori, Prezzo, ROI).

## 🗂️ Moduli Operativi

Al momento, l'ecosistema è composto dai seguenti moduli indipendenti:

* **`c01_pvp_aste`**: Modulo dedicato al Portale Vendite Pubbliche. Automatizza la ricerca di immobili in asta, estraendo dati essenziali da incrociare con le perizie.
* *(In Sviluppo)* **`c02_mercato_privato`**: Modulo per lo scouting su portali privati (es. Immobiliare, Idealista) con focus su metriche di mercato e Rent-to-Buy.
* *(Locale)* **`c03_blacklist`**: Database di esclusione e calcolo metriche mantenuto in locale per ragioni di privacy e strategia.

## Modulo 2: Mercato Privato (Ecosistema Modulare)
Un motore di ricerca avanzato che incrocia portali nazionali e agenzie locali, progettato con Architettura a Oggetti (OOP) e Feedback Loop umano.

* **Il Manuale (Dati):** File isolato con parametri finanziari, matrice distanze e keyword di setaccio.
* **Lo Stampo (Auditor):** Classe Python autonoma che giudica i dati grezzi in base al Manuale e gestisce un database locale tramite `pandas`.
* **Gli Specialisti (Scrapers):** Bot Playwright (`headless=False`) con navigazione organica per aggirare i sistemi anti-bot (DataDome, Cloudflare). Dotati di "Bisturi Regex" per estrarre MQ e Prezzi anche se nascosti in tag SVG o `aria-label`. Include sistema anti-loop basato sulle impronte testuali per bypassare le inserzioni "Vetrina".
* **Memoria Storica (Feedback Loop):** Registro CSV locale. Il bot ricorda gli annunci `SCARTATI` dall'Auditor Umano, ma li "resuscita" automaticamente se rileva un calo di prezzo incrociando i dati storici, calcolando anche i reali giorni di permanenza sul mercato.
---
*Progetto in continua evoluzione - Architettura scalabile.*