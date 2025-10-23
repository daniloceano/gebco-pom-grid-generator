# Gerador de Grade Batimétrica para Modelo POM

## 📋 Visão Geral

Este projeto fornece ferramentas para criar grades batimétricas interpoladas a partir dos dados globais do GEBCO (General Bathymetric Chart of the Oceans) para uso no modelo POM (Princeton Ocean Model). O sistema é projetado para ser robusto, bem documentado e fácil de usar por pesquisadores.

## ✨ Características

- 🌊 **Interpolação de alta qualidade** dos dados batimétricos do GEBCO
- 📐 **Grade regular customizável** com espaçamento horizontal definido pelo usuário
- 📝 **Formato ASCII compatível** com modelo POM (5 colunas: i, j, lon, lat, depth)
- 🖼️ **Visualização automática** da batimetria gerada
- 🔧 **Ambiente conda isolado** para evitar conflitos de dependências
- 📚 **Documentação completa** e exemplos práticos
- ✅ **Scripts de validação** para verificar instalação e funcionamento

## 📁 Estrutura do Projeto

```
POM/
├── gebco_2025_sub_ice_topo/       # Dados do GEBCO
│   ├── GEBCO_2025_sub_ice.nc      # Arquivo NetCDF com batimetria global
│   ├── GEBCO_Grid_documentation.pdf
│   └── GEBCO_Grid_terms_of_use.pdf
│
├── create_pom_bathymetry_grid.py  # Script principal (bem documentado)
├── quick_generate_grid.py         # Script de uso rápido com argumentos CLI
├── test_bathymetry_generator.py   # Script de validação e testes
│
├── setup_environment.sh           # Instalação automática do ambiente conda
├── run_pom.sh                     # Wrapper para executar scripts no ambiente
├── environment.yml                # Definição do ambiente conda
├── requirements.txt               # Dependências Python
│
├── README.md                      # Este arquivo
├── INSTALL.md                     # Guia detalhado de instalação
└── README_BATHYMETRY_GRID.md      # Documentação técnica completa
```

## 🚀 Início Rápido

### 1. Instalação do Ambiente

```bash
# Clone ou navegue até o diretório do projeto
cd /path/to/POM

# Execute o script de configuração
./setup_environment.sh
```

Isso criará um ambiente conda chamado `pom` com todas as dependências necessárias.

### 2. Validação

```bash
# Teste se tudo está funcionando
./run_pom.sh test_bathymetry_generator.py
```

### 3. Geração de Grade

**Opção A: Editar e executar script principal**

```bash
# 1. Edite create_pom_bathymetry_grid.py com suas configurações
# 2. Execute:
./run_pom.sh create_pom_bathymetry_grid.py
```

**Opção B: Usar script rápido com argumentos**

```bash
# Ver opções disponíveis
./run_pom.sh quick_generate_grid.py --help

# Exemplo: Costa brasileira sul
./run_pom.sh quick_generate_grid.py \
    --lon-min -55 --lon-max -40 \
    --lat-min -30 --lat-max -20 \
    --spacing 0.25 \
    --output minha_grade.asc

# Ou usar região pré-definida
./run_pom.sh quick_generate_grid.py --region brasil_sul
```

## 📖 Documentação

- **[INSTALL.md](INSTALL.md)** - Guia completo de instalação e solução de problemas
- **[README_BATHYMETRY_GRID.md](README_BATHYMETRY_GRID.md)** - Documentação técnica detalhada
- Comentários no código - Todos os scripts são extensivamente documentados

## 🛠️ Requisitos

### Software

