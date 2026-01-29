#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from difflib import get_close_matches
import unicodedata

# Lista completa de mapas do Overwatch
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
    "Runasapi"
]

def normalize_text(text):
    """Remove acentos e normaliza o texto para comparação"""
    # Remove acentos
    nfkd = unicodedata.normalize('NFKD', text)
    text_no_accents = ''.join([c for c in nfkd if not unicodedata.combining(c)])
    return text_no_accents.lower().strip()

def find_best_match(user_input):
    """Encontra o mapa que mais se parece com a entrada do usuário"""
    if not user_input.strip():
        return None
    
    # Normaliza a entrada do usuário
    normalized_input = normalize_text(user_input)
    
    # Cria versões normalizadas dos mapas para comparação
    normalized_maps = {normalize_text(map_name): map_name for map_name in MAPS}
    
    # Tenta encontrar correspondências exatas primeiro (ignorando case e acentos)
    if normalized_input in normalized_maps:
        return normalized_maps[normalized_input]
    
    # Usa fuzzy matching para encontrar a melhor correspondência
    matches = get_close_matches(normalized_input, normalized_maps.keys(), n=1, cutoff=0.4)
    
    if matches:
        return normalized_maps[matches[0]]
    
    return None

def save_to_file(map_name):
    """Salva o nome do mapa em map.txt"""
    with open('map.txt', 'w', encoding='utf-8') as f:
        f.write(map_name)

def main():
    print("=" * 50)
    print("OVERWATCH MAP MATCHER")
    print("=" * 50)
    print("\nDigite o nome de um mapa (pode ser aproximado):")
    print("Exemplos: 'ilios', 'kinsgrow', 'dorado', etc.\n")
    
    user_input = input("Mapa: ")
    
    best_match = find_best_match(user_input)
    
    if best_match:
        save_to_file(best_match)
        print(f"\n✓ Mapa encontrado: {best_match}")
        print(f"✓ Salvo em: map.txt")
    else:
        print("\n✗ Nenhum mapa encontrado que corresponda à sua entrada.")
        print("Tente novamente com um nome mais próximo ao original.")

if __name__ == "__main__":
    main()