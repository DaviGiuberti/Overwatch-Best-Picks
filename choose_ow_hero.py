"""
Módulo de ranking de heróis do Overwatch
Calcula pontuação baseada em matchups contra inimigos, sinergia com aliados e winrate no mapa
"""

import pandas as pd
from typing import List, Dict, Tuple
import os


def read_role() -> str:
    """
    Lê o arquivo Roles.txt para determinar qual role usar
    
    Returns:
        Nome da role (DPS, Suporte, Tank, AllRoles)
    """
    role_file = "Roles.txt"
    
    if not os.path.exists(role_file):
        print("Arquivo 'Roles.txt' não encontrado!")
        print("Por favor, crie o arquivo e defina sua Role (DPS, Suporte, Tank ou AllRoles)")
        return None
    
    with open(role_file, 'r', encoding='utf-8') as f:
        role = f.read().strip()
    
    if not role:
        print("Arquivo 'Roles.txt' está vazio!")
        print("Por favor, defina sua Role (DPS, Suporte, Tank ou AllRoles)")
        return None
    
    # Verifica se existe o arquivo correspondente
    role_heroes_file = f"{role}.txt"
    if not os.path.exists(role_heroes_file):
        print(f"Arquivo '{role_heroes_file}' não encontrado!")
        print("Por favor, defina sua Role e Personagens Favoritos corretamente.")
        print("Roles disponíveis: DPS, Suporte, Tank, AllRoles")
        return None
    
    return role


def read_playable_heroes(role: str) -> List[str]:
    """
    Lê o arquivo da role específica para obter os heróis jogáveis
    
    Args:
        role: Nome da role (DPS, Suporte, Tank, AllRoles)
    
    Returns:
        Lista com nomes dos heróis que o jogador usa
    """
    role_file = f"{role}.txt"
    
    with open(role_file, 'r', encoding='utf-8') as f:
        heroes = [line.strip() for line in f.readlines() if line.strip()]
    
    return heroes


def read_lineup(filepath: str = "lineup.txt") -> Tuple[List[str], List[str]]:
    """
    Lê o arquivo lineup.txt e separa aliados e inimigos
    
    Returns:
        Tuple contendo (aliados, inimigos)
    """
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines()]
    
    allies = lines[:4]
    enemies = lines[4:9]
    
    return allies, enemies


def read_heroes_ally_data(filepath: str = "heroes ally.xlsx") -> pd.DataFrame:
    """
    Lê o arquivo heroes ally.xlsx com os matchups de aliados
    
    Returns:
        DataFrame com os dados de sinergia com aliados
    """
    df = pd.read_excel(filepath, sheet_name=0, header=0)
    return df


def read_heroes_enemy_data(filepath: str = "heroes enemy.xlsx") -> pd.DataFrame:
    """
    Lê o arquivo heroes enemy.xlsx com os matchups contra inimigos
    
    Returns:
        DataFrame com os dados de matchups contra inimigos
    """
    df = pd.read_excel(filepath, sheet_name=0, header=0)
    return df


def read_winrate_data(filepath: str = "winrate.xlsx") -> Dict[str, float]:
    """
    Lê o arquivo winrate.xlsx e retorna dicionário {herói: winrate}
    
    Returns:
        Dicionário com winrate de cada herói
    """
    df = pd.read_excel(filepath, sheet_name=0)
    # Coluna A: Nome do personagem, Coluna E: Winrate
    winrate_dict = {}
    
    for _, row in df.iterrows():
        hero_name = row.iloc[0]  # Coluna A
        winrate_value = row.iloc[4]  # Coluna E
        
        if pd.notna(hero_name) and pd.notna(winrate_value):
            # Converter valor para string e trocar vírgula por ponto (formato brasileiro)
            winrate_str = str(winrate_value).replace(',', '.')
            try:
                winrate_dict[str(hero_name).strip()] = float(winrate_str)
            except ValueError:
                # Se ainda assim falhar, assume 0.0
                winrate_dict[str(hero_name).strip()] = 0.0
    
    return winrate_dict


