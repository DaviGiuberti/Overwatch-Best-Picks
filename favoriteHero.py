#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from difflib import get_close_matches
import unicodedata
import json
import os

# Lista completa de heróis do Overwatch organizados por função
HEROES = {
    "DPS": [
        "Ashe", "Bastion", "Cassidy", "Echo", "Freja", "Genji", "Hanzo",
        "Junkrat", "Mei", "Pharah", "Reaper", "Sojourn", "Soldier 76",
        "Sombra", "Symmetra", "Torbjörn", "Tracer", "Vendetta", "Venture",
        "Widowmaker"
    ],
    "Support": [
        "Ana", "Baptiste", "Brigitte", "Illari", "Juno", "Kiriko",
        "Lifeweaver", "Lúcio", "Mercy", "Moira", "Wuyang", "Zenyatta"
    ],
    "Tank": [
        "DVa", "Doomfist", "Hazard", "Junker Queen", "Mauga", "Orisa",
        "Ramattra", "Reinhardt", "Roadhog", "Sigma", "Winston",
        "Wrecking Ball", "Zarya"
    ]
}

FAVORITES_FILE = "favorites.json"

def normalize_text(text):
    """Remove acentos e normaliza o texto para comparação"""
    nfkd = unicodedata.normalize('NFKD', text)
    text_no_accents = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    return text_no_accents.lower().strip()

def get_all_heroes():
    """Retorna lista com todos os heróis"""
    all_heroes = []
    for role_heroes in HEROES.values():
        all_heroes.extend(role_heroes)
    return all_heroes

def get_hero_role(hero_name):
    """Retorna a função (role) de um herói"""
    for role, heroes in HEROES.items():
        if hero_name in heroes:
            return role
    return None

def find_best_match(user_input):
    """Encontra o herói que mais se parece com a entrada do usuário"""
    if not user_input.strip():
        return None
    
    normalized_input = normalize_text(user_input)
    all_heroes = get_all_heroes()
    
    # Cria versões normalizadas dos heróis para comparação
    normalized_heroes = {normalize_text(hero): hero for hero in all_heroes}
    
    # Tenta encontrar correspondências exatas primeiro (ignorando case e acentos)
    if normalized_input in normalized_heroes:
        return normalized_heroes[normalized_input]
    
    # Usa fuzzy matching para encontrar a melhor correspondência
    matches = get_close_matches(normalized_input, normalized_heroes.keys(), n=1, cutoff=0.4)
    
    if matches:
        return normalized_heroes[matches[0]]
    
    return None

def save_heroes_to_files(heroes_list):
    """Salva os heróis nos arquivos apropriados baseado em suas funções"""
    # Remove duplicatas mantendo a ordem
    heroes_list = list(dict.fromkeys(heroes_list))
    
    # Organiza os heróis por função
    heroes_by_role = {"DPS": [], "Support": [], "Tank": []}
    
    for hero in heroes_list:
        role = get_hero_role(hero)
        if role:
            heroes_by_role[role].append(hero)
    
    # Salva cada função em seu arquivo correspondente
    for role, filename in [("DPS", "DPS.txt"), ("Support", "Support.txt"), ("Tank", "Tank.txt")]:
        with open(filename, 'w', encoding='utf-8') as f:
            if heroes_by_role[role]:
                f.write('\n'.join(heroes_by_role[role]))
    
    # Salva todos os heróis em AllRoles.txt
    with open("AllRoles.txt", 'w', encoding='utf-8') as f:
        if heroes_list:
            f.write('\n'.join(heroes_list))

def load_favorites():
    """Carrega a lista de heróis favoritos"""
    if os.path.exists(FAVORITES_FILE):
        try:
            with open(FAVORITES_FILE, 'r', encoding='utf-8') as f:
                return json.load(f)
        except:
            return []
    return []

def save_favorites(favorites):
    """Salva a lista de heróis favoritos"""
    with open(FAVORITES_FILE, 'w', encoding='utf-8') as f:
        json.dump(favorites, f, ensure_ascii=False, indent=2)

def add_favorite(hero_name):
    """Adiciona um herói aos favoritos e salva direto nos arquivos"""
    favorites = load_favorites()
    if hero_name not in favorites:
        favorites.append(hero_name)
        save_favorites(favorites)
        save_heroes_to_files(favorites)
        print(f"✓ {hero_name} adicionado")
        return True
    else:
        print(f"✗ {hero_name} já existe")
        return False

def remove_favorite(hero_name):
    """Remove um herói dos favoritos e atualiza os arquivos"""
    favorites = load_favorites()
    if hero_name in favorites:
        favorites.remove(hero_name)
        save_favorites(favorites)
        save_heroes_to_files(favorites)
        print(f"✓ {hero_name} removido")
        return True
    else:
        print(f"✗ {hero_name} não está nos favoritos")
        return False

def list_favorites():
    """Lista todos os heróis favoritos"""
    favorites = load_favorites()
    if favorites:
        for hero in favorites:
            role = get_hero_role(hero)
            print(f"  {hero} ({role})")
    else:
        print("  Nenhum favorito")

def main_menu():
    """Menu principal"""
    while True:
        print("\n1. Adicionar herói")
        print("2. Remover herói")
        print("3. Ver favoritos")
        print("4. Sair")
        
        choice = input("\nOpção: ").strip()
        
        if choice == "1":
            user_input = input("Herói: ").strip()
            match = find_best_match(user_input)
            if match:
                add_favorite(match)
            else:
                print("✗ Herói não encontrado")
        
        elif choice == "2":
            user_input = input("Herói: ").strip()
            match = find_best_match(user_input)
            if match:
                remove_favorite(match)
            else:
                print("✗ Herói não encontrado")
        
        elif choice == "3":
            print("\nFavoritos:")
            list_favorites()
        
        elif choice == "4":
            break
        
        else:
            print("✗ Opção inválida")

if __name__ == "__main__":
    main_menu()