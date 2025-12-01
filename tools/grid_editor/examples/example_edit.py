#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo de Uso do Grid Editor
==============================

Demonstra como usar o editor de grades programaticamente.
"""

import sys
import os

# Adicionar src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from grid_editor import GridEditor

# Arquivo de exemplo
# Ajuste o caminho conforme necessário
grid_file = "../../../output/pom_bathymetry_grid.asc"

if not os.path.exists(grid_file):
    print(f"Erro: Arquivo não encontrado: {grid_file}")
    print("\nGere uma grade primeiro:")
    print("  cd ../../gebco_interpolation/scripts")
    print("  python generate_grid.py")
    sys.exit(1)

print("="*70)
print(" EXEMPLO: Editor de Grades")
print("="*70)
print()

# Criar editor
print("Criando editor...")
editor = GridEditor(
    grid_file,
    use_cartopy=True,      # Usar linha de costa real
    show_contours=True     # Mostrar contornos batimétricos
)

print("\nEditor criado com sucesso!")
print(f"Grade: {len(editor.lats)} x {len(editor.lons)} pontos")
print(f"Extensão: Lon [{editor.lons.min():.2f}, {editor.lons.max():.2f}]")
print(f"          Lat [{editor.lats.min():.2f}, {editor.lats.max():.2f}]")
print()

# Exemplo de modificação programática (opcional)
if False:  # Mude para True para testar modificação automática
    print("Exemplo de modificação programática:")
    print("  Convertendo célula (10, 10) terra → água")
    editor.toggle_cell(10, 10)
    print("  Salvando...")
    editor.save()
    print("  Pronto!")
    print()

# Mostrar interface
print("Abrindo interface gráfica...")
print("Use os controles:")
print("  • Click: alternar terra/água")
print("  • +/-: zoom")
print("  • g: toggle grade")
print("  • c: toggle linha de costa")
print("  • b: toggle contornos")
print("  • s: salvar")
print("  • q: sair")
print()

editor.show()
