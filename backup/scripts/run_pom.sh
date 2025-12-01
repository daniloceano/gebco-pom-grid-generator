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

# Resolver caminho do script Python (se o primeiro argumento for um script relativo)
SCRIPT_ARG="$1"
shift || true

# Se SCRIPT_ARG for um caminho absoluto existente, use-o
if [ -z "$SCRIPT_ARG" ]; then
    echo -e "${RED}✗ Erro: Nenhum script especificado${NC}"
    conda deactivate
    exit 1
fi

if [[ "$SCRIPT_ARG" = /* ]] && [ -f "$SCRIPT_ARG" ]; then
    SCRIPT_PATH="$SCRIPT_ARG"
else
    # Procurar o script em locais comuns: cwd do projeto (POM_ROOT), scripts/, tests/, src/
    # Determinar PROJECT_ROOT (pode ser exportado)
    if [ -n "$POM_ROOT" ]; then
        PR_ROOT="$POM_ROOT"
    else
        # assumir que o wrapper está em scripts/ dentro do projeto
        PR_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
    fi

    CANDIDATES=("$PR_ROOT/$SCRIPT_ARG" 
                "$PR_ROOT/scripts/$SCRIPT_ARG" 
                "$PR_ROOT/tests/$SCRIPT_ARG" 
                "$PR_ROOT/src/$SCRIPT_ARG" 
                "$PR_ROOT/$SCRIPT_ARG.py"
                )

    SCRIPT_PATH=""
    for c in "${CANDIDATES[@]}"; do
        if [ -f "$c" ]; then
            SCRIPT_PATH="$c"
            break
        fi
    done
fi

if [ -z "$SCRIPT_PATH" ]; then
    echo -e "${RED}✗ Erro: script '$SCRIPT_ARG' não encontrado em locais esperados.${NC}"
    echo "  Procurado em: $PR_ROOT, $PR_ROOT/scripts, $PR_ROOT/tests, $PR_ROOT/src"
    conda deactivate
    exit 2
fi

echo -e "${GREEN}✓ Executando: python $SCRIPT_PATH $@${NC}"
echo ""
# Garantir que o diretório src/ esteja no PYTHONPATH para imports locais
export PYTHONPATH="$PR_ROOT:$PR_ROOT/src:${PYTHONPATH:-}"

python "$SCRIPT_PATH" "$@"

# Capturar código de saída
exit_code=$?

# Desativar ambiente
conda deactivate

# Retornar com o mesmo código de saída do script Python
exit $exit_code
