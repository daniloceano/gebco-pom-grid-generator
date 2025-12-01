#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script principal para geração de grade batimétrica POM
======================================================

Este script utiliza a classe BathymetryGridGenerator para criar grades
batimétricas a partir dos dados do GEBCO.

Uso:
    python generate_grid.py
    
    Modifique os parâmetros na seção CONFIGURAÇÕES abaixo.
"""

import sys
import os
from datetime import datetime

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bathymetry_generator import BathymetryGridGenerator


# ============================================================================
# CONFIGURAÇÕES - MODIFIQUE AQUI PARA SUA APLICAÇÃO
# ============================================================================

# Caminho para o arquivo GEBCO
GEBCO_FILE = "../../../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"

# Espaçamento da grade em graus decimais
# Opção 1: Usar o mesmo espaçamento para longitude e latitude
GRID_SPACING = 0.25  # 0.25° ≈ 27.8 km no equador

# Opção 2: Usar espaçamentos diferentes para longitude (dx) e latitude (dy)
# Descomente as linhas abaixo para usar espaçamentos diferentes
# SPACING_LON = 0.25  # dx em graus
# SPACING_LAT = 0.20  # dy em graus

# Extensão geográfica da grade (exemplo: costa brasileira)
LON_MIN = -60.0   # Longitude oeste
LON_MAX = -30.0   # Longitude leste
LAT_MIN = -35.0   # Latitude sul
LAT_MAX = -5.0    # Latitude norte

# Diretório de saída

OUTPUT_DIR = "../../../output"

# Método de interpolação: 'linear', 'nearest', ou 'cubic'
INTERPOLATION_METHOD = 'linear'

# Usar processamento paralelo?
USE_PARALLEL = True

# Número de workers (None = auto)
N_WORKERS = None

# Função para gerar nome de arquivo de saída conforme configurações
def generate_output_filename(ext="asc"):
    # Espaçamento
    dx = globals().get('SPACING_LON', GRID_SPACING)
    dy = globals().get('SPACING_LAT', GRID_SPACING)
    # Domínio
    lon_str = f"lon{LON_MIN}_{LON_MAX}"
    lat_str = f"lat{LAT_MIN}_{LAT_MAX}"
    dx_str = f"dx{dx}"
    dy_str = f"dy{dy}"
    # Nome final
    filename = f"rectangular_grid_{lon_str}_{lat_str}_{dx_str}_{dy_str}_gebco.{ext}"
    return os.path.join(OUTPUT_DIR, filename)

OUTPUT_FILE = generate_output_filename("asc")

# Gerar visualização?
GENERATE_PLOT = True
PLOT_FILE = generate_output_filename("png")


# ============================================================================
# PROCESSAMENTO
# ============================================================================

def main():
    """
    Função principal para executar o processo completo de geração da grade.
    """
    
    print("="*70)
    print(" GERADOR DE GRADE BATIMÉTRICA PARA MODELO POM")
    print("="*70)
    print(f"Versão: 2.0 (Paralelizada)")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    # Garantir que o diretório de saída existe
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    
    try:
        # 1. Inicializar gerador
        if globals().get('SPACING_LON') is not None and globals().get('SPACING_LAT') is not None:
            generator = BathymetryGridGenerator(
                GEBCO_FILE,
                spacing_lon=globals().get('SPACING_LON'),
                spacing_lat=globals().get('SPACING_LAT'),
                n_workers=N_WORKERS
            )
        else:
            generator = BathymetryGridGenerator(
                GEBCO_FILE,
                spacing=GRID_SPACING,
                n_workers=N_WORKERS
            )

        # 2. Carregar dados do GEBCO
        if not generator.load_gebco_data():
            print("\nERRO: Falha ao carregar dados do GEBCO")
            return 1

        # 3. Definir extensão da grade
        generator.define_grid_extent(LON_MIN, LON_MAX, LAT_MIN, LAT_MAX)

        # 4. Interpolar batimetria
        if not generator.interpolate_bathymetry(method=INTERPOLATION_METHOD, parallel=USE_PARALLEL):
            print("\nERRO: Falha na interpolação")
            return 1

        # 5. Exportar para ASCII (formato POM - 5 colunas)
        if not generator.export_to_ascii(OUTPUT_FILE):
            print("\nERRO: Falha ao exportar arquivo")
            return 1

        # 6. Gerar visualização (opcional)
        if GENERATE_PLOT:
            generator.plot_bathymetry(PLOT_FILE)

        # 7. Limpeza
        generator.cleanup()

        print("\n" + "="*70)
        print(" PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print(f"\nArquivo de saída: {OUTPUT_FILE}")
        if GENERATE_PLOT:
            print(f"Visualização: {PLOT_FILE}")
        print("\nPróximos passos:")
        print(f"  - Para editar a grade: ./ocean-tools.sh edit {os.path.basename(OUTPUT_FILE)}")
        print(f"  - Use a grade em seu modelo oceânico: {os.path.basename(OUTPUT_FILE)}")
        print("="*70 + "\n")

        return 0

    except Exception as e:
        print(f"\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