def calculate_hero_score(
    hero_name: str,
    ally_df: pd.DataFrame,
    enemy_df: pd.DataFrame,
    allies: List[str],
    enemies: List[str],
    winrate_dict: Dict[str, float]
) -> Dict[str, float]:
    """
    Calcula a pontuação de um herói jogável
    
    Args:
        hero_name: Nome do herói a ser avaliado
        ally_df: DataFrame com dados de sinergia (heroes ally.xlsx)
        enemy_df: DataFrame com dados de matchups (heroes enemy.xlsx)
        allies: Lista de aliados
        enemies: Lista de inimigos
        winrate_dict: Dicionário com winrates
    
    Returns:
        Dicionário com enemy_score, ally_score, map_winrate e total
    """
    # Calcular Enemy Score
    # Busca a linha do herói na primeira coluna do enemy_df
    enemy_score = 0.0
    hero_row_enemy = enemy_df[enemy_df.iloc[:, 0] == hero_name]
    
    if not hero_row_enemy.empty:
        for enemy in enemies:
            # Busca a coluna do inimigo (primeira linha)
            if enemy in enemy_df.columns:
                value = hero_row_enemy[enemy].values[0]
                if pd.notna(value):
                    enemy_score += float(value)
    
    # Calcular Ally Score
    # Busca a linha do herói na primeira coluna do ally_df
    ally_score = 0.0
    hero_row_ally = ally_df[ally_df.iloc[:, 0] == hero_name]
    
    if not hero_row_ally.empty:
        for ally in allies:
            # Busca a coluna do aliado (primeira linha)
            if ally in ally_df.columns:
                value = hero_row_ally[ally].values[0]
                if pd.notna(value):
                    ally_score += float(value)
    
    # Buscar Map Winrate
    map_winrate = winrate_dict.get(hero_name, 0.0)
    
    # Calcular Total
    total_score = enemy_score + ally_score + map_winrate
    
    return {
        'hero': hero_name,
        'enemy_score': enemy_score,
        'ally_score': ally_score,
        'map_winrate': map_winrate,
        'total': total_score
    }


def print_ranking(rankings: List[Dict[str, float]]) -> None:
    """
    Imprime o ranking de forma organizada e visual
    """
    # Ordenar por total (decrescente)
    sorted_rankings = sorted(rankings, key=lambda x: x['total'], reverse=True)
    
    # Cabeçalho
    print("=" * 70)
    print(f"{'RANK':<6} | {'HERO':<15} | {'ENEMY':>8} | {'ALLY':>8} | {'MAP':>8} | {'TOTAL':>8}")
    print("=" * 70)
    
    # Linhas de dados
    for rank, hero_data in enumerate(sorted_rankings, start=1):
        print(
            f"{rank:<6} | "
            f"{hero_data['hero']:<15} | "
            f"{hero_data['enemy_score']:>8.2f} | "
            f"{hero_data['ally_score']:>8.2f} | "
            f"{hero_data['map_winrate']:>8.2f} | "
            f"{hero_data['total']:>8.2f}"
        )
    
    print("-" * 70)


def run_hero_ranking():
    """
    Função principal que executa todo o processo de ranking
    """
    # Ler a role do jogador
    role = read_role()
    if role is None:
        return
    
    print(f"Role selecionada: {role}")
    print()
    
    # Ler heróis jogáveis da role
    playable_heroes = read_playable_heroes(role)
    print(f"Heróis disponíveis: {', '.join(playable_heroes)}")
    print()
    
    # Ler dados
    allies, enemies = read_lineup()
    print(f"Aliados: {', '.join(allies)}")
    print(f"Inimigos: {', '.join(enemies)}")
    print()
    
    ally_df = read_heroes_ally_data()
    enemy_df = read_heroes_enemy_data()
    winrate_dict = read_winrate_data()
    
    # Calcular pontuação para cada herói jogável
    rankings = []
    for hero in playable_heroes:
        score_data = calculate_hero_score(
            hero,
            ally_df,
            enemy_df,
            allies,
            enemies,
            winrate_dict
        )
        rankings.append(score_data)
    
    # Imprimir ranking
    print_ranking(rankings)


# Execução automática quando o módulo é importado ou executado
if __name__ == "__main__":
    run_hero_ranking()