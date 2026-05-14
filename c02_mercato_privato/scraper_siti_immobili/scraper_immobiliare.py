# scraper_immobiliare.py
from playwright.sync_api import sync_playwright

# Il tuo mega-URL con la mappatura poligonale e i filtri a 130k
URL_IMMOBILIARE = (
    "https://www.immobiliare.it/search-list/?idContratto=1&idCategoria=1"
    "&prezzoMassimo=130000&superficieMinima=90&__lang=it"
    "&vrt=45.199129%2C10.911345%3B45.18544%2C10.897053%3B45.169386%2C10.830781%3B"
    "45.164974%2C10.833893%3B45.160635%2C10.836845%3B45.154153%2C10.83881%3B"
    "45.149466%2C10.841124%3B45.143592%2C10.846065%3B45.140149%2C10.846672%3B"
    "45.132208%2C10.845697%3B45.119028%2C10.859638%3B45.113083%2C10.880196%3B"
    "45.113768%2C10.898872%3B45.083525%2C10.954134%3B45.069329%2C10.990396%3B"
    "45.057589%2C11.027952%3B45.041739%2C11.07912%3B45.056975%2C11.1175%3B"
    "45.065609%2C11.118986%3B45.068469%2C11.124869%3B45.064948%2C11.129646%3B"
    "45.060517%2C11.132598%3B45.058527%2C11.133329%3B45.056207%2C11.13489%3B"
    "45.04441%2C11.151832%3B45.044743%2C11.159172%3B45.045871%2C11.171638%3B"
    "45.058138%2C11.193085%3B45.059165%2C11.20578%3B45.058309%2C11.210742%3B"
    "45.044948%2C11.233846%3B45.042452%2C11.239754%3B45.044267%2C11.24808%3B"
    "45.05271%2C11.257131%3B45.055688%2C11.264968%3B45.053902%2C11.26891%3B"
    "45.049607%2C11.271142%3B45.045978%2C11.270393%3B45.042707%2C11.269343%3B"
    "45.040659%2C11.268196%3B45.038665%2C11.266896%3B45.031763%2C11.263389%3B"
    "45.025231%2C11.262068%3B45.019192%2C11.263735%3B45.013812%2C11.295497%3B"
    "45.009768%2C11.315536%3B45.012874%2C11.320073%3B45.018064%2C11.324778%3B"
    "45.023615%2C11.324094%3B45.027048%2C11.320482%3B45.042042%2C11.31676%3B"
    "45.095757%2C11.311346%3B45.144881%2C11.283942%3B45.174381%2C11.258%3B"
    "45.183113%2C11.241047%3B45.190345%2C11.242852%3B45.19344%2C11.226883%3B"
    "45.203129%2C11.216166%3B45.210286%2C11.198376%3B45.223678%2C11.184554%3B"
    "45.254439%2C11.138498%3B45.258984%2C11.140974%3B45.266205%2C11.135285%3B"
    "45.269397%2C11.12304%3B45.253881%2C11.102827%3B45.247566%2C11.082871%3B"
    "45.243381%2C11.079541%3B45.230904%2C11.056273%3B45.236767%2C11.02286%3B"
    "45.23389%2C11.006629%3B45.239551%2C10.98725%3B45.247606%2C10.980125%3B"
    "45.245134%2C10.968279%3B45.240712%2C10.962771%3B45.199129%2C10.911345"
    "&pag=1&idTipologia%5B%5D=7&idTipologia%5B%5D=11&idTipologia%5B%5D=12"
    "&idTipologia%5B%5D=13#geohash-u0pb8np8"
)

def esegui_test_accesso():
    print("--- TEST INGRESSO: IMMOBILIARE.IT ---")
    
    with sync_playwright() as p:
        # Usiamo le stesse armi anti-riconoscimento delle aste
        browser = p.chromium.launch(headless=False, args=["--disable-blink-features=AutomationControlled"])
        context = browser.new_context(viewport={"width": 1920, "height": 1080})
        page = context.new_page()

        print("[*] Tentativo di atterraggio sul target...")
        page.goto(URL_IMMOBILIARE)
        page.wait_for_load_state("networkidle")
        
        # Facciamo finta di essere umani che leggono
        page.wait_for_timeout(4000) 
        
        # Verifichiamo se ci hanno messo un muro davanti
        titolo_pagina = page.title()
        print(f"[*] Titolo pagina letto dal bot: {titolo_pagina}")

        input("\n[>] Premi INVIO qui nel terminale per chiudere il browser...")
        browser.close()

if __name__ == "__main__":
    esegui_test_accesso()