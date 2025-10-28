#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Editor Interativo de Grade Batimétrica
========================================

Este script permite editar manualmente uma grade batimétrica já gerada,
convertendo pontos de água para terra e vice-versa. Isso é útil para
corrigir problemas que podem causar instabilidades no modelo POM.

Características:
- Visualização da batimetria com linha de costa
- Zoom in/out interativo
- Click para alternar terra/água
- Grade de células do modelo visível
- Salvamento automático das modificações

Controles:
- Click esquerdo: Alternar terra/água no ponto clicado
- Tecla '+' ou scroll up: Zoom in
- Tecla '-' ou scroll down: Zoom out
- Tecla 'r': Reset do zoom
- Tecla 's': Salvar modificações
- Tecla 'q' ou fechar janela: Sair

Uso:
    python edit_grid_interactive.py <arquivo_grade.asc>
    
Autor: Projeto POM
Data: Outubro 2025
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from matplotlib.collections import LineCollection
import sys
import os
from datetime import datetime
import argparse


class InteractiveBathymetryEditor:
    """
    Editor interativo de grades batimétricas com interface gráfica.
    """
    
    def __init__(self, grid_file):
        """
        Inicializa o editor.
        
        Parameters:
            grid_file (str): Caminho para o arquivo ASCII da grade
        """
        self.grid_file = grid_file
        self.backup_file = grid_file.replace('.asc', '_backup.asc')
        self.modified = False
        
        # Carregar dados
        self.load_grid()
        
        # Estado da interface
        self.show_grid = True
        self.show_coastline = True
        self.current_xlim = None
        self.current_ylim = None
        
        # Configurar figura
        self.setup_figure()
        
        print("\n" + "="*70)
        print(" EDITOR INTERATIVO DE GRADE BATIMÉTRICA")
        print("="*70)
        print("\nControles:")
        print("  Click esquerdo: Alternar terra/água")
        print("  '+' ou scroll up: Zoom in")
        print("  '-' ou scroll down: Zoom out")
        print("  'r': Reset do zoom")
        print("  'g': Toggle grade")
        print("  'c': Toggle linha de costa")
        print("  's': Salvar modificações")
        print("  'q': Sair")
        print("="*70 + "\n")
    
    def load_grid(self):
        """
        Carrega a grade batimétrica do arquivo ASCII.
        """
        print(f"\nCarregando grade de: {self.grid_file}")
        
        if not os.path.exists(self.grid_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.grid_file}")
        
        # Fazer backup se não existe
        if not os.path.exists(self.backup_file):
            import shutil
            shutil.copy2(self.grid_file, self.backup_file)
            print(f"Backup criado: {self.backup_file}")
        
        # Ler cabeçalho e dados
        with open(self.grid_file, 'r') as f:
            lines = f.readlines()
        
        # Parsear cabeçalho
        header = {}
        data_start = 0
        for i, line in enumerate(lines):
            if line.strip().startswith('#'):
                continue
            parts = line.strip().split()
            if len(parts) == 2:
                try:
                    header[parts[0]] = float(parts[1])
                    data_start = i + 1
                except ValueError:
                    break
            else:
                break
        
        self.ncols = int(header.get('ncols', header.get('NCOLS')))
        self.nrows = int(header.get('nrows', header.get('NROWS')))
        self.xllcorner = header.get('xllcorner', header.get('XLLCORNER'))
        self.yllcorner = header.get('yllcorner', header.get('YLLCORNER'))
        self.cellsize_lon = header.get('cellsize', header.get('CELLSIZE', header.get('dx', 0.25)))
        self.cellsize_lat = header.get('cellsize', header.get('CELLSIZE', header.get('dy', 0.25)))
        
        # Tentar pegar dx e dy separados se existirem
        if 'dx' in header:
            self.cellsize_lon = header['dx']
        if 'dy' in header:
            self.cellsize_lat = header['dy']
        
        self.nodata = header.get('NODATA_value', header.get('nodata_value', -9999))
        
        # Ler dados
        data_lines = lines[data_start:]
        self.depth = np.array([[float(val) for val in line.split()] 
                               for line in data_lines if line.strip()])
        
        # Criar coordenadas
        self.lons = self.xllcorner + np.arange(self.ncols) * self.cellsize_lon
        self.lats = self.yllcorner + np.arange(self.nrows) * self.cellsize_lat
        
        # Inverter se necessário (depende da convenção do arquivo)
        if self.depth.shape[0] != self.nrows or self.depth.shape[1] != self.ncols:
            self.depth = self.depth.T
        
        print(f"Grade carregada:")
        print(f"  Dimensões: {self.ncols} x {self.nrows}")
        print(f"  Longitude: {self.lons[0]:.2f} a {self.lons[-1]:.2f}")
        print(f"  Latitude: {self.lats[0]:.2f} a {self.lats[-1]:.2f}")
        print(f"  Cellsize lon (dx): {self.cellsize_lon}")
        print(f"  Cellsize lat (dy): {self.cellsize_lat}")
        print(f"  Profundidade: {self.depth.min():.1f} a {self.depth.max():.1f} m")
    
    def setup_figure(self):
        """
        Configura a figura matplotlib e conecta eventos.
        """
        self.fig, self.ax = plt.subplots(figsize=(14, 10))
        self.fig.canvas.manager.set_window_title('Editor de Grade Batimétrica - POM')
        
        # Plot inicial
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
        
        # Preparar dados para visualização
        depth_plot = np.ma.masked_where(self.depth == self.nodata, self.depth)
        
        # Plot batimetria com shading
        lon_edges = np.concatenate([self.lons - self.cellsize_lon/2, 
                                    [self.lons[-1] + self.cellsize_lon/2]])
        lat_edges = np.concatenate([self.lats - self.cellsize_lat/2, 
                                    [self.lats[-1] + self.cellsize_lat/2]])
        
        # Colormap: azul para água, verde/marrom para terra
        im = self.ax.pcolormesh(lon_edges, lat_edges, depth_plot, 
                                cmap='terrain', shading='flat',
                                vmin=-6000, vmax=1000)
        
        # Linha de costa (contorno de elevação zero)
        if self.show_coastline:
            try:
                cs = self.ax.contour(self.lons, self.lats, self.depth, 
                                    levels=[0], colors='red', linewidths=2)
                self.ax.clabel(cs, inline=True, fontsize=8, fmt='Costa')
            except:
                pass  # Se não houver linha de costa visível
        
        # Grade de células
        if self.show_grid:
            self.draw_grid()
        
        # Colorbar
        if not hasattr(self, 'cbar'):
            self.cbar = plt.colorbar(im, ax=self.ax, label='Elevação (m)')
        
        # Labels e título
        self.ax.set_xlabel('Longitude (°)')
        self.ax.set_ylabel('Latitude (°)')
        title = 'Grade Batimétrica POM - Clique para editar'
        if self.modified:
            title += ' [MODIFICADO]'
        self.ax.set_title(title)
        
        # Manter zoom se existir
        if self.current_xlim is not None:
            self.ax.set_xlim(self.current_xlim)
            self.ax.set_ylim(self.current_ylim)
        
        self.ax.grid(True, alpha=0.3)
        self.fig.canvas.draw()
    
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
        
        lc_v = LineCollection(lines_v, colors='gray', linewidths=0.5, alpha=0.4)
        lc_h = LineCollection(lines_h, colors='gray', linewidths=0.5, alpha=0.4)
        
        self.ax.add_collection(lc_v)
        self.ax.add_collection(lc_h)
    
    def find_nearest_cell(self, lon, lat):
        """
        Encontra a célula mais próxima de um ponto clicado.
        
        Returns:
            tuple: (i, j) índices da célula
        """
        i = np.argmin(np.abs(self.lats - lat))
        j = np.argmin(np.abs(self.lons - lon))
        return i, j
    
    def toggle_cell(self, i, j):
        """
        Alterna entre terra e água em uma célula.
        
        Parameters:
            i, j (int): Índices da célula
        """
        current_depth = self.depth[i, j]
        
        if current_depth == self.nodata or current_depth > 0:
            # Terra -> Água (profundidade média da região)
            water_cells = self.depth[self.depth < 0]
            if len(water_cells) > 0:
                new_depth = np.median(water_cells)
            else:
                new_depth = -100.0
            action = "TERRA → ÁGUA"
        else:
            # Água -> Terra
            new_depth = 100.0
            action = "ÁGUA → TERRA"
        
        self.depth[i, j] = new_depth
        self.modified = True
        
        print(f"[{action}] Célula ({i}, {j}): lon={self.lons[j]:.3f}°, "
              f"lat={self.lats[i]:.3f}°, nova profundidade={new_depth:.1f}m")
        
        self.update_plot()
    
    def on_click(self, event):
        """
        Callback para cliques do mouse.
        """
        if event.inaxes != self.ax:
            return
        
        if event.button == 1:  # Click esquerdo
            i, j = self.find_nearest_cell(event.xdata, event.ydata)
            self.toggle_cell(i, j)
    
    def on_key(self, event):
        """
        Callback para teclas pressionadas.
        """
        if event.key == 'q':
            self.quit()
        elif event.key == 's':
            self.save()
        elif event.key == 'r':
            self.reset_zoom()
        elif event.key == 'g':
            self.show_grid = not self.show_grid
            print(f"Grade: {'ON' if self.show_grid else 'OFF'}")
            self.update_plot()
        elif event.key == 'c':
            self.show_coastline = not self.show_coastline
            print(f"Linha de costa: {'ON' if self.show_coastline else 'OFF'}")
            self.update_plot()
        elif event.key in ['+', '=']:
            self.zoom(1.5)
        elif event.key == '-':
            self.zoom(0.67)
    
    def on_scroll(self, event):
        """
        Callback para scroll do mouse (zoom).
        """
        if event.inaxes != self.ax:
            return
        
        if event.button == 'up':
            self.zoom(1.2, event.xdata, event.ydata)
        elif event.button == 'down':
            self.zoom(0.83, event.xdata, event.ydata)
    
    def zoom(self, factor, x=None, y=None):
        """
        Aplica zoom na visualização.
        
        Parameters:
            factor (float): Fator de zoom (>1 = zoom in, <1 = zoom out)
            x, y (float): Coordenadas do centro do zoom
        """
        # Salvar limites atuais
        self.current_xlim = self.ax.get_xlim()
        self.current_ylim = self.ax.get_ylim()
        
        # Calcular novo range
        x_range = self.current_xlim[1] - self.current_xlim[0]
        y_range = self.current_ylim[1] - self.current_ylim[0]
        
        new_x_range = x_range / factor
        new_y_range = y_range / factor
        
        # Centro do zoom
        if x is None or y is None:
            x_center = sum(self.current_xlim) / 2
            y_center = sum(self.current_ylim) / 2
        else:
            x_center = x
            y_center = y
        
        # Aplicar
        self.ax.set_xlim([x_center - new_x_range/2, x_center + new_x_range/2])
        self.ax.set_ylim([y_center - new_y_range/2, y_center + new_y_range/2])
        
        self.current_xlim = self.ax.get_xlim()
        self.current_ylim = self.ax.get_ylim()
        
        self.fig.canvas.draw()
    
    def reset_zoom(self):
        """
        Restaura o zoom para visualização completa.
        """
        self.current_xlim = None
        self.current_ylim = None
        self.ax.set_xlim([self.lons[0] - self.cellsize_lon/2, 
                          self.lons[-1] + self.cellsize_lon/2])
        self.ax.set_ylim([self.lats[0] - self.cellsize_lat/2, 
                          self.lats[-1] + self.cellsize_lat/2])
        self.fig.canvas.draw()
        print("Zoom resetado")
    
    def save(self):
        """
        Salva as modificações no arquivo.
        """
        if not self.modified:
            print("Nenhuma modificação para salvar.")
            return
        
        print(f"\nSalvando modificações em: {self.grid_file}")
        
        # Criar novo arquivo com timestamp
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        version_file = self.grid_file.replace('.asc', f'_v{timestamp}.asc')
        
        with open(version_file, 'w') as f:
            # Escrever cabeçalho
            f.write(f"# Grade batimétrica editada - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"ncols         {self.ncols}\n")
            f.write(f"nrows         {self.nrows}\n")
            f.write(f"xllcorner     {self.xllcorner}\n")
            f.write(f"yllcorner     {self.yllcorner}\n")
            f.write(f"dx            {self.cellsize_lon}\n")
            f.write(f"dy            {self.cellsize_lat}\n")
            f.write(f"NODATA_value  {self.nodata}\n")
            
            # Escrever dados
            for row in self.depth:
                f.write(' '.join([f'{val:10.3f}' for val in row]) + '\n')
        
        print(f"Versão salva: {version_file}")
        
        # Sobrescrever original
        import shutil
        shutil.copy2(version_file, self.grid_file)
        print(f"Arquivo principal atualizado: {self.grid_file}")
        
        self.modified = False
        self.update_plot()
    
    def quit(self):
        """
        Sai do editor.
        """
        if self.modified:
            print("\n" + "="*70)
            print("ATENÇÃO: Existem modificações não salvas!")
            print("="*70)
            response = input("Deseja salvar antes de sair? (s/n): ").lower()
            if response == 's':
                self.save()
        
        print("\nEncerrando editor...")
        plt.close(self.fig)
    
    def run(self):
        """
        Inicia o editor interativo.
        """
        plt.show()


def main():
    """
    Função principal.
    """
    parser = argparse.ArgumentParser(
        description='Editor interativo de grade batimétrica POM',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Controles:
  Click esquerdo : Alternar terra/água
  + ou scroll up  : Zoom in
  - ou scroll down: Zoom out
  r              : Reset zoom
  g              : Toggle grade
  c              : Toggle linha de costa
  s              : Salvar
  q              : Sair

Exemplo:
  python edit_grid_interactive.py ../output/pom_bathymetry_grid.asc
        """
    )
    
    parser.add_argument('grid_file', help='Arquivo ASCII da grade batimétrica')
    
    args = parser.parse_args()
    
    try:
        editor = InteractiveBathymetryEditor(args.grid_file)
        editor.run()
    except KeyboardInterrupt:
        print("\n\nInterrompido pelo usuário.")
        sys.exit(0)
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
