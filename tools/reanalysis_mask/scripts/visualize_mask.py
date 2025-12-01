#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Visualizador de Máscaras Terra/Oceano
=====================================

Script para visualizar máscaras extraídas de reanálises.

Uso:
    python visualize_mask.py <arquivo_mascara.asc>
"""

import sys
import numpy as np
import matplotlib.pyplot as plt
import cartopy.crs as ccrs
import cartopy.feature as cfeature


def load_mask_file(filename):
    """Carrega máscara de arquivo ASCII."""
    print(f"Carregando máscara de: {filename}")
    
    data = []
    with open(filename, 'r') as f:
        for line in f:
            if line.startswith('#') or not line.strip():
                continue
            parts = line.split()
            if len(parts) >= 5:
                i, j, lon, lat, mask = map(float, parts[:5])
                data.append([lon, lat, int(mask)])
    
    data = np.array(data)
    
    # Reconstruir grade
    lons = np.unique(data[:, 0])
    lats = np.unique(data[:, 1])
    
    mask = np.zeros((len(lats), len(lons)))
    for row in data:
        lon_idx = np.where(lons == row[0])[0][0]
        lat_idx = np.where(lats == row[1])[0][0]
        mask[lat_idx, lon_idx] = row[2]
    
    print(f"✓ Máscara carregada: {len(lons)}x{len(lats)}")
    print(f"  Oceano: {np.sum(mask==1)} pontos")
    print(f"  Terra: {np.sum(mask==0)} pontos")
    
    return lons, lats, mask


def plot_mask(lons, lats, mask, output_file=None):
    """Plota máscara com Cartopy."""
    print("\nGerando visualização...")
    
    proj = ccrs.PlateCarree()
    fig, ax = plt.subplots(figsize=(14, 10), subplot_kw={'projection': proj})
    
    # Definir extensão
    ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], crs=proj)
    
    # Plotar máscara
    lon_mesh, lat_mesh = np.meshgrid(lons, lats)
    
    # Terra em cinza
    land_mask = np.ma.masked_where(mask != 0, mask)
    ax.pcolormesh(lon_mesh, lat_mesh, land_mask,
                 cmap='Greys', vmin=0, vmax=1,
                 shading='auto', transform=proj, alpha=0.5)
    
    # Oceano em azul
    ocean_mask = np.ma.masked_where(mask != 1, mask)
    ax.pcolormesh(lon_mesh, lat_mesh, ocean_mask,
                 cmap='Blues', vmin=0, vmax=2,
                 shading='auto', transform=proj)
    
    # Adicionar features
    ax.add_feature(cfeature.COASTLINE, edgecolor='red', linewidth=2, zorder=5)
    ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray', zorder=5)
    
    # Grid
    gl = ax.gridlines(draw_labels=True, alpha=0.3, linestyle='--', linewidth=0.5)
    gl.top_labels = False
    gl.right_labels = False
    
    # Título
    ax.set_xlabel('Longitude (°)', fontsize=12)
    ax.set_ylabel('Latitude (°)', fontsize=12)
    ax.set_title('Máscara Terra/Oceano - Reanálise', fontsize=14, fontweight='bold')
    
    plt.tight_layout()
    
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"✓ Figura salva: {output_file}")
    else:
        plt.show()
    
    plt.close()


def main():
    if len(sys.argv) < 2:
        print("Uso: python visualize_mask.py <arquivo_mascara.asc> [output.png]")
        return 1
    
    mask_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    try:
        lons, lats, mask = load_mask_file(mask_file)
        plot_mask(lons, lats, mask, output_file)
        print("\n✓ Concluído!")
        return 0
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
