# QUICKSTART — Editar uma grade no modo interativo

Este guia rápido explica, passo a passo e de forma didática, como clonar o repositório RecOM, configurar o ambiente e abrir o editor interativo para editar uma grade batimétrica.

**Plataforma:** macOS (terminal zsh) - mas funciona em Linux também.

---

## 1) Clonar o repositório

Abra o Terminal (Aplicativos → Utilitários → Terminal) e rode:

```bash
git clone https://github.com/daniloceano/RecOM.git
cd RecOM
```

Você estará agora na pasta raiz do projeto (`RecOM`).

---

## 2) Configurar o ambiente Conda (usando o wrapper)

O projeto possui um wrapper `ocean_mesh_tools.sh` que facilita todas as operações. Use-o para configurar o ambiente:

```bash
./ocean_mesh_tools.sh env
```

Este comando irá:
- Criar o ambiente conda `ocean_mesh_tools` automaticamente
- Instalar todas as dependências necessárias (Cartopy, numpy, matplotlib, xarray, etc.)
- Mostrar instruções para ativar o ambiente

**Observação:** Se você não tem conda instalado, instale Miniconda ou Miniforge primeiro:
- Miniforge (recomendado): https://github.com/conda-forge/miniforge
- Miniconda: https://docs.conda.io/en/latest/miniconda.html

---

## 3) Ativar o ambiente (sempre antes de usar)

Ative o ambiente criado (nome padrão usado pelos scripts: `ocean_mesh_tools`):

```bash
conda activate ocean_mesh_tools

# Verificar
echo $CONDA_DEFAULT_ENV   # deve imprimir: ocean_mesh_tools
```

Observação: os scripts (como `ocean_mesh_tools.sh`) assumem que o ambiente está ativo; caso contrário, eles pedirão para ativá-lo.

---

## 4) Conferir arquivos de grade (opcional)

Veja quais grades já estão no diretório de saída:

```bash
ls -1 output/*.asc
ls -1 output/*.png
```

---

## 5) Abrir o editor interativo

Use o wrapper `ocean_mesh_tools.sh` para abrir o editor:

```bash
./ocean_mesh_tools.sh edit output/pom_bathymetry_grid.asc
```

**Exemplo com uma grade existente:**

```bash
./ocean_mesh_tools.sh edit output/test_grid_southeast_Brazil_dx0.30_dy0.25_ocean.asc
```

**Notas importantes:**
- O wrapper verifica automaticamente se o ambiente conda está ativo
- Se não estiver ativo, ele avisará para você ativar primeiro (veja passo 3)
- Use caminhos relativos a partir da raiz do projeto (`RecOM`)

---

## 6) Controles básicos do editor (interativo)

- Mouse:
  - Click esquerdo — alterna terra ↔ água na célula clicada
  - Click direito + arrastar — mover / pan pelo mapa
  - Scroll — zoom in/out
- Teclado:
  - `+` ou `=` — zoom in
  - `-` — zoom out
  - `r` — reset do zoom
  - `g` — mostrar/ocultar grade de células
  - `c` — mostrar/ocultar linha de costa
  - `b` — mostrar/ocultar contornos batimétricos
  - `s` — salvar modificações (gera backup e versão com timestamp)
  - `q` — sair

Ao salvar, o editor mantém o formato ASCII de 5 colunas (`i j lon lat depth`) e cria backups com timestamp.

---

## 7) Visualizar somente (sem editar)

Se quiser apenas gerar/mostrar uma figura (sem abrir o editor):

```bash
# Mostrar sem salvar
./ocean_mesh_tools.sh view output/pom_bathymetry_grid.asc

# Salvar figura PNG
./ocean_mesh_tools.sh view output/pom_bathymetry_grid.asc -o output/minha_figura.png --dpi 300
```

---

## 8) Outros comandos úteis do wrapper

O wrapper `ocean_mesh_tools.sh` oferece vários comandos úteis:

```bash
# Ver ajuda completa
./ocean_mesh_tools.sh help

# Visualizar uma grade (sem editar)
./ocean_mesh_tools.sh view output/pom_bathymetry_grid.asc

# Salvar visualização em PNG
./ocean_mesh_tools.sh view output/pom_bathymetry_grid.asc -o output/figura.png --dpi 300

# Executar testes do projeto
./ocean_mesh_tools.sh test
```

---

## 9) Problemas comuns e soluções

**Problema:** `conda: command not found`  
**Solução:** Instale Miniforge (https://github.com/conda-forge/miniforge), reabra o terminal e execute `./ocean_mesh_tools.sh env`

**Problema:** "Ambiente conda não está ativo"  
**Solução:** Execute `conda activate ocean_mesh_tools` antes de usar o wrapper

**Problema:** Arquivo não encontrado  
**Solução:** Certifique-se de estar na pasta raiz do projeto (`RecOM`) ao executar os comandos

**Problema:** Editor não abre ou erro com Cartopy  
**Solução:** Recrie o ambiente: `conda env remove -n ocean_mesh_tools` e depois `./ocean_mesh_tools.sh env`

---

## 10) Resumo - Fluxo completo (copie e cole)

```bash
# 1. Clonar repositório
git clone https://github.com/daniloceano/RecOM.git
cd RecOM

# 2. Configurar ambiente (uma vez)
./ocean_mesh_tools.sh env

# 3. Ativar ambiente (sempre)
conda activate ocean_mesh_tools

# 4. Editar uma grade
./ocean_mesh_tools.sh edit output/pom_bathymetry_grid.asc

# Dentro do editor:
# - Click esquerdo = alternar terra/água
# - Click direito + arrastar = mover mapa
# - 's' = salvar
# - 'q' = sair
```

---

## 📚 Documentação adicional

- **README principal:** `README.md`
- **Referência rápida:** `docs/QUICK_REFERENCE.md`
- **Guia de instalação:** `docs/INSTALL.md`
- **Editor de grades:** `tools/grid_editor/README.md`