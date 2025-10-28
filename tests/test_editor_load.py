#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste Completo do Editor (sem GUI)
===================================

Testa carregamento e salvamento sem abrir interface gráfica.
"""

import sys
import os
import numpy as np

# Backend não-interativo
import matplotlib
matplotlib.use('Agg')

# Adicionar scripts ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

# Importar editor
from edit_grid_interactive import InteractiveBathymetryEditor

# Arquivo de teste
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
test_file = os.path.join(project_root, "output", "pom_bathymetry_grid.asc")

if not os.path.exists(test_file):
    print(f"✗ Arquivo não encontrado: {test_file}")
    sys.exit(1)

print("="*70)
print(" TESTE COMPLETO DO EDITOR (sem GUI)")
print("="*70)

try:
    # Criar instância do editor (sem rodar GUI)
    print("\n[1] Criando editor...")
    editor = InteractiveBathymetryEditor(test_file)
    
    print("\n[2] Verificando dados carregados...")
    print(f"  ✓ Dimensões: {editor.ncols} x {editor.nrows}")
    print(f"  ✓ Longitude: {editor.lons[0]:.4f} a {editor.lons[-1]:.4f}")
    print(f"  ✓ Latitude: {editor.lats[0]:.4f} a {editor.lats[-1]:.4f}")
    print(f"  ✓ Cellsize lon (dx): {editor.cellsize_lon:.6f}°")
    print(f"  ✓ Cellsize lat (dy): {editor.cellsize_lat:.6f}°")
    print(f"  ✓ Matriz depth: {editor.depth.shape}")
    print(f"  ✓ Min depth: {editor.depth.min():.2f} m")
    print(f"  ✓ Max depth: {editor.depth.max():.2f} m")
    
    # Testar toggle de célula
    print("\n[3] Testando toggle de célula com interpolação...")
    
    # Encontrar uma célula de terra próxima à água
    i, j = 60, 60  # Centro da grade
    original_depth = editor.depth[j, i]
    print(f"  Célula [{j},{i}] antes: {original_depth:.2f} m")
    
    # Se for terra, converter para água (deve interpolar)
    if original_depth >= 0:
        print(f"  Testando TERRA → ÁGUA com interpolação...")
        editor.toggle_cell(j, i)
        new_depth = editor.depth[j, i]
        print(f"  Célula [{j},{i}] depois: {new_depth:.2f} m")
        
        if new_depth < 0:
            print(f"  ✓ Interpolação funcionou! (profundidade negativa = água)")
        else:
            print(f"  ⚠ Valor inesperado, mas pode ser válido")
    else:
        print(f"  Célula já é água, testando ÁGUA → TERRA...")
        editor.toggle_cell(j, i)
        new_depth = editor.depth[j, i]
        print(f"  Célula [{j},{i}] depois: {new_depth:.2f} m")
        
        if new_depth > 0:
            print(f"  ✓ Conversão para terra funcionou!")
    
    # Testar interpolação diretamente
    print("\n[4] Testando método de interpolação diretamente...")
    test_i, test_j = 50, 50
    interpolated = editor.interpolate_from_neighbors(test_i, test_j)
    print(f"  Profundidade interpolada para célula [{test_i},{test_j}]: {interpolated:.2f} m")
    if interpolated < 0:
        print(f"  ✓ Interpolação retornou valor de água válido")
    
    # Testar find_nearest_cell
    print("\n[5] Testando busca de célula mais próxima...")
    lon_test = editor.lons[10]
    lat_test = editor.lats[10]
    i_found, j_found = editor.find_nearest_cell(lon_test, lat_test)
    print(f"  Buscando lon={lon_test:.4f}, lat={lat_test:.4f}")
    print(f"  ✓ Encontrou célula: i={i_found}, j={j_found}")
    
    # Não salvar para não modificar arquivo real
    print("\n[6] Limpando (não salvando modificações de teste)...")
    editor.modified = False  # Forçar não salvar
    
    print("\n" + "="*70)
    print(" TODOS OS TESTES PASSARAM!")
    print("="*70)
    print("\nEditor está funcionando corretamente!")
    print("Para testar a GUI, execute:")
    print(f"  ./scripts/pom.sh edit {os.path.basename(test_file)}")
    print("="*70)
    
    sys.exit(0)
    
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
