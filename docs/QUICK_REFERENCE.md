# Guia de Referência Rápida - Gerador de Grade Batimétrica POM

## 🎯 Comandos Essenciais

### Configuração Inicial (apenas uma vez)
```bash
./setup_environment.sh
```

### Ativar Ambiente
```bash
conda activate pom
```

### Desativar Ambiente
```bash
conda deactivate
```

### Executar com Wrapper (ativa automaticamente)
```bash
./run_pom.sh script.py [args]
```

## 📋 Fluxo de Trabalho Típico

```bash
# 1. Configurar ambiente (primeira vez)
./setup_environment.sh

# 2. Testar instalação
./run_pom.sh test_bathymetry_generator.py

# 3. Gerar grade (opção A - editar script)
# Edite create_pom_bathymetry_grid.py
./run_pom.sh create_pom_bathymetry_grid.py

# 3. Gerar grade (opção B - linha de comando)
./run_pom.sh quick_generate_grid.py \
    --lon-min -60 --lon-max -30 \
    --lat-min -35 --lat-max -5 \
    --spacing 0.25 \
    --output minha_grade.asc

# 4. Verificar saída
head -20 minha_grade.asc
open minha_grade.png  # Visualizar imagem
```

## 🗺️ Regiões Pré-Definidas

```bash
# Costa Sul/Sudeste do Brasil (-55/-40, -30/-20)
./run_pom.sh quick_generate_grid.py --region brasil_sul

# Costa Nordeste do Brasil (-45/-32, -18/-3)
./run_pom.sh quick_generate_grid.py --region brasil_nordeste

# Atlântico Sul-Ocidental (-60/-30, -45/-10)
./run_pom.sh quick_generate_grid.py --region atlantico_sw
```

## ⚙️ Parâmetros Comuns

### Espaçamento da Grade

| Valor | Resolução    | Uso Recomendado        |
|-------|--------------|------------------------|
| 1.0°  | ~111 km      | Oceano aberto, global  |
| 0.5°  | ~55 km       | Escala regional        |
| 0.25° | ~28 km       | **Padrão** - balanceado |
| 0.1°  | ~11 km       | Costeiro, alta res     |
| 0.05° | ~5.5 km      | Muito detalhado        |

### Métodos de Interpolação

| Método   | Velocidade | Qualidade | Uso                |
|----------|------------|-----------|-------------------|
| nearest  | ⚡⚡⚡     | ⭐        | Testes rápidos    |
| linear   | ⚡⚡       | ⭐⭐⭐    | **Padrão** - balanceado |
| cubic    | ⚡         | ⭐⭐⭐⭐⭐ | Máxima qualidade  |

## 🔧 Exemplos Quick Generate

### Exemplo 1: Básico
```bash
./run_pom.sh quick_generate_grid.py \
    --lon-min -50 --lon-max -40 \
    --lat-min -30 --lat-max -20 \
    --spacing 0.25
```

### Exemplo 2: Com nome customizado
```bash
./run_pom.sh quick_generate_grid.py \
    --region brasil_sul \
    --spacing 0.1 \
    --output grade_sul_alta_res.asc \
    --plot-output grade_sul_alta_res.png
```

### Exemplo 3: Sem visualização (mais rápido)
```bash
./run_pom.sh quick_generate_grid.py \
    --lon-min -55 --lon-max -45 \
    --lat-min -28 --lat-max -23 \
    --spacing 0.25 \
    --no-plot
```

### Exemplo 4: Interpolação cubic (melhor qualidade)
```bash
./run_pom.sh quick_generate_grid.py \
    --region brasil_sul \
    --method cubic \
    --output grade_cubic.asc
```

## 📝 Editar Script Principal

Abra `create_pom_bathymetry_grid.py` e modifique:

```python
# Linha ~543 - CONFIGURAÇÕES

# Arquivo GEBCO
GEBCO_FILE = "gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"

# Espaçamento (graus)
GRID_SPACING = 0.25

# Área de interesse
LON_MIN = -60.0    # Oeste
LON_MAX = -30.0    # Leste
LAT_MIN = -35.0    # Sul
LAT_MAX = -5.0     # Norte

# Arquivo de saída
OUTPUT_FILE = "pom_bathymetry_grid.asc"

# Visualização
GENERATE_PLOT = True
PLOT_FILE = "pom_bathymetry_grid.png"

# Método de interpolação
INTERPOLATION_METHOD = 'linear'
```

## 🐍 Uso Programático Python

```python
from create_pom_bathymetry_grid import BathymetryGridGenerator

# Criar e configurar
gen = BathymetryGridGenerator("gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc", 
                              spacing=0.25)

# Processar
gen.load_gebco_data()
gen.define_grid_extent(-60, -30, -35, -5)
gen.interpolate_bathymetry(method='linear')

# Exportar
gen.export_to_ascii("minha_grade.asc")
gen.plot_bathymetry("minha_grade.png")
gen.cleanup()
```

