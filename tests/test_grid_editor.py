#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Grid Editor
====================

Testa funcionalidades do editor sem abrir GUI.
"""

import sys
import os
import numpy as np

# Backend não-interativo
import matplotlib
matplotlib.use('Agg')

# Adicionar ao path
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(project_root, 'tools', 'grid_editor', 'src'))

from grid_editor import GridEditor

# Arquivo de teste
test_file = os.path.join(project_root, "output", "pom_bathymetry_grid.asc")

print("="*70)
print(" TESTE DO GRID EDITOR")
print("="*70)

if not os.path.exists(test_file):
    print(f"\n⚠ Arquivo de teste não encontrado: {test_file}")
    print("Execute o gerador de grade primeiro:")
    print("  cd tools/gebco_interpolation/scripts")
    print("  python generate_grid.py")
    sys.exit(0)

try:
    # Teste 1: Carregar grade
    print("\n[Teste 1] Carregando grade...")
    editor = GridEditor(test_file, use_cartopy=False, show_contours=False)
    print(f"✓ Grade carregada: {len(editor.lats)} x {len(editor.lons)} pontos")
    
    # Teste 2: Verificar dados carregados
    print("\n[Teste 2] Verificando dados...")
    assert len(editor.lons) > 0, "Lons vazios"
    assert len(editor.lats) > 0, "Lats vazios"
    assert editor.depth.shape == (len(editor.lats), len(editor.lons)), "Shape incorreto"
    print(f"✓ Formato correto: {editor.depth.shape}")
    print(f"✓ Range profundidade: [{editor.depth.min():.1f}, {editor.depth.max():.1f}] m")
    
    # Teste 3: Encontrar célula
    print("\n[Teste 3] Testando find_nearest_cell...")
    lon_test = editor.lons[len(editor.lons)//2]
    lat_test = editor.lats[len(editor.lats)//2]
    i, j = editor.find_nearest_cell(lon_test, lat_test)
    print(f"✓ Célula encontrada: i={i}, j={j}")
    print(f"  Coordenadas: ({editor.lons[j]:.2f}, {editor.lats[i]:.2f})")
    
    # Teste 4: Testar interpolação
    print("\n[Teste 4] Testando interpolação...")
    # Encontrar uma célula de água
    water_cells = np.where(editor.depth > 0)
    if len(water_cells[0]) > 0:
        i_water = water_cells[0][0]
        j_water = water_cells[1][0]
        
        # Testar interpolação nessa região
        interpolated = editor.interpolate_from_neighbors(i_water, j_water, max_radius=3)
        print(f"✓ Interpolação funcionou: {interpolated:.2f}m")
        assert interpolated > 0, "Interpolação retornou valor inválido"
    else:
        print("⚠ Nenhuma célula de água encontrada")
    
    # Teste 5: Toggle célula (sem salvar)
    print("\n[Teste 5] Testando toggle de célula...")
    depth_before = editor.depth[i, j]
    editor.toggle_cell(i, j)
    depth_after = editor.depth[i, j]
    
    assert depth_before != depth_after, "Toggle não modificou célula"
    print(f"✓ Toggle funcionou: {depth_before:.1f}m → {depth_after:.1f}m")
    print(f"✓ Modified flag: {editor.modified}")
    
    # Teste 6: Verificar cartopy
    print("\n[Teste 6] Verificando disponibilidade do Cartopy...")
    try:
        import cartopy
        print(f"✓ Cartopy instalado: versão {cartopy.__version__}")
        HAS_CARTOPY = True
    except ImportError:
        print("⚠ Cartopy não instalado (opcional)")
        print("  Para instalar: conda install -c conda-forge cartopy")
        HAS_CARTOPY = False
    
    # Teste 7: Criar editor com cartopy (se disponível)
    if HAS_CARTOPY:
        print("\n[Teste 7] Testando editor com Cartopy...")
        editor_cart = GridEditor(test_file, use_cartopy=True, show_contours=True)
        print(f"✓ Editor com Cartopy criado")
        print(f"✓ Projeção: {editor_cart.projection}")
    
    print("\n" + "="*70)
    print(" ✓ TODOS OS TESTES PASSARAM!")
    print("="*70)
    print("\nO editor está pronto para uso:")
    print(f"  cd tools/grid_editor/scripts")
    print(f"  python edit_grid.py {test_file}")
    print("\nOu via ocean-tools.sh:")
    print(f"  ./ocean-tools.sh edit output/pom_bathymetry_grid.asc")
    print("="*70 + "\n")
    
except Exception as e:
    print(f"\n❌ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
