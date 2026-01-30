#!/usr/bin/env python3
import time
from pathlib import Path
import math
import sys  # Adicionado
import os   # Adicionado

import cv2
import numpy as np
from PIL import Image

# ---------- Função Auxiliar para Caminhos (Passo 2) ----------
def resource_path(relative_path):
    """ Retorna o caminho absoluto, funcionando em dev ou no PyInstaller """
    try:
        # PyInstaller cria uma pasta temporária em _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")

    return os.path.join(base_path, relative_path)

# CONFIGURAÇÃO
# MUDANÇA AQUI: Usamos resource_path para encontrar a pasta 'heroes' empacotada
templates_dir = Path(resource_path("heroes"))     

# A pasta 'print' continua relativa ao local de execução (não usa resource_path)
watch_dir = Path("print")          
perks_names = ["0perk", "1perk", "2perk"]
output_filename = "lineup.txt"     
target_size = (42, 42)             

# ---------- utilitários ----------
def load_image_gray(path, target_size=None):
    """Carrega imagem, converte pra grayscale e retorna array float32."""
    img = Image.open(path).convert("L")
    if target_size is not None:
        img = img.resize(target_size, Image.NEAREST)
    arr = np.asarray(img, dtype=np.float32)
    return arr

def normalized_mae(a, b):
    """Mean Absolute Error normalizado entre 0 e 1 (divide por 255)."""
    mae = np.mean(np.abs(a - b))
    return mae / 255.0

# ---------- carregar templates ----------
def load_templates(templates_dir, target_size=(42,42)):
    templates = []
    if not templates_dir.exists():
        # Dica de debug caso esqueça de copiar a pasta no pyinstaller
        print(f"ERRO CRÍTICO: Pasta de templates não encontrada em: {templates_dir}")
        raise RuntimeError(f"Pasta de templates não existe: {templates_dir}")
    
    for p in sorted(templates_dir.iterdir()):
        if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}:
            arr = load_image_gray(p, target_size=target_size)
            templates.append((p.stem, arr))  # p.stem -> nome sem extensão
            
    if not templates:
        raise RuntimeError(f"Nenhuma template encontrada em {templates_dir}")
    return templates

# ---------- comparar uma imagem com as templates ----------
def find_best_match(img_arr, templates):
    best_name = None
    best_score = 1.0  # menor é melhor (MAE normalizado)
    for name, tpl in templates:
        if tpl.shape != img_arr.shape:
            tpl_r = cv2.resize(tpl, (img_arr.shape[1], img_arr.shape[0]), interpolation=cv2.INTER_NEAREST)
        else:
            tpl_r = tpl
        score = normalized_mae(img_arr, tpl_r)
        if score < best_score:
            best_score = score
            best_name = name
    return best_name, best_score

# ---------- processa uma pasta específica ----------
def process_folder(folder_path: Path, templates, target_size=(42,42)):
    folder_path.mkdir(parents=True, exist_ok=True)
    # coleta arquivos de imagem na pasta (ordenados por data de modificação)
    files = [p for p in folder_path.iterdir() if p.suffix.lower() in {".png", ".jpg", ".jpeg", ".bmp"}]
    files = sorted(files, key=lambda x: x.stat().st_mtime)

    results = []  # lista de tuples (input_filename, matched_name, score)
    for p in files:
        time.sleep(0.02)
        try:
            img = load_image_gray(p, target_size=target_size)
        except Exception as e:
            print(f"Falha ao abrir {p}: {e}  -> pulando")
            continue
        best_name, best_score = find_best_match(img, templates)
        results.append((p.name, best_name, best_score))
        print(f"[{folder_path.name}] {p.name} -> {best_name} (score={best_score:.4f})")
    return results

# ---------- main ----------
def executar():
    try:
        templates = load_templates(templates_dir, target_size=target_size)
    except RuntimeError as e:
        print(e)
        return

    # construir lista de pastas a verificar (apenas as 3 perks)
    perk_paths = [watch_dir / name for name in perks_names]

    all_found_any = False
    folder_stats = []  # lista de dicts: {path, results, avg_score}
    for ppath in perk_paths:
        # Verifica se a pasta existe antes de processar
        if not ppath.exists() or not ppath.is_dir():
            print(f"Pasta ausente (pulando): {ppath}")
            folder_stats.append({"path": ppath, "results": [], "avg_score": math.inf})
            continue

        results = process_folder(ppath, templates, target_size=target_size)
        if results:
            all_found_any = True
            scores = [r[2] for r in results]
            avg = float(np.mean(scores)) if scores else math.inf
        else:
            avg = math.inf
        folder_stats.append({"path": ppath, "results": results, "avg_score": avg})
        if results:
            print(f" -> {len(results)} imagens em {ppath} | avg score = {avg:.4f}")
        else:
            print(f" -> nenhuma imagem em {ppath}")

    # decidir qual pasta teve o melhor (menor) avg_score
    best = min(folder_stats, key=lambda x: x["avg_score"])
    if best["avg_score"] == math.inf:
        # nenhuma imagem encontrada em nenhuma pasta: criar lineup.txt vazio no diretório atual
        # ATENÇÃO: Output file usa Path.cwd() para salvar onde o usuário está rodando, não na pasta temp
        out_file = Path.cwd() / output_filename
        out_file.write_text("", encoding="utf-8")
        print(f"Nenhuma imagem encontrada em nenhuma pasta. Criei lineup.txt vazio em {out_file.resolve()}")
        return

    best_path = best["path"]
    best_results = best["results"]

    # escreve lineup.txt no diretório atual (não na pasta vencedora)
    out_file = Path.cwd() / output_filename
    with open(out_file, "w", encoding="utf-8") as f:
        for input_filename, matched_name, score in best_results:
            f.write(f"{matched_name}\n")

    print(f"Melhor pasta: {best_path} (avg_score={best['avg_score']:.4f}).")
    print(f"Gravado {len(best_results)} linhas em {out_file.resolve()}")

if __name__ == "__main__":
    executar()