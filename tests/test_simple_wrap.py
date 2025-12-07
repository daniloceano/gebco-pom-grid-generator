#!/usr/bin/env python3
"""
Teste simples: verificar se valores em ±180° estão corretos
na grade existente vs nova grade com correção
"""

import numpy as np

def check_grid(filename):
    """Verifica valores em ±180° de uma grade"""
    print(f"\nAnalisando: {filename}")
    print("-" * 60)
    
    data = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 5:
                lon = float(parts[2])
                lat = float(parts[3])
                depth = float(parts[4])
                
                # Verificar apenas região equatorial e pontos críticos
                if abs(lat) < 10 and (abs(lon - 180) < 1 or abs(lon + 180) < 1):
                    data.append((lon, lat, depth))
    
    # Agrupar por longitude
    lons_unique = sorted(set(d[0] for d in data))
    
    print(f"Pontos próximos a ±180° (lat entre -10° e 10°):")
    print(f"{'Longitude':<12} {'N° pontos':<12} {'Profund. média':<18} {'Status'}")
    print("-" * 60)
    
    has_zeros = False
    for lon in lons_unique:
        points = [d for d in data if d[0] == lon]
        depths = [d[2] for d in points]
        avg_depth = np.mean(depths)
        n_zeros = sum(1 for d in depths if d == 0)
        
        if lon in [180.0, -180.0]:
            marker = " ← CRÍTICO"
        else:
            marker = ""
        
        if n_zeros > 0:
            status = f"✗ {n_zeros} zeros"
            has_zeros = True
        else:
            status = "✓ OK"
        
        print(f"{lon:>10.1f}° {len(points):>10d} {avg_depth:>15.2f} m   {status}{marker}")
    
    return has_zeros

print("="*70)
print("TESTE: Verificação de Wrap-Around em ±180°")
print("="*70)

# Verificar grade existente
has_problem = check_grid('output/rectangular_grid_lon-180.0_180.0_lat-90.0_90.0_dx0.3_dy0.25_gebco.asc')

print("\n" + "="*70)
print("RESULTADO")
print("="*70)

if has_problem:
    print("✗ PROBLEMA CONFIRMADO: Grade tem zeros em ±180°")
    print("\nEste é o problema que a correção resolve.")
    print("Após regenerar a grade com o código corrigido,")
    print("os valores em ±180° devem ter profundidade válida.")
else:
    print("✓ Grade OK: Nenhum problema detectado em ±180°")
