#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de teste e validação do gerador de grade batimétrica
===========================================================

Este script verifica se todas as dependências estão instaladas
e testa as funcionalidades básicas do gerador de grade.

Uso:
    python test_bathymetry_generator.py
"""

import sys
import os

# Determinar o diretório raiz do projeto (assumindo que tests/ está no root)
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))

# Adicionar o projeto root ao PYTHONPATH para garantir imports
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def test_imports():
    """
    Testa se todas as dependências necessárias estão instaladas.
    
    Returns:
        bool: True se todas as dependências estão OK
    """
    print("\n" + "="*70)
    print(" TESTE 1: Verificação de Dependências")
    print("="*70)
    
    required_modules = {
        'numpy': 'Manipulação de arrays numéricos',
        'scipy': 'Interpolação científica',
        'xarray': 'Leitura de dados NetCDF',
        'netCDF4': 'Suporte NetCDF',
    }
    
    optional_modules = {
        'matplotlib': 'Visualização de dados',
    }
    
    all_ok = True
    
    # Testar módulos obrigatórios
    print("\nMódulos obrigatórios:")
    for module, description in required_modules.items():
        try:
            __import__(module)
            version = __import__(module).__version__
            print(f"  ✓ {module:15s} {version:10s} - {description}")
        except ImportError:
            print(f"  ✗ {module:15s} {'FALTANDO':10s} - {description}")
            all_ok = False
    
    # Testar módulos opcionais
    print("\nMódulos opcionais:")
    for module, description in optional_modules.items():
        try:
            __import__(module)
            version = __import__(module).__version__
            print(f"  ✓ {module:15s} {version:10s} - {description}")
        except ImportError:
            print(f"  ⚠ {module:15s} {'FALTANDO':10s} - {description} (opcional)")
    
    if all_ok:
        print("\n✓ Todas as dependências obrigatórias estão instaladas!")
    else:
        print("\n✗ Algumas dependências estão faltando.")
        print("  Instale com: pip install -r requirements.txt")
    
    return all_ok


def test_gebco_file():
    """
    Verifica se o arquivo GEBCO está presente e acessível.
    
    Returns:
        bool: True se o arquivo existe
    """
    print("\n" + "="*70)
    print(" TESTE 2: Verificação do Arquivo GEBCO")
    print("="*70)
    
    gebco_file = os.path.join(PROJECT_ROOT, "gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc")
    
    if os.path.exists(gebco_file):
        size_mb = os.path.getsize(gebco_file) / (1024**2)
        print(f"\n✓ Arquivo GEBCO encontrado: {gebco_file}")
        print(f"  Tamanho: {size_mb:.1f} MB")
        return True
    else:
        print(f"\n✗ Arquivo GEBCO não encontrado: {gebco_file}")
        print("  Certifique-se de que o arquivo está no local correto.")
        return False


def test_generator_class():
    """
    Testa a importação e inicialização da classe geradora.
    
    Returns:
        bool: True se a classe pode ser importada e inicializada
    """
    print("\n" + "="*70)
    print(" TESTE 3: Verificação da Classe Geradora")
    print("="*70)
    
    try:
        from create_pom_bathymetry_grid import BathymetryGridGenerator
        print("\n✓ Classe BathymetryGridGenerator importada com sucesso")
        
        # Testar inicialização (sem carregar dados)
        try:
            generator = BathymetryGridGenerator("dummy.nc", spacing=0.25)
            print("✓ Classe pode ser inicializada")
            return True
        except FileNotFoundError:
            # Esperado, já que usamos arquivo dummy
            print("✓ Classe inicializa corretamente (validação de arquivo OK)")
            return True
            
    except ImportError as e:
        print(f"\n✗ Erro ao importar classe: {e}")
        return False
    except Exception as e:
        print(f"\n✗ Erro inesperado: {e}")
        return False


def test_small_grid():
    """
    Testa a geração de uma grade pequena (rápido).
    
    Returns:
        bool: True se conseguiu gerar uma grade de teste
    """
    print("\n" + "="*70)
    print(" TESTE 4: Geração de Grade de Teste")
    print("="*70)
    
    gebco_file = os.path.join(PROJECT_ROOT, "gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc")
    
    if not os.path.exists(gebco_file):
        print("\n⚠ Pulando teste (arquivo GEBCO não encontrado)")
        return True  # Não falhar o teste se o arquivo não existir
    
    try:
        from create_pom_bathymetry_grid import BathymetryGridGenerator
        import numpy as np
        
        print("\nGerando grade de teste pequena (1° x 1°)...")
        print("Isso deve ser rápido (~10-30 segundos)")
        
        # Criar gerador com grade bem pequena
        generator = BathymetryGridGenerator(gebco_file, spacing=0.5)
        
        # Carregar dados
        print("  Carregando dados GEBCO...")
        if not generator.load_gebco_data():
            print("✗ Falha ao carregar dados")
            return False
        
        # Grade pequena de teste: 1° x 1° no meio do oceano
        print("  Definindo grade de teste...")
        generator.define_grid_extent(-46.0, -45.0, -24.0, -23.0)
        
        # Interpolar
        print("  Interpolando...")
        if not generator.interpolate_bathymetry(method='linear'):
            print("✗ Falha na interpolação")
            return False
        
        # Exportar para arquivo temporário
        test_file = os.path.join(PROJECT_ROOT, "test_grid.asc")
        print(f"  Exportando para {test_file}...")
        if not generator.export_to_ascii(test_file):
            print("✗ Falha ao exportar")
            return False
        
        # Verificar arquivo
        if os.path.exists(test_file):
            lines = 0
            with open(test_file, 'r') as f:
                for line in f:
                    if not line.startswith('#'):
                        lines += 1
            
            print(f"\n✓ Grade de teste gerada com sucesso!")
            print(f"  Arquivo: {test_file}")
            print(f"  Linhas de dados: {lines}")
            print(f"  Tamanho: {os.path.getsize(test_file)} bytes")
            
            # Limpar
            generator.cleanup()
            
            # Perguntar se quer remover arquivo de teste
            print(f"\n  Arquivo de teste mantido: {test_file}")
            print("  (Você pode deletá-lo se quiser)")
            
            return True
        else:
            print("✗ Arquivo de teste não foi criado")
            return False
            
    except Exception as e:
        print(f"\n✗ Erro durante teste de geração: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """
    Executa todos os testes.
    """
    print("\n" + "="*70)
    print(" VALIDAÇÃO DO GERADOR DE GRADE BATIMÉTRICA POM")
    print("="*70)
    print("\nEste script verifica se tudo está pronto para gerar grades.")
    
    results = {}
    
    # Executar testes
    results['imports'] = test_imports()
    results['gebco_file'] = test_gebco_file()
    results['generator_class'] = test_generator_class()
    
    # Teste de geração apenas se os anteriores passaram
    if results['imports'] and results['gebco_file']:
        results['small_grid'] = test_small_grid()
    else:
        print("\n" + "="*70)
        print(" TESTE 4: Geração de Grade de Teste")
        print("="*70)
        print("\n⚠ Pulando teste (dependências ou arquivo GEBCO faltando)")
        results['small_grid'] = None
    
    # Resumo
    print("\n" + "="*70)
    print(" RESUMO DOS TESTES")
    print("="*70)
    
    test_names = {
        'imports': 'Dependências',
        'gebco_file': 'Arquivo GEBCO',
        'generator_class': 'Classe Geradora',
        'small_grid': 'Geração de Grade'
    }
    
    for key, name in test_names.items():
        result = results[key]
        if result is True:
            status = "✓ PASSOU"
        elif result is False:
            status = "✗ FALHOU"
        else:
            status = "⚠ PULADO"
        print(f"  {name:25s} {status}")
    
    # Conclusão
    all_passed = all(r in [True, None] for r in results.values())
    critical_passed = results['imports'] and results['generator_class']
    
    print("\n" + "="*70)
    if all_passed and results['small_grid']:
        print(" ✓ TODOS OS TESTES PASSARAM!")
        print("="*70)
        print("\nO sistema está pronto para gerar grades batimétricas.")
        print("\nPróximos passos:")
        print("  1. Edite create_pom_bathymetry_grid.py com suas configurações")
        print("  2. Execute: python create_pom_bathymetry_grid.py")
        print("  Ou use: python quick_generate_grid.py --help para opções rápidas")
        return 0
    elif critical_passed:
        print(" ⚠ SISTEMA PARCIALMENTE FUNCIONAL")
        print("="*70)
        print("\nOs componentes críticos estão funcionando, mas:")
        if not results['gebco_file']:
            print("  - Arquivo GEBCO não encontrado")
        if results['small_grid'] is False:
            print("  - Teste de geração falhou")
        print("\nVerifique os erros acima e tente novamente.")
        return 1
    else:
        print(" ✗ SISTEMA NÃO FUNCIONAL")
        print("="*70)
        print("\nCorreia os problemas listados acima antes de continuar.")
        if not results['imports']:
            print("\nInstale as dependências com:")
            print("  pip install -r requirements.txt")
        return 1


if __name__ == "__main__":
    sys.exit(main())
