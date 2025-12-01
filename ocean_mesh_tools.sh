#!/bin/bash
# ==============================================================================
# RecOM - Rectangular Ocean Mesh Tools - Script Principal
# ==============================================================================
#
# Script de comandos para o pacote RecOM
#
# Uso:
#   ./ocean_mesh_tools.sh <comando> [argumentos]
#
# Comandos disponíveis:
#   env        - Configurar ambiente conda
#   gebco      - Ir para ferramenta GEBCO
#   mask       - Extrair máscara de reanálise
#   apply      - Aplicar máscara em grade
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
    echo "  🌊 RecOM - Rectangular Ocean Mesh Tools"
    echo "  Ferramentas para geração de grades oceânicas"
    echo "======================================================================"
    echo -e "${NC}"
}

# Detectar diretório raiz do projeto
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

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
    
    echo "Criando ambiente 'ocean_mesh_tools' a partir de environment.yml..."
    cd "$PROJECT_ROOT"
    conda env create -f environment.yml
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Ambiente criado com sucesso!${NC}"
        echo ""
        echo "Para ativar o ambiente, execute:"
        echo -e "  ${YELLOW}conda activate ocean_mesh_tools${NC}"
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

# Comando: extrair máscara de reanálise
cmd_mask() {
    show_banner
    echo -e "${GREEN}Ferramenta: Extração de Máscara de Reanálise${NC}"
    echo ""
    
    if [ -z "$1" ]; then
        echo -e "${YELLOW}Uso: ./ocean_mesh_tools.sh mask <arquivo_netcdf> [opções]${NC}"
        echo ""
        echo "Opções:"
        echo "  --lon-range MIN MAX    - Intervalo de longitude"
        echo "  --lat-range MIN MAX    - Intervalo de latitude"
        echo "  --target-res DX DY     - Resolução alvo em graus"
        echo "  --variable VAR         - Nome da variável (padrão: auto-detecta)"
        echo "  --threshold THR        - Limiar para agregação (padrão: 0.5)"
        echo ""
        echo "Exemplos:"
        echo "  # Extrair máscara do BRAN2020"
        echo "  ./ocean_mesh_tools.sh mask /path/to/bran2020.nc \\"
        echo "    --lon-range -60 -30 --lat-range -35 -5 --target-res 0.25 0.25"
        echo ""
        echo "  # Com limiar customizado"
        echo "  ./ocean_mesh_tools.sh mask /path/to/glorys.nc \\"
        echo "    --lon-range 100 150 --lat-range -20 10 --target-res 0.5 0.5 --threshold 0.7"
        echo ""
        echo "Documentação: tools/reanalysis_mask/README.md"
        echo ""
        echo "Visualizar máscara:"
        echo "  python tools/reanalysis_mask/scripts/visualize_mask.py output/mask_ocean_*.asc"
        exit 0
    fi
    
    NETCDF_FILE="$1"
    shift
    
    if [ ! -f "$NETCDF_FILE" ]; then
        echo -e "${RED}Erro: Arquivo não encontrado: $NETCDF_FILE${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Extraindo máscara de reanálise...${NC}"
    echo "Arquivo: $NETCDF_FILE"
    echo ""
    
    # Verificar se ambiente está ativo
    if [[ "$CONDA_DEFAULT_ENV" != "ocean_mesh_tools" ]]; then
        echo -e "${YELLOW}Ativando ambiente conda 'ocean_mesh_tools'...${NC}"
        eval "$(conda shell.bash hook)"
        conda activate ocean_mesh_tools
    fi
    
    cd "$SCRIPT_DIR"
    python tools/reanalysis_mask/scripts/extract_mask.py "$NETCDF_FILE" "$@"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Máscara extraída com sucesso!${NC}"
        echo ""
        echo "Arquivo salvo em: output/mask_ocean_*.asc"
        echo ""
        echo "Para aplicar máscara a uma grade:"
        echo "  python tools/reanalysis_mask/scripts/apply_mask.py \\"
        echo "    output/rectangular_grid_*.asc output/mask_ocean_*.asc"
    fi
}

# Comando: aplicar máscara
cmd_apply() {
    show_banner
    echo -e "${GREEN}Ferramenta: Aplicar Máscara de Reanálise${NC}"
    echo ""
    
    if [ -z "$1" ]; then
        echo -e "${YELLOW}Uso: ./ocean_mesh_tools.sh apply <grid_file> <mask_file> [--output <output>]${NC}"
        echo ""
        echo "Argumentos:"
        echo "  grid_file  - Arquivo de grade (.asc)"
        echo "  mask_file  - Arquivo de máscara (.asc)"
        echo ""
        echo "Opções:"
        echo "  --output, -o  - Arquivo de saída (padrão: <grid>_<mask>.asc)"
        echo ""
        echo "Exemplos:"
        echo "  # Aplicar máscara BRAN2020 em grade GEBCO"
        echo "  ./ocean_mesh_tools.sh apply \\"
        echo "    output/rectangular_grid_lon-60_-30_lat-35_-5_dx0.25_dy0.25_gebco.asc \\"
        echo "    output/mask_ocean_bran2020_lon-60_-30_lat-35_-5_dx0.25_dy0.25.asc"
        echo ""
        echo "  # Com nome de saída customizado"
        echo "  ./ocean_mesh_tools.sh apply grid.asc mask.asc --output my_grid.asc"
        exit 0
    fi
    
    GRID_FILE="$1"
    MASK_FILE="$2"
    shift 2
    
    if [ ! -f "$GRID_FILE" ]; then
        echo -e "${RED}Erro: Grade não encontrada: $GRID_FILE${NC}"
        exit 1
    fi
    
    if [ ! -f "$MASK_FILE" ]; then
        echo -e "${RED}Erro: Máscara não encontrada: $MASK_FILE${NC}"
        exit 1
    fi
    
    echo -e "${GREEN}Aplicando máscara...${NC}"
    echo "Grade: $GRID_FILE"
    echo "Máscara: $MASK_FILE"
    echo ""
    
    # Verificar se ambiente está ativo
    if [[ "$CONDA_DEFAULT_ENV" != "ocean_mesh_tools" ]]; then
        echo -e "${YELLOW}Ativando ambiente conda 'ocean_mesh_tools'...${NC}"
        eval "$(conda shell.bash hook)"
        conda activate ocean_mesh_tools
    fi
    
    cd "$SCRIPT_DIR"
    python tools/reanalysis_mask/scripts/apply_mask.py "$GRID_FILE" "$MASK_FILE" "$@"
    
    if [ $? -eq 0 ]; then
        echo ""
        echo -e "${GREEN}✓ Máscara aplicada com sucesso!${NC}"
    fi
}

