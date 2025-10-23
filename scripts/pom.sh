#!/bin/bash
# ==============================================================================
# Script de Comandos Comuns - Projeto POM
# ==============================================================================
#
# Este script fornece atalhos para comandos frequentemente usados no projeto
# de geração de grades batimétricas POM.
#
# Uso:
#   ./pom.sh <comando> [argumentos]
#
# Comandos disponíveis:
#   setup      - Instalar/configurar ambiente conda
#   test       - Executar testes de validação
#   run        - Executar script principal
#   quick      - Executar gerador rápido
#   clean      - Limpar arquivos temporários
#   help       - Mostrar esta ajuda
#
# Configuração (opcional):
#   Você pode definir a variável de ambiente POM_ROOT para especificar o
#   diretório raiz do projeto. Se não definida, o script tentará detectar
#   automaticamente assumindo que está em <projeto>/scripts/pom.sh.
#
#   Exemplo:
#     export POM_ROOT=/path/to/gebco-pom-grid-generator
#     ./pom.sh test
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
    echo "  🌊 GERADOR DE GRADE BATIMÉTRICA POM"
    echo "======================================================================"
    echo -e "${NC}"
}

# === Inicialização de caminhos =================================================
# Determina o diretório deste script e o diretório raiz do projeto. Isso torna
# as chamadas a outros scripts robustas mesmo quando o usuário executa este
# script a partir de diferentes diretórios.
#
# Você pode sobrescrever o diretório do projeto exportando a variável
# de ambiente POM_ROOT antes de chamar este script.
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Se POM_ROOT estiver definido, use-o; senão, assuma que o projeto root é o pai
# do diretório de scripts (../)
if [ -n "$POM_ROOT" ]; then
    PROJECT_ROOT="$POM_ROOT"
else
    PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

# Caminhos absolutos para scripts usados pelo pom.sh
# Procurar por run_pom.sh e setup_environment.sh em locais comuns e usar o primeiro
# encontrado (PROJECT_ROOT, SCRIPT_DIR). Isso permite executar o script tanto
# a partir da raiz do projeto quanto da pasta scripts/.
if [ -f "$PROJECT_ROOT/run_pom.sh" ]; then
    RUN_WRAPPER="$PROJECT_ROOT/run_pom.sh"
elif [ -f "$SCRIPT_DIR/run_pom.sh" ]; then
    RUN_WRAPPER="$SCRIPT_DIR/run_pom.sh"
else
    RUN_WRAPPER=""
fi

if [ -f "$PROJECT_ROOT/setup_environment.sh" ]; then
    SETUP_SCRIPT="$PROJECT_ROOT/setup_environment.sh"
elif [ -f "$SCRIPT_DIR/setup_environment.sh" ]; then
    SETUP_SCRIPT="$SCRIPT_DIR/setup_environment.sh"
else
    SETUP_SCRIPT=""
fi

# Avisos se não encontrados
if [ -z "$RUN_WRAPPER" ]; then
    echo "[AVISO] run_pom.sh não encontrado em: $PROJECT_ROOT ou $SCRIPT_DIR"
fi
if [ -z "$SETUP_SCRIPT" ]; then
    echo "[AVISO] setup_environment.sh não encontrado em: $PROJECT_ROOT ou $SCRIPT_DIR"
fi


# Ajuda
show_help() {
    show_banner
    echo "Uso: ./pom.sh <comando> [argumentos]"
    echo ""
    echo "Comandos disponíveis:"
    echo ""
    echo -e "  ${GREEN}setup${NC}        - Instalar/configurar ambiente conda"
    echo -e "  ${GREEN}test${NC}         - Executar testes de validação"
    echo -e "  ${GREEN}run${NC}          - Executar script principal de geração"
    echo -e "  ${GREEN}quick${NC}        - Executar gerador rápido com argumentos CLI"
    echo -e "  ${GREEN}env${NC}          - Ativar ambiente conda interativamente"
    echo -e "  ${GREEN}status${NC}       - Verificar status do ambiente"
    echo -e "  ${GREEN}clean${NC}        - Limpar arquivos temporários e de teste"
    echo -e "  ${GREEN}help${NC}         - Mostrar esta ajuda"
    echo ""
    echo "Exemplos:"
    echo ""
    echo "  # Configuração inicial"
    echo "  ./pom.sh setup"
    echo ""
    echo "  # Testar instalação"
    echo "  ./pom.sh test"
    echo ""
    echo "  # Gerar grade com script principal"
    echo "  ./pom.sh run"
    echo ""
    echo "  # Gerar grade rápido"
    echo "  ./pom.sh quick --region brasil_sul"
    echo "  ./pom.sh quick --lon-min -60 --lon-max -30 --lat-min -35 --lat-max -5"
    echo ""
    echo "  # Ver status"
    echo "  ./pom.sh status"
    echo ""
    echo "  # Limpar arquivos temporários"
    echo "  ./pom.sh clean"
    echo ""
}

# Setup
cmd_setup() {
    show_banner
    echo -e "${GREEN}Configurando ambiente conda...${NC}"
    echo ""
    "$SETUP_SCRIPT"
}

# Test
cmd_test() {
    show_banner
    echo -e "${GREEN}Executando testes de validação...${NC}"
    echo ""
    "$RUN_WRAPPER" test_bathymetry_generator.py
}

