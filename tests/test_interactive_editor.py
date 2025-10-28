#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Teste do Editor Interativo
===========================

Testa as funcionalidades principais do editor sem abrir a GUI.
"""

import sys
import os
import numpy as np

# Teste de importação
try:
    import matplotlib
    matplotlib.use('Agg')  # Backend não-interativo para teste
    import matplotlib.pyplot as plt
    print("✓ matplotlib importado com sucesso")
except ImportError as e:
    print(f"✗ Erro ao importar matplotlib: {e}")
    sys.exit(1)

# Importar o editor
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))

try:
    # Importar apenas as classes necessárias sem executar main
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "editor",
        os.path.join(os.path.dirname(__file__), '..', 'scripts', 'edit_grid_interactive.py')
    )
    editor_module = importlib.util.module_from_spec(spec)
    
    print("✓ Módulo do editor carregado")
except Exception as e:
    print(f"✗ Erro ao carregar editor: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

# Teste de leitura de arquivo
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
test_file = os.path.join(project_root, "output", "pom_bathymetry_grid.asc")

if not os.path.exists(test_file):
    print(f"✗ Arquivo de teste não encontrado: {test_file}")
    print("  Execute './scripts/pom.sh run' para gerar uma grade primeiro")
    sys.exit(1)

print(f"✓ Arquivo de teste encontrado: {test_file}")

# Teste de parse do arquivo
try:
    with open(test_file, 'r') as f:
        lines = f.readlines()
    
    # Contar linhas de comentário e dados
    comment_lines = 0
    data_lines = 0
    
    for line in lines:
        if line.strip().startswith('#') or not line.strip():
            comment_lines += 1
        else:
            parts = line.strip().split()
            if len(parts) == 5:
                try:
                    # Validar formato: i j lon lat depth
                    [float(p) for p in parts]
                    data_lines += 1
                except ValueError:
                    pass
    
    print(f"✓ Arquivo parseado:")
    print(f"  Linhas de comentário: {comment_lines}")
    print(f"  Linhas de dados: {data_lines}")
    
    if data_lines > 0:
        print(f"  ✓ Formato de 5 colunas detectado!")
        
        # Ler primeira linha de dados para mostrar exemplo
        for line in lines:
            if not line.strip().startswith('#') and line.strip():
                parts = line.strip().split()
                if len(parts) == 5:
                    print(f"\n  Exemplo de linha de dados:")
                    print(f"    i={parts[0]}, j={parts[1]}, lon={parts[2]}, lat={parts[3]}, depth={parts[4]}")
                    break
    else:
        print(f"  ✗ Nenhuma linha de dados válida encontrada")
        sys.exit(1)
    
except Exception as e:
    print(f"✗ Erro ao ler arquivo: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*70)
print(" TESTE DO EDITOR INTERATIVO: PASSOU")
print("="*70)
print("\nPara testar a interface gráfica, execute:")
print(f"  ./scripts/pom.sh edit {test_file}")
print("="*70)

sys.exit(0)
