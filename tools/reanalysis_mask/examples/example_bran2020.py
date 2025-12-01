#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Exemplo: Extrair e Aplicar Máscara de Reanálise
===============================================

Este exemplo demonstra como extrair máscara de um arquivo BRAN2020
e aplicá-la em uma grade.
"""

import sys
import os

# Adicionar diretório src ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from mask_extractor import ReanalysisMaskExtractor


def main():
    print("="*70)
    print(" EXEMPLO: EXTRAÇÃO DE MÁSCARA BRAN2020")
    print("="*70)
    
    # Configuração
    bran_file = "/path/to/BRAN2020/ocean_eta_t_2023_07.nc"
    variable = "eta_t"
    target_resolution = (0.25, 0.25)  # dx, dy em graus
    
    # Domínio (costa brasileira)
    lon_range = (-60, -30)
    lat_range = (-35, -5)
    
    print(f"\nConfiguração:")
    print(f"  Arquivo: {os.path.basename(bran_file)}")
    print(f"  Variável: {variable}")
    print(f"  Resolução alvo: {target_resolution[0]}° x {target_resolution[1]}°")
    print(f"  Domínio: lon {lon_range}, lat {lat_range}")
    
    # Verificar se arquivo existe
    if not os.path.exists(bran_file):
        print(f"\n⚠ Arquivo não encontrado: {bran_file}")
        print("\nPara executar este exemplo:")
        print("  1. Baixe dados do BRAN2020")
        print("  2. Ajuste o caminho 'bran_file' neste script")
        print("  3. Execute novamente")
        return 1
    
    try:
        # 1. Inicializar extrator
        print("\n1. Inicializando extrator...")
        extractor = ReanalysisMaskExtractor(bran_file, variable)
        
        # 2. Carregar dados
        print("\n2. Carregando dados...")
        extractor.load_data()
        
        # 3. Extrair máscara
        print("\n3. Extraindo máscara...")
        extractor.extract_mask(time_index=0)
        
        # 4. Recortar domínio
        print("\n4. Recortando domínio espacial...")
        lon_mask = (extractor.lons >= lon_range[0]) & (extractor.lons <= lon_range[1])
        lat_mask = (extractor.lats >= lat_range[0]) & (extractor.lats <= lat_range[1])
        
        extractor.lons = extractor.lons[lon_mask]
        extractor.lats = extractor.lats[lat_mask]
        extractor.mask = extractor.mask[lat_mask, :][:, lon_mask]
        
        # 5. Degradar resolução
        print("\n5. Degradando para resolução alvo...")
        coarsened_mask, coarsened_lons, coarsened_lats = extractor.coarsen_mask(
            target_resolution[0], target_resolution[1],
            threshold=0.5
        )
        
        # 6. Exportar máscara
        output_file = "mask_bran2020_example.asc"
        print(f"\n6. Exportando para {output_file}...")
        extractor.export_mask(output_file, coarsened_mask, coarsened_lons, coarsened_lats)
        
        # 7. Limpeza
        extractor.cleanup()
        
        print("\n" + "="*70)
        print(" EXEMPLO CONCLUÍDO COM SUCESSO!")
        print("="*70)
        print(f"\nMáscara exportada: {output_file}")
        print("\nPróximos passos:")
        print("  1. Visualizar: python ../scripts/visualize_mask.py " + output_file)
        print("  2. Aplicar em grade: python ../scripts/apply_mask.py <grade.asc> " + output_file)
        print("="*70 + "\n")
        
        return 0
        
    except Exception as e:
        print(f"\nERRO: {e}")
        import traceback
        traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
