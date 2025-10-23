#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script para criação de grade batimétrica para o modelo POM
==========================================================

Este script realiza a interpolação de dados batimétricos do GEBCO 
para uma grade regular com espaçamento horizontal definido pelo usuário,
gerando um arquivo ASCII no formato requerido pelo modelo POM.

Formato de saída:
    Arquivo ASCII com 5 colunas: i, j, lon, lat, depth
    - i: índice da coluna (começando em 1)
    - j: índice da linha (começando em 1)
    - lon: longitude em graus decimais
    - lat: latitude em graus decimais
    - depth: profundidade em metros (valores positivos)

Autor: [Seu nome]
Data de criação: Outubro 2025
Versão: 1.0

Dependências:
    - numpy
    - netCDF4 ou xarray
    - scipy
    - matplotlib (opcional, para visualização)

Uso:
    python create_pom_bathymetry_grid.py
    
    Ou modifique os parâmetros na seção CONFIGURAÇÕES no final do script.
"""

import numpy as np
import xarray as xr
from scipy.interpolate import RegularGridInterpolator
import os
import sys
from datetime import datetime


class BathymetryGridGenerator:
    """
    Classe para gerar grades batimétricas interpoladas do GEBCO para o modelo POM.
    
    Attributes:
        gebco_file (str): Caminho para o arquivo NetCDF do GEBCO
        spacing (float): Espaçamento da grade em graus decimais
        lon_min, lon_max (float): Limites de longitude
        lat_min, lat_max (float): Limites de latitude
        gebco_data (xarray.Dataset): Dados do GEBCO carregados
        grid_lons (np.array): Longitudes da nova grade
        grid_lats (np.array): Latitudes da nova grade
        depth_grid (np.array): Profundidades interpoladas
    """
    
    def __init__(self, gebco_file, spacing=0.25):
        """
        Inicializa o gerador de grade batimétrica.
        
        Parameters:
            gebco_file (str): Caminho para o arquivo NetCDF do GEBCO
            spacing (float): Espaçamento horizontal da grade em graus (padrão: 0.25)
        """
        self.gebco_file = gebco_file
        self.spacing = spacing
        self.gebco_data = None
        self.grid_lons = None
        self.grid_lats = None
        self.depth_grid = None
        
        # Verificar se o arquivo existe
        if not os.path.exists(gebco_file):
            raise FileNotFoundError(f"Arquivo GEBCO não encontrado: {gebco_file}")
        
        print(f"Inicializado gerador de grade com espaçamento de {spacing}°")
    
    
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
            print(f"Dimensões: {dict(self.gebco_data.dims)}")
            print(f"Variáveis: {list(self.gebco_data.data_vars)}")
            print(f"Coordenadas: {list(self.gebco_data.coords)}")
            
            # Identificar nomes das variáveis (podem variar entre versões)
            self._identify_variable_names()
            
            print(f"\nExtensão dos dados:")
            print(f"  Longitude: {self.gebco_data[self.lon_name].min().values:.2f}° a "
                  f"{self.gebco_data[self.lon_name].max().values:.2f}°")
            print(f"  Latitude: {self.gebco_data[self.lat_name].min().values:.2f}° a "
                  f"{self.gebco_data[self.lat_name].max().values:.2f}°")
            print(f"  Elevação: {self.gebco_data[self.elev_name].min().values:.1f} m a "
                  f"{self.gebco_data[self.elev_name].max().values:.1f} m")
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
        self.grid_lons = np.arange(lon_min, lon_max + self.spacing, self.spacing)
        self.grid_lats = np.arange(lat_min, lat_max + self.spacing, self.spacing)
        
        n_lons = len(self.grid_lons)
        n_lats = len(self.grid_lats)
        
        print(f"  Número de pontos: {n_lons} (lon) x {n_lats} (lat) = {n_lons * n_lats} pontos")
        print(f"  Espaçamento: {self.spacing}°")
    
    
    def interpolate_bathymetry(self, method='linear'):
        """
        Interpola os dados do GEBCO para a nova grade definida.
        
        Parameters:
            method (str): Método de interpolação ('linear', 'nearest', 'cubic')
                         Padrão: 'linear' (bom equilíbrio entre precisão e velocidade)
        
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
        
        try:
            # Extrair subset dos dados do GEBCO na região de interesse
            # Adicionar uma margem para garantir boa interpolação nas bordas
            margin = 1.0  # graus
            gebco_subset = self.gebco_data.sel(
                {self.lon_name: slice(self.lon_min - margin, self.lon_max + margin),
                 self.lat_name: slice(self.lat_min - margin, self.lat_max + margin)}
            )
            
            print(f"Subset extraído: {dict(gebco_subset.dims)}")
            
            # Obter arrays de coordenadas e dados
            gebco_lons = gebco_subset[self.lon_name].values
            gebco_lats = gebco_subset[self.lat_name].values
            gebco_elevation = gebco_subset[self.elev_name].values
            
            # Criar interpolador
            # Nota: GEBCO usa elevação (negativa para oceano)
            # O POM geralmente usa profundidade (positiva para oceano)
            print("Criando interpolador...")
            interpolator = RegularGridInterpolator(
                (gebco_lats, gebco_lons),
                gebco_elevation,
                method=method,
                bounds_error=False,
                fill_value=0  # Usar 0 para pontos fora do domínio
            )
            
            # Criar malha de pontos para interpolação
            print("Interpolando para a nova grade...")
            lon_mesh, lat_mesh = np.meshgrid(self.grid_lons, self.grid_lats)
            points = np.column_stack([lat_mesh.ravel(), lon_mesh.ravel()])
            
            # Interpolar
            elevation_interp = interpolator(points)
            elevation_interp = elevation_interp.reshape(lon_mesh.shape)
            
            # Converter elevação para profundidade (inverter sinal para oceano)
            # Valores positivos em GEBCO = terra → manter como 0 (sem profundidade)
            # Valores negativos em GEBCO = oceano → converter para profundidade positiva
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
    
    
    def export_to_ascii(self, output_file, format_spec='%6d %6d %10.4f %10.4f %10.2f'):
        """
        Exporta a grade interpolada para arquivo ASCII no formato POM.
        
        O formato de saída é:
            i  j  lon  lat  depth
        
        Parameters:
            output_file (str): Caminho para o arquivo de saída
            format_spec (str): Especificação de formato para numpy.savetxt
                              Padrão: 6 dígitos para i,j; 10.4 para lon,lat; 10.2 para depth
        
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
            # Criar listas para armazenar os dados
            data_list = []
            
            # Iterar sobre a grade
            # j varia de 1 a n_lats (sul para norte)
            # i varia de 1 a n_lons (oeste para leste)
            for j in range(n_lats):
                for i in range(n_lons):
                    i_idx = i + 1  # Índices começam em 1
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
        Cria uma visualização da batimetria interpolada.
        
        Parameters:
            output_file (str): Caminho para salvar a figura (opcional)
                              Se None, apenas mostra a figura
        """
        try:
            import matplotlib.pyplot as plt
            from matplotlib.colors import LinearSegmentedColormap
            
            if self.depth_grid is None:
                print("ERRO: Dados interpolados não disponíveis.")
                return False
            
            print("\nGerando visualização da batimetria...")
            
            fig, ax = plt.subplots(figsize=(12, 8))
            
            # Criar mapa de cores apropriado (azul para oceano)
            colors_ocean = plt.cm.Blues_r(np.linspace(0.2, 1, 256))
            cmap_ocean = LinearSegmentedColormap.from_list('ocean', colors_ocean)
            
            # Plotar batimetria
            lon_mesh, lat_mesh = np.meshgrid(self.grid_lons, self.grid_lats)
            
            # Mascarar terra
            depth_masked = np.ma.masked_where(self.depth_grid == 0, self.depth_grid)
            
            im = ax.pcolormesh(lon_mesh, lat_mesh, depth_masked, 
                              cmap=cmap_ocean, shading='auto')
            
            # Adicionar contornos de profundidade
            if np.max(self.depth_grid) > 0:
                contour_levels = np.linspace(0, np.max(self.depth_grid), 10)
                cs = ax.contour(lon_mesh, lat_mesh, self.depth_grid, 
                               levels=contour_levels, colors='gray', 
                               alpha=0.3, linewidths=0.5)
                ax.clabel(cs, inline=True, fontsize=8, fmt='%d m')
            
            # Formatação
            ax.set_xlabel('Longitude (°)', fontsize=12)
            ax.set_ylabel('Latitude (°)', fontsize=12)
            ax.set_title(f'Grade Batimétrica - Espaçamento {self.spacing}°', 
                        fontsize=14, fontweight='bold')
            ax.grid(True, alpha=0.3)
            ax.set_aspect('equal')
            
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
    
    
    def cleanup(self):
        """Fecha o arquivo NetCDF e libera memória."""
        if self.gebco_data is not None:
            self.gebco_data.close()
            print("\nArquivo GEBCO fechado.")