## 🧪 Testes e Validação

```bash
# Teste completo
./run_pom.sh test_bathymetry_generator.py

# Verificar dependências apenas
conda activate pom
python -c "import numpy, scipy, xarray, netCDF4, matplotlib; print('OK')"

# Verificar arquivo GEBCO
ls -lh gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc

# Verificar ambiente conda
conda env list | grep pom
```

## 📊 Verificar Saída

```bash
# Ver cabeçalho do arquivo
head -20 minha_grade.asc

# Contar linhas de dados
grep -v "^#" minha_grade.asc | wc -l

# Ver últimas linhas
tail -10 minha_grade.asc

# Verificar tamanho
ls -lh minha_grade.asc

# Abrir imagem (macOS)
open minha_grade.png

# Ou (Linux)
xdg-open minha_grade.png
```

## 🔍 Análise Rápida em Python

```python
import numpy as np

# Carregar dados
data = np.loadtxt('minha_grade.asc')
i, j, lon, lat, depth = data.T

# Estatísticas
print(f"Pontos: {len(depth)}")
print(f"Oceano: {np.sum(depth > 0)} ({100*np.sum(depth > 0)/len(depth):.1f}%)")
print(f"Prof. max: {np.max(depth):.1f} m")
print(f"Prof. média: {np.mean(depth[depth > 0]):.1f} m")
print(f"Extensão lon: {lon.min():.2f} a {lon.max():.2f}")
print(f"Extensão lat: {lat.min():.2f} a {lat.max():.2f}")
```

## 🛠️ Manutenção do Ambiente

```bash
# Listar ambientes
conda env list

# Listar pacotes instalados
conda activate pom
conda list

# Atualizar pacotes
conda activate pom
conda update --all

# Atualizar pacote específico
conda activate pom
conda update numpy

# Adicionar novo pacote
conda activate pom
conda install nome-pacote
# ou
pip install nome-pacote

# Remover ambiente (se necessário)
conda deactivate
conda env remove -n pom

# Recriar ambiente
./setup_environment.sh
```

## 💾 Exportar/Importar Ambiente

```bash
# Exportar configuração atual
conda activate pom
conda env export > environment_backup.yml

# Recriar em outra máquina
conda env create -f environment_backup.yml
conda activate pom
```

## ⚠️ Problemas Comuns

### Script não executa
```bash
# Dar permissão de execução
chmod +x setup_environment.sh run_pom.sh
```

### Conda não encontrado
```bash
# Adicionar ao PATH
export PATH="$HOME/miniconda3/bin:$PATH"
source ~/.zshrc
```

### Ambiente não ativa
```bash
# Inicializar conda no shell
conda init zsh
source ~/.zshrc
```

### Erro de memória
```python
# Reduzir área ou aumentar espaçamento
LON_MIN, LON_MAX = -50, -40  # Área menor
GRID_SPACING = 0.5           # Maior espaçamento
```

### Processo muito lento
```python
# Usar método mais rápido
INTERPOLATION_METHOD = 'linear'  # ou 'nearest'
GRID_SPACING = 0.5               # Maior espaçamento
```

## 📁 Arquivos Importantes

| Arquivo                          | Descrição                           |
|----------------------------------|-------------------------------------|
| `create_pom_bathymetry_grid.py` | Script principal (completo)         |
| `quick_generate_grid.py`        | Script rápido (CLI)                 |
| `test_bathymetry_generator.py`  | Validação e testes                  |
| `setup_environment.sh`          | Instalação do ambiente              |
| `run_pom.sh`                    | Wrapper de execução                 |
| `environment.yml`               | Definição conda                     |
| `requirements.txt`              | Dependências pip                    |
| `README.md`                     | Documentação principal              |
| `INSTALL.md`                    | Guia de instalação                  |
| `README_BATHYMETRY_GRID.md`     | Documentação técnica                |
| `QUICK_REFERENCE.md`            | Este arquivo                        |

## 🔗 Links Úteis

- GEBCO: https://www.gebco.net/
- POM: http://www.ccpo.odu.edu/POMWEB/
- Conda: https://docs.conda.io/
- Xarray: https://docs.xarray.dev/

## 📞 Ajuda

```bash
# Ver ajuda do script rápido
./run_pom.sh quick_generate_grid.py --help

# Ver código-fonte
less create_pom_bathymetry_grid.py

# Ver documentação
cat README.md
cat INSTALL.md
```

---

**Dica:** Adicione este atalho ao seu `~/.zshrc`:
```bash
alias pom="conda activate pom"
alias pom-test="conda activate pom && python test_bathymetry_generator.py"
alias pom-gen="conda activate pom && python quick_generate_grid.py"
```

Depois use simplesmente: `pom`, `pom-test`, `pom-gen --help`
