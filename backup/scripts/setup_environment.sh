#!/bin/bash
# ==============================================================================
# Script de Configuração do Ambiente Conda para Projeto POM
# ==============================================================================
#
# Este script cria e configura um ambiente conda chamado "pom" com todas as
# dependências necessárias para o gerador de grade batimétrica.
#
# Uso:
#   bash setup_environment.sh
#
# Ou torne executável e execute:
#   chmod +x setup_environment.sh
#   ./setup_environment.sh
#
# ==============================================================================

echo "======================================================================"
echo " CONFIGURAÇÃO DO AMBIENTE CONDA - PROJETO POM"
echo "======================================================================"
echo ""

# Verificar se conda está instalado
if ! command -v conda &> /dev/null; then
    echo "✗ ERRO: conda não encontrado!"
    echo "  Por favor, instale Anaconda ou Miniconda primeiro:"
    echo "  https://docs.conda.io/en/latest/miniconda.html"
    exit 1
fi

echo "✓ Conda encontrado: $(conda --version)"
echo ""

# Verificar se o ambiente "pom" já existe
if conda env list | grep -q "^pom "; then
    echo "⚠️  O ambiente 'pom' já existe."
    read -p "Deseja removê-lo e criar novamente? (s/N): " resposta
    if [[ $resposta =~ ^[Ss]$ ]]; then
        echo "  Removendo ambiente existente..."
        conda env remove -n pom -y
        echo "  ✓ Ambiente removido"
    else
        echo "  Mantendo ambiente existente."
        echo "  Para atualizar pacotes, use: conda activate pom && pip install -r requirements.txt"
        exit 0
    fi
fi

echo "Criando novo ambiente conda 'pom'..."
echo ""

# Criar ambiente com Python 3.10 (versão estável e compatível)
echo "Passo 1/3: Criando ambiente base com Python 3.10..."
conda create -n pom python=3.10 -y

if [ $? -ne 0 ]; then
    echo "✗ Erro ao criar ambiente conda"
    exit 1
fi

echo ""
echo "✓ Ambiente base criado com sucesso"
echo ""

# Ativar ambiente
echo "Passo 2/3: Ativando ambiente..."
eval "$(conda shell.bash hook)"
conda activate pom

if [ $? -ne 0 ]; then
    echo "✗ Erro ao ativar ambiente"
    exit 1
fi

echo "✓ Ambiente ativado"
echo ""

# Instalar pacotes via conda (mais rápido e confiável para pacotes científicos)
echo "Passo 3/3: Instalando dependências científicas..."
echo "  Instalando numpy, scipy, xarray, netCDF4, matplotlib..."
conda install -c conda-forge numpy scipy xarray netcdf4 matplotlib -y

if [ $? -ne 0 ]; then
    echo "⚠️  Erro ao instalar via conda, tentando via pip..."
    pip install -r requirements.txt
fi

echo ""
echo "✓ Dependências instaladas"
echo ""

# Verificar instalação
echo "======================================================================"
echo " VERIFICANDO INSTALAÇÃO"
echo "======================================================================"
echo ""

python -c "
import sys
try:
    import numpy as np
    import scipy
    import xarray as xr
    import netCDF4
    import matplotlib
    print('✓ numpy version:', np.__version__)
    print('✓ scipy version:', scipy.__version__)
    print('✓ xarray version:', xr.__version__)
    print('✓ netCDF4 version:', netCDF4.__version__)
    print('✓ matplotlib version:', matplotlib.__version__)
    print('')
    print('✓ Todas as dependências instaladas com sucesso!')
    sys.exit(0)
except ImportError as e:
    print('✗ Erro ao importar módulo:', e)
    sys.exit(1)
"

if [ $? -eq 0 ]; then
    echo ""
    echo "======================================================================"
    echo " ✓ AMBIENTE CONFIGURADO COM SUCESSO!"
    echo "======================================================================"
    echo ""
    echo "Próximos passos:"
    echo ""
    echo "1. Para ativar o ambiente, use:"
    echo "   conda activate pom"
    echo ""
    echo "2. Para executar os scripts:"
    echo "   python create_pom_bathymetry_grid.py"
    echo "   ou"
    echo "   python quick_generate_grid.py --help"
    echo ""
    echo "3. Para testar a instalação:"
    echo "   python test_bathymetry_generator.py"
    echo ""
    echo "4. Para desativar o ambiente quando terminar:"
    echo "   conda deactivate"
    echo ""
    echo "======================================================================"
else
    echo ""
    echo "======================================================================"
    echo " ✗ PROBLEMAS NA INSTALAÇÃO"
    echo "======================================================================"
    echo ""
    echo "Algumas dependências não foram instaladas corretamente."
    echo "Tente instalar manualmente:"
    echo "  conda activate pom"
    echo "  pip install -r requirements.txt"
    echo ""
    exit 1
fi
