#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compatibilidade: módulo shim para manter a API antiga
---------------------------------------------------

Este arquivo mantém compatibilidade com scripts antigos que importam
`create_pom_bathymetry_grid`. 

IMPORTANTE: Este é apenas um arquivo de compatibilidade legado.
Para novos scripts, use diretamente:
    from tools.gebco_interpolation.src.bathymetry_generator import BathymetryGridGenerator

Ou execute o script principal:
    tools/gebco_interpolation/scripts/generate_grid.py
"""

import sys
import os

# Adicionar diretório src ao path (compatibilidade com estrutura antiga)
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'tools', 'gebco_interpolation', 'src'))

try:
    from bathymetry_generator import BathymetryGridGenerator
    __all__ = ["BathymetryGridGenerator"]
except ImportError:
    # Fallback para estrutura antiga se ainda existir
    try:
        from src.bathymetry_generator import BathymetryGridGenerator
        __all__ = ["BathymetryGridGenerator"]
    except ImportError:
        print("ERRO: Não foi possível importar BathymetryGridGenerator")
        print("Estrutura esperada: tools/gebco_interpolation/src/bathymetry_generator.py")
        sys.exit(1)


def main():
    """CLI de compatibilidade que redireciona para o script correto."""
    print("=" * 70)
    print(" AVISO: Script Legado")
    print("=" * 70)
    print()
    print("Este script (create_pom_bathymetry_grid.py) é apenas para")
    print("compatibilidade com a estrutura antiga do projeto.")
    print()
    print("Para gerar grades, use o script principal:")
    print()
    print("  cd tools/gebco_interpolation/scripts")
    print("  python generate_grid.py")
    print()
    print("Ou use o script mestre:")
    print()
    print("  ./ocean-tools.sh gebco")
    print()
    print("Documentação: tools/gebco_interpolation/README.md")
    print("=" * 70)


if __name__ == '__main__':
    main()
