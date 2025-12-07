#!/usr/bin/env python3
"""
Gerar grade pequena cruzando ±180° para testar wrap-around
Região: Pacífico equatorial, 178°E a 178°W
"""

import sys
import os

# Adicionar path
sys.path.insert(0, 'tools/gebco_interpolation/src')

from bathymetry_generator import BathymetryGridGenerator

print("="*70)
print("TESTE: Grade pequena cruzando linha de data (±180°)")
print("="*70)

# Criar gerador
generator = BathymetryGridGenerator(
    'gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc',
    spacing_lon=0.6,  # Espaçamento maior = mais rápido
    spacing_lat=1.0,
    n_workers=2
)

# Carregar
print("\n1. Carregando GEBCO...")
if not generator.load_gebco_data():
    print("✗ Erro ao carregar")
    sys.exit(1)

# Definir região pequena
print("\n2. Definindo região de teste:")
print("   Pacífico: 178°E a 182°E (= -178°W)")
print("   Equador: -5° a 5°")

generator.define_grid_extent(
    lon_min=178.0,
    lon_max=-178.0,  # Equivalente a 182°, cruza ±180°
    lat_min=-5.0,
    lat_max=5.0
)

# Interpolar
print("\n3. Interpolando...")
if not generator.interpolate_bathymetry(method='linear', parallel=True):
    print("✗ Erro na interpolação")
    sys.exit(1)

# Salvar
output_file = 'output/test_dateline_region.asc'
print(f"\n4. Salvando em: {output_file}")
generator.save_grid(output_file)

# Análise
print("\n" + "="*70)
print("ANÁLISE DOS RESULTADOS")
print("="*70)

import numpy as np

depth = generator.depth_grid
lons = generator.grid_lons
lats = generator.grid_lats

# Pegar linha equatorial
lat_idx = np.argmin(np.abs(lats))

print(f"\nProfundidades ao longo do equador (lat={lats[lat_idx]:.1f}°):")
print("-" * 50)

for lon, d in zip(lons, depth[lat_idx, :]):
    marker = " ← CRÍTICO" if abs(lon - 180) < 0.5 or abs(lon + 180) < 0.5 else ""
    status = "✗ ZERO" if d == 0 else "✓"
    print(f"  {status} Lon {lon:7.1f}°: {d:8.2f} m{marker}")

# Verificar
n_zeros = np.sum(depth[lat_idx, :] == 0)
idx_180 = np.argmin(np.abs(lons - 180))
idx_m180 = np.argmin(np.abs(lons + 180))

print("\n" + "="*70)
print(f"Zeros encontrados: {n_zeros}/{len(lons)} pontos")
print(f"Profundidade em +180°: {depth[lat_idx, idx_180]:.2f} m")
print(f"Profundidade em -180°: {depth[lat_idx, idx_m180]:.2f} m")

if n_zeros == 0:
    print("\n✓ SUCESSO: Correção de wrap-around funcionando!")
else:
    print(f"\n✗ PROBLEMA: Ainda há {n_zeros} pontos zerados")

print("="*70)