# Run
cmd_run() {
    show_banner
    echo -e "${GREEN}Executando gerador principal...${NC}"
    echo ""
    echo -e "${YELLOW}Nota: Certifique-se de ter editado as configurações em create_pom_bathymetry_grid.py${NC}"
    echo ""
    read -p "Continuar? (s/N): " resposta
    if [[ $resposta =~ ^[Ss]$ ]]; then
        "$RUN_WRAPPER" create_pom_bathymetry_grid.py
    else
        echo "Cancelado."
    fi
}

# Quick
cmd_quick() {
    show_banner
    echo -e "${GREEN}Executando gerador rápido...${NC}"
    echo ""
    
    if [ $# -eq 0 ]; then
        echo -e "${YELLOW}Nenhum argumento fornecido. Mostrando ajuda:${NC}"
        echo ""
        "$RUN_WRAPPER" quick_generate_grid.py --help
    else
        "$RUN_WRAPPER" quick_generate_grid.py "$@"
    fi
}

# Env (ativar ambiente interativamente)
cmd_env() {
    show_banner
    echo -e "${GREEN}Ativando ambiente conda 'pom'...${NC}"
    echo ""
    echo -e "${YELLOW}Execute este comando:${NC}"
    echo ""
    echo "  conda activate pom"
    echo ""
    echo -e "${YELLOW}Para desativar depois:${NC}"
    echo ""
    echo "  conda deactivate"
    echo ""
}

# Status
cmd_status() {
    show_banner
    echo -e "${GREEN}Verificando status do sistema...${NC}"
    echo ""
    
    # Verificar conda
    echo -n "Conda: "
    if command -v conda &> /dev/null; then
        echo -e "${GREEN}✓ Instalado ($(conda --version))${NC}"
    else
        echo -e "${RED}✗ Não encontrado${NC}"
    fi
    
    # Verificar ambiente pom
    echo -n "Ambiente 'pom': "
    if conda env list | grep -q "^pom "; then
        echo -e "${GREEN}✓ Existe${NC}"
    else
        echo -e "${RED}✗ Não existe${NC}"
        echo "  Execute: ./pom.sh setup"
    fi
    
    # Verificar arquivo GEBCO
    echo -n "Arquivo GEBCO: "
    GEBCO_PATH="$PROJECT_ROOT/gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"
    if [ -f "$GEBCO_PATH" ]; then
        size=$(du -h "$GEBCO_PATH" | cut -f1)
        echo -e "${GREEN}✓ Presente (${size})${NC}"
    else
        echo -e "${RED}✗ Não encontrado${NC}"
    fi
    
    # Verificar scripts
    echo -n "Scripts executáveis: "
    if [ -x "$SETUP_SCRIPT" ] && [ -x "$RUN_WRAPPER" ]; then
        echo -e "${GREEN}✓ Prontos${NC}"
    else
        echo -e "${YELLOW}⚠ Executando chmod...${NC}"
        chmod +x "$SETUP_SCRIPT" "$RUN_WRAPPER" "$SCRIPT_DIR/pom.sh"
        echo -e "${GREEN}✓ Corrigido${NC}"
    fi
    
    echo ""
    echo -e "${BLUE}Arquivos de saída existentes:${NC}"
    OUTPUT_DIR="$PROJECT_ROOT/output"
    if [ -d "$OUTPUT_DIR" ] && (ls "$OUTPUT_DIR"/*.asc "$OUTPUT_DIR"/*.png 2>/dev/null | grep -v test_grid); then
        echo ""
    else
        echo "  (nenhum)"
    fi
    
    echo ""
}

# Clean
cmd_clean() {
    show_banner
    echo -e "${GREEN}Limpando arquivos temporários...${NC}"
    echo ""
    
    # Listar arquivos a serem removidos
    files_to_remove=()
    
    if [ -f "test_grid.asc" ]; then
        files_to_remove+=("test_grid.asc")
    fi
    
    # Adicionar arquivos Python temporários
    temp_files=$(find . -name "*.pyc" -o -name "__pycache__" -o -name ".DS_Store" 2>/dev/null)
    if [ ! -z "$temp_files" ]; then
        files_to_remove+=($temp_files)
    fi
    
    if [ ${#files_to_remove[@]} -eq 0 ]; then
        echo "Nenhum arquivo temporário encontrado."
    else
        echo "Arquivos a serem removidos:"
        printf '  %s\n' "${files_to_remove[@]}"
        echo ""
        read -p "Confirmar remoção? (s/N): " resposta
        if [[ $resposta =~ ^[Ss]$ ]]; then
            rm -rf "${files_to_remove[@]}"
            echo -e "${GREEN}✓ Arquivos removidos${NC}"
        else
            echo "Cancelado."
        fi
    fi
    echo ""
}

# Main
main() {
    if [ $# -eq 0 ]; then
        show_help
        exit 0
    fi
    
    command=$1
    shift
    
    case $command in
        setup)
            cmd_setup
            ;;
        test)
            cmd_test
            ;;
        run)
            cmd_run
            ;;
        quick)
            cmd_quick "$@"
            ;;
        env)
            cmd_env
            ;;
        status)
            cmd_status
            ;;
        clean)
            cmd_clean
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            echo -e "${RED}✗ Comando desconhecido: $command${NC}"
            echo ""
            echo "Use './pom.sh help' para ver comandos disponíveis."
            exit 1
            ;;
    esac
}

main "$@"
