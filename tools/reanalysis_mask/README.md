# Reanalysis Mask - RecOM

Módulo para extrair máscaras terra/oceano de reanálises oceânicas e aplicá-las em grades.

## Visão Geral

Este módulo permite:
- ✅ Extrair máscara terra/oceano de arquivos NetCDF de reanálises
- ✅ Degradar resolução da máscara (ex: 0.1° → 0.3°)
- ✅ Alinhar grades automaticamente
- ✅ Aplicar máscara em grades existentes (via script apply_mask.py)
- ✅ Suporta BRAN2020, GLORYS, HYCOM, e outros formatos NetCDF

## Estrutura

```
reanalysis_mask/
├── src/
│   ├── __init__.py
│   └── mask_extractor.py      # Classe principal
├── scripts/
│   ├── extract_mask.py        # CLI para extrair máscaras
│   └── visualize_mask.py      # Visualizar máscaras
├── examples/
│   └── example_bran2020.py    # Exemplo completo
├── tests/
│   └── test_reanalysis_mask.py # Testes automatizados
└── README.md
```

## Instalação

O módulo já está incluído no pacote RecOM. Certifique-se de que o ambiente conda está ativo:

```bash
conda activate ocean_mesh_tools
```

## Uso Básico

### 1. Extrair Máscara de Reanálise

**Resolução original:**
```bash
cd tools/reanalysis_mask/scripts
python extract_mask.py /path/to/ocean_eta_t_2023_07.nc
```

**Com degradação de resolução:**
```bash
python extract_mask.py /path/to/ocean_eta_t_2023_07.nc \\
    --target-res 0.25 0.25
```

**Com domínio espacial específico:**
```bash
python extract_mask.py /path/to/ocean_eta_t_2023_07.nc \\
    --variable eta_t \\
    --lon-range -60 -30 \\
    --lat-range -35 -5 \\
    --target-res 0.25 0.25 \\
    --output mask_braz_coast.asc
```

### 2. Visualizar Máscara

```bash
python visualize_mask.py mask_braz_coast.asc
```

Ou salvar figura:
```bash
python visualize_mask.py mask_braz_coast.asc mask_visualization.png
```

### 3. Aplicar Máscara em Grade

```bash
# Aplicar máscara extraída a uma grade existente
python apply_mask.py \\
    ../../output/rectangular_grid_*.asc \\
    mask_braz_coast.asc

# Especificar arquivo de saída
python apply_mask.py \\
    ../../output/my_grid.asc \\
    mask_braz_coast.asc \\
    --output ../../output/my_grid_bran2020.asc

# Preservar colunas de longitude -180°/+180° (recomendado para grades globais)
python apply_mask.py \\
    ../../output/rectangular_grid_*.asc \\
    mask_braz_coast.asc \\
    --preserve-boundaries
```

O script gera automaticamente um nome com sufixo indicando a máscara aplicada (ex: `_bran2020`).

**⚠ Importante para grades globais:** Use `--preserve-boundaries` para evitar perda das colunas em -180° e +180° quando a máscara estiver em formato 0-360.

## Uso Programático

### Exemplo Python

```python
import sys
sys.path.insert(0, 'tools/reanalysis_mask/src')
from mask_extractor import ReanalysisMaskExtractor

# Inicializar
extractor = ReanalysisMaskExtractor(
    'ocean_eta_t_2023_07.nc',
    variable_name='eta_t'
)

# Carregar e extrair
extractor.load_data()
extractor.extract_mask(time_index=0)

# Degradar resolução
coarsened_mask, lons, lats = extractor.coarsen_mask(
    target_resolution_lon=0.25,
    target_resolution_lat=0.25,
    threshold=0.5  # 50% de oceano para definir célula como oceano
)

# Exportar
extractor.export_mask('mask_output.asc', coarsened_mask, lons, lats)

# Limpeza
extractor.cleanup()
```

## Parâmetros Importantes

### extract_mask.py

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `--variable` | Nome da variável NetCDF | Auto-detectar |
| `--time-index` | Índice temporal a usar | 0 |
| `--target-res DX DY` | Resolução alvo em graus | Original |
| `--threshold` | Fração mínima de oceano (0-1) | 0.5 |
| `--lon-range MIN MAX` | Limites de longitude | Tudo |
| `--lat-range MIN MAX` | Limites de latitude | Tudo |
| `--output` | Arquivo de saída | Auto-gerado |
| `--no-align` | Não alinhar à grade original | Alinhar |

### apply_mask.py

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `grid_file` | Arquivo de grade (.asc) | **Obrigatório** |
| `mask_file` | Arquivo de máscara (.asc) | **Obrigatório** |
| `--output, -o` | Arquivo de saída | Auto-gerado |
| `--preserve-boundaries` | Preserva colunas em -180°/+180° | Desabilitado |

### ReanalysisMaskExtractor.coarsen_mask()

| Parâmetro | Descrição | Padrão |
|-----------|-----------|--------|
| `target_resolution_lon` | Resolução alvo longitude (°) | **Obrigatório** |
| `target_resolution_lat` | Resolução alvo latitude (°) | **Obrigatório** |
| `threshold` | Fração de oceano (0-1) | 0.5 |
| `align_to_grid` | Alinhar à grade original | True |

**Threshold:**
- `0.5`: Célula é oceano se ≥50% dos pontos finos forem oceano
- `0.7`: Mais conservador (mais terra)
- `0.3`: Menos conservador (mais oceano)

