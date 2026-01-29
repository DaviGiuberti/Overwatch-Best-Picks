import keyboard
import subprocess
import sys
import os
import time

BASE_DIR = os.path.dirname(__file__)
PYTHON = sys.executable

# Buffer para capturar digitação
typed_buffer = []
last_key_time = time.time()

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

def run_map_pipeline():
    try:
        print("Executando map.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "map.py")], check=True)
        print("Executando site.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "site.py")], check=True)
        print("Executando retirarWinrate.py...")
        subprocess.run([PYTHON, os.path.join(BASE_DIR, "retirarWinrate.py")], check=True)
        print("Pipeline 'map' finalizado.\n")
    except subprocess.CalledProcessError as e:
        print("Erro ao executar um dos scripts:", e)

def on_key_event(event):
    global typed_buffer, last_key_time
    
    # Detecta TAB + 1
    if event.name == "1" and event.event_type == "down":
        if keyboard.is_pressed("tab"):
            run_pipeline()
            time.sleep(0.5)
            return
    
    # Detecta digitação de "map"
    if event.event_type == "down" and len(event.name) == 1:
        current_time = time.time()
        
        # Limpa buffer se passou mais de 1 segundo desde a última tecla
        if current_time - last_key_time > 1.0:
            typed_buffer.clear()
        
        last_key_time = current_time
        typed_buffer.append(event.name.lower())
        
        # Mantém apenas os últimos 3 caracteres
        if len(typed_buffer) > 3:
            typed_buffer.pop(0)
        
        # Verifica se digitou "map"
        if ''.join(typed_buffer) == "000":
            print("\n'map' detectado!")
            typed_buffer.clear()
            run_map_pipeline()

print("Aguardando TAB + 1 ou digitação de '000'... Ctrl+C para sair")
keyboard.hook(on_key_event)
keyboard.wait()