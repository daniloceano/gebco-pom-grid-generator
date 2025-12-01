#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Módulo para geração de grades batimétricas para o modelo POM
============================================================

Este módulo contém a classe BathymetryGridGenerator que realiza a interpolação
de dados batimétricos do GEBCO para uma grade regular, com suporte a processamento
paralelo para melhor performance.

Classes:
    BathymetryGridGenerator: Geradora principal de grades batimétricas

Autor: Projeto POM
Data de criação: Outubro 2025
Versão: 2.0
"""

import numpy as np
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
import os
import sys
from datetime import datetime
from multiprocessing import Pool, cpu_count
from functools import partial


class BathymetryGridGenerator:
    """
    Classe para gerar grades batimétricas interpoladas do GEBCO para o modelo POM.
    
    Esta versão inclui suporte a processamento paralelo para acelerar a interpolação
    de grades grandes.
    
    Attributes:
        gebco_file (str): Caminho para o arquivo NetCDF do GEBCO
        spacing_lon (float): Espaçamento da grade em longitude (graus decimais)
        spacing_lat (float): Espaçamento da grade em latitude (graus decimais)
        lon_min, lon_max (float): Limites de longitude
        lat_min, lat_max (float): Limites de latitude
        gebco_data (xarray.Dataset): Dados do GEBCO carregados
        grid_lons (np.array): Longitudes da nova grade
        grid_lats (np.array): Latitudes da nova grade
        depth_grid (np.array): Profundidades interpoladas
        n_workers (int): Número de processos paralelos a usar
    """
    
    def __init__(self, gebco_file, spacing=None, spacing_lon=None, spacing_lat=None, n_workers=None):
        """
        Inicializa o gerador de grade batimétrica.
        
        Parameters:
            gebco_file (str): Caminho para o arquivo NetCDF do GEBCO
            spacing (float): Espaçamento horizontal da grade em graus (padrão: 0.25)
                           Se fornecido, aplica o mesmo espaçamento para lon e lat
            spacing_lon (float): Espaçamento em longitude (dx). Sobrescreve 'spacing' se fornecido
            spacing_lat (float): Espaçamento em latitude (dy). Sobrescreve 'spacing' se fornecido
            n_workers (int): Número de processos paralelos. Se None, usa cpu_count()-1
        """
        self.gebco_file = gebco_file
        
        # Configurar espaçamentos (suporte a dx e dy diferentes)
        if spacing_lon is not None and spacing_lat is not None:
            self.spacing_lon = spacing_lon
            self.spacing_lat = spacing_lat
        elif spacing is not None:
            self.spacing_lon = spacing
            self.spacing_lat = spacing
        else:
            # Valores padrão
            self.spacing_lon = 0.25
            self.spacing_lat = 0.25
        
        # Manter compatibilidade com código legado
        self.spacing = self.spacing_lon  # Para compatibilidade
        
        self.gebco_data = None
        self.grid_lons = None
        self.grid_lats = None
        self.depth_grid = None
        
        # Configurar número de workers
        if n_workers is None:
            self.n_workers = max(1, cpu_count() - 1)
        else:
            self.n_workers = max(1, min(n_workers, cpu_count()))
        
        # Verificar se o arquivo existe
        if not os.path.exists(gebco_file):
            raise FileNotFoundError(f"Arquivo GEBCO não encontrado: {gebco_file}")
        
        print(f"Inicializado gerador de grade:")
        print(f"  Espaçamento longitude (dx): {self.spacing_lon}°")
        print(f"  Espaçamento latitude (dy): {self.spacing_lat}°")
        print(f"  Processamento paralelo: {self.n_workers} workers")
    
    
    def load_gebco_data(self):
        """
        Carrega os dados do GEBCO a partir do arquivo NetCDF.
        
        O GEBCO fornece dados globais de batimetria/topografia.
        As elevações positivas representam terra, valores negativos representam oceano.
        """
        print(f"\nCarregando dados do GEBCO de: {self.gebco_file}")
        print("Aguarde, isso pode levar alguns momentos...")
        
        try:
            # Carregar usando xarray (mais eficiente para arquivos grandes)
            self.gebco_data = xr.open_dataset(self.gebco_file)
            
            # Mostrar informações básicas do dataset
            print("\n" + "="*60)
            print("INFORMAÇÕES DO DATASET GEBCO")
            print("="*60)
            print(f"Dimensões: {dict(self.gebco_data.sizes)}")
            print(f"Variáveis: {list(self.gebco_data.data_vars)}")
            print(f"Coordenadas: {list(self.gebco_data.coords)}")
            
            # Identificar nomes das variáveis (podem variar entre versões)
            self._identify_variable_names()
            
            print(f"\nExtensão dos dados:")
            print(f"  Longitude: {float(self.gebco_data[self.lon_name].min()):.2f}° a "
                  f"{float(self.gebco_data[self.lon_name].max()):.2f}°")
            print(f"  Latitude: {float(self.gebco_data[self.lat_name].min()):.2f}° a "
                  f"{float(self.gebco_data[self.lat_name].max()):.2f}°")
            print(f"  Elevação: {float(self.gebco_data[self.elev_name].min()):.1f} m a "
                  f"{float(self.gebco_data[self.elev_name].max()):.1f} m")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"ERRO ao carregar dados do GEBCO: {e}")
            return False
    
    
    def _identify_variable_names(self):
        """
        Identifica os nomes das variáveis no dataset GEBCO.
        Diferentes versões do GEBCO podem usar nomes diferentes.
        """
        # Nomes comuns para longitude
        lon_candidates = ['lon', 'longitude', 'x']
        self.lon_name = None
        for name in lon_candidates:
            if name in self.gebco_data.coords or name in self.gebco_data.variables:
                self.lon_name = name
                break
        
        # Nomes comuns para latitude
        lat_candidates = ['lat', 'latitude', 'y']
        self.lat_name = None
        for name in lat_candidates:
            if name in self.gebco_data.coords or name in self.gebco_data.variables:
                self.lat_name = name
                break
        
        # Nomes comuns para elevação/batimetria
        elev_candidates = ['elevation', 'Band1', 'z', 'depth']
        self.elev_name = None
        for name in elev_candidates:
            if name in self.gebco_data.variables:
                self.elev_name = name
                break
        
        if not all([self.lon_name, self.lat_name, self.elev_name]):
            raise ValueError("Não foi possível identificar todas as variáveis necessárias no arquivo GEBCO")
        
        print(f"\nVariáveis identificadas:")
        print(f"  Longitude: {self.lon_name}")
        print(f"  Latitude: {self.lat_name}")
        print(f"  Elevação: {self.elev_name}")
    
    
    def define_grid_extent(self, lon_min, lon_max, lat_min, lat_max):
        """
        Define a extensão geográfica da grade a ser gerada.
        
        Parameters:
            lon_min (float): Longitude mínima (oeste)
            lon_max (float): Longitude máxima (leste)
            lat_min (float): Latitude mínima (sul)
            lat_max (float): Latitude máxima (norte)
        """
        self.lon_min = lon_min
        self.lon_max = lon_max
        self.lat_min = lat_min
        self.lat_max = lat_max
        
        print(f"\nExtensão da grade definida:")
        print(f"  Longitude: {lon_min}° a {lon_max}°")
        print(f"  Latitude: {lat_min}° a {lat_max}°")
        
        # Criar vetores de coordenadas da nova grade
        self.grid_lons = np.arange(lon_min, lon_max + self.spacing_lon, self.spacing_lon)
        self.grid_lats = np.arange(lat_min, lat_max + self.spacing_lat, self.spacing_lat)
        
        n_lons = len(self.grid_lons)
        n_lats = len(self.grid_lats)
        
        print(f"  Número de pontos: {n_lons} (lon) x {n_lats} (lat) = {n_lons * n_lats} pontos")
        print(f"  Espaçamento longitude (dx): {self.spacing_lon}°")
        print(f"  Espaçamento latitude (dy): {self.spacing_lat}°")
    
    
    @staticmethod
    def _interpolate_chunk(args):
        """
        Função auxiliar para interpolar um chunk de dados em paralelo.
        
        Parameters:
            args (tuple): (lat_indices, interpolator, grid_lons, grid_lats)
        
        Returns:
            tuple: (lat_indices, interpolated_data)
        """
        lat_indices, interpolator, grid_lons, grid_lats = args
        
        # Criar sub-malha para este chunk
        lon_mesh, lat_mesh = np.meshgrid(grid_lons, grid_lats[lat_indices])
        points = np.column_stack([lat_mesh.ravel(), lon_mesh.ravel()])
        
        # Interpolar
        elevation_chunk = interpolator(points)
        elevation_chunk = elevation_chunk.reshape(len(lat_indices), len(grid_lons))
        
        return (lat_indices, elevation_chunk)
    
    
    def interpolate_bathymetry(self, method='linear', parallel=True):
        """
        Interpola os dados do GEBCO para a nova grade definida.
        
        Parameters:
            method (str): Método de interpolação ('linear', 'nearest', 'cubic')
                         Padrão: 'linear' (bom equilíbrio entre precisão e velocidade)
            parallel (bool): Se True, usa processamento paralelo
        
        Returns:
            bool: True se a interpolação foi bem-sucedida
        """
        if self.gebco_data is None:
            print("ERRO: Dados do GEBCO não carregados. Execute load_gebco_data() primeiro.")
            return False
        
        if self.grid_lons is None or self.grid_lats is None:
            print("ERRO: Grade não definida. Execute define_grid_extent() primeiro.")
            return False
        
        print(f"\nIniciando interpolação dos dados do GEBCO...")
        print(f"Método de interpolação: {method}")
        print(f"Processamento paralelo: {'Sim' if parallel and self.n_workers > 1 else 'Não'}")
        
        try:
            # Extrair subset dos dados do GEBCO na região de interesse
            # Adicionar uma margem para garantir boa interpolação nas bordas
            margin = 1.0  # graus
            gebco_subset = self.gebco_data.sel(
                {self.lon_name: slice(self.lon_min - margin, self.lon_max + margin),
                 self.lat_name: slice(self.lat_min - margin, self.lat_max + margin)}
            )
            
            print(f"Subset extraído: {dict(gebco_subset.sizes)}")
            
            # Obter arrays de coordenadas e dados
            gebco_lons = gebco_subset[self.lon_name].values
            gebco_lats = gebco_subset[self.lat_name].values
            gebco_elevation = gebco_subset[self.elev_name].values
            
            # Criar interpolador
            print("Criando interpolador...")
            interpolator = RegularGridInterpolator(
                (gebco_lats, gebco_lons),
                gebco_elevation,
                method=method,
                bounds_error=False,
                fill_value=0
            )
            
            # Interpolar
            if parallel and self.n_workers > 1:
                print(f"Interpolando em paralelo usando {self.n_workers} workers...")
                elevation_interp = self._interpolate_parallel(interpolator)
            else:
                print("Interpolando...")
                elevation_interp = self._interpolate_serial(interpolator)
            
            # Converter elevação para profundidade (inverter sinal para oceano)
            self.depth_grid = np.where(elevation_interp < 0, -elevation_interp, 0)
            
            # Estatísticas
            ocean_points = np.sum(self.depth_grid > 0)
            land_points = np.sum(self.depth_grid == 0)
            max_depth = np.max(self.depth_grid)
            mean_depth = np.mean(self.depth_grid[self.depth_grid > 0]) if ocean_points > 0 else 0
            
            print("\n" + "="*60)
            print("INTERPOLAÇÃO CONCLUÍDA")
            print("="*60)
            print(f"Pontos oceânicos: {ocean_points} ({100*ocean_points/(ocean_points+land_points):.1f}%)")
            print(f"Pontos terrestres: {land_points} ({100*land_points/(ocean_points+land_points):.1f}%)")
            print(f"Profundidade máxima: {max_depth:.1f} m")
            print(f"Profundidade média (oceano): {mean_depth:.1f} m")
            print("="*60 + "\n")
            
            return True
            
        except Exception as e:
            print(f"ERRO durante a interpolação: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def _interpolate_serial(self, interpolator):
        """
        Interpolação serial (sem paralelização).
        
        Parameters:
            interpolator: Interpolador RegularGridInterpolator
        
        Returns:
            np.array: Dados interpolados
        """
        lon_mesh, lat_mesh = np.meshgrid(self.grid_lons, self.grid_lats)
        points = np.column_stack([lat_mesh.ravel(), lon_mesh.ravel()])
        elevation_interp = interpolator(points)
        return elevation_interp.reshape(lon_mesh.shape)
    
    
    def _interpolate_parallel(self, interpolator):
        """
        Interpolação paralela dividindo por linhas de latitude.
        
        Parameters:
            interpolator: Interpolador RegularGridInterpolator
        
        Returns:
            np.array: Dados interpolados
        """
        n_lats = len(self.grid_lats)
        
        # Dividir latitudes em chunks para processamento paralelo
        chunk_size = max(1, n_lats // self.n_workers)
        chunks = []
        
        for i in range(0, n_lats, chunk_size):
            lat_indices = range(i, min(i + chunk_size, n_lats))
            chunks.append((lat_indices, interpolator, self.grid_lons, self.grid_lats))
        
        # Processar chunks em paralelo
        elevation_interp = np.zeros((n_lats, len(self.grid_lons)))
        
        with Pool(processes=self.n_workers) as pool:
            results = pool.map(self._interpolate_chunk, chunks)
        
        # Combinar resultados
        for lat_indices, chunk_data in results:
            for idx, lat_idx in enumerate(lat_indices):
                elevation_interp[lat_idx, :] = chunk_data[idx, :]
        
        return elevation_interp
    
    
    def export_to_ascii(self, output_file, format_spec='%6d %6d %10.4f %10.4f %10.2f'):
        """
        Exporta a grade interpolada para arquivo ASCII no formato POM.
        
        O formato de saída é:
            i  j  lon  lat  depth
        
        Parameters:
            output_file (str): Caminho para o arquivo de saída
            format_spec (str): Especificação de formato para numpy.savetxt
        
        Returns:
            bool: True se a exportação foi bem-sucedida
        """
        if self.depth_grid is None:
            print("ERRO: Dados interpolados não disponíveis. Execute interpolate_bathymetry() primeiro.")
            return False
        
        print(f"\nExportando grade para: {output_file}")
        
        try:
            # Criar arrays de índices
            n_lats, n_lons = self.depth_grid.shape
            
            # Preparar dados para exportação
            data_list = []
            
            # Iterar sobre a grade
            for j in range(n_lats):
                for i in range(n_lons):
                    i_idx = i + 1
                    j_idx = j + 1
                    lon = self.grid_lons[i]
                    lat = self.grid_lats[j]
                    depth = self.depth_grid[j, i]
                    
                    data_list.append([i_idx, j_idx, lon, lat, depth])
            
            # Converter para array numpy
            data_array = np.array(data_list)
            
            # Criar cabeçalho descritivo
            header = f"""Grade batimétrica para modelo POM
