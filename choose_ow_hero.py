"""
Módulo de ranking de heróis do Overwatch
Calcula pontuação baseada em matchups contra inimigos, sinergia com aliados e winrate no mapa
"""

import pandas as pd
from typing import List, Dict, Tuple


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


def read_heroes_data(filepath: str = "heroes.xlsx") -> pd.DataFrame:
    """
    Lê o arquivo heroes.xlsx com os matchups
    
    Returns:
        DataFrame com os dados dos heróis
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


def get_playable_heroes(df: pd.DataFrame) -> List[str]:
    """
    Identifica os heróis jogáveis baseado nas colunas do DataFrame
    Procura por colunas que terminam com ' Enemy' e ' Ally'
    
    Returns:
        Lista com nomes dos heróis jogáveis
    """
    playable_heroes = []
    columns = df.columns.tolist()
    
    for col in columns:
        col_str = str(col)
        if col_str.endswith(' Enemy'):
            hero_name = col_str.replace(' Enemy', '')
            # Verifica se existe a coluna Ally correspondente
            if f'{hero_name} Ally' in columns:
                playable_heroes.append(hero_name)
    
    return playable_heroes


def calculate_hero_score(
    hero_name: str,
    df: pd.DataFrame,
    allies: List[str],
    enemies: List[str],
    winrate_dict: Dict[str, float]
) -> Dict[str, float]:
    """
    Calcula a pontuação de um herói jogável
    
    Returns:
        Dicionário com enemy_score, ally_score, map_winrate e total
    """
    enemy_col = f'{hero_name} Enemy'
    ally_col = f'{hero_name} Ally'
    
    # Calcular Enemy Score
    enemy_score = 0.0
    for enemy in enemies:
        # Busca o herói inimigo na coluna A (primeira coluna)
        hero_row = df[df.iloc[:, 0] == enemy]
        if not hero_row.empty and enemy_col in df.columns:
            value = hero_row[enemy_col].values[0]
            if pd.notna(value):
                enemy_score += float(value)
    
    # Calcular Ally Score
    ally_score = 0.0
    for ally in allies:
        hero_row = df[df.iloc[:, 0] == ally]
        if not hero_row.empty and ally_col in df.columns:
            value = hero_row[ally_col].values[0]
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
    # Ler dados
    allies, enemies = read_lineup()
    heroes_df = read_heroes_data()
    winrate_dict = read_winrate_data()
    playable_heroes = get_playable_heroes(heroes_df)
    
    # Calcular pontuação para cada herói jogável
    rankings = []
    for hero in playable_heroes:
        score_data = calculate_hero_score(
            hero,
            heroes_df,
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