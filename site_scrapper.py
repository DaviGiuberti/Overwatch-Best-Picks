from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sys
import os
import unicodedata


def executar():
    # lista de mapas
    MAPS = [
        # Control
        "antarctic-peninsula",
        "busan",
        "ilios",
        "lijiang-tower",
        "nepal",
        "oasis",
        "samoa",
        # Escort
        "circuit-royal",
        "dorado",
        "havana",
        "junkertown",
        "rialto",
        "route-66",
        "shambali-monastery",
        "watchpoint-gibraltar",
        # Hybrid
        "blizzard-world",
        "eichenwalde",
        "hollywood",
        "kings-row",
        "midtown",
        "numbani",
        "paraiso",
        # Push
        "colosseo",
        "esperanca",
        "new-queen-street",
        "runasapi",
        # Flashpoint
        "aatlis",
        "new-junk-city",
        "suravasa",
    ]

    # tiers que você tinha antes (adicione/remova se quiser)
    TIERS = ["Master", "Grandmaster"]

    OUTDIR = "winratemaps"
    os.makedirs(OUTDIR, exist_ok=True)

    # configurações do Chrome (headless)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # se quiser rodar com janela visível, comente a linha acima

    driver = webdriver.Chrome(options=chrome_options)

    try:
        for map_name in MAPS:
            for tier in TIERS:
                filename = f"{map_name}_{tier}.html"
                filepath = os.path.join(OUTDIR, filename)

                url = (
                    "https://overwatch.blizzard.com/en-us/rates/"
                    f"?input=PC&map={map_name}&region=Americas&role=Damage&rq=2&tier={tier}"
                )
                try:
                    print(f"Obtendo: {url}")
                    driver.get(url)

                    # esperar carregar (ajuste se necessário)
                    time.sleep(3)

                    html_completo = driver.page_source
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(html_completo)
                except Exception as e:
                    print(f"Erro ao processar {map_name} ({tier}): {e}")
    finally:
        driver.quit()

if __name__ == "__main__":
    executar()