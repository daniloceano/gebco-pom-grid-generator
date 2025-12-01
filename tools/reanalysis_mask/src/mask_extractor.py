#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Extrator de Máscaras de Reanálises Oceânicas
=============================================

Este módulo extrai máscaras terra/oceano de reanálises oceânicas (BRAN2020, etc)
e permite degradar a resolução para grades alvo.

Classes:
    ReanalysisMaskExtractor: Extrator principal de máscaras

Data: Dezembro 2025
"""

import numpy as np
import xarray as xr
import os
from datetime import datetime


class ReanalysisMaskExtractor:
    """
    Extrator de máscaras terra/oceano de reanálises oceânicas.
    
    Identifica automaticamente onde há dados válidos (oceano) e onde
    não há dados (terra/máscara).
    """
    
    def __init__(self, reanalysis_file, variable_name=None):
        """
        Inicializa o extrator.
        
        Parameters:
            reanalysis_file (str): Caminho para arquivo NetCDF da reanálise
            variable_name (str): Nome da variável a usar (None = auto-detectar)
        """
        self.reanalysis_file = reanalysis_file
        self.variable_name = variable_name
        self.dataset = None
        self.mask = None
        self.lons = None
        self.lats = None
        self.resolution_lon = None
        self.resolution_lat = None
        
        print(f"Inicializando extrator de máscara:")
        print(f"  Arquivo: {os.path.basename(reanalysis_file)}")
    
    def load_data(self):
        """
        Carrega dados da reanálise e identifica variável.
        """
        print(f"\nCarregando dados de: {self.reanalysis_file}")
        
        if not os.path.exists(self.reanalysis_file):
            raise FileNotFoundError(f"Arquivo não encontrado: {self.reanalysis_file}")
        
        # Carregar dataset
        self.dataset = xr.open_dataset(self.reanalysis_file)
        
        print(f"✓ Dataset carregado")
        print(f"  Dimensões: {dict(self.dataset.sizes)}")
        print(f"  Variáveis: {list(self.dataset.data_vars)}")
        
        # Identificar coordenadas
        self._identify_coordinates()
        
        # Identificar variável se não especificada
        if self.variable_name is None:
            self._identify_variable()
        
        print(f"  Variável selecionada: {self.variable_name}")
        print(f"  Coordenadas: lon='{self.lon_name}', lat='{self.lat_name}'")
        
        return True
    
    def _identify_coordinates(self):
        """
        Identifica nomes das coordenadas lon/lat.
        """
        # Possíveis nomes para longitude
        lon_candidates = ['lon', 'longitude', 'xt_ocean', 'x', 'nav_lon']
        self.lon_name = None
        for name in lon_candidates:
            if name in self.dataset.coords or name in self.dataset.variables:
                self.lon_name = name
                break
        
        # Possíveis nomes para latitude
        lat_candidates = ['lat', 'latitude', 'yt_ocean', 'y', 'nav_lat']
        self.lat_name = None
        for name in lat_candidates:
            if name in self.dataset.coords or name in self.dataset.variables:
                self.lat_name = name
                break
        
        if not self.lon_name or not self.lat_name:
            raise ValueError("Não foi possível identificar coordenadas lon/lat")
        
        # Extrair arrays de coordenadas
        self.lons = self.dataset[self.lon_name].values
        self.lats = self.dataset[self.lat_name].values
        
        # Calcular resolução
        if len(self.lons) > 1:
            self.resolution_lon = np.abs(np.diff(self.lons).mean())
        if len(self.lats) > 1:
            self.resolution_lat = np.abs(np.diff(self.lats).mean())
        
        print(f"  Resolução original: {self.resolution_lon:.3f}° x {self.resolution_lat:.3f}°")
    
    def _identify_variable(self):
        """
        Identifica variável apropriada para extrair máscara.
        Prioriza variáveis 3D ou 2D com dimensões espaciais.
        """
        # Variáveis preferenciais (oceânicas)
        preferred_vars = ['eta_t', 'ssh', 'zos', 'temp', 'salt', 'u', 'v']
        
        for var in preferred_vars:
            if var in self.dataset.data_vars:
                self.variable_name = var
                return
        
        # Se não encontrou, pegar primeira variável com dimensões lon/lat
        for var in self.dataset.data_vars:
            dims = self.dataset[var].dims
            if self.lon_name in dims and self.lat_name in dims:
                self.variable_name = var
                return
        
        raise ValueError("Não foi possível identificar variável apropriada para máscara")
    
    def extract_mask(self, time_index=0):
        """
        Extrai máscara terra/oceano da reanálise.
        
        Parameters:
            time_index (int): Índice temporal a usar (se houver dimensão temporal)
        
        Returns:
            bool: True se extração foi bem-sucedida
        """
        print(f"\nExtraindo máscara da variável '{self.variable_name}'...")
        
        try:
            var_data = self.dataset[self.variable_name]
            
            # Se tem dimensão temporal, selecionar primeiro passo
            if 'Time' in var_data.dims or 'time' in var_data.dims:
                time_dim = 'Time' if 'Time' in var_data.dims else 'time'
                var_data = var_data.isel({time_dim: time_index})
                print(f"  Usando time_index={time_index}")
            
            # Se tem dimensão vertical, pegar superfície
            depth_dims = ['depth', 'st_ocean', 'lev', 'z']
            for dim in depth_dims:
                if dim in var_data.dims:
                    var_data = var_data.isel({dim: 0})
                    print(f"  Usando superfície (dim='{dim}')")
                    break
            
            # Carregar dados
            data_array = var_data.values
            
            # Criar máscara: 1 = oceano (dados válidos), 0 = terra (NaN/masked)
            self.mask = np.where(np.isfinite(data_array), 1, 0).astype(np.int8)
            
            # Estatísticas
            n_ocean = np.sum(self.mask == 1)
            n_land = np.sum(self.mask == 0)
            total = self.mask.size
            
            print(f"\n✓ Máscara extraída:")
            print(f"  Dimensões: {self.mask.shape}")
            print(f"  Pontos oceânicos: {n_ocean} ({100*n_ocean/total:.1f}%)")
            print(f"  Pontos terrestres: {n_land} ({100*n_land/total:.1f}%)")
            
            return True
            
        except Exception as e:
            print(f"ERRO ao extrair máscara: {e}")
            import traceback
            traceback.print_exc()
            return False
    
    def coarsen_mask(self, target_resolution_lon, target_resolution_lat, 
                     threshold=0.5, align_to_grid=True):
        """
        Degrada máscara para resolução mais grosseira.
        
        Parameters:
            target_resolution_lon (float): Resolução alvo em longitude (graus)
            target_resolution_lat (float): Resolução alvo em latitude (graus)
            threshold (float): Fração mínima de pontos oceânicos para célula ser oceano (0-1)
            align_to_grid (bool): Alinhar grade alvo à grade original
        
        Returns:
            tuple: (coarsened_mask, coarsened_lons, coarsened_lats)
        """
        print(f"\nDegradando máscara:")
        print(f"  Resolução original: {self.resolution_lon:.3f}° x {self.resolution_lat:.3f}°")
        print(f"  Resolução alvo: {target_resolution_lon:.3f}° x {target_resolution_lat:.3f}°")
        print(f"  Threshold oceano: {threshold:.2f}")
        
        # Calcular fator de agregação
        factor_lon = int(np.round(target_resolution_lon / self.resolution_lon))
        factor_lat = int(np.round(target_resolution_lat / self.resolution_lat))
        
        print(f"  Fator de agregação: {factor_lon}x (lon), {factor_lat}x (lat)")
        
        # Definir grade alvo
        if align_to_grid:
            # Alinhar à grade original
            lon_min = self.lons[0]
            lon_max = self.lons[-1]
            lat_min = self.lats[0]
            lat_max = self.lats[-1]
        else:
            lon_min = self.lons.min()
            lon_max = self.lons.max()
            lat_min = self.lats.min()
            lat_max = self.lats.max()
        
        coarsened_lons = np.arange(lon_min, lon_max + target_resolution_lon, target_resolution_lon)
        coarsened_lats = np.arange(lat_min, lat_max + target_resolution_lat, target_resolution_lat)
        
        # Criar máscara degradada
        n_lons_coarse = len(coarsened_lons)
        n_lats_coarse = len(coarsened_lats)
        coarsened_mask = np.zeros((len(coarsened_lats), len(coarsened_lons)), dtype=np.int8)
        
        # Agregar por blocos
        for i, lon in enumerate(coarsened_lons):
            for j, lat in enumerate(coarsened_lats):
                # Encontrar índices na grade fina
                lon_idx_start = np.argmin(np.abs(self.lons - lon))
                lat_idx_start = np.argmin(np.abs(self.lats - lat))
                
                lon_idx_end = min(lon_idx_start + factor_lon, len(self.lons))
                lat_idx_end = min(lat_idx_start + factor_lat, len(self.lats))
                
                # Extrair bloco da máscara fina
                block = self.mask[lat_idx_start:lat_idx_end, lon_idx_start:lon_idx_end]
                
                if block.size > 0:
                    # Calcular fração de pontos oceânicos
                    ocean_fraction = np.sum(block == 1) / block.size
                    
                    # Aplicar threshold
                    coarsened_mask[j, i] = 1 if ocean_fraction >= threshold else 0
        
        # Estatísticas
        n_ocean = np.sum(coarsened_mask == 1)
        n_land = np.sum(coarsened_mask == 0)
        total = coarsened_mask.size
        
        print(f"\n✓ Máscara degradada:")
        print(f"  Dimensões: {coarsened_mask.shape}")
        print(f"  Pontos oceânicos: {n_ocean} ({100*n_ocean/total:.1f}%)")
        print(f"  Pontos terrestres: {n_land} ({100*n_land/total:.1f}%)")
        
        return coarsened_mask, coarsened_lons, coarsened_lats
    
    def export_mask(self, output_file, mask=None, lons=None, lats=None):
        """
        Exporta máscara para arquivo ASCII (formato compatível com grid editor).
        
        Parameters:
            output_file (str): Caminho para arquivo de saída
            mask (np.array): Máscara a exportar (None = usar self.mask)
            lons (np.array): Longitudes (None = usar self.lons)
            lats (np.array): Latitudes (None = usar self.lats)
        """
        if mask is None:
            mask = self.mask
        if lons is None:
            lons = self.lons
        if lats is None:
            lats = self.lats
        
        print(f"\nExportando máscara para: {output_file}")
        
        with open(output_file, 'w') as f:
            # Cabeçalho
            f.write(f"# Máscara terra/oceano extraída de reanálise\n")
            f.write(f"# Gerada em: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write(f"# Fonte: {os.path.basename(self.reanalysis_file)}\n")
            f.write(f"# Variável: {self.variable_name}\n")
            f.write(f"# Formato: i j lon lat mask (1=oceano, 0=terra)\n")
            f.write(f"#\n")
            
            # Dados
            for j, lat in enumerate(lats):
                for i, lon in enumerate(lons):
                    i_idx = i + 1
                    j_idx = j + 1
                    mask_val = mask[j, i]
                    f.write(f"{i_idx:6d} {j_idx:6d} {lon:10.4f} {lat:10.4f} {mask_val:6d}\n")
        
        print(f"✓ Máscara exportada:")
        print(f"  Total de pontos: {len(lons) * len(lats)}")
        print(f"  Tamanho: {os.path.getsize(output_file) / 1024:.1f} KB")
    
    def cleanup(self):
        """Fecha dataset e libera memória."""
        if self.dataset is not None:
            self.dataset.close()
            print("\nDataset fechado.")
