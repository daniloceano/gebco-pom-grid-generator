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
# Se executar de tools/gebco_interpolation/scripts/, usar caminho relativo
# Se executar da raiz do projeto, usar caminho direto
GEBCO_FILE = os.path.join(os.path.dirname(__file__), "../../../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc")
GEBCO_FILE = os.path.abspath(GEBCO_FILE)

# Espaçamento da grade em graus decimais
# Use SPACING_LON (dx) e SPACING_LAT (dy) para espaçamentos diferentes
# ou defina apenas GRID_SPACING para usar o mesmo valor em ambas direções
SPACING_LON = 0.3  # dx em graus
SPACING_LAT = 0.3  # dy em graus

# Extensão geográfica da grade
# TESTE: Região pequena cruzando a linha de data (±180°)
# Pacífico equatorial: 178°E a 178°W (= -178°)
LON_MIN = 178.0    # Longitude oeste (178°E)
LON_MAX = -178.0   # Longitude leste (178°W) - CRUZA ±180°
LAT_MIN = -5.0     # Latitude sul
LAT_MAX = 5.0      # Latitude norte

# Para grade global, use:
# LON_MIN = -180.0
# LON_MAX = 180.0
# LAT_MIN = -90.0
# LAT_MAX = 90.0

# Diretório de saída
OUTPUT_DIR = os.path.join(os.path.dirname(__file__), "../../../output")
OUTPUT_DIR = os.path.abspath(OUTPUT_DIR)

# Método de interpolação: 'linear', 'nearest', ou 'cubic'
INTERPOLATION_METHOD = 'linear'

# Usar processamento paralelo?
USE_PARALLEL = True

# Número de workers (None = auto)
N_WORKERS = None

# Função para gerar nome de arquivo de saída conforme configurações
def generate_output_filename(ext="asc"):
    # Espaçamento - usa SPACING_LON/LAT se definidos, senão usa GRID_SPACING padrão
    dx = globals().get('SPACING_LON', globals().get('GRID_SPACING', 0.25))
    dy = globals().get('SPACING_LAT', globals().get('GRID_SPACING', 0.25))
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
