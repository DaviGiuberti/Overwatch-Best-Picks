#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import keyboard
import time
import threading
import sys
import os

# Importando seus módulos (os arquivos .py que estão na mesma pasta)
# Certifique-se que todos eles tenham uma função chamada 'executar()' ou equivalente.
import choose_ow_hero
import comparar
import favoriteHero
import map as map_script  # Renomeado para não conflitar com 'map' nativo do Python
import retirarWinrate
import roles
import screenshot
import site_scrapper

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MAP_FILE = os.path.join(BASE_DIR, "map.txt")

# Estado global indicando se estamos no "main" (menu) ou em outro script
IN_MAIN = True
_pipeline_hotkey_id = None  # id retornado por keyboard.add_hotkey

# ---------- Menus ----------

def print_main_menu():
    print(
        "Comandos disponíveis:\n"
        "  2 -> modificar mapa analisado\n"
        "  3 -> alterar Role/Função\n"
        "  4 -> adicionar/remover heróis favoritos\n"
        "  5 -> atualizar winrate dos mapas\n"
        "  6 -> remover mapa selecionado\n"
    )

def print_small_menu():
    print(
        "\n[2] Mapa  [3] Role  [4] Favoritos  [5] Atualizar Winrate  [6] Remover mapa\n"
    )

# ---------- Pipelines ----------

def run_pipeline():
    """ Executa o fluxo principal: Print -> Comparar -> Escolher Herói """
    try:
        print(">>> Executando screenshot...")
        screenshot.executar()

        print(">>> Executando comparação...")
        comparar.executar()

        print(">>> Executando escolha de herói...")
        if hasattr(choose_ow_hero, 'run_hero_ranking'):
            choose_ow_hero.run_hero_ranking()
        elif hasattr(choose_ow_hero, 'executar'):
            choose_ow_hero.executar()
        else:
            print("Erro: Função principal não encontrada em choose_ow_hero.py")

        print("Pipeline finalizado.")
    except Exception as e:
        print(f"Erro no pipeline: {e}")
        import traceback
        traceback.print_exc()
    finally:
        # Ao terminar, exibe o menu resumido (não altera estado IN_MAIN)
        print_small_menu()

def run_site():
    try:
        print(">>> Executando site_scraper.py (Scraper)...")
        site_scrapper.executar()
    except Exception as e:
        print(f"Erro no site.py: {e}")

def run_map():
    try:
        print(">>> Executando map.py...")
        map_script.executar()

        print(">>> Retirando a winrate do mapa...")
        retirarWinrate.executar()

        print("Pipeline 'map' finalizado.")
    except Exception as e:
        print(f"Erro no mapa: {e}")

def run_role():
    try:
        print(">>> Executando roles.py...")
        roles.executar()
        print("Role atualizada.")
    except Exception as e:
        print(f"Erro em roles: {e}")

def run_favorite():
    try:
        print(">>> Executando favoriteHero.py...")
        if hasattr(favoriteHero, 'executar'):
            favoriteHero.executar()
        elif hasattr(favoriteHero, 'main_menu'):
            favoriteHero.main_menu()
        else:
            print("Erro: Função não encontrada em favoriteHero.py")
        print("Herói favorito atualizado.")
    except Exception as e:
        print(f"Erro em favoritos: {e}")

def remove_map():
    if os.path.exists(MAP_FILE):
        try:
            os.remove(MAP_FILE)
            print("map.txt removido com sucesso.")
        except Exception as e:
            print(f"Erro ao remover arquivo: {e}")
    else:
        print("Nenhum map.txt encontrado para remover.")

# ---------- Threads e Inputs ----------

def spawn_in_thread(func, *args, **kwargs):
    """Executa func em uma thread separada (daemon)"""
    t = threading.Thread(target=func, args=args, kwargs=kwargs, daemon=True)
    t.start()
    return t

# ---------- Hook-based hotkey (mais resiliente) ----------

_tab_pressed = False
_use_hook_hotkey = True  # mude para False para desativar este método

def _on_key_event(event):
    global _tab_pressed, IN_MAIN
    # event.event_type é 'down' ou 'up'
    name = event.name
    if name == 'tab':
        _tab_pressed = (event.event_type == 'down')
    elif name == '1' and event.event_type == 'down':
        if _tab_pressed and IN_MAIN:
            # evita reentrância: desativa o hook temporariamente
            try:
                keyboard.unhook(_on_key_event)
            except Exception:
                pass
            print("[hotkey-hook] Detectado TAB+1 -> executando pipeline.")
            spawn_in_thread(run_pipeline)
            # reativa hook com pequeno delay para evitar múltiplos triggers rápidos
            def rehook():
                time.sleep(0.2)
                try:
                    keyboard.hook(_on_key_event)
                except Exception:
                    pass
            spawn_in_thread(rehook)

