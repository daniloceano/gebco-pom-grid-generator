#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script simplificado para gerar grade batimétrica POM
====================================================

Este é um script de uso rápido que utiliza a classe BathymetryGridGenerator
para casos comuns. Execute diretamente ou modifique os parâmetros conforme
necessário.

Uso rápido:
    python quick_generate_grid.py

Ou com argumentos de linha de comando:
    python quick_generate_grid.py --lon-min -60 --lon-max -30 --lat-min -35 --lat-max -5 --spacing 0.25
"""

import argparse
import sys
from create_pom_bathymetry_grid import BathymetryGridGenerator


def parse_arguments():
    """
    Processa argumentos de linha de comando.
    """
    parser = argparse.ArgumentParser(
        description='Gera grade batimétrica para modelo POM a partir do GEBCO',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos de uso:

  # Usar configurações padrão
  python quick_generate_grid.py

  # Especificar região customizada
  python quick_generate_grid.py --lon-min -55 --lon-max -40 --lat-min -30 --lat-max -20

  # Mudar espaçamento
  python quick_generate_grid.py --spacing 0.1

  # Especificar arquivo de saída
  python quick_generate_grid.py --output minha_grade.asc

  # Sem visualização
  python quick_generate_grid.py --no-plot

Regiões pré-definidas (use --region):
  - brasil_sul: Sul/Sudeste do Brasil (-55/-40, -30/-20)
  - brasil_nordeste: Nordeste do Brasil (-45/-32, -18/-3)
  - atlantico_sw: Atlântico Sul-Ocidental (-60/-30, -45/-10)
        """
    )
    
    parser.add_argument('--gebco-file', type=str, 
                       default='gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc',
                       help='Caminho para arquivo GEBCO NetCDF')
    
    parser.add_argument('--lon-min', type=float, 
                       help='Longitude mínima (oeste)')
    
    parser.add_argument('--lon-max', type=float,
                       help='Longitude máxima (leste)')
    
    parser.add_argument('--lat-min', type=float,
                       help='Latitude mínima (sul)')
    
    parser.add_argument('--lat-max', type=float,
                       help='Latitude máxima (norte)')
    
    parser.add_argument('--spacing', type=float, default=0.25,
                       help='Espaçamento da grade em graus (padrão: 0.25)')
    
    parser.add_argument('--output', type=str, default='pom_bathymetry_grid.asc',
                       help='Arquivo de saída ASCII (padrão: pom_bathymetry_grid.asc)')
    
    parser.add_argument('--plot-output', type=str, default='pom_bathymetry_grid.png',
                       help='Arquivo de saída da visualização')
    
    parser.add_argument('--no-plot', action='store_true',
                       help='Não gerar visualização')
    
    parser.add_argument('--method', type=str, default='linear',
                       choices=['linear', 'nearest', 'cubic'],
                       help='Método de interpolação (padrão: linear)')
    
    parser.add_argument('--region', type=str,
                       choices=['brasil_sul', 'brasil_nordeste', 'atlantico_sw'],
                       help='Usar região pré-definida')
    
    return parser.parse_args()


def get_predefined_region(region_name):
    """
    Retorna coordenadas de regiões pré-definidas.
    
    Parameters:
        region_name (str): Nome da região
    
    Returns:
        tuple: (lon_min, lon_max, lat_min, lat_max)
    """
    regions = {
        'brasil_sul': (-55.0, -40.0, -30.0, -20.0),
        'brasil_nordeste': (-45.0, -32.0, -18.0, -3.0),
        'atlantico_sw': (-60.0, -30.0, -45.0, -10.0),
    }
    
    return regions.get(region_name)


def main():
    """
    Função principal do script simplificado.
    """
    # Processar argumentos
    args = parse_arguments()
    
    # Determinar coordenadas
    if args.region:
        # Usar região pré-definida
        coords = get_predefined_region(args.region)
        if coords is None:
            print(f"ERRO: Região '{args.region}' não reconhecida")
            return 1
        lon_min, lon_max, lat_min, lat_max = coords
        print(f"\n✓ Usando região pré-definida: {args.region}")
    elif all([args.lon_min, args.lon_max, args.lat_min, args.lat_max]):
        # Usar coordenadas fornecidas
        lon_min = args.lon_min
        lon_max = args.lon_max
        lat_min = args.lat_min
        lat_max = args.lat_max
    else:
        # Usar valores padrão (costa brasileira)
        print("\n⚠️  Coordenadas não especificadas. Usando valores padrão (costa brasileira)")
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
    print(f"  Saída: {args.output}")
    if not args.no_plot:
        print(f"  Visualização: {args.plot_output}")
    print("="*70)
    
    try:
        # Criar gerador
        generator = BathymetryGridGenerator(args.gebco_file, spacing=args.spacing)
        
        # Carregar dados
        if not generator.load_gebco_data():
            return 1
        
        # Definir grade
        generator.define_grid_extent(lon_min, lon_max, lat_min, lat_max)
        
        # Interpolar
        if not generator.interpolate_bathymetry(method=args.method):
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
        print(f"\nArquivo pronto para uso: {args.output}")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\n✗ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
