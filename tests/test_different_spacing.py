#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Espaçamentos Diferentes (dx ≠ dy)
==========================================

Este script testa a funcionalidade de espaçamentos diferentes
para longitude e latitude.

Autor: Projeto POM
Data: Outubro 2025
"""

import sys
import os

# Adicionar nova estrutura ao path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(project_root, 'tools', 'gebco_interpolation', 'src'))

from bathymetry_generator import BathymetryGridGenerator
import numpy as np


def test_different_spacing():
    """
    Testa geração com dx ≠ dy
    """
    print("="*70)
    print(" TESTE: Espaçamentos Diferentes (dx ≠ dy)")
    print("="*70)
    
    # Caminho do GEBCO
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    gebco_file = os.path.join(project_root, "gebco_2025_sub_ice_topo", "GEBCO_2025_sub_ice.nc")
    
    if not os.path.exists(gebco_file):
        print(f"\n✗ ERRO: Arquivo GEBCO não encontrado: {gebco_file}")
        return False
    
    try:
        # Teste 1: Inicialização com spacing_lon e spacing_lat
        print("\n[Teste 1] Inicializando com spacing_lon=0.5, spacing_lat=0.3...")
        gen1 = BathymetryGridGenerator(
            gebco_file,
            spacing_lon=0.5,
            spacing_lat=0.3,
            n_workers=2
        )
        
        assert gen1.spacing_lon == 0.5, "spacing_lon incorreto"
        assert gen1.spacing_lat == 0.3, "spacing_lat incorreto"
        print("✓ Inicialização com dx ≠ dy: OK")
        
        # Teste 2: Inicialização com spacing único (compatibilidade)
        print("\n[Teste 2] Inicializando com spacing=0.25 (modo compatibilidade)...")
        gen2 = BathymetryGridGenerator(
            gebco_file,
            spacing=0.25,
            n_workers=2
        )
        
        assert gen2.spacing_lon == 0.25, "spacing_lon deveria ser 0.25"
        assert gen2.spacing_lat == 0.25, "spacing_lat deveria ser 0.25"
        print("✓ Modo compatibilidade (spacing único): OK")
        
        # Teste 3: Definir extensão e verificar grade
        print("\n[Teste 3] Definindo extensão da grade...")
        gen1.load_gebco_data()
        gen1.define_grid_extent(-50, -45, -25, -20)
        
        # Verificar dimensões
        expected_nlons = int(np.ceil((-45 - (-50)) / 0.5)) + 1
        expected_nlats = int(np.ceil((-20 - (-25)) / 0.3)) + 1
        
        actual_nlons = len(gen1.grid_lons)
        actual_nlats = len(gen1.grid_lats)
        
        print(f"  Esperado: {expected_nlons} lons x {expected_nlats} lats")
        print(f"  Obtido:   {actual_nlons} lons x {actual_nlats} lats")
        
        # Aceitar pequenas diferenças devido a arredondamento
        assert abs(actual_nlons - expected_nlons) <= 1, "Número de longitudes incorreto"
        assert abs(actual_nlats - expected_nlats) <= 1, "Número de latitudes incorreto"
        print("✓ Dimensões da grade: OK")
        
        # Teste 4: Verificar espaçamento real
        print("\n[Teste 4] Verificando espaçamento real da grade...")
        lon_spacing = np.diff(gen1.grid_lons)
        lat_spacing = np.diff(gen1.grid_lats)
        
        avg_lon_spacing = np.mean(lon_spacing)
        avg_lat_spacing = np.mean(lat_spacing)
        
        print(f"  dx médio: {avg_lon_spacing:.6f}° (esperado: 0.5°)")
        print(f"  dy médio: {avg_lat_spacing:.6f}° (esperado: 0.3°)")
        
        assert abs(avg_lon_spacing - 0.5) < 0.001, "Espaçamento lon incorreto"
        assert abs(avg_lat_spacing - 0.3) < 0.001, "Espaçamento lat incorreto"
        print("✓ Espaçamento da grade: OK")
        
        # Cleanup
        gen1.cleanup()
        gen2.cleanup()
        
        print("\n" + "="*70)
        print(" TODOS OS TESTES PASSARAM!")
        print("="*70)
        return True
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == '__main__':
    success = test_different_spacing()
    sys.exit(0 if success else 1)
