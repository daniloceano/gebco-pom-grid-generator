# Guia de Instalação - RecOM (Rectangular Ocean Mesh Tools)

## Pré-requisitos

### 1. Anaconda ou Miniconda

**Por que Conda?**
- Gerencia dependências científicas complexas
- Evita conflitos entre pacotes
- Isola ambientes de projetos diferentes

**Download:**
- **Anaconda** (completo, ~500 MB): https://www.anaconda.com/download
- **Miniconda** (mínimo, ~50 MB): https://docs.conda.io/en/latest/miniconda.html

**Verificar instalação:**
```bash
conda --version
```

### 2. Dados GEBCO (para usar interpolação GEBCO)

Baixe em: https://www.gebco.net/data_and_products/gridded_bathymetry_data/

Coloque o arquivo NetCDF em:
```
gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc
```

## Instalação

### Passo 1: Clonar/Baixar o Repositório

```bash
# Se usar git
git clone https://github.com/daniloceano/RecOM.git
cd RecOM

# Ou baixe o ZIP e extraia
```

### Passo 2: Criar Ambiente Conda

```bash
# Criar ambiente a partir do arquivo YAML
conda env create -f environment.yml

# Aguarde a instalação (~2-5 minutos)
```

### Passo 3: Ativar Ambiente

```bash
conda activate ocean_mesh_tools
```

Você verá `(ocean_mesh_tools)` no início do prompt.

### Passo 4: Verificar Instalação

```bash
# Verificar pacotes instalados
conda list

# Verificar Python
python --version  # Deve mostrar Python 3.10 ou superior
```

## Uso Básico

### Sempre ativar o ambiente antes de usar

```bash
conda activate ocean_mesh_tools
```

### Executar ferramenta GEBCO

```bash
cd tools/gebco_interpolation/scripts
python generate_grid.py
```

### Desativar ambiente quando terminar

```bash
conda deactivate
```

## Instalação Manual (Alternativa)

Se preferir instalar manualmente:

### 1. Criar ambiente conda

```bash
conda create -n pom python=3.10 -y
conda activate ocean_mesh_tools
```

### 2. Instalar dependências

#### Via conda-forge (recomendado):
```bash
conda install -c conda-forge \
    numpy scipy xarray netcdf4 matplotlib -y
```

#### Via pip (alternativa):
```bash
pip install numpy scipy xarray netCDF4 matplotlib
```

### 3. Verificar instalação

```bash
python -c "import numpy, scipy, xarray, netCDF4, matplotlib; print('OK')"
```

## Troubleshooting

### Erro: "conda: command not found"

**Solução:**
- Reinicie o terminal após instalar conda
- Ou execute: `source ~/.bashrc` (Linux) ou `source ~/.zshrc` (macOS)

### Erro ao criar ambiente: "ResolvePackageNotFound"

**Solução 1 - Atualizar conda:**
```bash
conda update -n base conda
```

**Solução 2 - Usar conda-forge:**
```bash
conda config --add channels conda-forge
conda config --set channel_priority strict
conda env create -f environment.yml
```

### Erro: "Solving environment: failed with initial frozen solve"

**Solução - Forçar resolução:**
```bash
conda env create -f environment.yml --force
```

### Ambiente muito lento para resolver dependências

**Solução - Usar mamba (conda alternativo mais rápido):**
```bash
# Instalar mamba
conda install -c conda-forge mamba -y

# Criar ambiente com mamba
mamba env create -f environment.yml
```

### Erro ao importar netCDF4

**Solução:**
```bash
conda activate ocean_mesh_tools
conda install -c conda-forge netcdf4 --force-reinstall
```

### ImportError: "No module named 'bathymetry_generator'"

**Causa:** Você está rodando o script do diretório errado.

**Solução:**
```bash
# Certifique-se de estar no diretório correto
cd tools/gebco_interpolation/scripts
python generate_grid.py
```

## Dependências

### Obrigatórias

| Pacote | Versão Mínima | Função |
|--------|---------------|--------|
| Python | 3.8+ | Linguagem base |
| numpy | 1.20+ | Computação numérica |
| scipy | 1.7+ | Interpolação |
| xarray | 2022.3+ | Manipulação de dados NetCDF |
| netCDF4 | 1.5+ | Leitura de GEBCO |
| matplotlib | 3.5+ | Visualização e editor |

### Opcionais

| Pacote | Função |
|--------|--------|
| cartopy | Mapas com projeções (futuro) |
| jupyter | Notebooks interativos (futuro) |

## Atualizar Ambiente

### Atualizar pacotes

```bash
conda activate ocean_mesh_tools
conda update --all
```

### Adicionar novo pacote

```bash
conda activate ocean_mesh_tools
conda install -c conda-forge nome_do_pacote
```

### Recriar ambiente do zero

```bash
# Remover ambiente antigo
conda deactivate
conda env remove -n pom

# Criar novo
conda env create -f environment.yml
```

## Remover Ambiente

Se não precisar mais do projeto:

```bash
# Desativar se estiver ativo
conda deactivate

# Remover ambiente
conda env remove -n pom

# Confirmar remoção
conda env list  # "pom" não deve aparecer
```

## Estrutura Após Instalação

```
ocean-grid-tools/
├── environment.yml          # ✓ Ambiente criado
├── tools/
│   └── gebco_interpolation/ # ✓ Pronto para usar
│       └── scripts/
│           └── generate_grid.py
└── gebco_2025_sub_ice_topo/ # ⚠️ Você deve baixar GEBCO
    └── GEBCO_2025_sub_ice.nc
```

## Próximos Passos

Após a instalação:

1. **Ler documentação rápida**: [QUICK_REFERENCE.md](QUICK_REFERENCE.md)
2. **Testar ferramenta GEBCO**: [tools/gebco_interpolation/README.md](../tools/gebco_interpolation/README.md)
3. **Ver exemplos**: `tools/gebco_interpolation/examples/`

## Sistemas Operacionais Testados

- ✅ macOS (Apple Silicon e Intel)
- ✅ Linux (Ubuntu 20.04+, Debian, Fedora)
- ✅ Windows 10/11 (via Anaconda Prompt ou WSL)

## Requisitos de Hardware

### Mínimo
- CPU: 2 cores
- RAM: 4 GB
- Disco: 10 GB livres (incluindo dados GEBCO)

### Recomendado
- CPU: 4+ cores (para processamento paralelo)
- RAM: 8+ GB
- Disco: 20 GB livres
- SSD (para leitura rápida do GEBCO)

## Ajuda Adicional

**Problema não listado aqui?**

1. Verifique se conda está atualizado: `conda update -n base conda`
2. Tente recriar o ambiente do zero
3. Verifique a documentação do conda: https://docs.conda.io/
