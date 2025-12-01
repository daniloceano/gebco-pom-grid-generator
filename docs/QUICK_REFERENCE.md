# Guia de Referência Rápida - Ocean Grid Tools

## 🎯 Comandos Essenciais

### Configuração Inicial (apenas uma vez)
```bash
conda env create -f environment.yml
conda activate pom
```

### Ativar/Desativar Ambiente
```bash
conda activate pom    # Ativar
conda deactivate      # Desativar
```

## 📋 Fluxo de Trabalho

### 1. Gerar Grade com GEBCO

```bash
# Entrar no módulo
cd tools/gebco_interpolation/scripts

# Editar configurações
nano generate_grid.py

# Executar
python generate_grid.py
```

**O que editar em `generate_grid.py`:**
```python
# Extensão geográfica (exemplo: costa brasileira)
LON_MIN = -60.0   # Longitude oeste
LON_MAX = -30.0   # Longitude leste
LAT_MIN = -35.0   # Latitude sul
LAT_MAX = -5.0    # Latitude norte

# Espaçamento da grade
GRID_SPACING = 0.25  # 0.25° ≈ 27.8 km
```

### 2. Editar Grade Interativamente

```bash
# Abrir editor
python edit_grid_interactive.py ../../../output/pom_bathymetry_grid.asc
```

**Controles:**
- **Click esquerdo**: Alternar terra ↔ água
- **+** ou **scroll up**: Zoom in
- **-** ou **scroll down**: Zoom out
- **r**: Reset do zoom
- **s**: Salvar modificações
- **q**: Sair

### 3. Verificar Saída

```bash
# Ver primeiras linhas
head -20 ../../../output/pom_bathymetry_grid.asc

# Visualizar (macOS)
open ../../../output/pom_bathymetry_grid.png

# Visualizar (Linux)
xdg-open ../../../output/pom_bathymetry_grid.png
```

## 📐 Guia de Espaçamento

### Tabela de Resolução

| Valor | Resolução no Equador | Uso Recomendado |
|-------|---------------------|-----------------|
| 1.0°  | ~111 km            | Oceano aberto, global |
| 0.5°  | ~55 km             | Escala regional |
| 0.25° | ~28 km             | **Padrão** - balanceado |
| 0.1°  | ~11 km             | Costeiro, detalhado |
| 0.05° | ~5.5 km            | Muito alta resolução |

### Espaçamentos Diferentes (dx ≠ dy)

Se você precisa de resolução diferente em longitude e latitude:

```python
# Em vez de GRID_SPACING, use:
SPACING_LON = 0.25  # dx em graus
SPACING_LAT = 0.20  # dy em graus
```

## 🗺️ Regiões Exemplo

### Costa Sul/Sudeste do Brasil
```python
LON_MIN, LON_MAX = -55.0, -40.0
LAT_MIN, LAT_MAX = -30.0, -20.0
GRID_SPACING = 0.1  # Alta resolução costeira
```

### Costa Nordeste do Brasil
```python
LON_MIN, LON_MAX = -45.0, -32.0
LAT_MIN, LAT_MAX = -18.0, -3.0
GRID_SPACING = 0.25
```

### Atlântico Sul-Ocidental
```python
LON_MIN, LON_MAX = -60.0, -30.0
LAT_MIN, LAT_MAX = -45.0, -10.0
GRID_SPACING = 0.5  # Escala regional
```

### Região Equatorial
```python
LON_MIN, LON_MAX = -50.0, -30.0
LAT_MIN, LAT_MAX = -10.0, 10.0
# Maior resolução meridional para correntes equatoriais
SPACING_LON = 0.30
SPACING_LAT = 0.15
```

## ⚙️ Parâmetros Avançados

### Métodos de Interpolação

Em `generate_grid.py`:
```python
INTERPOLATION_METHOD = 'linear'  # Opções: 'linear', 'nearest', 'cubic'
```

| Método | Velocidade | Qualidade | Quando Usar |
|--------|-----------|-----------|-------------|
| `'linear'` | ⚡⚡ | ⭐⭐⭐ | **Padrão** - bom balanço |
| `'nearest'` | ⚡⚡⚡ | ⭐ | Testes rápidos |
| `'cubic'` | ⚡ | ⭐⭐⭐⭐⭐ | Máxima suavidade |

### Processamento Paralelo

```python
USE_PARALLEL = True   # Ativar/desativar paralelização
N_WORKERS = None      # None = auto (todos os núcleos)
```

## 🐍 Uso Programático

### Exemplo Básico

```python
import sys
sys.path.insert(0, '../src')
from bathymetry_generator import BathymetryGridGenerator

# Criar gerador
gen = BathymetryGridGenerator(
    '../../../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc',
    spacing=0.25
)

# Carregar e processar
gen.load_gebco_data()
gen.define_grid_extent(-60, -30, -35, -5)
gen.interpolate_bathymetry(method='linear', parallel=True)

# Exportar
gen.export_to_ascii('../../../output/grade.asc')
gen.plot_bathymetry('../../../output/grade.png')
```

### Exemplo com dx ≠ dy

```python
gen = BathymetryGridGenerator(
    'gebco.nc',
    spacing_lon=0.30,  # dx = 0.30°
    spacing_lat=0.15   # dy = 0.15°
)
```

## 📊 Formato de Saída

### Estrutura do Arquivo ASCII

```
# Gerado em: 2025-12-01 10:30:00
# Região: Lon [-60.0, -30.0], Lat [-35.0, -5.0]
# Espaçamento: 0.25° lon, 0.25° lat
# Dimensões: 121 x 121 pontos
    1    1  -60.0000  -35.0000    0.0000
    1    2  -60.0000  -34.7500  245.3000
    1    3  -60.0000  -34.5000  512.7000
    ...
```

**5 colunas**: `i, j, lon, lat, depth`

**Convenção**: depth > 0 = oceano, depth = 0 = terra

## 🔍 Troubleshooting Rápido

### Arquivo GEBCO não encontrado
```bash
# Verificar caminho
ls ../../../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc

# Ajustar em generate_grid.py se necessário
GEBCO_FILE = "../../../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"
```

### Erro de memória
```python
# Aumentar espaçamento ou reduzir área
GRID_SPACING = 0.5  # Em vez de 0.25
```

### Interpolação muito lenta
```python
# Ativar paralelização
USE_PARALLEL = True
```

### Grade com terra onde deveria ser oceano
```bash
# Usar editor interativo para corrigir
python edit_grid_interactive.py ../../../output/pom_bathymetry_grid.asc
```

## 📁 Estrutura de Arquivos

```
tools/gebco_interpolation/
├── README.md                    # Documentação completa
├── src/
│   └── bathymetry_generator.py  # Classe principal
├── scripts/
│   ├── generate_grid.py         # ← Editar e executar
│   ├── edit_grid_interactive.py # ← Editor visual
│   └── quick_generate.py        # CLI rápido
└── examples/
    ├── example_basic.py
    ├── example_advanced.py
    └── generate_grid_different_spacing.py
```

## 🔗 Ver Também

- **[README Principal](../../README.md)** - Visão geral do projeto
- **[GEBCO Interpolation README](../tools/gebco_interpolation/README.md)** - Doc detalhada
- **[INSTALL.md](INSTALL.md)** - Guia de instalação completo