# Comando: editar grade
cmd_edit() {
    show_banner
    
    if [ -z "$1" ]; then
        echo -e "${YELLOW}Uso: ./ocean_mesh_tools.sh edit <arquivo.asc>${NC}"
        echo ""
        echo "Exemplo:"
        echo "  ./ocean_mesh_tools.sh edit output/pom_bathymetry_grid.asc"
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
    if [[ "$CONDA_DEFAULT_ENV" != "ocean_mesh_tools" ]]; then
        echo -e "${YELLOW}Ativando ambiente conda 'ocean_mesh_tools'...${NC}"
        eval "$(conda shell.bash hook)"
        conda activate ocean_mesh_tools
    fi
    
    cd "$SCRIPT_DIR/tools/grid_editor/scripts"
    python edit_grid.py "$SCRIPT_DIR/$GRID_FILE"
}

# Comando: executar testes
cmd_test() {
    show_banner
    echo -e "${GREEN}Executando testes...${NC}"
    echo ""
    
    # Verificar se ambiente está ativo
    if [[ "$CONDA_DEFAULT_ENV" != "ocean_mesh_tools" ]]; then
        echo -e "${YELLOW}Ativando ambiente conda 'ocean_mesh_tools'...${NC}"
        eval "$(conda shell.bash hook)"
        conda activate ocean_mesh_tools
    fi
    
    cd "$SCRIPT_DIR"
    python run_tests.py "$@"
}

# Comando: ajuda
cmd_help() {
    show_banner
    echo "Uso: ./ocean_mesh_tools.sh <comando> [argumentos]"
    echo ""
    echo "Comandos disponíveis:"
    echo ""
    echo -e "  ${GREEN}env${NC}                    - Configurar ambiente conda"
    echo -e "  ${GREEN}test${NC} [--quick]        - Executar testes de validação"
    echo -e "  ${GREEN}gebco${NC}                  - Acessar ferramenta de interpolação GEBCO"
    echo -e "  ${GREEN}mask${NC} <netcdf> [opts]  - Extrair máscara de reanálise"
    echo -e "  ${GREEN}apply${NC} <grid> <mask>   - Aplicar máscara em grade"
    echo -e "  ${GREEN}edit${NC} <arquivo>        - Editar grade interativamente"
    echo -e "  ${GREEN}help${NC}                   - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo ""
    echo "  # Configurar ambiente (primeira vez)"
    echo "  ./ocean_mesh_tools.sh env"
    echo ""
    echo "  # Executar testes"
    echo "  ./ocean_mesh_tools.sh test"
    echo "  ./ocean_mesh_tools.sh test --quick  # Apenas testes rápidos"
    echo ""
    echo "  # Usar ferramenta GEBCO"
    echo "  ./ocean_mesh_tools.sh gebco"
    echo ""
    echo "  # Extrair máscara de reanálise"
    echo "  ./ocean_mesh_tools.sh mask /path/to/bran2020.nc --lon-range -60 -30 --lat-range -35 -5 --target-res 0.25 0.25"
    echo ""
    echo "  # Aplicar máscara em grade"
    echo "  ./ocean_mesh_tools.sh apply output/rectangular_grid_*.asc output/mask_ocean_*.asc"
    echo ""
    echo "  # Editar grade"
    echo "  ./ocean_mesh_tools.sh edit output/pom_bathymetry_grid.asc"
    echo ""
    echo "Estrutura do projeto:"
    echo ""
    echo "  tools/                   - Ferramentas disponíveis"
    echo "    ├─ gebco_interpolation/ - Interpolação GEBCO"
    echo "    ├─ grid_editor/         - Editor interativo"
    echo "    └─ reanalysis_mask/     - Máscaras de reanálises"
    echo "  docs/                    - Documentação"
    echo "  output/                  - Arquivos gerados"
    echo ""
    echo "Documentação:"
    echo "  • README.md                              - Visão geral"
    echo "  • docs/INSTALL.md                        - Instalação"
    echo "  • docs/QUICK_REFERENCE.md                - Referência rápida"
    echo "  • tools/gebco_interpolation/README.md    - Doc GEBCO"
    echo "  • tools/grid_editor/README.md            - Doc Grid Editor"
    echo "  • tools/reanalysis_mask/README.md        - Doc Máscaras"
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
    test)
        shift
        cmd_test "$@"
        ;;
    gebco)
        cmd_gebco
        ;;
    mask)
        shift
        cmd_mask "$@"
        ;;
    apply)
        shift
        cmd_apply "$@"
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
