from selenium import webdriver
from selenium.webdriver.chrome.options import Options
import time
import sys
import os

# Lê e processa o mapa de map.txt
map_file = "map.txt"
if not os.path.exists(map_file):
    print(f"Erro: '{map_file}' não encontrado.")
    sys.exit(1)

with open(map_file, "r", encoding="utf-8") as f:
    raw = f.read().strip()

# transforma: tudo minúsculo, remove ":" e substitui espaços por "-"
map_param = raw.lower().replace(":", "").replace(" ", "-")

# configurações do Chrome (headless)
chrome_options = Options()
chrome_options.add_argument("--headless")
# se quiser rodar sem headless, comente a linha acima

driver = webdriver.Chrome(options=chrome_options)

try:
    # lista de (tier, nome_do_arquivo)
    targets = [
        ("Master", "winrate1.html"),
        ("Grandmaster", "winrate2.html"),
    ]

    for tier, filename in targets:
        url = (
            "https://overwatch.blizzard.com/en-us/rates/"
            f"?input=PC&map={map_param}&region=Americas&role=Damage&rq=1&tier={tier}"
        )
        print(f"Obtendo: {url}")
        driver.get(url)

        # esperar carregar (ajuste se necessário)
        time.sleep(3)

        html_completo = driver.page_source
        with open(filename, "w", encoding="utf-8") as f:
            f.write(html_completo)
        print(f"Salvo em: {filename}")

finally:
    driver.quit()

print("Concluído.")
