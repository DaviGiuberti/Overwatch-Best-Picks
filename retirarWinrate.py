#!/usr/bin/env python3
# extract_winrates_two_files.py

import re
import html
import sys
import os
from openpyxl import Workbook

MAP_FILE = "map.txt"
WINRATE_DIR = "winratemaps"
OUTPUT_XLSX = "winrate.xlsx"

pattern = re.compile(
    r'{"name"\s*:\s*"(?P<name>[^"]+)"[^}]*?"winrate"\s*:\s*(?P<wr>\d+(?:\.\d+)?)',
    re.IGNORECASE | re.UNICODE
)

def get_input_files():
    try:
        with open(MAP_FILE, "r", encoding="utf-8") as f:
            map_name = f.read().strip()
    except FileNotFoundError:
        print(f"Erro: '{MAP_FILE}' não encontrado.")
        sys.exit(1)

    if not map_name:
        print("Erro: 'map.txt' está vazio.")
        sys.exit(1)

    html_master = os.path.join(WINRATE_DIR, f"{map_name}_Master.html")
    html_grandmaster = os.path.join(WINRATE_DIR, f"{map_name}_Grandmaster.html")

    return html_master, html_grandmaster

def parse_file(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = f.read()
    except FileNotFoundError:
        print(f"Erro: '{path}' não encontrado.")
        sys.exit(1)

    text = html.unescape(raw)
    num_map = {}
    str_map = {}

    for m in pattern.finditer(text):
        name = m.group("name").strip()
        name = name.replace(":", "").replace(".", "")

        wr_text = m.group("wr").strip()
        try:
            wr_num = float(wr_text)
        except ValueError:
            continue

        num_map[name] = wr_num
        str_map[name] = wr_text.replace(".", ",")

    return num_map, str_map

def main():
    INPUT_HTML1, INPUT_HTML2 = get_input_files()

    num1, str1 = parse_file(INPUT_HTML1)
    num2, str2 = parse_file(INPUT_HTML2)

    names_sorted = sorted(
        set(num1.keys()) | set(num2.keys()),
        key=lambda s: s.lower()
    )

    if not names_sorted:
        print("Nenhuma winrate encontrada nos arquivos.")
        sys.exit(0)

    wb = Workbook()
    ws = wb.active
    ws.title = "Winrates"

    ws["A1"] = "Hero"
    ws["B1"] = "Winrate Master"
    ws["C1"] = "Winrate Grandmaster"
    ws["D1"] = "Average"
    ws["E1"] = "Saida (0,2*avg - 10) * 2"

    row = 2
    for name in names_sorted:
        ws.cell(row=row, column=1, value=name)

        if name in str1:
            ws.cell(row=row, column=2, value=str1[name])

        if name in str2:
            ws.cell(row=row, column=3, value=str2[name])

        if name in num1 and name in num2:
            avg = (num1[name] + num2[name]) / 2
            ws.cell(row=row, column=4, value=f"{avg:.2f}".replace(".", ","))

            saida = (0.2 * avg - 10.0) * 2
            ws.cell(row=row, column=5, value=f"{saida:.2f}".replace(".", ","))

        row += 1

    wb.save(OUTPUT_XLSX)
    print(f"OK — {len(names_sorted)} heróis salvos em '{OUTPUT_XLSX}'.")

if __name__ == "__main__":
    main()
