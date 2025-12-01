#!/usr/bin/env python3
"""
Script para aplicar máscara de reanálise a uma grade oceânica.

Lê uma grade existente e uma máscara, aplica a máscara (convertendo pontos 
oceânicos para terra quando indicado pela máscara), e salva uma nova grade
com sufixo '_masked' no nome.

Uso:
    python apply_mask.py <grid_file> <mask_file> [--output <output_file>]

Exemplo:
    python apply_mask.py \\
        output/rectangular_grid_lon-60_-30_lat-35_-5_dx0.25_dy0.25_gebco.asc \\
        output/mask_ocean_bran2020_lon-60_-30_lat-35_-5_dx0.25_dy0.25.asc
"""

import numpy as np
import argparse
import sys
import os
from datetime import datetime

def load_grid(filename):
    """
    Carrega grade ASCII.
    
    Returns:
        header (list): Linhas de cabeçalho
        lons (array): Coordenadas longitude
        lats (array): Coordenadas latitude
        depth (array): Profundidades [nj, ni]
    """
    print(f"Carregando grade: {filename}")
    
    header = []
    data = []
    
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#'):
                header.append(line.strip())
            elif line.strip():
                parts = line.split()
                if len(parts) >= 5:
                    i, j, lon, lat, depth = map(float, parts[:5])
                    data.append([lon, lat, depth])
    
    data = np.array(data)
    
    # Reconstruir grade
    lons = np.unique(data[:, 0])
    lats = np.unique(data[:, 1])
    
    depth = np.zeros((len(lats), len(lons)))
    for row in data:
        lon_idx = np.where(lons == row[0])[0][0]
        lat_idx = np.where(lats == row[1])[0][0]
        depth[lat_idx, lon_idx] = row[2]
    
    print(f"  ✓ Grade: {len(lons)} x {len(lats)} pontos")
    print(f"    Oceano: {np.sum(depth > 0)} pontos")
    print(f"    Terra: {np.sum(depth == 0)} pontos")
    
    return header, lons, lats, depth

def load_mask(filename):
    """
    Carrega máscara ASCII.
    
    Returns:
        mask_lons (array): Coordenadas longitude
        mask_lats (array): Coordenadas latitude
        mask (array): Valores da máscara [nj, ni] (1=oceano, 0=terra)
    """
    print(f"\nCarregando máscara: {filename}")
    
    mask_data = []
    
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 5:
                i, j, lon, lat, mask_val = map(float, parts[:5])
                mask_data.append([lon, lat, int(mask_val)])
    
    mask_data = np.array(mask_data)
    
    # Reconstruir grade da máscara
    mask_lons = np.unique(mask_data[:, 0])
    mask_lats = np.unique(mask_data[:, 1])
    
    mask = np.zeros((len(mask_lats), len(mask_lons)))
    for row in mask_data:
        lon_idx = np.where(mask_lons == row[0])[0][0]
        lat_idx = np.where(mask_lats == row[1])[0][0]
        mask[lat_idx, lon_idx] = row[2]
    
    print(f"  ✓ Máscara: {len(mask_lons)} x {len(mask_lats)} pontos")
    print(f"    Oceano: {np.sum(mask == 1)} pontos")
    print(f"    Terra: {np.sum(mask == 0)} pontos")
    
    return mask_lons, mask_lats, mask

def apply_mask(lons, lats, depth, mask_lons, mask_lats, mask):
    """
    Aplica máscara à grade.
    
    Onde a máscara indica terra (0), converte pontos oceânicos para terra.
    Não cria oceano onde não havia.
    
    Returns:
        depth_masked (array): Grade com máscara aplicada
        n_changes (int): Número de pontos alterados
    """
    print("\nAplicando máscara...")
    
    depth_masked = depth.copy()
    n_changes = 0
    
    for j, lat in enumerate(lats):
        for i, lon in enumerate(lons):
            # Encontrar ponto mais próximo na máscara
            lon_idx = np.argmin(np.abs(mask_lons - lon))
            lat_idx = np.argmin(np.abs(mask_lats - lat))
            
            mask_val = mask[lat_idx, lon_idx]
            
            # Se máscara diz terra (0), zerar profundidade
            if mask_val == 0 and depth_masked[j, i] > 0:
                depth_masked[j, i] = 0.0
                n_changes += 1
    
    print(f"  ✓ {n_changes} pontos convertidos para terra")
    print(f"  Oceano final: {np.sum(depth_masked > 0)} pontos")
    print(f"  Terra final: {np.sum(depth_masked == 0)} pontos")
    
    return depth_masked, n_changes

