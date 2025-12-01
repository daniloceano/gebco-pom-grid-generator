#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo 1: Geração básica de grade para costa brasileira sul
===========================================================
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bathymetry_generator import BathymetryGridGenerator

# Configuração
GEBCO_FILE = "../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"
OUTPUT_DIR = "../output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Criar gerador
generator = BathymetryGridGenerator(GEBCO_FILE, spacing=0.25)

# Processar
generator.load_gebco_data()
generator.define_grid_extent(-55.0, -40.0, -30.0, -20.0)  # Costa Sul
generator.interpolate_bathymetry(method='linear', parallel=True)
generator.export_to_ascii(os.path.join(OUTPUT_DIR, "brasil_sul.asc"))
generator.plot_bathymetry(os.path.join(OUTPUT_DIR, "brasil_sul.png"))
generator.cleanup()

print("\n✓ Exemplo concluído! Veja os arquivos em output/")
