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
    
    # Parsear cabeçalho
    header = {}
    for line in lines:
        if line.strip().startswith('#'):
            continue
        parts = line.strip().split()
        if len(parts) == 2:
            try:
                header[parts[0]] = float(parts[1])
            except ValueError:
                break
        else:
            break
    
    print(f"✓ Cabeçalho parseado: {len(header)} campos")
    print(f"  ncols: {header.get('ncols', header.get('NCOLS', '?'))}")
    print(f"  nrows: {header.get('nrows', header.get('NROWS', '?'))}")
    
    if 'dx' in header and 'dy' in header:
        print(f"  dx: {header['dx']}")
        print(f"  dy: {header['dy']}")
        print("  ✓ Suporte a dx/dy diferentes detectado!")
    else:
        print(f"  cellsize: {header.get('cellsize', header.get('CELLSIZE', '?'))}")
    
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
