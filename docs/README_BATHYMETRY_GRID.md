# Gerador de Grade Batimétrica para Modelo POM

## Descrição

Este conjunto de scripts permite criar grades batimétricas interpoladas a partir dos dados do GEBCO para uso no modelo POM (Princeton Ocean Model). O script principal (`create_pom_bathymetry_grid.py`) realiza a interpolação de dados batimétricos globais para uma grade regular com espaçamento definido pelo usuário.

## Requisitos

### Dependências Python

```bash
pip install numpy scipy xarray netCDF4 matplotlib
```

**Versões recomendadas:**
- Python >= 3.8
- numpy >= 1.20
- scipy >= 1.7
- xarray >= 0.19
- netCDF4 >= 1.5
- matplotlib >= 3.3 (opcional, apenas para visualização)

## Dados de Entrada

### GEBCO (General Bathymetric Chart of the Oceans)

O script utiliza dados do GEBCO 2025, que fornece:
- Cobertura global de batimetria e topografia
- Resolução de 15 arc-seconds (~450 m)
- Formato NetCDF
- Valores negativos = oceano (profundidade)
- Valores positivos = terra (elevação)

**Arquivo esperado:** `gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc`

## Formato de Saída

O arquivo ASCII gerado contém 5 colunas:

```
i  j  lon  lat  depth
```

Onde:
- **i**: Índice da coluna (1 a n_cols)
- **j**: Índice da linha (1 a n_rows)
- **lon**: Longitude em graus decimais
- **lat**: Latitude em graus decimais
- **depth**: Profundidade em metros (valores positivos para oceano, 0 para terra)

### Exemplo de saída:

```
#      i      j        lon        lat      depth
      1      1   -60.0000   -35.0000      45.32
      2      1   -59.7500   -35.0000     123.45
      3      1   -59.5000   -35.0000     234.56
    ...    ...        ...        ...        ...
```

## Uso

### 1. Uso Básico

Edite a seção de configurações no script `create_pom_bathymetry_grid.py`:

```python
# CONFIGURAÇÕES
GEBCO_FILE = "gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"
GRID_SPACING = 0.25  # Espaçamento em graus
LON_MIN = -60.0      # Longitude mínima (oeste)
LON_MAX = -30.0      # Longitude máxima (leste)
LAT_MIN = -35.0      # Latitude mínima (sul)
LAT_MAX = -5.0       # Latitude máxima (norte)
OUTPUT_FILE = "pom_bathymetry_grid.asc"
```

Execute o script:

```bash
python create_pom_bathymetry_grid.py
```

### 2. Uso Programático

Você também pode importar e usar a classe em seus próprios scripts:

```python
from create_pom_bathymetry_grid import BathymetryGridGenerator

# Criar gerador
generator = BathymetryGridGenerator("gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc", 
                                    spacing=0.25)

# Carregar dados
generator.load_gebco_data()

# Definir região de interesse
generator.define_grid_extent(lon_min=-60, lon_max=-30, 
                            lat_min=-35, lat_max=-5)

# Interpolar
generator.interpolate_bathymetry(method='linear')

# Exportar
generator.export_to_ascii("minha_grade.asc")

# Visualizar (opcional)
generator.plot_bathymetry("minha_grade.png")

# Limpar
generator.cleanup()
```

## Parâmetros de Configuração

### Espaçamento da Grade

O espaçamento da grade é definido em graus decimais. Conversão aproximada:

| Graus | km (equador) | km (lat 30°) | Descrição |
|-------|--------------|--------------|-----------|
| 1.0   | ~111 km      | ~96 km       | Baixa resolução |
| 0.5   | ~55 km       | ~48 km       | Resolução moderada |
| 0.25  | ~28 km       | ~24 km       | **Recomendado** |
| 0.1   | ~11 km       | ~9.6 km      | Alta resolução |
| 0.05  | ~5.5 km      | ~4.8 km      | Muito alta resolução |

**Nota:** Espaçamentos menores resultam em:
- ✓ Maior precisão
- ✗ Maior tempo de processamento
- ✗ Arquivos maiores
- ✗ Maior uso de memória

### Extensão Geográfica

Defina os limites da sua região de interesse:

**Exemplos de regiões:**

