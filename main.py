import keyboard
import subprocess
import sys
import os
import time
import threading

BASE_DIR = os.path.dirname(__file__)
PYTHON = sys.executable
MAP_FILE = os.path.join(BASE_DIR, "map.txt")

# ---------- Menus ----------

def print_main_menu():
    print(
        "Comandos disponíveis:\n"
        "  1 -> modificar mapa analisado\n"
        "  2 -> alterar Role/Função\n"
        "  3 -> adicionar/remover heróis favoritos\n"
        "  4 -> atualizar winrate dos mapas\n"
        "  5 -> remover mapa selecionado\n"
        "  6 -> sair do programa\n"
    )

def print_small_menu():
    print(
        "\n[1] Mapa  [2] Role  [3] Favoritos  [4] Winrate  [5] Remover mapa  [6] Sair\n"
    )

# ---------- Pipelines ----------

def run_pipeline():
    try:
        print("Executando screenshot.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "screenshot.py")], check=True)

        print("Executando comparar.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "comparar.py")], check=True)

        print("Executando choose_ow_hero.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "choose_ow_hero.py")], check=True)

        print("Pipeline finalizado.")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar pipeline:", e)
    finally:
        print_small_menu()


def run_site():
    try:
        print("Executando site.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "site.py")], check=True)
    except subprocess.CalledProcessError as e:
        print("Erro ao executar site.py:", e)
    finally:
        print_small_menu()


def run_map():
    try:
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "map.py")], check=True)

        print("Retirando a winrate do mapa...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "retirarWinrate.py")], check=True)

        print("Pipeline 'map' finalizado.")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar map:", e)
    finally:
        print_small_menu()


def run_role():
    try:
        print("Executando roles.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "roles.py")], check=True)
        print("Role atualizado.")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar Role.py:", e)
    finally:
        print_small_menu()


def run_favorite():
    try:
        print("Executando favoriteHero.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "favoriteHero.py")], check=True)
        print("Herói favorito atualizado.")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar favoriteHero.py:", e)
    finally:
        print_small_menu()


def remove_map():
    if os.path.exists(MAP_FILE):
        os.remove(MAP_FILE)
        print("map.txt removido com sucesso.")
    else:
        print("Nenhum map.txt encontrado para remover.")
    print_small_menu()

# ---------- Input thread ----------

def input_loop():
    print_main_menu()

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada interrompida.")
            break

        if not cmd:
            continue

        if cmd == "1":
            run_map()
        elif cmd == "2":
            run_role()
        elif cmd in ("3", "favorite", "fav"):
            run_favorite()
        elif cmd == "4":
            run_site()
        elif cmd == "5":
            remove_map()
        elif cmd in ("6", "exit", "quit"):
            print("Encerrando programa...")
            keyboard.clear_all_hotkeys()
            os._exit(0)
        else:
            print("Comando não reconhecido.")
            print_main_menu()

# ---------- Hotkeys ----------

keyboard.add_hotkey("tab+1", run_pipeline)

input_thread = threading.Thread(target=input_loop, daemon=True)
input_thread.start()

print("TAB+1 executa o pipeline | ou digite um comando e ENTER")

try:
    while input_thread.is_alive():
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nInterrompido pelo usuário.")
    keyboard.clear_all_hotkeys()

print("Programa finalizado.")
