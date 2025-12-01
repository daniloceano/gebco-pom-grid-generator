#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para extrair máscara terra/oceano de reanálises
======================================================

Extrai máscara de arquivos NetCDF de reanálises oceânicas (BRAN2020, etc)
e opcionalmente degrada para resolução alvo.

Uso:
    python extract_mask.py <arquivo_netcdf> [opções]

Exemplos:
    # Extrair máscara na resolução original
    python extract_mask.py ocean_eta_t_2023_07.nc
    
    # Extrair e degradar para 0.3°
    python extract_mask.py ocean_eta_t_2023_07.nc --target-res 0.3
    
    # Especificar variável e domínio
    python extract_mask.py ocean_eta_t_2023_07.nc --variable eta_t \\
        --lon-range -60 -30 --lat-range -35 -5 --target-res 0.25
"""

import sys
import os
import argparse

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mask_extractor import ReanalysisMaskExtractor


def main():
    parser = argparse.ArgumentParser(
        description='Extrair máscara terra/oceano de reanálises oceânicas',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Extrair máscara na resolução original
  %(prog)s ocean_eta_t_2023_07.nc
  
  # Degradar para 0.3 graus
  %(prog)s ocean_eta_t_2023_07.nc --target-res 0.3 0.3
  
  # Especificar variável e domínio
  %(prog)s ocean_eta_t_2023_07.nc --variable eta_t \\
      --lon-range -60 -30 --lat-range -35 -5 --target-res 0.25 0.25
  
  # Ajustar threshold de agregação
  %(prog)s ocean_eta_t_2023_07.nc --target-res 0.3 0.3 --threshold 0.7

Formatos suportados:
  - BRAN2020 (CSIRO)
  - GLORYS (Copernicus)
  - HYCOM
  - Qualquer NetCDF com coordenadas lon/lat
        """
    )
    
    parser.add_argument('netcdf_file', help='Arquivo NetCDF da reanálise')
    parser.add_argument('--variable', '-v', help='Nome da variável (auto-detect se não especificado)')
    parser.add_argument('--time-index', '-t', type=int, default=0,
                       help='Índice temporal a usar (padrão: 0)')
    parser.add_argument('--target-res', '-r', nargs=2, type=float, metavar=('DX', 'DY'),
                       help='Resolução alvo em graus (dx dy)')
    parser.add_argument('--threshold', type=float, default=0.5,
                       help='Threshold para agregação: fração mínima de oceano (0-1, padrão: 0.5)')
    parser.add_argument('--lon-range', nargs=2, type=float, metavar=('MIN', 'MAX'),
                       help='Limites de longitude (min max)')
    parser.add_argument('--lat-range', nargs=2, type=float, metavar=('MIN', 'MAX'),
                       help='Limites de latitude (min max)')
    parser.add_argument('--output', '-o', help='Arquivo de saída (auto-gerado se não especificado)')
    parser.add_argument('--no-align', action='store_true',
                       help='Não alinhar grade alvo à grade original')
    
    args = parser.parse_args()
    
    try:
        print("="*70)
        print(" EXTRATOR DE MÁSCARA - REANÁLISES OCEÂNICAS")
        print("="*70)
        
        # Inicializar extrator
        extractor = ReanalysisMaskExtractor(args.netcdf_file, args.variable)
        
        # Carregar dados
        if not extractor.load_data():
            print("\nERRO: Falha ao carregar dados")
            return 1
        
        # Extrair máscara
        if not extractor.extract_mask(time_index=args.time_index):
            print("\nERRO: Falha ao extrair máscara")
            return 1
        
        # Aplicar recorte espacial se especificado
        if args.lon_range or args.lat_range:
            print("\nAplicando recorte espacial...")
            if args.lon_range:
                lon_mask = (extractor.lons >= args.lon_range[0]) & (extractor.lons <= args.lon_range[1])
                extractor.lons = extractor.lons[lon_mask]
                extractor.mask = extractor.mask[:, lon_mask]
                print(f"  Longitude: [{args.lon_range[0]}, {args.lon_range[1]}]")
            
            if args.lat_range:
                lat_mask = (extractor.lats >= args.lat_range[0]) & (extractor.lats <= args.lat_range[1])
                extractor.lats = extractor.lats[lat_mask]
                extractor.mask = extractor.mask[lat_mask, :]
                print(f"  Latitude: [{args.lat_range[0]}, {args.lat_range[1]}]")
        
        # Degradar resolução se especificado
        if args.target_res:
            target_lon, target_lat = args.target_res
            coarsened_mask, coarsened_lons, coarsened_lats = extractor.coarsen_mask(
                target_lon, target_lat, 
                threshold=args.threshold,
                align_to_grid=not args.no_align
            )
            mask_to_export = coarsened_mask
            lons_to_export = coarsened_lons
            lats_to_export = coarsened_lats
            res_str = f"{target_lon}x{target_lat}"
        else:
            mask_to_export = extractor.mask
            lons_to_export = extractor.lons
            lats_to_export = extractor.lats
            res_str = "original"
        
        # Encontrar diretório output/ no top-level
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
        output_dir = os.path.join(project_root, 'output')
        
        # Criar diretório output se não existir
        os.makedirs(output_dir, exist_ok=True)
        
        # Gerar nome de arquivo de saída
        if args.output:
            # Se caminho absoluto, usar como está
            if os.path.isabs(args.output):
                output_file = args.output
            else:
                # Se relativo, colocar em output/
                output_file = os.path.join(output_dir, args.output)
        else:
            base_name = os.path.splitext(os.path.basename(args.netcdf_file))[0]
            lon_range_str = f"lon{lons_to_export.min():.1f}_{lons_to_export.max():.1f}"
            lat_range_str = f"lat{lats_to_export.min():.1f}_{lats_to_export.max():.1f}"
            
            # Formatar resolução para nome de arquivo
            if args.target_res:
                dx_str = f"dx{target_lon}"
                dy_str = f"dy{target_lat}"
                res_str = f"{dx_str}_{dy_str}"
            else:
                res_str = "original"
            
            filename = f"mask_ocean_{base_name}_{lon_range_str}_{lat_range_str}_{res_str}.asc"
            output_file = os.path.join(output_dir, filename)
        
        # Exportar máscara
        extractor.export_mask(output_file, mask_to_export, lons_to_export, lats_to_export)
        
        # Limpeza
        extractor.cleanup()
        
        print("\n" + "="*70)
        print(" EXTRAÇÃO CONCLUÍDA COM SUCESSO!")
        print("="*70)
        print(f"\nArquivo de máscara: {output_file}")
        print("\nPróximos passos:")
        print(f"  • Visualizar: python visualize_mask.py {output_file}")
        print(f"  • Aplicar em grade: use grid_editor (tecla 'm')")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
