#!/bin/bash
# ==============================================================================
# Script Wrapper para Executar Scripts Python no Ambiente POM
# ==============================================================================
#
# Este script automaticamente ativa o ambiente conda "pom" e executa
# qualquer script Python passado como argumento.
#
# Uso:
#   ./run_pom.sh script.py [argumentos...]
#
# Exemplos:
#   ./run_pom.sh create_pom_bathymetry_grid.py
#   ./run_pom.sh quick_generate_grid.py --help
#   ./run_pom.sh test_bathymetry_generator.py
#
# ==============================================================================

# Cores para output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Verificar se foi passado um argumento
if [ $# -eq 0 ]; then
    echo -e "${RED}✗ Erro: Nenhum script especificado${NC}"
    echo ""
    echo "Uso: $0 script.py [argumentos...]"
    echo ""
    echo "Exemplos:"
    echo "  $0 create_pom_bathymetry_grid.py"
    echo "  $0 quick_generate_grid.py --help"
    echo "  $0 test_bathymetry_generator.py"
    exit 1
fi

# Verificar se conda está instalado
if ! command -v conda &> /dev/null; then
    echo -e "${RED}✗ Erro: conda não encontrado!${NC}"
    echo "Por favor, instale Anaconda ou Miniconda."
    exit 1
fi

# Verificar se o ambiente "pom" existe
if ! conda env list | grep -q "^pom "; then
    echo -e "${YELLOW}⚠️  O ambiente conda 'pom' não existe.${NC}"
    echo ""
    echo "Execute o script de configuração primeiro:"
    echo "  bash setup_environment.sh"
    exit 1
fi

# Ativar ambiente
echo -e "${GREEN}✓ Ativando ambiente conda 'pom'...${NC}"
eval "$(conda shell.bash hook)"
conda activate pom

if [ $? -ne 0 ]; then
    echo -e "${RED}✗ Erro ao ativar ambiente 'pom'${NC}"
    exit 1
fi

# Executar script Python com todos os argumentos
echo -e "${GREEN}✓ Executando: python $@${NC}"
echo ""
python "$@"

# Capturar código de saída
exit_code=$?

# Desativar ambiente
conda deactivate

# Retornar com o mesmo código de saída do script Python
exit $exit_code
