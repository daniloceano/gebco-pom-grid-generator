#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualizador de Grades - RecOM
===============================

Cria visualização de grades oceânicas (formato ASCII de 5 colunas).
Mostra batimetria com linha de costa real (Cartopy) e contornos de profundidade.

Características:
- Terra pintada em cinza (direto da grade, não de cfeature.LAND)
- Oceano em azul com escala de profundidade
- Linha de costa real via Cartopy/Natural Earth
- Contornos batimétricos com labels

Uso:
    python visualize_grid.py <arquivo.asc>
    python visualize_grid.py <arquivo.asc> -o figura.png
    python visualize_grid.py <arquivo.asc> --output figura.png --dpi 300

Autor: RecOM Team
Data: Dezembro 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.colors import LinearSegmentedColormap
import sys
import os
import argparse


def load_grid(grid_file):
    """
    Carrega grade do arquivo ASCII formato POM (5 colunas).
    Formato: i j lon lat depth
    
    Returns:
        tuple: (lons, lats, depth_2d, header)
    """
    print(f"Carregando grade de: {grid_file}")
    
    if not os.path.exists(grid_file):
        raise FileNotFoundError(f"Arquivo não encontrado: {grid_file}")
    
    # Ler arquivo
    header_lines = []
    data_lines = []
    
    with open(grid_file, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('#') or not line:
                header_lines.append(line)
            else:
                data_lines.append(line)
    
    print(f"✓ {len(header_lines)} linhas de cabeçalho")
    print(f"✓ {len(data_lines)} linhas de dados")
    
    # Parse dos dados
    data = []
    for line in data_lines:
        parts = line.split()
        if len(parts) >= 5:
            i, j, lon, lat, depth = map(float, parts[:5])
            data.append([int(i), int(j), lon, lat, depth])
    
    data = np.array(data)
    
    # Extrair informações
    indices_i = data[:, 0].astype(int)
    indices_j = data[:, 1].astype(int)
    lon_data = data[:, 2]
    lat_data = data[:, 3]
    depth_data = data[:, 4]
    
    # Reconstruir grade 2D
    lons = np.unique(lon_data)
    lats = np.unique(lat_data)
    
    ni = len(lons)
    nj = len(lats)
    
    # Criar grade 2D: [lat, lon] = [nj, ni]
    depth = np.zeros((nj, ni))
    for idx in range(len(data)):
        i = indices_i[idx] - 1  # Converter para índice 0-based
        j = indices_j[idx] - 1
        depth[j, i] = depth_data[idx]
    
    print(f"✓ Grade: {ni} x {nj} pontos")
    print(f"✓ Extensão lon: [{lons.min():.2f}, {lons.max():.2f}]")
    print(f"✓ Extensão lat: [{lats.min():.2f}, {lats.max():.2f}]")
    print(f"✓ Profundidade: [{depth.min():.1f}, {depth.max():.1f}] m")
    
    return lons, lats, depth, header_lines


def plot_grid(lons, lats, depth, output_file=None, dpi=300):
    """
    Cria visualização da grade batimétrica.
    
    Parameters:
        lons (array): Array de longitudes
        lats (array): Array de latitudes
        depth (array): Grade 2D de profundidades [nj, ni]
        output_file (str): Caminho para salvar (None = mostrar)
        dpi (int): DPI da figura salva
    """
    print("\nGerando visualização...")
    
    import cartopy.crs as ccrs
    import cartopy.feature as cfeature
    
    # Criar figura com Cartopy
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={'projection': proj})
    ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=proj)
    
    # Preparar dados
    lon_mesh, lat_mesh = np.meshgrid(lons, lats)
    
    # Criar máscaras separadas para terra e oceano
    land_mask = depth == 0  # Terra (depth = 0)
    ocean_mask = depth > 0  # Oceano (depth > 0)
    
    # Pintar terra em cinza (direto da grade, não do cfeature.LAND)
    print("✓ Pintando células de terra da grade em cinza")
    land_depth = np.ma.masked_where(~land_mask, depth)
    ax.pcolormesh(lon_mesh, lat_mesh, land_depth,
                 cmap='Greys', vmin=-1, vmax=1,
                 transform=ccrs.PlateCarree(), zorder=2)
    
    # Preparar dados de oceano
    depth_masked = np.ma.masked_where(~ocean_mask, depth)
    
    # Criar mapa de cores para oceano
    colors_ocean = plt.cm.Blues_r(np.linspace(0.2, 1, 256))
    cmap_ocean = LinearSegmentedColormap.from_list('ocean', colors_ocean)
    
    # Plotar batimetria do oceano
    print("✓ Pintando células de oceano com escala de profundidade")
    im = ax.pcolormesh(lon_mesh, lat_mesh, depth_masked,
                      cmap=cmap_ocean, shading='auto',
                      transform=ccrs.PlateCarree(), zorder=3)
    
    # Adicionar linha de costa real e bordas
    print("✓ Adicionando linha de costa real (Cartopy/Natural Earth)")
    ax.add_feature(cfeature.COASTLINE, edgecolor='red', linewidth=2, zorder=5)
    ax.add_feature(cfeature.BORDERS, edgecolor='darkred', linewidth=0.5, 
                  linestyle='--', alpha=0.5, zorder=5)
    
    # Contornos batimétricos
    if np.max(depth) > 0:
        levels = [500, 1000, 2000, 3000, 4000, 5000, 6000]
        levels = [l for l in levels if l < np.max(depth)]
        
        cs = ax.contour(lon_mesh, lat_mesh, depth,
                      levels=levels, colors='gray', linewidths=0.5,
                      alpha=0.3, transform=ccrs.PlateCarree(), zorder=4)
        
        ax.clabel(cs, inline=True, fontsize=8, fmt='%d m')
        print(f"✓ Contornos: {levels}")
    
    # Formatação
    ax.set_xlabel('Longitude (°)', fontsize=12)
    ax.set_ylabel('Latitude (°)', fontsize=12)
    
    # Calcular espaçamento médio
    dx = np.diff(lons).mean() if len(lons) > 1 else 0
    dy = np.diff(lats).mean() if len(lats) > 1 else 0
    
    title = f'Grade Batimétrica'
    if dx > 0 or dy > 0:
        title += f' - Espaçamento: dx={dx:.3f}°, dy={dy:.3f}°'
    
    ax.set_title(title, fontsize=14, fontweight='bold')
    
    # Grid e labels
    gl = ax.gridlines(draw_labels=True, alpha=0.3, linestyle='--', linewidth=0.5)
    gl.top_labels = False
    gl.right_labels = False
    
    # Colorbar
    cbar = plt.colorbar(im, ax=ax, label='Profundidade (m)',
                       fraction=0.046, pad=0.04)
    
    plt.tight_layout()
    
    # Salvar ou mostrar
    if output_file:
        print(f"Salvando figura em: {output_file}")
        try:
            plt.savefig(output_file, dpi=dpi, bbox_inches='tight')
            print(f"✓ Figura salva com sucesso!")
            # Verificar tamanho do arquivo
            import os
            if os.path.exists(output_file):
                size_mb = os.path.getsize(output_file) / (1024 * 1024)
                print(f"  Tamanho: {size_mb:.2f} MB")
        except Exception as e:
            print(f"❌ Erro ao salvar: {e}")
            raise
        finally:
            plt.close()
    else:
        print("\n✓ Abrindo janela de visualização...")
        print("  Feche a janela para continuar")
        plt.show()
    
    return True


def main():
    """
    Função principal CLI.
    """
    parser = argparse.ArgumentParser(
        description='Visualizador de Grades - RecOM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  # Mostrar grade (não salvar)
  %(prog)s grade.asc

  # Salvar figura
  %(prog)s grade.asc -o figura.png
  
  # Alta resolução
  %(prog)s grade.asc -o figura.png --dpi 600
        """
    )
    
    parser.add_argument('grid_file', help='Arquivo de grade ASCII (5 colunas)')
    parser.add_argument('-o', '--output', help='Arquivo de saída para salvar figura')
    parser.add_argument('--dpi', type=int, default=300,
                       help='DPI da figura (padrão: 300)')
    
    args = parser.parse_args()
    
    try:
        # Carregar grade
        lons, lats, depth, header = load_grid(args.grid_file)
        
        # Plotar
        plot_grid(lons, lats, depth, 
                 output_file=args.output,
                 dpi=args.dpi)
        
        print("\n✓ Visualização concluída!")
        return 0
        
    except Exception as e:
        print(f"\n❌ ERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())
