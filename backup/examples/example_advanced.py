#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo 2: Grade de alta resolução com processamento customizado
===============================================================
"""

import sys
import os
import numpy as np
from scipy.ndimage import gaussian_filter

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bathymetry_generator import BathymetryGridGenerator

# Configuração
GEBCO_FILE = "../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"
OUTPUT_DIR = "../output"

os.makedirs(OUTPUT_DIR, exist_ok=True)

# Criar gerador com alta resolução
generator = BathymetryGridGenerator(GEBCO_FILE, spacing=0.1, n_workers=4)

# Processar
generator.load_gebco_data()
generator.define_grid_extent(-50.0, -45.0, -28.0, -23.0)  # Santa Catarina
generator.interpolate_bathymetry(method='linear', parallel=True)

# Processamento customizado: suavizar batimetria
print("\nAplicando suavização gaussiana...")
generator.depth_grid = gaussian_filter(generator.depth_grid, sigma=1)

# Definir profundidade mínima
print("Definindo profundidade mínima de 10m...")
generator.depth_grid = np.maximum(generator.depth_grid, 10)

# Exportar
generator.export_to_ascii(os.path.join(OUTPUT_DIR, "santa_catarina_suavizada.asc"))
generator.plot_bathymetry(os.path.join(OUTPUT_DIR, "santa_catarina_suavizada.png"))
generator.cleanup()

print("\n✓ Exemplo com processamento customizado concluído!")
