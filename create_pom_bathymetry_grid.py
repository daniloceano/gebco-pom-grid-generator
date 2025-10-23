#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Compatibilidade: módulo shim para manter a API antiga
---------------------------------------------------

Este arquivo reexporta a classe BathymetryGridGenerator do pacote
`src.bathymetry_generator` para manter compatibilidade com scripts e
testes que importam `create_pom_bathymetry_grid`.

Você pode modificar o comportamento CLI abaixo se desejar manter a
versão antiga do script principal.
"""

from src.bathymetry_generator import BathymetryGridGenerator

__all__ = ["BathymetryGridGenerator"]


def main():
    # Pequeno CLI de compatibilidade que apenas mostra como usar a classe.
    import argparse
    parser = argparse.ArgumentParser(description="Shim CLI para BathymetryGridGenerator")
    parser.add_argument('--info', action='store_true', help='Mostrar info do shim e sair')
    args = parser.parse_args()
    if args.info:
        print("Este é um shim que reexporta BathymetryGridGenerator do pacote src.")
        print("Importe diretamente de src.bathymetry_generator para uso avançado.")


if __name__ == '__main__':
    main()
