#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Script de Testes - RecOM
===================================

Executa todos os testes disponíveis para validar a instalação
e funcionalidades do projeto.

Uso:
    python run_tests.py
    python run_tests.py --quick  # Apenas testes rápidos
"""

import sys
import os
import argparse

# Adicionar diretório raiz ao path
PROJECT_ROOT = os.path.abspath(os.path.dirname(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def run_test(test_file, description):
    """
    Executa um arquivo de teste.
    
    Args:
        test_file: Nome do arquivo de teste
        description: Descrição do teste
    
    Returns:
        bool: True se passou, False se falhou
    """
    print(f"\n{'='*70}")
    print(f" {description}")
    print(f"{'='*70}\n")
    
    test_path = os.path.join(PROJECT_ROOT, 'tests', test_file)
    
    if not os.path.exists(test_path):
        print(f"⚠️  Teste não encontrado: {test_file}")
        return None
    
    try:
        # Executar teste como subprocesso
        import subprocess
        result = subprocess.run(
            [sys.executable, test_path],
            cwd=PROJECT_ROOT,
            capture_output=False,
            text=True
        )
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Erro ao executar teste: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(description='Executar testes do RecOM')
    parser.add_argument('--quick', action='store_true', 
                       help='Executar apenas testes rápidos (sem geração de grade)')
    parser.add_argument('--test', type=str, 
                       help='Executar apenas um teste específico')
    args = parser.parse_args()
    
    print("\n" + "="*70)
    print(" 🌊 RecOM - Suite de Testes")
    print("="*70)
    
    # Definir testes disponíveis
    tests = {
        'basic': {
            'file': 'test_bathymetry_generator.py',
            'description': 'Testes Básicos (Dependências e Importações)',
            'quick': True
        },
        'spacing': {
            'file': 'test_different_spacing.py',
            'description': 'Teste de Espaçamentos Diferentes (dx ≠ dy)',
            'quick': False  # Carrega GEBCO
        },
        'editor': {
            'file': 'test_editor_load.py',
            'description': 'Teste do Editor Interativo (Carregamento)',
            'quick': True
        },
        'interpolation': {
            'file': 'test_interpolation.py',
            'description': 'Teste de Interpolação IDW',
            'quick': True
        }
    }
    
    # Filtrar testes
    if args.test:
        if args.test not in tests:
            print(f"\n❌ Teste '{args.test}' não encontrado.")
            print(f"\nTestes disponíveis: {', '.join(tests.keys())}")
            return 1
        tests_to_run = {args.test: tests[args.test]}
    elif args.quick:
        tests_to_run = {k: v for k, v in tests.items() if v['quick']}
    else:
        tests_to_run = tests
    
    # Executar testes
    results = {}
    for test_name, test_info in tests_to_run.items():
        result = run_test(test_info['file'], test_info['description'])
        results[test_name] = result
    
    # Resumo
    print("\n" + "="*70)
    print(" RESUMO DOS TESTES")
    print("="*70)
    
    passed = sum(1 for r in results.values() if r is True)
    failed = sum(1 for r in results.values() if r is False)
    skipped = sum(1 for r in results.values() if r is None)
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASSOU" if result is True else "❌ FALHOU" if result is False else "⚠️  PULADO"
        print(f"  {test_name:15s} {status}")
    
    print(f"\nTotal: {total} | Passou: {passed} | Falhou: {failed} | Pulado: {skipped}")
    
    if failed > 0:
        print("\n❌ Alguns testes falharam. Verifique a saída acima.")
        return 1
    elif passed == total:
        print("\n✅ Todos os testes passaram!")
        print("\n📚 Próximos passos:")
        print("  1. Leia: README.md")
        print("  2. Use: ./ocean-tools.sh gebco")
        print("  3. Doc: tools/gebco_interpolation/README.md")
        return 0
    else:
        print(f"\n⚠️  {passed}/{total} testes passaram. Alguns foram pulados.")
        return 0


if __name__ == '__main__':
    sys.exit(main())