def save_grid(filename, header, lons, lats, depth, mask_file):
    """
    Salva grade com máscara aplicada.
    """
    print(f"\nSalvando grade com máscara aplicada: {filename}")
    
    with open(filename, 'w') as f:
        # Cabeçalho original
        for line in header:
            f.write(line + '\n')
        
        # Informações da máscara aplicada
        f.write(f"# Máscara aplicada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
        f.write(f"# Arquivo de máscara: {os.path.basename(mask_file)}\n")
        
        # Dados da grade
        idx = 0
        for j, lat in enumerate(lats):
            for i, lon in enumerate(lons):
                f.write(f"{i:6d} {j:6d} {lon:12.6f} {lat:12.6f} {depth[j,i]:12.2f}\n")
                idx += 1
    
    print(f"  ✓ {len(lons) * len(lats)} pontos salvos")

def main():
    parser = argparse.ArgumentParser(
        description='Aplica máscara de reanálise a uma grade oceânica',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Aplicar máscara BRAN2020 a grade GEBCO
  python apply_mask.py \\
      output/rectangular_grid_lon-60_-30_lat-35_-5_dx0.25_dy0.25_gebco.asc \\
      output/mask_ocean_bran2020_lon-60_-30_lat-35_-5_dx0.25_dy0.25.asc

  # Especificar nome de saída
  python apply_mask.py grid.asc mask.asc --output grid_bran2020.asc
        """
    )
    
    parser.add_argument('grid_file', help='Arquivo de grade (.asc)')
    parser.add_argument('mask_file', help='Arquivo de máscara (.asc)')
    parser.add_argument('--output', '-o', help='Arquivo de saída (padrão: <grid>_masked.asc)')
    
    args = parser.parse_args()
    
    # Validar arquivos
    if not os.path.exists(args.grid_file):
        print(f"ERRO: Arquivo de grade não encontrado: {args.grid_file}")
        sys.exit(1)
    
    if not os.path.exists(args.mask_file):
        print(f"ERRO: Arquivo de máscara não encontrado: {args.mask_file}")
        sys.exit(1)
    
    # Gerar nome de saída
    if args.output:
        output_file = args.output
    else:
        # Adicionar sufixo '_masked' antes da extensão
        base = args.grid_file.replace('.asc', '')
        # Extrair nome base da máscara (ex: bran2020 de mask_ocean_bran2020_...)
        mask_base = os.path.basename(args.mask_file)
        if mask_base.startswith('mask_ocean_'):
            mask_name = mask_base.split('_')[2]  # Pega terceiro elemento (ex: bran2020)
        else:
            mask_name = 'masked'
        output_file = f"{base}_{mask_name}.asc"
    
    print("="*70)
    print(" APLICAR MÁSCARA DE REANÁLISE")
    print("="*70)
    
    # Carregar dados
    header, lons, lats, depth = load_grid(args.grid_file)
    mask_lons, mask_lats, mask = load_mask(args.mask_file)
    
    # Verificar compatibilidade de domínios
    grid_lon_range = (lons.min(), lons.max())
    grid_lat_range = (lats.min(), lats.max())
    mask_lon_range = (mask_lons.min(), mask_lons.max())
    mask_lat_range = (mask_lats.min(), mask_lats.max())
    
    print("\nDomínios:")
    print(f"  Grade: lon {grid_lon_range[0]:.2f} a {grid_lon_range[1]:.2f}, "
          f"lat {grid_lat_range[0]:.2f} a {grid_lat_range[1]:.2f}")
    print(f"  Máscara: lon {mask_lon_range[0]:.2f} a {mask_lon_range[1]:.2f}, "
          f"lat {mask_lat_range[0]:.2f} a {mask_lat_range[1]:.2f}")
    
    # Aviso se domínios não cobrem completamente
    if (grid_lon_range[0] < mask_lon_range[0] or grid_lon_range[1] > mask_lon_range[1] or
        grid_lat_range[0] < mask_lat_range[0] or grid_lat_range[1] > mask_lat_range[1]):
        print("\n⚠ AVISO: Domínio da grade excede domínio da máscara")
        print("  Pontos fora da máscara usarão vizinho mais próximo")
    
    # Aplicar máscara
    depth_masked, n_changes = apply_mask(lons, lats, depth, mask_lons, mask_lats, mask)
    
    # Salvar resultado
    save_grid(output_file, header, lons, lats, depth_masked, args.mask_file)
    
    print("\n" + "="*70)
    print("✓ CONCLUÍDO!")
    print("="*70)
    print(f"\nGrade com máscara salva em: {output_file}")
    print(f"Pontos alterados: {n_changes}")
    print(f"\nVisualize o resultado:")
    print(f"  python tools/grid_editor/scripts/edit_grid.py {output_file}")
    print()

if __name__ == '__main__':
    main()
