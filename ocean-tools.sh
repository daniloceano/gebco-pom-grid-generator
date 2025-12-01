#!/bin/bash
# ==============================================================================
# Ocean Grid Tools - Script Principal
# ==============================================================================
#
# Script de comandos para o pacote Ocean Grid Tools
#
# Uso:
#   ./ocean-tools.sh <comando> [argumentos]
#
# Comandos disponíveis:
#   env        - Configurar ambiente conda
#   gebco      - Ir para ferramenta GEBCO
#   edit       - Editar grade interativamente
#   help       - Mostrar esta ajuda
#
# ==============================================================================

# Cores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Banner
show_banner() {
    echo -e "${BLUE}"
    echo "======================================================================"
    echo "  🌊 OCEAN GRID TOOLS"
    echo "  Ferramentas para geração de grades oceânicas"
    echo "======================================================================"
    echo -e "${NC}"
}

# Detectar diretório raiz do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Comando: configurar ambiente
cmd_env() {
    show_banner
    echo -e "${GREEN}Configurando ambiente conda...${NC}"
    echo ""
    
    if ! command -v conda &> /dev/null; then
        echo -e "${RED}Erro: conda não encontrado${NC}"
        echo "Instale Anaconda ou Miniconda primeiro:"
        echo "  https://docs.conda.io/en/latest/miniconda.html"
        exit 1
    fi
    
    echo "Criando ambiente 'pom' a partir de environment.yml..."
    cd "$PROJECT_ROOT"
    conda env create -f environment.yml
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Ambiente criado com sucesso!${NC}"
        echo ""
        echo "Para ativar o ambiente, execute:"
        echo -e "  ${YELLOW}conda activate pom${NC}"
    else
        echo -e "${RED}✗ Erro ao criar ambiente${NC}"
        echo "Veja docs/INSTALL.md para troubleshooting"
        exit 1
    fi
}

# Comando: acessar ferramenta GEBCO
cmd_gebco() {
    show_banner
    echo -e "${GREEN}Ferramenta: Interpolação GEBCO${NC}"
    echo ""
    echo "Localização: tools/gebco_interpolation/"
    echo ""
    echo "Scripts disponíveis:"
    echo "  • generate_grid.py         - Gerador principal"
    echo "  • edit_grid_interactive.py - Editor interativo"
    echo "  • quick_generate.py        - Interface CLI"
    echo ""
    echo "Para usar:"
    echo -e "  ${YELLOW}cd tools/gebco_interpolation/scripts${NC}"
    echo -e "  ${YELLOW}python generate_grid.py${NC}"
    echo ""
    echo "Documentação: tools/gebco_interpolation/README.md"
    echo ""
    read -p "Abrir diretório? (s/N): " resposta
    if [[ $resposta =~ ^[Ss]$ ]]; then
        cd "$PROJECT_ROOT/tools/gebco_interpolation/scripts"
        echo ""
        echo -e "${GREEN}Você está em: $(pwd)${NC}"
        echo ""
        exec $SHELL
    fi
}

# Comando: editar grade
cmd_edit() {
    show_banner
    
    if [ -z "$1" ]; then
        echo -e "${YELLOW}Uso: ./ocean-tools.sh edit <arquivo.asc>${NC}"
        echo ""
        echo "Exemplo:"
        echo "  ./ocean-tools.sh edit output/pom_bathymetry_grid.asc"
        exit 1
    fi
    
    GRID_FILE="$1"
    
    if [ ! -f "$GRID_FILE" ]; then
        echo -e "${RED}Erro: Arquivo não encontrado: $GRID_FILE${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Abrindo editor interativo...${NC}"
    echo "Arquivo: $GRID_FILE"
    echo ""
    
    # Verificar se ambiente está ativo
    if [[ "$CONDA_DEFAULT_ENV" != "pom" ]]; then
        echo -e "${YELLOW}Ativando ambiente conda 'pom'...${NC}"
        eval "$(conda shell.bash hook)"
        conda activate pom
    fi
    
    cd "$PROJECT_ROOT/tools/gebco_interpolation/scripts"
    python edit_grid_interactive.py "$PROJECT_ROOT/$GRID_FILE"
}

# Comando: ajuda
cmd_help() {
    show_banner
    echo "Uso: ./ocean-tools.sh <comando> [argumentos]"
    echo ""
    echo "Comandos disponíveis:"
    echo ""
    echo -e "  ${GREEN}env${NC}                    - Configurar ambiente conda"
    echo -e "  ${GREEN}gebco${NC}                  - Acessar ferramenta de interpolação GEBCO"
    echo -e "  ${GREEN}edit${NC} <arquivo>        - Editar grade interativamente"
    echo -e "  ${GREEN}help${NC}                   - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo ""
    echo "  # Configurar ambiente (primeira vez)"
    echo "  ./ocean-tools.sh env"
    echo ""
    echo "  # Usar ferramenta GEBCO"
    echo "  ./ocean-tools.sh gebco"
    echo ""
    echo "  # Editar grade"
    echo "  ./ocean-tools.sh edit output/pom_bathymetry_grid.asc"
    echo ""
    echo "Estrutura do projeto:"
    echo ""
    echo "  tools/                   - Ferramentas disponíveis"
    echo "    └─ gebco_interpolation/ - Interpolação GEBCO"
    echo "  docs/                    - Documentação"
    echo "  output/                  - Arquivos gerados"
    echo ""
    echo "Documentação:"
    echo "  • README.md                              - Visão geral"
    echo "  • docs/INSTALL.md                        - Instalação"
    echo "  • docs/QUICK_REFERENCE.md                - Referência rápida"
    echo "  • tools/gebco_interpolation/README.md    - Doc GEBCO"
    echo ""
}

# Main
if [ $# -eq 0 ]; then
    cmd_help
    exit 0
fi

case "$1" in
    env)
        cmd_env
        ;;
    gebco)
        cmd_gebco
        ;;
    edit)
        shift
        cmd_edit "$@"
        ;;
    help|--help|-h)
        cmd_help
        ;;
    *)
        echo -e "${RED}Erro: Comando desconhecido: $1${NC}"
        echo ""
        cmd_help
        exit 1
        ;;
esac