def enable_pipeline_hotkey_hook():
    global _use_hook_hotkey
    _use_hook_hotkey = True
    try:
        keyboard.hook(_on_key_event)
        print("[hotkey-hook] Hook ativado.")
    except Exception as e:
        print(f"[hotkey-hook] Erro ao ativar hook: {e}")

def disable_pipeline_hotkey_hook():
    global _use_hook_hotkey
    _use_hook_hotkey = False
    try:
        keyboard.unhook(_on_key_event)
        print("[hotkey-hook] Hook desativado.")
    except Exception as e:
        print(f"[hotkey-hook] Erro ao desativar hook: {e}")

# ---------- Hotkey management (método add_hotkey original) ----------

def enable_pipeline_hotkey():
    """ Registra TAB+1 se ainda não estiver registrado """
    global _pipeline_hotkey_id
    if _use_hook_hotkey:
        enable_pipeline_hotkey_hook()
        return
    
    if _pipeline_hotkey_id is None:
        # registra hotkey que dispara o pipeline em uma thread para não bloquear o callback
        _pipeline_hotkey_id = keyboard.add_hotkey("tab+1", lambda: spawn_in_thread(_pipeline_callback))
        # Observação: add_hotkey retorna um identificador (string ou inteiro) dependendo da versão
        # Nós guardamos para podermos remover depois

def disable_pipeline_hotkey():
    """ Remove o hotkey TAB+1 se estiver ativo """
    global _pipeline_hotkey_id
    if _use_hook_hotkey:
        disable_pipeline_hotkey_hook()
        return
    
    if _pipeline_hotkey_id is not None:
        try:
            keyboard.remove_hotkey(_pipeline_hotkey_id)
        except Exception:
            # fallback: tentar limpar todos os hotkeys (cautela)
            try:
                keyboard.clear_all_hotkeys()
            except Exception:
                pass
        _pipeline_hotkey_id = None

def _pipeline_callback():
    """Callback invocado pelo hotkey; só executa se estivermos em main."""
    global IN_MAIN
    if not IN_MAIN:
        # ignorar se não estivermos no menu principal
        return
    # rodar pipeline em thread separada para não travar captura de teclado
    run_pipeline()

# ---------- Controle de Input ----------

def call_and_pause_main(func, *args, **kwargs):
    """
    Chama func bloqueante (por exemplo módulos interativos). Enquanto ele executa:
    - desativa o hotkey do pipeline (TAB+1)
    - marca IN_MAIN = False (indicando que main está 'fora')
    Ao terminar, reativa hotkey e retorna ao menu.
    """
    global IN_MAIN
    # sinaliza que saímos do main
    IN_MAIN = False
    disable_pipeline_hotkey()
    try:
        func(*args, **kwargs)
    finally:
        # voltamos ao main
        IN_MAIN = True
        enable_pipeline_hotkey()
        print("\nRetornando ao menu principal.")
        print_small_menu()

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

        if cmd == "2":
            # executar map de forma bloqueante e pausar main enquanto roda
            call_and_pause_main(run_map)
        elif cmd == "3":
            call_and_pause_main(run_role)
        elif cmd in ("4", "favorite", "fav"):
            call_and_pause_main(run_favorite)
        elif cmd == "5":
            call_and_pause_main(run_site)
        elif cmd == "6":
            # remover mapa é imediato, não precisa 'pausar' longa execução,
            # mas vamos mantê-lo sincronizado com o fluxo de pausa/remissão
            call_and_pause_main(remove_map)
        elif cmd in ("7", "exit", "quit"):
            print("Encerrando programa...")
            disable_pipeline_hotkey()
            try:
                keyboard.clear_all_hotkeys()
            except Exception:
                pass
            os._exit(0)
        else:
            print("Comando não reconhecido.")
            print_small_menu()

# ---------- Configuração Inicial ----------

if __name__ == "__main__":
    # Inicialmente estamos no menu principal
    IN_MAIN = True
    enable_pipeline_hotkey()  # registra TAB+1 (hook ou add_hotkey dependendo de _use_hook_hotkey)

    # Iniciar Thread de Input (rodando o input() em thread para que hotkey global funcione)
    input_thread = threading.Thread(target=input_loop, daemon=True)
    input_thread.start()

    print("="*50)
    print(" PROGRAMA INICIADO")
    if _use_hook_hotkey:
        print("")
    else:
        print("")
    print(" - Pressione TAB+1 (global) para executar o pipeline quando estiver no menu principal.")
    print(" - Use os números do menu e ENTER para rodar os outros comandos.")
    print("="*50)

    # Loop principal para manter o programa vivo
    try:
        while True:
            time.sleep(1)
            # se o thread de input morrer, encerramos
            if not input_thread.is_alive():
                break
    except KeyboardInterrupt:
        print("\nInterrompido pelo usuário.")
    finally:
        disable_pipeline_hotkey()
        try:
            keyboard.clear_all_hotkeys()
        except Exception:
            pass
        print("Programa finalizado.")