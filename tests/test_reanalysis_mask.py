#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Testes para Extrator de Máscaras de Reanálises
==============================================

Testes automatizados para o módulo reanalysis_mask.
"""

import sys
import os
import numpy as np
import tempfile

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'tools', 'reanalysis_mask', 'src'))

from mask_extractor import ReanalysisMaskExtractor


def create_fake_reanalysis_file():
    """Cria arquivo NetCDF fake para testes."""
    try:
        import xarray as xr
        
        # Criar dados sintéticos
        lons = np.arange(-60, -30, 0.1)
        lats = np.arange(-35, -5, 0.1)
        
        lon_mesh, lat_mesh = np.meshgrid(lons, lats)
        
        # Criar dados com máscara (oceano/terra)
        # Simples: oceano onde lon < -45, terra onde lon >= -45
        data = np.where(lon_mesh < -45, 10.0, np.nan)
        
        # Criar dataset
        ds = xr.Dataset({
            'eta_t': (['yt_ocean', 'xt_ocean'], data)
        },
        coords={
            'xt_ocean': lons,
            'yt_ocean': lats
        })
        
        # Salvar
        temp_file = tempfile.NamedTemporaryFile(delete=False, suffix='.nc')
        ds.to_netcdf(temp_file.name)
        temp_file.close()
        
        return temp_file.name
    
    except ImportError:
        return None


def test_mask_extraction():
    """Testa extração de máscara."""
    print("\nTeste 1: Extração de Máscara")
    print("-" * 50)
    
    fake_file = create_fake_reanalysis_file()
    
    if fake_file is None:
        print("⚠ xarray não disponível, pulando teste")
        return True
    
    try:
        extractor = ReanalysisMaskExtractor(fake_file, 'eta_t')
        
        # Carregar dados
        assert extractor.load_data(), "Falha ao carregar dados"
        
        # Extrair máscara
        assert extractor.extract_mask(), "Falha ao extrair máscara"
        
        # Verificar máscara
        assert extractor.mask is not None, "Máscara não foi criada"
        assert extractor.mask.shape[0] > 0, "Máscara vazia"
        assert extractor.mask.shape[1] > 0, "Máscara vazia"
        
        # Verificar valores (0 ou 1)
        unique_vals = np.unique(extractor.mask)
        assert np.all(np.isin(unique_vals, [0, 1])), "Máscara deve conter apenas 0 e 1"
        
        # Verificar que há oceano e terra
        assert np.sum(extractor.mask == 1) > 0, "Deve haver pontos oceânicos"
        assert np.sum(extractor.mask == 0) > 0, "Deve haver pontos terrestres"
        
        extractor.cleanup()
        os.unlink(fake_file)
        
        print("✓ Teste passou!")
        return True
        
    except Exception as e:
        print(f"✗ Teste falhou: {e}")
        if fake_file and os.path.exists(fake_file):
            os.unlink(fake_file)
        return False


def test_mask_coarsening():
    """Testa degradação de resolução."""
    print("\nTeste 2: Degradação de Resolução")
    print("-" * 50)
    
    fake_file = create_fake_reanalysis_file()
    
    if fake_file is None:
        print("⚠ xarray não disponível, pulando teste")
        return True
    
    try:
        extractor = ReanalysisMaskExtractor(fake_file, 'eta_t')
        extractor.load_data()
        extractor.extract_mask()
        
        original_shape = extractor.mask.shape
        
        # Degradar para resolução 3x mais grosseira
        target_res = (extractor.resolution_lon * 3, extractor.resolution_lat * 3)
        coarsened_mask, coarsened_lons, coarsened_lats = extractor.coarsen_mask(
            target_res[0], target_res[1]
        )
        
        # Verificar dimensões
        assert coarsened_mask.shape[0] < original_shape[0], "Degradação não reduziu linhas"
        assert coarsened_mask.shape[1] < original_shape[1], "Degradação não reduziu colunas"
        
        # Verificar valores
        unique_vals = np.unique(coarsened_mask)
        assert np.all(np.isin(unique_vals, [0, 1])), "Máscara degradada deve conter apenas 0 e 1"
        
        extractor.cleanup()
        os.unlink(fake_file)
        
        print("✓ Teste passou!")
        return True
        
    except Exception as e:
        print(f"✗ Teste falhou: {e}")
        if fake_file and os.path.exists(fake_file):
            os.unlink(fake_file)
        return False


def test_mask_export():
    """Testa exportação de máscara."""
    print("\nTeste 3: Exportação de Máscara")
    print("-" * 50)
    
    fake_file = create_fake_reanalysis_file()
    
    if fake_file is None:
        print("⚠ xarray não disponível, pulando teste")
        return True
    
    try:
        extractor = ReanalysisMaskExtractor(fake_file, 'eta_t')
        extractor.load_data()
        extractor.extract_mask()
        
        # Exportar
        temp_output = tempfile.NamedTemporaryFile(delete=False, suffix='.asc')
        temp_output.close()
        
        extractor.export_mask(temp_output.name)
        
        # Verificar arquivo foi criado
        assert os.path.exists(temp_output.name), "Arquivo de saída não foi criado"
        assert os.path.getsize(temp_output.name) > 0, "Arquivo de saída está vazio"
        
        # Verificar formato
        with open(temp_output.name, 'r') as f:
            lines = f.readlines()
            
        # Deve ter cabeçalho
        header_lines = [l for l in lines if l.startswith('#')]
        assert len(header_lines) > 0, "Arquivo deve ter cabeçalho"
        
        # Deve ter dados
        data_lines = [l for l in lines if not l.startswith('#') and l.strip()]
        assert len(data_lines) > 0, "Arquivo deve ter dados"
        
        # Verificar formato dos dados (5 colunas)
        first_data_line = data_lines[0]
        parts = first_data_line.split()
        assert len(parts) == 5, "Dados devem ter 5 colunas"
        
        extractor.cleanup()
        os.unlink(fake_file)
        os.unlink(temp_output.name)
        
        print("✓ Teste passou!")
        return True
        
    except Exception as e:
        print(f"✗ Teste falhou: {e}")
        if fake_file and os.path.exists(fake_file):
            os.unlink(fake_file)
        return False


def main():
    """Executa todos os testes."""
    print("="*70)
    print(" TESTES: REANALYSIS MASK")
    print("="*70)
    
    results = []
    
    results.append(test_mask_extraction())
    results.append(test_mask_coarsening())
    results.append(test_mask_export())
    
    print("\n" + "="*70)
    print(" RESUMO DOS TESTES")
    print("="*70)
    
    passed = sum(results)
    total = len(results)
    
    print(f"Testes executados: {total}")
    print(f"Testes aprovados: {passed}")
    print(f"Testes falhados: {total - passed}")
    
    if passed == total:
        print("\n✓ Todos os testes passaram!")
        return 0
    else:
        print(f"\n✗ {total - passed} teste(s) falharam")
        return 1


if __name__ == "__main__":
    sys.exit(main())
