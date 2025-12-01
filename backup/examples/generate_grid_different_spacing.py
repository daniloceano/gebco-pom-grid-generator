#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo: Geração de grade com espaçamentos diferentes
======================================================

Este script demonstra como gerar uma grade batimétrica com
espaçamentos diferentes para longitude (dx) e latitude (dy).

Isso pode ser útil para:
- Ajustar resolução em latitudes altas
- Balancear resolução meridional vs zonal
- Criar grades mais eficientes para certas aplicações

Autor: Projeto POM
Data: Outubro 2025
"""

import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bathymetry_generator import BathymetryGridGenerator


# ============================================================================
# CONFIGURAÇÕES
# ============================================================================

# Caminho para o arquivo GEBCO
GEBCO_FILE = "../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"

# Espaçamentos DIFERENTES para longitude (dx) e latitude (dy)
SPACING_LON = 0.30  # dx = 0.30° (mais espaçado em longitude)
SPACING_LAT = 0.20  # dy = 0.20° (mais refinado em latitude)

# Região: Sudeste do Brasil
LON_MIN = -50.0
LON_MAX = -38.0
LAT_MIN = -28.0
LAT_MAX = -20.0

# Arquivos de saída
OUTPUT_DIR = "../output"
OUTPUT_FILE = os.path.join(OUTPUT_DIR, "pom_grid_dx030_dy020.asc")
PLOT_FILE = os.path.join(OUTPUT_DIR, "pom_grid_dx030_dy020.png")


# ============================================================================
# PROCESSAMENTO
# ============================================================================

def main():
    """
    Gera grade com espaçamentos diferentes.
    """
    
    print("="*70)
    print(" EXEMPLO: GRADE COM ESPAÇAMENTOS DIFERENTES")
    print("="*70)
    print(f"\nConfiguração:")
    print(f"  dx (longitude): {SPACING_LON}°")
    print(f"  dy (latitude):  {SPACING_LAT}°")
    print(f"  Região: {LON_MIN}°E a {LON_MAX}°E, {LAT_MIN}°N a {LAT_MAX}°N")
    print("="*70 + "\n")
    
    # Garantir diretório de saída
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        # 1. Inicializar com spacing_lon e spacing_lat
        generator = BathymetryGridGenerator(
            GEBCO_FILE,
            spacing_lon=SPACING_LON,
            spacing_lat=SPACING_LAT,
            n_workers=None  # Auto
        )
        
        # 2. Carregar GEBCO
        if not generator.load_gebco_data():
            return 1
        
        # 3. Definir extensão
        generator.define_grid_extent(LON_MIN, LON_MAX, LAT_MIN, LAT_MAX)
        
        # 4. Interpolar
        if not generator.interpolate_bathymetry(method='linear', parallel=True):
            return 1
        
        # 5. Exportar
        if not generator.export_to_ascii(OUTPUT_FILE):
            return 1
        
        # 6. Plotar
        generator.plot_bathymetry(PLOT_FILE)
        
        # 7. Limpar
        generator.cleanup()
        
        print("\n" + "="*70)
        print(" CONCLUÍDO!")
        print("="*70)
        print(f"\nGrade gerada: {OUTPUT_FILE}")
        print(f"Visualização: {PLOT_FILE}")
        print("\nNote que a grade tem:")
        print(f"  - Resolução horizontal (dx): {SPACING_LON}° ≈ {SPACING_LON*111:.1f} km")
        print(f"  - Resolução vertical (dy): {SPACING_LAT}° ≈ {SPACING_LAT*111:.1f} km")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