```python
# Costa Brasileira Sul-Sudeste
LON_MIN, LON_MAX = -55.0, -40.0
LAT_MIN, LAT_MAX = -30.0, -20.0

# Atlântico Sul Ocidental
LON_MIN, LON_MAX = -60.0, -30.0
LAT_MIN, LAT_MAX = -45.0, -10.0

# Região Nordeste
LON_MIN, LON_MAX = -45.0, -32.0
LAT_MIN, LAT_MAX = -18.0, -3.0

# Região Amazônica (plataforma)
LON_MIN, LON_MAX = -55.0, -40.0
LAT_MIN, LAT_MAX = -5.0, 10.0
```

### Métodos de Interpolação

- **'linear'** (padrão): Bom equilíbrio entre precisão e velocidade
- **'nearest'**: Mais rápido, menos suave, preserva valores originais
- **'cubic'**: Mais suave, mais lento, pode gerar artefatos

## Saídas Geradas

1. **Arquivo ASCII** (`pom_bathymetry_grid.asc`):
   - Formato de 5 colunas para o POM
   - Inclui cabeçalho com metadados
   - Pronto para uso no modelo

2. **Visualização** (`pom_bathymetry_grid.png`, opcional):
   - Mapa de cores da batimetria
   - Contornos de profundidade
   - Útil para verificação visual

## Interpretação dos Resultados

O script fornece estatísticas úteis:

```
INTERPOLAÇÃO CONCLUÍDA
==========================================
Pontos oceânicos: 14520 (85.3%)
Pontos terrestres: 2480 (14.7%)
Profundidade máxima: 5432.1 m
Profundidade média (oceano): 2156.8 m
==========================================
```

**Verifique:**
- Proporção oceano/terra está correta para sua região?
- Profundidade máxima é realista?
- Profundidade média condiz com o esperado?

## Resolução de Problemas

### Erro: "File not found"
```
Solução: Verifique se o caminho para o arquivo GEBCO está correto
```

### Erro: "Memory error"
```
Solução: 
1. Reduza a extensão geográfica da grade
2. Aumente o espaçamento da grade
3. Use um computador com mais RAM
```

### Interpolação muito lenta
```
Solução:
1. Use method='linear' ou 'nearest'
2. Reduza a extensão da grade
3. Aumente o espaçamento
```

### Valores estranhos na batimetria
```
Verificar:
1. A região está dentro dos limites do GEBCO?
2. Os sinais estão corretos (depth positivo = oceano)?
3. A grade tem resolução adequada?
```

## Validação

Após gerar a grade, recomenda-se:

1. **Inspeção visual**: Abra a imagem PNG gerada
2. **Verificação de estatísticas**: Confira os valores máximo, mínimo e médio
3. **Teste no modelo**: Execute o POM com a grade e verifique estabilidade
4. **Comparação**: Compare com outras fontes de batimetria se disponível

## Customização

### Modificar formato de saída

Edite o parâmetro `format_spec` em `export_to_ascii()`:

```python
# Mais casas decimais
generator.export_to_ascii("saida.asc", 
                         format_spec='%8d %8d %12.6f %12.6f %12.4f')

# Formato compacto
generator.export_to_ascii("saida.asc", 
                         format_spec='%d %d %.4f %.4f %.2f')
```

### Adicionar processamento adicional

```python
# Após interpolação, antes de exportar:
# Exemplo: Limitar profundidade máxima
generator.depth_grid = np.minimum(generator.depth_grid, 6000)

# Exemplo: Suavizar batimetria
from scipy.ndimage import gaussian_filter
generator.depth_grid = gaussian_filter(generator.depth_grid, sigma=1)

# Exemplo: Definir profundidade mínima
generator.depth_grid = np.maximum(generator.depth_grid, 10)
```

## Referências

- **GEBCO**: https://www.gebco.net/
- **Modelo POM**: http://www.ccpo.odu.edu/POMWEB/
- **NetCDF**: https://www.unidata.ucar.edu/software/netcdf/
- **Xarray**: https://docs.xarray.dev/

## Citação

Se utilizar este script em publicações científicas, por favor cite:

```
GEBCO Compilation Group (2025) GEBCO 2025 Grid
DOI: 10.5285/a29c5465-b138-234d-e053-6c86abc040b9
```

## Contato e Suporte

Para questões, sugestões ou relatar problemas:
- Abra uma issue no repositório
- Entre em contato com o desenvolvedor
- Consulte a documentação do POM

## Licença

Este script é fornecido "como está", sem garantias. Você é livre para modificar e distribuir conforme necessário para fins de pesquisa científica.

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0