Gerada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Fonte: GEBCO 2025
Espaçamento: {self.spacing}° ({self.spacing * 111:.1f} km no equador)
Extensão: Lon [{self.lon_min}°, {self.lon_max}°], Lat [{self.lat_min}°, {self.lat_max}°]
Dimensões: {n_lons} x {n_lats} = {len(data_list)} pontos
Formato: i (col), j (row), longitude (°), latitude (°), profundidade (m)
"""
            
            # Salvar arquivo
            np.savetxt(
                output_file,
                data_array,
                fmt=format_spec,
                header=header,
                comments='# '
            )
            
            print(f"✓ Arquivo salvo com sucesso!")
            print(f"  Total de linhas: {len(data_list)}")
            print(f"  Tamanho do arquivo: {os.path.getsize(output_file) / 1024:.1f} KB")
            
            return True
            
        except Exception as e:
            print(f"ERRO ao exportar arquivo: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def plot_bathymetry(self, output_file=None):
        """
        Cria uma visualização da batimetria interpolada, com linha de costa usando Cartopy se disponível.
        
        Parameters:
            output_file (str): Caminho para salvar a figura (opcional)
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.colors import LinearSegmentedColormap
            import cartopy.crs as ccrs
            import cartopy.feature as cfeature

            if self.depth_grid is None:
                print("ERRO: Dados interpolados não disponíveis.")
                return False

            print("\nGerando visualização da batimetria...")

            # Usar Cartopy se disponível
            proj = ccrs.PlateCarree()
            fig, ax = plt.subplots(figsize=(12, 8), subplot_kw={'projection': proj})
            ax.set_extent([self.lon_min, self.lon_max, self.lat_min, self.lat_max], crs=proj)
            # Adicionar linha de costa
            ax.add_feature(cfeature.COASTLINE, linewidth=2, edgecolor='black')
            ax.add_feature(cfeature.BORDERS, linestyle=':', edgecolor='gray')
            ax.add_feature(cfeature.LAND, facecolor='lightgray')
            # Criar mapa de cores apropriado (azul para oceano)
            colors_ocean = plt.cm.Blues_r(np.linspace(0.2, 1, 256))
            cmap_ocean = LinearSegmentedColormap.from_list('ocean', colors_ocean)

            # Plotar batimetria
            lon_mesh, lat_mesh = np.meshgrid(self.grid_lons, self.grid_lats)
            depth_masked = np.ma.masked_where(self.depth_grid == 0, self.depth_grid)

            im = ax.pcolormesh(lon_mesh, lat_mesh, depth_masked,
                               cmap=cmap_ocean, shading='auto', transform=ccrs.PlateCarree())
            # Adicionar contornos de profundidade
            if np.max(self.depth_grid) > 0:
                contour_levels = np.linspace(0, np.max(self.depth_grid), 10)
                cs = ax.contour(lon_mesh, lat_mesh, self.depth_grid,
                                levels=contour_levels, colors='gray',
                                alpha=0.3, linewidths=0.5, transform=ccrs.PlateCarree())
                ax.clabel(cs, inline=True, fontsize=8, fmt='%d m')

            # Formatação
            ax.set_xlabel('Longitude (°)', fontsize=12)
            ax.set_ylabel('Latitude (°)', fontsize=12)
            ax.set_title(f'Grade Batimétrica - Espaçamento {self.spacing}°',
                        fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)

            # Barra de cores
            cbar = plt.colorbar(im, ax=ax, label='Profundidade (m)')

            plt.tight_layout()

            if output_file:
                plt.savefig(output_file, dpi=300, bbox_inches='tight')
                print(f"✓ Figura salva em: {output_file}")
            else:
                plt.show()

            plt.close()
            return True

        except ImportError:
            print("Matplotlib não disponível. Pulando visualização.")
            return False
        except Exception as e:
            print(f"ERRO ao criar visualização: {e}")
            return False
    
    
    def export_to_asc_grid(self, output_file):
        """
        Exporta a grade interpolada para formato ASC Grid (ESRI ASCII Raster).
        
        Este formato é compatível com o editor interativo e ferramentas GIS.
        
        Parameters:
            output_file (str): Caminho para o arquivo de saída
        
        Returns:
            bool: True se a exportação foi bem-sucedida
        """
        if self.depth_grid is None:
            print("ERRO: Dados interpolados não disponíveis. Execute interpolate_bathymetry() primeiro.")
            return False
        
        print(f"\nExportando grade ASC Grid para: {output_file}")
        
        try:
            n_lats, n_lons = self.depth_grid.shape
            
            with open(output_file, 'w') as f:
                # Escrever cabeçalho
                f.write(f"# Grade batimétrica POM - Formato ASC Grid\n")
                f.write(f"# Gerada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                f.write(f"# Fonte: GEBCO 2025\n")
                f.write(f"ncols         {n_lons}\n")
                f.write(f"nrows         {n_lats}\n")
                f.write(f"xllcorner     {self.grid_lons[0]}\n")
                f.write(f"yllcorner     {self.grid_lats[0]}\n")
                f.write(f"dx            {self.spacing_lon}\n")
                f.write(f"dy            {self.spacing_lat}\n")
                f.write(f"NODATA_value  -9999\n")
                
                # Escrever dados (linha por linha)
                for j in range(n_lats):
                    row_values = []
                    for i in range(n_lons):
                        depth = self.depth_grid[j, i]
                        row_values.append(f'{depth:10.3f}')
                    f.write(' '.join(row_values) + '\n')
            
            print(f"✓ Arquivo ASC Grid salvo com sucesso!")
            print(f"  Dimensões: {n_lons} x {n_lats}")
            print(f"  Tamanho: {os.path.getsize(output_file) / 1024:.1f} KB")
            print(f"  Compatível com editor interativo e ferramentas GIS")
            
            return True
            
        except Exception as e:
            print(f"ERRO ao exportar ASC Grid: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    
    def cleanup(self):
        """Fecha o arquivo NetCDF e libera memória."""
        if self.gebco_data is not None:
            self.gebco_data.close()
            print("\nArquivo GEBCO fechado.")
