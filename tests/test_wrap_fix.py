#!/usr/bin/env python3
"""
Teste rápido para verificar a correção do wrap-around em ±180°
Região pequena: Pacífico próximo à linha de data internacional
"""

import sys
sys.path.insert(0, 'tools/gebco_interpolation/src')

from bathymetry_generator import BathymetryGridGenerator
import numpy as np

print("="*70)
print("TESTE: Correção de Wrap-Around em ±180°")
print("="*70)

# Criar gerador com espaçamento de 0.3° (compatível com o teste)
generator = BathymetryGridGenerator(
    'gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc',
    spacing_lon=0.3,
    spacing_lat=0.3,
    n_workers=2
)

# Carregar GEBCO
generator.load_gebco_data()

# Definir uma pequena região cruzando a linha de data
# Pacífico equatorial: 178°E a 178°W (equivalente a -182°)
# Cobre a linha de ±180° com margem de 2° de cada lado
print("\nDefinindo região de teste:")
print("  Lon: 178.0° a -178.0° (cruza linha de data em ±180°)")
print("  Lat: -5.0° a 5.0° (equador)")

generator.define_grid_extent(
    lon_min=178.0,
    lon_max=-178.0,  # Equivalente a 182.0, cruza ±180°
    lat_min=-5.0,
    lat_max=5.0
)

# Interpolar
success = generator.interpolate_bathymetry(method='linear', parallel=True)

if success:
    print("\n" + "="*70)
    print("RESULTADO DO TESTE")
    print("="*70)
    
    # Verificar valores em pontos específicos
    depth = generator.depth_grid
    lons = generator.grid_lons
    lats = generator.grid_lats
    
    print(f"\nGrade gerada: {len(lons)} x {len(lats)} pontos")
    
    # Pegar linha do equador (lat mais próxima de 0)
    lat_idx = np.argmin(np.abs(lats))
    depth_equator = depth[lat_idx, :]
    
    print(f"\nProfundidades ao longo do equador (lat={lats[lat_idx]:.2f}°):")
    print("-" * 45)
    for i, (lon, d) in enumerate(zip(lons, depth_equator)):
        status = "✓" if d > 0 else "✗ ZERO"
        # Destacar pontos críticos próximos a ±180°
        if abs(lon - 180) < 0.5 or abs(lon + 180) < 0.5:
            marker = " ← CRÍTICO (±180°)"
        else:
            marker = ""
        print(f"  {status} Lon {lon:7.1f}°: {d:8.2f} m{marker}")
    
    # Análise
    print("\n" + "="*70)
    print("ANÁLISE")
    print("="*70)
    n_zeros = np.sum(depth_equator == 0)
    n_ocean = np.sum(depth_equator > 0)
    
    # Verificar pontos específicos críticos
    idx_180 = np.argmin(np.abs(lons - 180))
    idx_m180 = np.argmin(np.abs(lons + 180))
    
    print(f"Total de pontos: {len(depth_equator)}")
    print(f"  Oceano (depth > 0): {n_ocean}")
    print(f"  Terra/Zero (depth = 0): {n_zeros}")
    print(f"\nPontos críticos:")
    print(f"  Lon +180°: {lons[idx_180]:.2f}° → {depth_equator[idx_180]:.2f} m")
    print(f"  Lon -180°: {lons[idx_m180]:.2f}° → {depth_equator[idx_m180]:.2f} m")
    
    if n_zeros == 0:
        print("\n✓ SUCESSO: Todos os pontos têm batimetria válida!")
        print("  A correção de wrap-around está funcionando!")
    else:
        print(f"\n✗ FALHA: {n_zeros} pontos com profundidade zero")
        if depth_equator[idx_180] == 0 or depth_equator[idx_m180] == 0:
            print("  PROBLEMA: Pontos em ±180° ainda estão zerados!")
    
    # Salvar grade de teste
    output_file = 'output/test_wrap_dateline.asc'
    print(f"\nSalvando grade de teste em: {output_file}")
    generator.save_grid(output_file)
    print("✓ Grade salva!")
else:
    print("\n✗ ERRO na interpolação")
