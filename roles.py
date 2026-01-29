#!/usr/bin/env python3
# salva a escolha em Roles.txt (substitui o conteúdo anterior)
import msvcrt

mapping = {
    '1': 'AllRoles',  # Fila Aberta
    '2': 'Tank',      # Tanque
    '3': 'Support',   # Suporte
    '4': 'DPS'        # DPS
}

print("1=Fila Aberta  2=Tanque  3=Suporte  4=DPS")
print("Pressione 1, 2, 3 ou 4...")

while True:
    b = msvcrt.getch()         # captura uma tecla (único caractere)
    try:
        key = b.decode()
    except:
        continue
    if key in mapping:
        with open("Roles.txt", "w", encoding="utf-8") as f:
            f.write(mapping[key])
        print("Escolhido:", mapping[key])
        break