## Formatos Suportados

### Reanálises Testadas

- ✅ **BRAN2020** (CSIRO) - `xt_ocean`, `yt_ocean`
- ✅ **GLORYS** (Copernicus) - `longitude`, `latitude`
- ✅ **HYCOM** - `lon`, `lat`
- ✅ Qualquer NetCDF com coordenadas lon/lat padrão

### Formato de Saída

Arquivo ASCII (5 colunas):
```
# Cabeçalho com metadados
i  j  lon  lat  mask
1  1  -60.0000  -35.0000  0
2  1  -59.7500  -35.0000  1
...
```

Onde `mask`:
- `1` = Oceano (dados válidos)
- `0` = Terra (NaN/masked)

## Integração com Grid Editor

O grid editor tem suporte nativo para aplicar máscaras de reanálise:

**Controles:**
- `m`: Carregar e aplicar máscara de reanálise
- `s`: Salvar grade modificada
- `q`: Sair

**Processo:**
1. Abra uma grade no editor
2. Pressione `m`
3. Digite o caminho da máscara quando solicitado
4. A máscara será aplicada (pontos terrestres na máscara → depth=0 na grade)
5. Pressione `s` para salvar

**Nota:** A aplicação da máscara é conservadora - apenas converte oceano em terra onde a máscara indica terra. Não cria oceano onde não havia.

## Exemplos

### Exemplo 1: BRAN2020 para grade 0.25°

```bash
python extract_mask.py /path/to/BRAN/ocean_eta_t_2023_07.nc \\
    --variable eta_t \\
    --lon-range -60 -30 \\
    --lat-range -35 -5 \\
    --target-res 0.25 0.25 \\
    --threshold 0.5 \\
    --output mask_bran_0.25deg.asc
```

### Exemplo 2: GLORYS para POM

```bash
python extract_mask.py /path/to/GLORYS/glorys12v1_2020_01.nc \\
    --lon-range -60 -30 \\
    --lat-range -35 -5 \\
    --target-res 0.3 0.3 \\
    --output mask_glorys_pom.asc
```

### Exemplo 3: Uso em Pipeline

```bash
# 1. Extrair máscara
python extract_mask.py reanalysis.nc --target-res 0.25 0.25 -o mask.asc

# 2. Visualizar
python visualize_mask.py mask.asc mask_plot.png

# 3. Gerar grade GEBCO
cd ../../gebco_interpolation/scripts
python generate_grid.py  # Ajustar configurações no script

# 4. Aplicar máscara na grade GEBCO
cd ../../reanalysis_mask/scripts
python apply_mask.py \\
    ../../../output/rectangular_grid_*.asc \\
    mask.asc
```

## Troubleshooting

### Erro: "Arquivo não encontrado"
Verifique o caminho completo do arquivo NetCDF.

### Erro: "Não foi possível identificar variável"
Especifique explicitamente com `--variable nome_variavel`.

### Grade mascarada perdeu colunas em -180°/+180°
**Problema:** Grade global (ex: -180° a +180°) perde bordas longitudinais após aplicar máscara em formato 0-360.

**Solução:** Use `--preserve-boundaries` ao aplicar a máscara:
```bash
python apply_mask.py grid.asc mask.asc --preserve-boundaries
```

Isso preserva as colunas originais em -180° e +180° para manter continuidade longitudinal no modelo oceânico.

### Máscara não alinha com costa
- Verifique a resolução alvo
- Ajuste o `--threshold` (tente 0.3 ou 0.7)
- Garanta que o domínio espacial está correto

### Muita terra na grade
- Reduza `--threshold` (ex: 0.3)
- Verifique se a reanálise tem boa resolução na costa

### Muita água na grade
- Aumente `--threshold` (ex: 0.7)

## Testes

Execute os testes automatizados:

```bash
cd tools/reanalysis_mask/tests
python test_reanalysis_mask.py
```

Testes incluem:
- ✓ Extração de máscara
- ✓ Degradação de resolução
- ✓ Exportação de arquivo
- ✓ Verificação de formato

## Limitações

- **Resolução mínima:** A máscara degradada não pode ser mais fina que a original
- **Alinhamento:** Funciona melhor com grades regulares (lat/lon)
- **Memória:** Arquivos muito grandes podem precisar de mais RAM

## Dicas

1. **Threshold:** Use 0.5 como padrão. Ajuste se necessário:
   - Costa complexa → 0.3 (mais oceano)
   - Costa suave → 0.7 (mais conservador)

2. **Resolução:** Para degradar 0.1° → 0.3°, use `--target-res 0.3 0.3`

3. **Performance:** Para domínios grandes, especifique `--lon-range` e `--lat-range`

4. **Visualização:** Sempre visualize a máscara antes de aplicar

## Referências

- **BRAN2020:** https://research.csiro.au/bluelink/outputs/data-and-products/
- **GLORYS:** https://marine.copernicus.eu/
- **HYCOM:** https://www.hycom.org/

## Suporte

Para problemas ou dúvidas:
1. Veja a documentação principal: `README.md` (raiz do projeto)
2. Execute os testes: `python tests/test_reanalysis_mask.py`
3. Consulte exemplos: `examples/example_bran2020.py`

---

**RecOM - Rectangular Ocean Mesh Tools** | Dezembro 2025
