from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sys
import os
import unicodedata


def executar():
    # lista de mapas (copiada do seu post)
    MAPS = [
        # Control
        "Antarctic Peninsula",
        "Busan",
        "Ilios",
        "Lijiang Tower",
        "Nepal",
        "Oasis",
        "Samoa",
        # Escort
        "Circuit Royal",
        "Dorado",
        "Havana",
        "Junkertown",
        "Rialto",
        "Route 66",
        "Shambali Monastery",
        "Watchpoint: Gibraltar",
        # Hybrid
        "Blizzard World",
        "Eichenwalde",
        "Hollywood",
        "King's Row",
        "Midtown",
        "Numbani",
        "Paraíso",
        # Push
        "Colosseo",
        "Esperança",
        "New Queen Street",
        "Runasapi",
        # Flashpoint
        "Aatlis"
        "New Junk City"
        "Suravasa"
    ]

    # tiers que você tinha antes (adicione/remova se quiser)
    TIERS = ["Master", "Grandmaster"]

    OUTDIR = "winratemaps"
    os.makedirs(OUTDIR, exist_ok=True)

    def remove_accents(text: str) -> str:
        # normaliza e remove diacríticos
        nfkd = unicodedata.normalize("NFKD", text)
        return "".join([c for c in nfkd if not unicodedata.combining(c)])

    def make_map_param(raw: str) -> str:
        s = remove_accents(raw)         # tira acento
        s = s.lower()                   # minúsculas
        s = s.replace(":", "")          # remove ':'
        s = s.replace(" ", "-")         # espaços -> '-'
        # opcional: remover caracteres não-ASCII restantes
        s = "".join(ch for ch in s if ord(ch) < 128)
        return s

    # configurações do Chrome (headless)
    chrome_options = Options()
    chrome_options.add_argument("--headless")
    # se quiser rodar com janela visível, comente a linha acima

    driver = webdriver.Chrome(options=chrome_options)

    try:
        for map_name in MAPS:
            map_param = make_map_param(map_name)
            # também usar uma versão "sanitize" para o filename (sem acento, espaços -> -)
            filename_base = make_map_param(map_name)  # já é sem acento e com '-' e minúsculo

            for tier in TIERS:
                filename = f"{filename_base}_{tier}.html"
                filepath = os.path.join(OUTDIR, filename)

                url = (
                    "https://overwatch.blizzard.com/en-us/rates/"
                    f"?input=PC&map={map_param}&region=Americas&role=Damage&rq=1&tier={tier}"
                )
                try:
                    print(f"Obtendo: {url}")
                    driver.get(url)

                    # esperar carregar (ajuste se necessário)
                    time.sleep(3)

                    html_completo = driver.page_source
                    with open(filepath, "w", encoding="utf-8") as f:
                        f.write(html_completo)
                    print(f"Salvo em: {filepath}")
                except Exception as e:
                    print(f"Erro ao processar {map_name} ({tier}): {e}")
    finally:
        driver.quit()

    print("Concluído.")

if __name__ == "__main__":
    executar()