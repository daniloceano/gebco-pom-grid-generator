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

def normalize_longitude(lon):
    """
    Normaliza longitude para -180 a 180.
    """
    while lon > 180:
        lon -= 360
    while lon < -180:
        lon += 360
    return lon

def apply_mask(lons, lats, depth, mask_lons, mask_lats, mask, preserve_boundaries=False):
    """
    Aplica máscara à grade.
    
    Corta a grade para o domínio da máscara e aplica.
    Onde a máscara indica terra (0), converte pontos oceânicos para terra.
    
    Args:
        preserve_boundaries (bool): Se True, preserva colunas de longitude em -180/180
                                   usando dados originais quando forem cortadas
    
    Returns:
        lons_cropped (array): Longitudes cortadas
        lats_cropped (array): Latitudes cortadas
        depth_masked (array): Grade com máscara aplicada
        n_changes (int): Número de pontos alterados
        n_removed (int): Número de pontos removidos (fora do domínio)
    """
    print("\nAplicando máscara...")
    
    # Converter longitudes da máscara para -180/180 se necessário
    mask_lons_norm = mask_lons.copy()
    if np.any(mask_lons > 180):
        print("  Convertendo longitudes da máscara de [0,360] para [-180,180]")
        mask_lons_norm = np.array([normalize_longitude(lon) for lon in mask_lons])
        # Reordenar se necessário
        if not np.all(mask_lons_norm[:-1] <= mask_lons_norm[1:]):
            sort_idx = np.argsort(mask_lons_norm)
            mask_lons_norm = mask_lons_norm[sort_idx]
            mask = mask[:, sort_idx]
    
    # Determinar limites do domínio da máscara
    mask_lon_min = mask_lons_norm.min()
    mask_lon_max = mask_lons_norm.max()
    mask_lat_min = mask_lats.min()
    mask_lat_max = mask_lats.max()
    
    print(f"  Domínio da máscara: lon [{mask_lon_min:.2f}, {mask_lon_max:.2f}], "
          f"lat [{mask_lat_min:.2f}, {mask_lat_max:.2f}]")
    
    # Encontrar índices da grade que estão dentro do domínio da máscara
    lon_mask = (lons >= mask_lon_min) & (lons <= mask_lon_max)
    lat_mask = (lats >= mask_lat_min) & (lats <= mask_lat_max)
    
    # Preservar bordas de longitude se solicitado
    preserve_lon_180 = False
    preserve_lon_minus180 = False
    
    if preserve_boundaries:
        # Verificar se grade original tem -180 ou +180 que seriam cortados
        has_lon_180 = np.any(np.abs(lons - 180.0) < 0.001)
        has_lon_minus180 = np.any(np.abs(lons + 180.0) < 0.001)
        
        # Verificar se essas longitudes seriam removidas pelo corte
        if has_lon_180 and not lon_mask[np.argmin(np.abs(lons - 180.0))]:
            preserve_lon_180 = True
            print("  ℹ Preservando coluna em longitude +180° (fora do domínio da máscara)")
        
        if has_lon_minus180 and not lon_mask[np.argmin(np.abs(lons + 180.0))]:
            preserve_lon_minus180 = True
            print("  ℹ Preservando coluna em longitude -180° (fora do domínio da máscara)")
    
    lons_cropped = lons[lon_mask]
    lats_cropped = lats[lat_mask]
    
    # Extrair subgrade
    depth_cropped = depth[np.ix_(lat_mask, lon_mask)]
    
    n_original = len(lons) * len(lats)
    n_cropped = len(lons_cropped) * len(lats_cropped)
    n_removed = n_original - n_cropped
    
    print(f"  Grade original: {len(lons)} x {len(lats)} = {n_original} pontos")
    print(f"  Grade cortada: {len(lons_cropped)} x {len(lats_cropped)} = {n_cropped} pontos")
    print(f"  Pontos removidos (fora do domínio): {n_removed}")
    
    # Aplicar máscara
    depth_masked = depth_cropped.copy()
    n_changes = 0
    
    for j, lat in enumerate(lats_cropped):
        for i, lon in enumerate(lons_cropped):
            # Encontrar ponto mais próximo na máscara
            lon_idx = np.argmin(np.abs(mask_lons_norm - lon))
            lat_idx = np.argmin(np.abs(mask_lats - lat))
            
            mask_val = mask[lat_idx, lon_idx]
            
            # Se máscara diz terra (0), zerar profundidade
            if mask_val == 0 and depth_masked[j, i] > 0:
                depth_masked[j, i] = 0.0
                n_changes += 1
    
    print(f"  ✓ {n_changes} pontos convertidos para terra")
    
    # Adicionar colunas de borda se necessário
    if preserve_lon_minus180 or preserve_lon_180:
        lons_final = []
        depth_cols = []
        
        # Adicionar coluna -180 se necessário
        if preserve_lon_minus180:
            lon_idx_orig = np.argmin(np.abs(lons + 180.0))
            lons_final.append(-180.0)
            depth_cols.append(depth[np.ix_(lat_mask, [lon_idx_orig])])
        
        # Adicionar dados principais
        lons_final.extend(lons_cropped)
        depth_cols.append(depth_masked)
        
        # Adicionar coluna +180 se necessário
        if preserve_lon_180:
            lon_idx_orig = np.argmin(np.abs(lons - 180.0))
            lons_final.append(180.0)
            depth_cols.append(depth[np.ix_(lat_mask, [lon_idx_orig])])
        
        lons_cropped = np.array(lons_final)
        depth_masked = np.concatenate(depth_cols, axis=1)
        
        print(f"  ✓ Colunas de borda preservadas: {len(lons_cropped)} x {len(lats_cropped)} pontos")
    
    print(f"  Oceano final: {np.sum(depth_masked > 0)} pontos")
    print(f"  Terra final: {np.sum(depth_masked == 0)} pontos")
    
    return lons_cropped, lats_cropped, depth_masked, n_changes, n_removed

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

  # Preservar colunas de longitude -180/+180 (recomendado para grades globais)
  python apply_mask.py grid.asc mask.asc --preserve-boundaries

  # Especificar nome de saída
  python apply_mask.py grid.asc mask.asc --output grid_bran2020.asc
        """
    )
    
    parser.add_argument('grid_file', help='Arquivo de grade (.asc)')
    parser.add_argument('mask_file', help='Arquivo de máscara (.asc)')
    parser.add_argument('--output', '-o', help='Arquivo de saída (padrão: <grid>_masked.asc)')
    parser.add_argument('--preserve-boundaries', action='store_true',
                       help='Preserva colunas de longitude em -180°/+180° usando dados originais')
    
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
        print("  A grade será cortada para o domínio da máscara")
    
    # Aplicar máscara (corta a grade para o domínio da máscara)
    lons_masked, lats_masked, depth_masked, n_changes, n_removed = apply_mask(
        lons, lats, depth, mask_lons, mask_lats, mask, 
        preserve_boundaries=args.preserve_boundaries
    )
    
    # Salvar resultado
    save_grid(output_file, header, lons_masked, lats_masked, depth_masked, args.mask_file)
    
    print("\n" + "="*70)
    print("✓ CONCLUÍDO!")
    print("="*70)
    print(f"\nGrade com máscara salva em: {output_file}")
    print(f"Pontos alterados pela máscara: {n_changes}")
    if n_removed > 0:
        print(f"Pontos removidos (fora do domínio): {n_removed}")
    print(f"\nVisualize o resultado:")
    print(f"  ./ocean_mesh_tools.sh view {output_file}")
    print()

if __name__ == '__main__':
    main()
