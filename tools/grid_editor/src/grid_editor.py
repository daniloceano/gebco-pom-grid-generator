#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Editor Interativo de Grades - RecOM
====================================

Editor visual para manipulação manual de grades oceânicas.
Suporta diferentes formatos de grade e pode ser usado por múltiplas
ferramentas do pacote.

Características:
- Visualização com linha de costa real (Cartopy)
- Contornos batimétricos
- Zoom in/out interativo
- Click para alternar terra/água
- Grade de células do modelo visível
- Interpolação automática IDW
- Salvamento automático das modificações

Controles:
- Click esquerdo: Alternar terra/água no ponto clicado
- Tecla '+' ou scroll up: Zoom in
- Tecla '-' ou scroll down: Zoom out
- Tecla 'r': Reset do zoom
- Tecla 'g': Toggle grade
- Tecla 'c': Toggle linha de costa
- Tecla 'b': Toggle contornos batimétricos
- Tecla 's': Salvar modificações
- Tecla 'q' ou fechar janela: Sair

Nota: Para aplicar máscaras de reanálise, use o script separado:
    python tools/reanalysis_mask/scripts/apply_mask.py <grade> <mascara>

Uso:
    python grid_editor.py <arquivo_grade.asc>
    
    # Com opções
    python grid_editor.py <arquivo> --no-coastline --no-contours
    
Autor: RecOM Team
Data: Dezembro 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
import sys
import os
from datetime import datetime
import argparse
import cartopy.crs as ccrs
import cartopy.feature as cfeature


