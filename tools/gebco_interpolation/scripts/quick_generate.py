#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de uso rápido para geração de grade batimétrica POM
=========================================================

Interface de linha de comando para gerar grades rapidamente.

Uso:
    python quick_generate.py [opções]
    
Exemplos:
    python quick_generate.py --region brasil_sul
    python quick_generate.py --lon-min -60 --lon-max -30 --lat-min -35 --lat-max -5
"""

import argparse
import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from bathymetry_generator import BathymetryGridGenerator


def parse_arguments():
    """Processa argumentos de linha de comando."""
    parser = argparse.ArgumentParser(
        description='Gera grade batimétrica para modelo POM a partir do GEBCO',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Usar região pré-definida
  python quick_generate.py --region brasil_sul

  # Especificar região customizada
  python quick_generate.py --lon-min -55 --lon-max -40 --lat-min -30 --lat-max -20

  # Mudar espaçamento e desabilitar paralelização
  python quick_generate.py --region brasil_sul --spacing 0.1 --no-parallel

Regiões pré-definidas:
  - brasil_sul: Sul/Sudeste do Brasil
  - brasil_nordeste: Nordeste do Brasil
  - atlantico_sw: Atlântico Sul-Ocidental
        """
    )
    
    parser.add_argument('--gebco-file', type=str, 
                       default='../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc',
                       help='Caminho para arquivo GEBCO NetCDF')
    
    parser.add_argument('--lon-min', type=float, help='Longitude mínima (oeste)')
    parser.add_argument('--lon-max', type=float, help='Longitude máxima (leste)')
    parser.add_argument('--lat-min', type=float, help='Latitude mínima (sul)')
    parser.add_argument('--lat-max', type=float, help='Latitude máxima (norte)')
    
    parser.add_argument('--spacing', type=float, default=0.25,
                       help='Espaçamento da grade em graus (padrão: 0.25)')
    
    parser.add_argument('--output', type=str, default='../output/pom_grid.asc',
                       help='Arquivo de saída ASCII')
    
    parser.add_argument('--plot-output', type=str, default='../output/pom_grid.png',
                       help='Arquivo de saída da visualização')
    
    parser.add_argument('--no-plot', action='store_true',
                       help='Não gerar visualização')
    
    parser.add_argument('--method', type=str, default='linear',
                       choices=['linear', 'nearest', 'cubic'],
                       help='Método de interpolação (padrão: linear)')
    
    parser.add_argument('--region', type=str,
                       choices=['brasil_sul', 'brasil_nordeste', 'atlantico_sw'],
                       help='Usar região pré-definida')
    
    parser.add_argument('--no-parallel', action='store_true',
                       help='Desabilitar processamento paralelo')
    
    parser.add_argument('--workers', type=int, default=None,
                       help='Número de workers para processamento paralelo')
    
    return parser.parse_args()


def get_predefined_region(region_name):
    """Retorna coordenadas de regiões pré-definidas."""
    regions = {
        'brasil_sul': (-55.0, -40.0, -30.0, -20.0),
        'brasil_nordeste': (-45.0, -32.0, -18.0, -3.0),
        'atlantico_sw': (-60.0, -30.0, -45.0, -10.0),
    }
    return regions.get(region_name)


def main():
    """Função principal."""
    args = parse_arguments()
    
    # Determinar coordenadas
    if args.region:
        coords = get_predefined_region(args.region)
        if coords is None:
            print(f"ERRO: Região '{args.region}' não reconhecida")
            return 1
        lon_min, lon_max, lat_min, lat_max = coords
        print(f"\n✓ Usando região pré-definida: {args.region}")
    elif all([args.lon_min, args.lon_max, args.lat_min, args.lat_max]):
        lon_min = args.lon_min
        lon_max = args.lon_max
        lat_min = args.lat_min
        lat_max = args.lat_max
    else:
        print("\n⚠️  Coordenadas não especificadas. Usando valores padrão")
        lon_min, lon_max = -60.0, -30.0
        lat_min, lat_max = -35.0, -5.0
    
    print("\n" + "="*70)
    print(" GERAÇÃO RÁPIDA DE GRADE BATIMÉTRICA")
    print("="*70)
    print(f"\nParâmetros:")
    print(f"  Arquivo GEBCO: {args.gebco_file}")
    print(f"  Região: Lon [{lon_min}°, {lon_max}°], Lat [{lat_min}°, {lat_max}°]")
    print(f"  Espaçamento: {args.spacing}°")
    print(f"  Método: {args.method}")
    print(f"  Paralelo: {'Não' if args.no_parallel else 'Sim'}")
    print(f"  Saída: {args.output}")
    if not args.no_plot:
        print(f"  Visualização: {args.plot_output}")
    print("="*70)
    
    # Garantir que diretório de saída existe
    os.makedirs(os.path.dirname(args.output), exist_ok=True)
    
    try:
        # Criar gerador
        generator = BathymetryGridGenerator(
            args.gebco_file, 
            spacing=args.spacing,
            n_workers=args.workers
        )
        
        # Carregar dados
        if not generator.load_gebco_data():
            return 1
        
        # Definir grade
        generator.define_grid_extent(lon_min, lon_max, lat_min, lat_max)
        
        # Interpolar
        if not generator.interpolate_bathymetry(
            method=args.method, 
            parallel=not args.no_parallel
        ):
            return 1
        
        # Exportar
        if not generator.export_to_ascii(args.output):
            return 1
        
        # Visualizar
        if not args.no_plot:
            generator.plot_bathymetry(args.plot_output)
        
        # Limpar
        generator.cleanup()
        
        print("\n" + "="*70)
        print(" ✓ CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print(f"\nArquivo pronto: {args.output}")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
