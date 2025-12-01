# Interpolação de Dados GEBCO

## O que faz

Esta ferramenta interpola dados batimétricos globais do GEBCO (General Bathymetric Chart of the Oceans) para gerar grades regulares customizadas. É útil para criar grades de entrada para modelos oceânicos como POM, ROMS, MOM, etc.

**Principais funcionalidades:**
- Interpolação de dados GEBCO para grade regular com espaçamento definido pelo usuário
- Suporte a espaçamentos diferentes em longitude (dx) e latitude (dy)
- Processamento paralelo para grandes áreas
- Editor interativo para correções manuais (terra ↔ água)
- Exportação em formato ASCII de 5 colunas: `i, j, lon, lat, depth`

## Formato de saída

O arquivo gerado segue a convenção POM:
- **5 colunas**: índice i, índice j, longitude, latitude, profundidade
- **Convenção de profundidade**: depth > 0 = oceano, depth = 0 = terra
- **Arquivo ASCII** simples, fácil de ler e processar

Exemplo:
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

## Como usar

### 1. Uso básico (geração de grade)

```bash
cd scripts
python generate_grid.py
```

**Antes de executar**, edite o arquivo `generate_grid.py` e configure:

```python
# Extensão geográfica (exemplo: costa brasileira)
LON_MIN = -60.0   # Longitude oeste
LON_MAX = -30.0   # Longitude leste
LAT_MIN = -35.0   # Latitude sul
LAT_MAX = -5.0    # Latitude norte

# Espaçamento da grade
GRID_SPACING = 0.25  # 0.25° ≈ 27.8 km no equador
```

### 2. Espaçamentos diferentes (dx ≠ dy)

Se você precisa de resolução diferente em longitude e latitude:

```python
# Em vez de GRID_SPACING, use:
SPACING_LON = 0.25  # dx em graus
SPACING_LAT = 0.20  # dy em graus (maior resolução meridional)
```

### 3. Editor interativo

Para corrigir manualmente pontos da grade (fechar baías, abrir canais, etc):

```bash
python edit_grid_interactive.py ../output/pom_bathymetry_grid.asc
```

**Controles do editor:**
- **Click esquerdo**: Alternar terra ↔ água
- **+ / scroll up**: Zoom in
- **- / scroll down**: Zoom out
- **r**: Reset do zoom
- **s**: Salvar
- **q**: Sair

Quando você converte terra → água, o programa automaticamente interpola a profundidade dos vizinhos usando IDW (Inverse Distance Weighting).

### 4. Uso via Python (programático)

```python
from bathymetry_generator import BathymetryGridGenerator

# Criar gerador
gen = BathymetryGridGenerator(
    gebco_file='../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc',
    spacing_lon=0.25,
    spacing_lat=0.25
)

# Carregar dados
gen.load_gebco_data()

# Definir área
gen.define_grid_extent(
    lon_min=-60.0, lon_max=-30.0,
    lat_min=-35.0, lat_max=-5.0
)

# Interpolar
gen.interpolate_bathymetry(method='linear', parallel=True)

# Exportar
gen.export_to_ascii('minha_grade.asc')

# Visualizar
gen.plot_bathymetry('minha_grade.png')
```

## Parâmetros principais

### BathymetryGridGenerator

| Parâmetro | Tipo | Descrição | Padrão |
|-----------|------|-----------|--------|
| `gebco_file` | str | Caminho para arquivo NetCDF do GEBCO | obrigatório |
| `spacing` | float | Espaçamento uniforme (dx = dy) em graus | None |
| `spacing_lon` | float | Espaçamento em longitude (dx) em graus | None |
| `spacing_lat` | float | Espaçamento em latitude (dy) em graus | None |
| `n_workers` | int | Número de processos paralelos | auto |

**Nota**: Use `spacing` OU (`spacing_lon` + `spacing_lat`), não ambos.

### Métodos de interpolação

| Método | Descrição | Quando usar |
|--------|-----------|-------------|
| `'linear'` | Interpolação bilinear | Padrão, bom balanço |
| `'nearest'` | Vizinho mais próximo | Grades muito esparsas |
| `'cubic'` | Interpolação cúbica | Suavização máxima |

## Exemplos

### Exemplo 1: Costa brasileira (espaçamento uniforme)

```python
gen = BathymetryGridGenerator('gebco.nc', spacing=0.25)
gen.load_gebco_data()
gen.define_grid_extent(-60, -30, -35, -5)
gen.interpolate_bathymetry()
gen.export_to_ascii('brasil.asc')
```

### Exemplo 2: Região equatorial (maior resolução meridional)

```python
# Mais resolução em latitude para capturar correntes equatoriais
gen = BathymetryGridGenerator(
    'gebco.nc',
    spacing_lon=0.30,  # ~33 km
    spacing_lat=0.15   # ~17 km
)
gen.load_gebco_data()
gen.define_grid_extent(-50, -30, -10, 10)
gen.interpolate_bathymetry()
gen.export_to_ascii('equatorial.asc')
```

### Exemplo 3: Edição manual de grade

```bash
# 1. Gerar grade inicial
python generate_grid.py

# 2. Editar interativamente
python edit_grid_interactive.py ../output/pom_bathymetry_grid.asc

# 3. Arquivo editado é salvo automaticamente com timestamp
# Exemplo: pom_bathymetry_grid_edited_20251201_103045.asc
```

## Requisitos

- Python 3.8+
- numpy
- scipy
- xarray
- netCDF4
- matplotlib

Instale todas as dependências com:
```bash
conda env create -f ../../environment.yml
conda activate pom
```

## Estrutura de arquivos

```
gebco_interpolation/
├── README.md                    # Este arquivo
├── src/
│   ├── __init__.py
│   └── bathymetry_generator.py  # Classe principal
├── scripts/
│   ├── generate_grid.py         # Script de geração
│   ├── edit_grid_interactive.py # Editor interativo
│   └── quick_generate.py        # Interface CLI rápida
└── examples/
    ├── example_basic.py         # Exemplo básico
    ├── example_advanced.py      # Exemplo avançado
    └── generate_grid_different_spacing.py  # Exemplo dx≠dy
```

## Dados GEBCO

Faça download dos dados GEBCO em:
https://www.gebco.net/data_and_products/gridded_bathymetry_data/

Coloque o arquivo NetCDF em `../../gebco_2025_sub_ice_topo/`

## Notas técnicas

### Interpolação

O programa usa `scipy.interpolate.RegularGridInterpolator` para interpolar do grid global do GEBCO (resolução ~450m) para sua grade customizada. O processamento paralelo divide a grade em blocos e processa simultaneamente.

### Editor interativo

O editor usa Inverse Distance Weighting (IDW) para interpolar profundidades quando você converte terra em água. A busca é feita em um raio de até 5 células, e a profundidade final é a média ponderada pelo inverso da distância ao quadrado.

### Performance

Para grandes áreas:
- Use `parallel=True` na interpolação
- Ajuste `n_workers` conforme seus núcleos de CPU
- Grades 500x500 levam ~5-10 segundos
- Grades 2000x2000 levam ~2-5 minutos

## Troubleshooting

**"FileNotFoundError: GEBCO file not found"**
→ Verifique o caminho do arquivo GEBCO no script

**"MemoryError"**
→ Reduza a área ou aumente o espaçamento da grade

**"Interpolation very slow"**
→ Ative processamento paralelo: `parallel=True`

**"Grid has land where should be ocean"**
→ Use o editor interativo para corrigir manualmente