- **Conda** (Anaconda ou Miniconda) - [Download](https://docs.conda.io/en/latest/miniconda.html)
- macOS, Linux ou Windows (via WSL)

### Dependências Python (instaladas automaticamente)

- Python 3.10
- numpy ≥ 1.20
- scipy ≥ 1.7
- xarray ≥ 0.19
- netCDF4 ≥ 1.5
- matplotlib ≥ 3.3 (opcional, para visualização)

### Dados

- Arquivo GEBCO 2025 NetCDF (~7 GB)
- Já incluído no projeto em `gebco_2025_sub_ice_topo/`

## 💡 Exemplos de Uso

### Exemplo 1: Grade de resolução moderada

```bash
./run_pom.sh quick_generate_grid.py \
    --lon-min -60 --lon-max -30 \
    --lat-min -35 --lat-max -5 \
    --spacing 0.25 \
    --output atlantico_sudoeste.asc
```

### Exemplo 2: Grade de alta resolução para área pequena

```bash
./run_pom.sh quick_generate_grid.py \
    --lon-min -50 --lon-max -45 \
    --lat-min -28 --lat-max -23 \
    --spacing 0.1 \
    --output santa_catarina.asc
```

### Exemplo 3: Usar diferentes métodos de interpolação

```python
# Edite create_pom_bathymetry_grid.py

# Para interpolação mais suave (mais lenta)
INTERPOLATION_METHOD = 'cubic'

# Para mais rápida (menos suave)
INTERPOLATION_METHOD = 'nearest'

# Padrão (equilíbrio)
INTERPOLATION_METHOD = 'linear'
```

## 📊 Formato de Saída

O arquivo ASCII gerado tem o seguinte formato:

```
# [Cabeçalho com metadados]
     i      j        lon        lat      depth
     1      1   -60.0000   -35.0000      45.32
     2      1   -59.7500   -35.0000     123.45
     3      1   -59.5000   -35.0000     234.56
   ...    ...        ...        ...        ...
```

Onde:
- **i**: Índice da coluna (1 a n_cols)
- **j**: Índice da linha (1 a n_rows)
- **lon**: Longitude em graus decimais
- **lat**: Latitude em graus decimais
- **depth**: Profundidade em metros (positivo = oceano, 0 = terra)

## 🎯 Casos de Uso

### Regiões Pré-Definidas

O script `quick_generate_grid.py` inclui regiões pré-configuradas:

```bash
# Costa Sul/Sudeste do Brasil
./run_pom.sh quick_generate_grid.py --region brasil_sul

# Costa Nordeste do Brasil
./run_pom.sh quick_generate_grid.py --region brasil_nordeste

# Atlântico Sul-Ocidental
./run_pom.sh quick_generate_grid.py --region atlantico_sw
```

### Customização Avançada

Para processamento customizado, use a classe `BathymetryGridGenerator`:

```python
from create_pom_bathymetry_grid import BathymetryGridGenerator

# Criar gerador
gen = BathymetryGridGenerator("gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc", 
                              spacing=0.25)

# Carregar e processar
gen.load_gebco_data()
gen.define_grid_extent(-60, -30, -35, -5)
gen.interpolate_bathymetry(method='linear')

# Aplicar processamento customizado
import numpy as np
from scipy.ndimage import gaussian_filter

# Suavizar batimetria
gen.depth_grid = gaussian_filter(gen.depth_grid, sigma=1)

# Definir profundidade mínima
gen.depth_grid = np.maximum(gen.depth_grid, 10)

# Exportar
gen.export_to_ascii("grade_customizada.asc")
gen.cleanup()
```

## 🔍 Validação e Qualidade

Após gerar a grade, recomenda-se:

1. ✅ **Inspeção visual** - Verifique a imagem PNG gerada
2. ✅ **Estatísticas** - Confira profundidades mín/máx/média no output
3. ✅ **Teste no POM** - Execute o modelo para verificar estabilidade
4. ✅ **Comparação** - Compare com outras fontes de batimetria se disponível

### Exemplo de output de validação:

```
INTERPOLAÇÃO CONCLUÍDA
==========================================
Pontos oceânicos: 14520 (85.3%)
Pontos terrestres: 2480 (14.7%)
Profundidade máxima: 5432.1 m
Profundidade média (oceano): 2156.8 m
==========================================
```

## ⚡ Desempenho

| Resolução | Área               | Tempo aprox. | Pontos   | Arquivo |
|-----------|--------------------|--------------|----------|---------|
| 1.0°      | Global             | ~10 min      | 64,800   | ~4 MB   |
| 0.5°      | Atlântico Sul      | ~5 min       | 21,600   | ~1.5 MB |
| 0.25°     | Costa brasileira   | ~2 min       | 17,040   | ~1 MB   |
| 0.1°      | Região específica  | ~30 seg      | 12,100   | ~700 KB |

*Tempos em computador moderno (8 GB RAM, SSD)*

## 🐛 Solução de Problemas

### Problema: "conda: command not found"

```bash
# Adicione conda ao PATH
export PATH="$HOME/miniconda3/bin:$PATH"
source ~/.zshrc
```

### Problema: Processo muito lento

```python
# Reduza a área ou aumente o espaçamento
LON_MIN, LON_MAX = -50, -40  # Área menor
GRID_SPACING = 0.5           # Espaçamento maior
INTERPOLATION_METHOD = 'linear'  # Método mais rápido
```

### Problema: Erro de memória

```python
# Trabalhe com áreas menores ou:
# 1. Feche outros programas
# 2. Use espaçamento maior (0.5° ou 1.0°)
# 3. Processe regiões separadamente e combine depois
```

Para mais soluções, consulte [INSTALL.md](INSTALL.md).

## 📝 Citações

Se utilizar este código em publicações científicas, por favor cite:

### Dados GEBCO:
```
GEBCO Compilation Group (2025) GEBCO 2025 Grid
DOI: 10.5285/a29c5465-b138-234d-e053-6c86abc040b9
```

### Modelo POM:
```
Blumberg, A. F., and G. L. Mellor (1987), A description of a 
three-dimensional coastal ocean circulation model, 
Three-Dimensional Coastal Ocean Models, Coastal Estuarine Sci., 
vol. 4, edited by N. S. Heaps, pp. 1-16, AGU, Washington, D.C.
```

## 🤝 Contribuindo

Este projeto foi desenvolvido para uso em pesquisa oceanográfica. Se você:
- Encontrar bugs
- Tiver sugestões de melhorias
- Desenvolver novas funcionalidades

Por favor, documente e compartilhe com a comunidade científica!

## 📜 Licença

Este código é fornecido "como está" para fins de pesquisa científica. Você é livre para modificar e distribuir, mantendo os créditos apropriados.

## 👥 Autores e Contato

**Desenvolvido para:** Projeto POM - Modelagem Oceanográfica  
**Data:** Outubro 2025  
**Versão:** 1.0

Para questões técnicas ou suporte, consulte a documentação ou entre em contato com o desenvolvedor.

## 🔗 Recursos Adicionais

- [GEBCO Website](https://www.gebco.net/)
- [Modelo POM](http://www.ccpo.odu.edu/POMWEB/)
- [Documentação NetCDF](https://www.unidata.ucar.edu/software/netcdf/)
- [Xarray Docs](https://docs.xarray.dev/)
- [Conda User Guide](https://docs.conda.io/)

---

**Última atualização:** Outubro 22, 2025  
**Status:** ✅ Testado e funcional  
**Plataforma:** macOS (compatível com Linux/Windows WSL)