class GridEditor:
    """
    Editor interativo de grades com interface gráfica avançada.
    """
    
    def __init__(self, grid_file, show_contours=True):
        """
        Inicializa o editor.
        
        Parameters:
            grid_file (str): Caminho para o arquivo ASCII da grade
            show_contours (bool): Mostrar contornos batimétricos
        """
        self.grid_file = grid_file
        self.backup_file = grid_file.replace('.asc', '_backup.asc')
        self.modified = False
        self.enable_contours = show_contours
        
        # Carregar dados
        self.load_grid()
        
        # Estado da interface
        self.show_grid = True
        self.show_coastline = True
        self.show_bathy_contours = show_contours
        self.current_xlim = None
        self.current_ylim = None
        
        # Configurar figura
        self.setup_figure()
        
        print("\n" + "="*70)
        print(" EDITOR INTERATIVO DE GRADES - OCEAN GRID TOOLS")
        print("="*70)
        print("\nControles:")
        print("  Click esquerdo: Alternar terra/água")
        print("  '+' ou scroll up: Zoom in")
        print("  '-' ou scroll down: Zoom out")
        print("  'r': Reset do zoom")
        print("  'g': Toggle grade")
        print("  'c': Toggle linha de costa")
        print("  'b': Toggle contornos batimétricos")
        print("  'm': Aplicar máscara de reanálise")
        print("  's': Salvar modificações")
        print("  'q': Sair")
        print("="*70)
        print("✓ Usando linha de costa real (Cartopy)")
        print("="*70 + "\n")
    
    def load_grid(self):
        """
        Carrega a grade do arquivo ASCII formato POM (5 colunas).
        Formato: i j lon lat depth
        """
        print(f"\nCarregando grade de: {self.grid_file}")
        
        if not os.path.exists(self.grid_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.grid_file}")
        
        # Fazer backup se não existe
        if not os.path.exists(self.backup_file):
            import shutil
            shutil.copy2(self.grid_file, self.backup_file)
            print(f"Backup criado: {self.backup_file}")
        
        # Ler arquivo
        header_lines = []
        data_lines = []
        
        with open(self.grid_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('#') or not line:
                    header_lines.append(line)
                else:
                    data_lines.append(line)
        
        self.header = header_lines
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
        self.indices_i = data[:, 0].astype(int)
        self.indices_j = data[:, 1].astype(int)
        self.lon_data = data[:, 2]
        self.lat_data = data[:, 3]
        self.depth_data = data[:, 4]
        
        # Reconstruir grade 2D
        ni = len(np.unique(self.indices_i))
        nj = len(np.unique(self.indices_j))
        
        self.lons = np.unique(self.lon_data)
        self.lats = np.unique(self.lat_data)
        
        # Criar grade 2D corretamente: [lat, lon] = [nj, ni]
        self.depth = np.zeros((nj, ni))
        for idx in range(len(data)):
            i = self.indices_i[idx] - 1  # Converter para índice 0-based
            j = self.indices_j[idx] - 1
            # depth[j, i] porque j é índice de latitude e i de longitude
            self.depth[j, i] = self.depth_data[idx]
        
        # Calcular espaçamento
        self.cellsize_lon = np.diff(self.lons).mean() if len(self.lons) > 1 else 0.25
        self.cellsize_lat = np.diff(self.lats).mean() if len(self.lats) > 1 else 0.25
        
        self.nodata = 0.0  # Convenção POM: 0 = terra
        
        print(f"✓ Grade: {ni} x {nj} pontos")
        print(f"✓ Extensão lon: [{self.lons.min():.2f}, {self.lons.max():.2f}]")
        print(f"✓ Extensão lat: [{self.lats.min():.2f}, {self.lats.max():.2f}]")
        print(f"✓ Espaçamento: dx={self.cellsize_lon:.4f}°, dy={self.cellsize_lat:.4f}°")
        print(f"✓ Profundidade: [{self.depth.min():.1f}, {self.depth.max():.1f}] m")
    
    def setup_figure(self):
        """
        Configura a figura matplotlib com cartopy.
        """
        # Usar projeção PlateCarree (lat/lon simples)
        self.projection = ccrs.PlateCarree()
        self.fig = plt.figure(figsize=(14, 10))
        self.ax = plt.subplot(111, projection=self.projection)
        
        self.update_plot()
        
        # Conectar eventos
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.fig.canvas.mpl_connect('scroll_event', self.on_scroll)
        
        plt.tight_layout()
    
    def update_plot(self):
        """
        Atualiza o plot com os dados atuais.
        """
        self.ax.clear()
        
        # Definir extensão do mapa
        self.ax.set_extent([self.lons.min(), self.lons.max(), 
                           self.lats.min(), self.lats.max()], crs=self.projection)
        
        # Preparar dados para visualização usando meshgrid como no bathymetry_generator
        lon_mesh, lat_mesh = np.meshgrid(self.lons, self.lats)
        
        # Mascarar oceano (depth == 0 é terra)
        depth_masked = np.ma.masked_where(self.depth == 0, self.depth)
        
        # Plot batimetria (apenas oceano)
        im = self.ax.pcolormesh(lon_mesh, lat_mesh, depth_masked,
                               cmap='Blues_r', shading='auto',
                               vmin=0, vmax=6000,
                               transform=self.projection)
        
        # Contornos batimétricos
        if self.show_bathy_contours and self.enable_contours:
            self.draw_bathymetry_contours()
        
        # Linha de costa
        if self.show_coastline:
            self.draw_cartopy_coastline()
        
        # Grade de células
        if self.show_grid:
            self.draw_grid()
        
        # Colorbar
        if not hasattr(self, 'cbar') or self.cbar is None:
            self.cbar = plt.colorbar(im, ax=self.ax, label='Profundidade (m)',
                                    fraction=0.046, pad=0.04)
        
        # Labels e título
        self.ax.set_xlabel('Longitude (°)', fontsize=12)
        self.ax.set_ylabel('Latitude (°)', fontsize=12)
        title = 'Editor de Grade Oceânica'
        if self.modified:
            title += ' [MODIFICADO - Pressione \'s\' para salvar]'
        self.ax.set_title(title, fontsize=14, fontweight='bold')
        
        # Manter zoom se existir
        if self.current_xlim is not None:
            self.ax.set_xlim(self.current_xlim)
            self.ax.set_ylim(self.current_ylim)
        else:
            # Definir limites iniciais com margem
            margin_lon = (self.lons.max() - self.lons.min()) * 0.05
            margin_lat = (self.lats.max() - self.lats.min()) * 0.05
            self.ax.set_xlim(self.lons.min() - margin_lon, self.lons.max() + margin_lon)
            self.ax.set_ylim(self.lats.min() - margin_lat, self.lats.max() + margin_lat)
        
        # Grid com labels
        gl = self.ax.gridlines(draw_labels=True, alpha=0.3, linestyle='--', linewidth=0.5)
        gl.top_labels = False
        gl.right_labels = False
        
        self.fig.canvas.draw()
    
    def draw_cartopy_coastline(self):
        """
        Desenha linha de costa real usando Cartopy.
        """
        # Adicionar features do cartopy
        self.ax.add_feature(cfeature.LAND, facecolor='lightgray', zorder=3)
        self.ax.add_feature(cfeature.COASTLINE, edgecolor='red', linewidth=2, zorder=5)
        self.ax.add_feature(cfeature.BORDERS, edgecolor='darkred', linewidth=0.5, 
                          linestyle='--', alpha=0.5, zorder=5)
    
    def draw_bathymetry_contours(self):
        """
        Desenha contornos de batimetria.
        """
        # Contornos a cada 1000m até 6000m
        levels = [500, 1000, 2000, 3000, 4000, 5000, 6000]
        
        lon_mesh, lat_mesh = np.meshgrid(self.lons, self.lats)
        cs = self.ax.contour(lon_mesh, lat_mesh, self.depth,
                           levels=levels, colors='gray', linewidths=0.5,
                           alpha=0.3, transform=self.projection, zorder=4)
        
        # Labels nos contornos
        self.ax.clabel(cs, inline=True, fontsize=8, fmt='%d m')
    
    def draw_grid(self):
        """
        Desenha a grade de células do modelo.
        """
        # Criar linhas verticais e horizontais
        lines_v = [[(lon, self.lats[0]), (lon, self.lats[-1])] 
                   for lon in self.lons]
        lines_h = [[(self.lons[0], lat), (self.lons[-1], lat)] 
                   for lat in self.lats]
        
        # Adicionar bordas
        lines_v.append([(self.lons[-1] + self.cellsize_lon, self.lats[0]), 
                        (self.lons[-1] + self.cellsize_lon, self.lats[-1])])
        lines_h.append([(self.lons[0], self.lats[-1] + self.cellsize_lat), 
                        (self.lons[-1], self.lats[-1] + self.cellsize_lat)])
        
        lc_v = LineCollection(lines_v, colors='gray', linewidths=0.3, alpha=0.6, zorder=6)
        lc_h = LineCollection(lines_h, colors='gray', linewidths=0.3, alpha=0.6, zorder=6)
        
        self.ax.add_collection(lc_v)
        self.ax.add_collection(lc_h)
    
    def find_nearest_cell(self, lon, lat):
        """
        Encontra a célula mais próxima de um ponto clicado.
        
        Returns:
            tuple: (j, i) índices da célula (j=lat, i=lon)
        """
        j = np.argmin(np.abs(self.lats - lat))
        i = np.argmin(np.abs(self.lons - lon))
        return j, i
    
    def interpolate_from_neighbors(self, j, i, max_radius=5):
        """
        Interpola profundidade das células vizinhas válidas (água).
        
        Usa IDW - Inverse Distance Weighting.
        
        Parameters:
            j, i: Índices da célula (j=lat, i=lon)
            max_radius: Raio máximo de busca
            
        Returns:
            float: Profundidade interpolada ou valor padrão
        """
        nj, ni = self.depth.shape
        
        # Buscar vizinhos válidos (profundidade > 0 = água)
        neighbors = []
        weights = []
        
        for radius in range(1, max_radius + 1):
            for dj in range(-radius, radius + 1):
                for di in range(-radius, radius + 1):
                    j_check = j + dj
                    i_check = i + di
                    
                    if (0 <= j_check < nj and 0 <= i_check < ni and 
                        (dj != 0 or di != 0)):
                        depth_val = self.depth[j_check, i_check]
                        
                        if depth_val > 0:  # Água
                            distance = np.sqrt(dj**2 + di**2)
                            neighbors.append(depth_val)
                            weights.append(1.0 / (distance ** 2))
            
            if len(neighbors) >= 4:
                break
        
        if len(neighbors) > 0:
            weights = np.array(weights)
            neighbors = np.array(neighbors)
            interpolated = np.sum(neighbors * weights) / np.sum(weights)
            
            print(f"  Interpolado de {len(neighbors)} vizinhos: {interpolated:.2f}m")
            return interpolated
        else:
            print(f"  Nenhum vizinho válido encontrado. Usando profundidade padrão: 100m")
            return 100.0
    
    def toggle_cell(self, j, i):
        """
        Alterna uma célula entre terra e água.
        
        Parameters:
            j, i: Índices da célula (j=lat, i=lon)
        """
        current_depth = self.depth[j, i]
        lon = self.lons[i]
        lat = self.lats[j]
        
        if current_depth <= 0:
            # Terra → Água: interpolar profundidade
            print(f"\nConvertendo terra → água em ({lon:.2f}°, {lat:.2f}°)")
            new_depth = self.interpolate_from_neighbors(j, i)
            self.depth[j, i] = new_depth
            print(f"✓ Nova profundidade: {new_depth:.2f}m")
        else:
            # Água → Terra
            print(f"\nConvertendo água → terra em ({lon:.2f}°, {lat:.2f}°)")
            print(f"  Profundidade antiga: {current_depth:.2f}m")
            self.depth[j, i] = 0.0
            print(f"✓ Agora é terra (depth = 0)")
        
        self.modified = True
        self.update_plot()
    
    def on_click(self, event):
        """
        Callback para cliques do mouse.
        """
        if event.inaxes != self.ax or event.button != 1:
            return
        
        # Obter coordenadas do click
        lon, lat = event.xdata, event.ydata
        
        if lon is None or lat is None:
            return
        
        # Encontrar célula mais próxima
        j, i = self.find_nearest_cell(lon, lat)
        
        # Toggle célula
        self.toggle_cell(j, i)
    
    def on_key(self, event):
        """
        Callback para teclas pressionadas.
        """
        if event.key == 'q':
            if self.modified:
                print("\n⚠ Grade modificada mas não salva!")
                print("Pressione 's' para salvar ou feche a janela para descartar.")
            else:
                plt.close(self.fig)
        
        elif event.key == 's':
            self.save()
        
        elif event.key == 'r':
            # Reset zoom
            self.current_xlim = None
            self.current_ylim = None
            self.update_plot()
            print("Zoom resetado")
        
        elif event.key == 'g':
            # Toggle grade
            self.show_grid = not self.show_grid
            self.update_plot()
            print(f"Grade: {'ON' if self.show_grid else 'OFF'}")
        
        elif event.key == 'c':
            # Toggle linha de costa
            self.show_coastline = not self.show_coastline
            self.update_plot()
            print(f"Linha de costa: {'ON' if self.show_coastline else 'OFF'}")
        
        elif event.key == 'b':
            # Toggle contornos batimétricos
            self.show_bathy_contours = not self.show_bathy_contours
            self.update_plot()
            print(f"Contornos batimétricos: {'ON' if self.show_bathy_contours else 'OFF'}")
        
        elif event.key in ['+', '=']:
            # Zoom in
            self.zoom(1.2)
        
        elif event.key == '-':
            # Zoom out
            self.zoom(0.8)
    
    def on_scroll(self, event):
        """
        Callback para scroll do mouse (zoom).
        """
        if event.inaxes != self.ax:
            return
        
        if event.button == 'up':
            self.zoom(1.2)
        elif event.button == 'down':
            self.zoom(0.8)
    
    def zoom(self, factor):
        """
        Aplica zoom mantendo o centro.
        
        Parameters:
            factor: Fator de zoom (>1 = zoom in, <1 = zoom out)
        """
        # Obter limites atuais
        xlim = self.ax.get_xlim()
        ylim = self.ax.get_ylim()
        
        # Calcular centro
        cx = (xlim[0] + xlim[1]) / 2
        cy = (ylim[0] + ylim[1]) / 2
        
        # Calcular nova largura/altura
        w = (xlim[1] - xlim[0]) / factor
        h = (ylim[1] - ylim[0]) / factor
        
        # Aplicar novos limites
        self.current_xlim = [cx - w/2, cx + w/2]
        self.current_ylim = [cy - h/2, cy + h/2]
        
        self.ax.set_xlim(self.current_xlim)
        self.ax.set_ylim(self.current_ylim)
        self.fig.canvas.draw()
    
    def save(self):
        """
        Salva a grade modificada em arquivo.
        """
        if not self.modified:
            print("\nNenhuma modificação para salvar.")
            return
        
        # Gerar nome de arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        base = self.grid_file.replace('.asc', '')
        output_file = f"{base}_edited_{timestamp}.asc"
        
        print(f"\nSalvando grade modificada em: {output_file}")
        
        with open(output_file, 'w') as f:
            # Escrever cabeçalho original
            for line in self.header:
                f.write(line + '\n')
            
            # Adicionar linha indicando edição
            f.write(f"# Editado em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            
            # Escrever dados
            # A grade original usa formato: i j lon lat depth
            # onde i é índice de longitude e j é índice de latitude
            for j in range(len(self.lats)):
                for i in range(len(self.lons)):
                    i_idx = i + 1  # 1-based
                    j_idx = j + 1  # 1-based
                    lon = self.lons[i]
                    lat = self.lats[j]
                    depth = self.depth[j, i]
                    f.write(f"{i_idx:6d} {j_idx:6d} {lon:10.4f} {lat:10.4f} {depth:10.2f}\n")
        
        print(f"✓ Grade salva com sucesso!")
        print(f"  Total de pontos: {len(self.lats) * len(self.lons)}")
        self.modified = False
        self.update_plot()
    
    def show(self):
        """
        Mostra a janela do editor.
        """
        plt.show()


def main():
    """
    Função principal CLI.
    """
    parser = argparse.ArgumentParser(
        description='Editor Interativo de Grades - RecOM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Exemplos:
  %(prog)s grade.asc
  %(prog)s grade.asc --no-coastline
  %(prog)s grade.asc --no-contours
  %(prog)s grade.asc --no-cartopy
        """
    )
    
    parser.add_argument('grid_file', help='Arquivo de grade ASCII')
    parser.add_argument('--no-coastline', action='store_true',
                       help='Não mostrar linha de costa inicialmente')
    parser.add_argument('--no-contours', action='store_true',
                       help='Não mostrar contornos batimétricos')
    
    args = parser.parse_args()
    
    try:
        editor = GridEditor(
            args.grid_file,
            show_contours=not args.no_contours
        )
        
        if args.no_coastline:
            editor.show_coastline = False
        
        editor.show()
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == '__main__':
    sys.exit(main())
