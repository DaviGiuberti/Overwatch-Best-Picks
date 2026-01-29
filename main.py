import keyboard
import subprocess
import sys
import os
import time
import threading

BASE_DIR = os.path.dirname(__file__)
PYTHON = sys.executable

# ---------- Pipelines ----------

def run_pipeline():
    try:
        print("Executando screenshot.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "screenshot.py")], check=True)
        print("Executando comparar.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "comparar.py")], check=True)
        print("Executando choose_ow_hero.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "choose_ow_hero.py")], check=True)
        print("Pipeline finalizado.\n")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar um dos scripts:", e)


def run_site():
    try:
        print("Executando site.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "site.py")], check=True)
    except subprocess.CalledProcessError as e:
        print("Erro ao executar um dos scripts:", e)

def run_map():
    try:
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "map.py")], check=True)
        print("Retirando a winrate do mapa...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "retirarWinrate.py")], check=True)
        print("Pipeline 'map' finalizado.\n")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar um dos scripts:", e)


def run_role():
    try:
        print("Executando Role.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "Role.py")], check=True)
        print("Role atualizado.\n")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar Role.py:", e)


def run_favorite():
    try:
        print("Executando favoriteHero.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "favoriteHero.py")], check=True)
        print("Heroi favorito atualizado.\n")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar favoriteHero.py:", e)


# ---------- Input thread (escolha por ENTER) ----------

def input_loop():
    """Loop que espera o usuário digitar um comando no terminal e dar ENTER.
    Comandos suportados: map, role, favorite, pipeline, exit (ou quit)
    """
    help_text = (
        "Comandos disponíveis:\n"
        "  1      -> modifica o mapa analisado\n"
        "  2      -> Alterar a Role/Função jogada\n"
        "  3      -> adicionar ou remover herois favoritos\n"
        "  4      -> atualiza a winrate dos mapas (faça apenas após grandes atualizações)\n"
        "  5      -> sai do programa\n"
    )
    print(help_text)

    while True:
        try:
            cmd = input("> ").strip().lower()
        except (EOFError, KeyboardInterrupt):
            print("\nEntrada interrompida. Saindo do input loop.")
            break

        if not cmd:
            continue

        if cmd == "1":
            run_map()
        elif cmd == "2":
            run_role()
        elif cmd in ("favorite", "fav", "favoritehero", "favorite_hero", "3"):
            run_favorite()
        elif cmd in ("4"):
            run_site()
        elif cmd in ("exit", "quit", "5"):
            print("Encerrando programa por comando do usuário...")
            # Limpa hotkeys e termina o programa
            keyboard.clear_all_hotkeys()
            os._exit(0)
        else:
            print("Comando não reconhecido.\n")
            print(help_text)


# ---------- Configuração das hotkeys ----------

# Usa add_hotkey para não ficar 'hookando' todas as teclas — isto respeita sua
# exigência de "não detectar todas as teclas que estão sendo apertadas".
# Ainda assim, TAB+1 continuará funcionando exatamente como antes.
keyboard.add_hotkey('tab+1', run_pipeline)

# Inicia a thread que lê comandos via ENTER no terminal
input_thread = threading.Thread(target=input_loop, daemon=True)
input_thread.start()

print("Aguardando TAB+1 ou digite um comando e pressione ENTER. (Ctrl+C para sair)")

# Mantém o programa rodando enquanto a thread de input estiver viva.
try:
    while input_thread.is_alive():
        time.sleep(0.5)
except KeyboardInterrupt:
    print("\nInterrompido pelo usuário. Saindo...")
    keyboard.clear_all_hotkeys()

print("Programa finalizado.")
