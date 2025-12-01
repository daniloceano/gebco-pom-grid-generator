#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste de Interpolação com Células Reais
========================================

Testa a interpolação em uma região com água.
"""

import sys
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, os.path.join(project_root, 'tools', 'gebco_interpolation', 'scripts'))
from edit_grid_interactive import InteractiveBathymetryEditor

test_file = os.path.join(project_root, "output", "pom_bathymetry_grid.asc")

print("="*70)
print(" TESTE DE INTERPOLAÇÃO COM CÉLULAS OCEÂNICAS")
print("="*70)

try:
    # Carregar editor
    print("\n[1] Carregando grade...")
    editor = InteractiveBathymetryEditor(test_file)
    
    # Encontrar uma célula com água (profundidade > 0 no formato POM!)
    print("\n[2] Procurando células oceânicas...")
    ocean_cells = []
    for i in range(editor.nrows):
        for j in range(editor.ncols):
            if editor.depth[i, j] > 10:  # Água com pelo menos 10m de profundidade
                ocean_cells.append((i, j, editor.depth[i, j]))
                if len(ocean_cells) >= 10:
                    break
        if len(ocean_cells) >= 10:
            break
    
    if len(ocean_cells) == 0:
        print("  ✗ Nenhuma célula oceânica encontrada!")
        sys.exit(1)
    
    print(f"  ✓ Encontradas {len(ocean_cells)} células oceânicas")
    print(f"  Exemplos:")
    for idx, (i, j, depth) in enumerate(ocean_cells[:3]):
        print(f"    [{i},{j}]: lon={editor.lons[j]:.2f}, lat={editor.lats[i]:.2f}, depth={depth:.1f}m")
    
    # Testar interpolação em célula adjacente
    print("\n[3] Testando interpolação em célula adjacente à água...")
    test_i, test_j = ocean_cells[0][0], ocean_cells[0][1]
    
    # Procurar célula de terra próxima (profundidade == 0)
    found_land = False
    for di in range(-2, 3):
        for dj in range(-2, 3):
            ni, nj = test_i + di, test_j + dj
            if 0 <= ni < editor.nrows and 0 <= nj < editor.ncols:
                if editor.depth[ni, nj] == 0:  # Terra (profundidade zero)
                    # Verificar se tem água ao redor
                    has_water_neighbor = False
                    for ddi in [-1, 0, 1]:
                        for ddj in [-1, 0, 1]:
                            nni, nnj = ni + ddi, nj + ddj
                            if 0 <= nni < editor.nrows and 0 <= nnj < editor.ncols:
                                if editor.depth[nni, nnj] > 0:  # Água
                                    has_water_neighbor = True
                                    break
                        if has_water_neighbor:
                            break
                    
                    if has_water_neighbor:
                        test_i, test_j = ni, nj
                        found_land = True
                        break
        if found_land:
            break
    
    if not found_land:
        print("  Não encontrou célula de terra próxima à água, usando célula oceânica")
        test_i, test_j = ocean_cells[0][0] + 1, ocean_cells[0][1] + 1
    
    original_depth = editor.depth[test_i, test_j]
    print(f"  Célula de teste [{test_i},{test_j}]:")
    print(f"    lon={editor.lons[test_j]:.4f}, lat={editor.lats[test_i]:.4f}")
    print(f"    Profundidade original: {original_depth:.2f}m")
    
    # Testar interpolação
    print("\n[4] Interpolando profundidade...")
    interpolated = editor.interpolate_from_neighbors(test_i, test_j, max_radius=5)
    print(f"  Profundidade interpolada: {interpolated:.2f}m")
    
    if interpolated > 0:
        print(f"  ✓ Interpolação bem-sucedida! (água = profundidade > 0)")
        
        # Mostrar vizinhos usados
        print(f"\n[5] Analisando vizinhos usados na interpolação...")
        count = 0
        for radius in range(1, 6):
            for di in range(-radius, radius + 1):
                for dj in range(-radius, radius + 1):
                    if di == 0 and dj == 0:
                        continue
                    ni, nj = test_i + di, test_j + dj
                    if 0 <= ni < editor.nrows and 0 <= nj < editor.ncols:
                        if editor.depth[ni, nj] > 0:  # Água
                            dist = np.sqrt(di**2 + dj**2)
                            if count < 5:  # Mostrar apenas primeiros 5
                                print(f"    Vizinho [{ni},{nj}]: depth={editor.depth[ni, nj]:.1f}m, dist={dist:.2f}")
                            count += 1
        print(f"  Total de vizinhos com água encontrados: {count}")
    else:
        print(f"  ⚠ Interpolação retornou terra (sem vizinhos com água suficientes)")
    
    # Testar toggle
    print("\n[6] Testando toggle com interpolação...")
    if original_depth == 0:  # Terra
        print(f"  Convertendo TERRA → ÁGUA...")
        editor.toggle_cell(test_i, test_j)
        new_depth = editor.depth[test_i, test_j]
        print(f"  Nova profundidade: {new_depth:.2f}m")
        
        if abs(new_depth - interpolated) < 0.01:
            print(f"  ✓ Toggle usou interpolação corretamente!")
        else:
            print(f"  ⚠ Toggle não usou valor interpolado (esperado={interpolated:.2f}, obtido={new_depth:.2f})")
    
    editor.modified = False  # Não salvar
    
    print("\n" + "="*70)
    print(" TESTE DE INTERPOLAÇÃO CONCLUÍDO!")
    print("="*70)
    
except Exception as e:
    print(f"\n✗ ERRO: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