# ============================================================================
# FUNÇÃO PRINCIPAL
# ============================================================================

def main():
    """
    Função principal para executar o processo completo de geração da grade.
    
    Modifique os parâmetros abaixo conforme necessário para sua aplicação.
    """
    
    # ========================================================================
    # CONFIGURAÇÕES - MODIFIQUE AQUI PARA SUA APLICAÇÃO
    # ========================================================================
    
    # Caminho para o arquivo GEBCO
    GEBCO_FILE = "gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"
    
    # Espaçamento da grade em graus decimais
    GRID_SPACING = 0.25  # 0.25° ≈ 27.8 km no equador
    
    # Extensão geográfica da grade (exemplo: costa brasileira)
    # Modifique estes valores para sua região de interesse
    LON_MIN = -180.0   # Longitude oeste
    LON_MAX = 180.0   # Longitude leste
    LAT_MIN = -90.0   # Latitude sul
    LAT_MAX = 90.0    # Latitude norte
    
    # Arquivo de saída
    OUTPUT_FILE = "pom_bathymetry_grid.asc"
    
    # Gerar visualização? (requer matplotlib)
    GENERATE_PLOT = True
    PLOT_FILE = "pom_bathymetry_grid.png"
    
    # Método de interpolação: 'linear', 'nearest', ou 'cubic'
    INTERPOLATION_METHOD = 'linear'
    
    # ========================================================================
    # PROCESSAMENTO
    # ========================================================================
    
    print("="*70)
    print(" GERADOR DE GRADE BATIMÉTRICA PARA MODELO POM")
    print("="*70)
    print(f"Versão: 1.0")
    print(f"Data: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*70)
    
    try:
        # 1. Inicializar gerador
        generator = BathymetryGridGenerator(GEBCO_FILE, spacing=GRID_SPACING)
        
        # 2. Carregar dados do GEBCO
        if not generator.load_gebco_data():
            print("\nERRO: Falha ao carregar dados do GEBCO")
            return 1
        
        # 3. Definir extensão da grade
        generator.define_grid_extent(LON_MIN, LON_MAX, LAT_MIN, LAT_MAX)
        
        # 4. Interpolar batimetria
        if not generator.interpolate_bathymetry(method=INTERPOLATION_METHOD):
            print("\nERRO: Falha na interpolação")
            return 1
        
        # 5. Exportar para ASCII
        if not generator.export_to_ascii(OUTPUT_FILE):
            print("\nERRO: Falha ao exportar arquivo")
            return 1
        
        # 6. Gerar visualização (opcional)
        if GENERATE_PLOT:
            generator.plot_bathymetry(PLOT_FILE)
        
        # 7. Limpeza
        generator.cleanup()
        
        print("\n" + "="*70)
        print(" PROCESSAMENTO CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print(f"\nArquivo de saída: {OUTPUT_FILE}")
        if GENERATE_PLOT:
            print(f"Visualização: {PLOT_FILE}")
        print("\nO arquivo pode ser usado diretamente no modelo POM.")
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\nERRO FATAL: {e}")
        import traceback
        traceback.print_exc()
        return 1


# ============================================================================
# PONTO DE ENTRADA
# ============================================================================

if __name__ == "__main__":
    sys.exit(main())
