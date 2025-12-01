# RecOM - Rectangular Ocean Mesh Tools

Ferramentas para geração de grades retangulares para modelos oceânicos.

## 📋 Sobre

RecOM (**Rec**tangular **O**cean **M**esh Tools) é um conjunto de ferramentas (toolkit) para auxiliar na criação e manipulação de grades retangulares utilizadas em modelos oceânicos numéricos. O projeto é modular, permitindo adicionar novas funcionalidades de forma independente.

## 🗂️ Ferramentas Disponíveis

### 1. Interpolação de Dados GEBCO

Interpola dados batimétricos globais do GEBCO para criar grades regulares customizadas.

**Localização**: `tools/gebco_interpolation/`

**Características**:
- ✨ Interpolação de alta qualidade dos dados batimétricos
- 🚀 Processamento paralelo para grandes áreas
- 📐 Espaçamentos diferentes para dx e dy
-  Formato ASCII simples (5 colunas: i, j, lon, lat, depth)

**Uso rápido**:
```bash
cd tools/gebco_interpolation/scripts
python generate_grid.py
```

👉 **[Ver documentação completa](tools/gebco_interpolation/README.md)**

---

### 2. Editor de Grades

Editor visual interativo para manipulação manual de grades oceânicas.

**Localização**: `tools/grid_editor/`

**Características**:
- 🗺️ Linha de costa real (Cartopy/Natural Earth)
- 📊 Contornos batimétricos com labels
- 🎨 Terra em cinza, oceano em azul
- 🖱️ Click para alternar terra ↔ água
- 🔍 Zoom interativo
- 🧮 Interpolação automática (IDW)

**Uso rápido**:
```bash
./ocean_mesh_tools.sh edit output/pom_bathymetry_grid.asc
```

👉 **[Ver documentação completa](tools/grid_editor/README.md)**

---

### 3. Extração de Máscaras de Reanálises

Extrai máscaras terra/oceano de dados de reanálises oceânicas para aplicar em grades customizadas.

**Localização**: `tools/reanalysis_mask/`

**Características**:
- 🌊 Identifica oceano vs terra a partir de dados válidos
- 📉 Degradação de resolução com agregação configurável
-  Suporta BRAN2020, GLORYS, HYCOM e outros
- 🎯 Alinhamento preciso de grades
- 💾 Gera novas grades com sufixo indicando máscara aplicada

**Uso rápido**:
```bash
# Extrair máscara
python tools/reanalysis_mask/scripts/extract_mask.py /path/to/reanalysis.nc \
    --lon-range -60 -30 --lat-range -35 -5 --target-res 0.25 0.25

# Aplicar máscara à grade
python tools/reanalysis_mask/scripts/apply_mask.py \
    output/rectangular_grid_*.asc output/mask_ocean_*.asc
```

👉 **[Ver documentação completa](tools/reanalysis_mask/README.md)**

---

### 4. [Futuras Ferramentas]

Espaço reservado para novas funcionalidades de geração de grades.

## 🚀 Início Rápido

### 1. Instalação do Ambiente

```bash
# Criar ambiente conda com todas as dependências
conda env create -f environment.yml
conda activate ocean_mesh_tools
```

### 2. Download dos Dados GEBCO

Faça download em: https://www.gebco.net/data_and_products/gridded_bathymetry_data/

Coloque o arquivo NetCDF em `gebco_2025_sub_ice_topo/`

### 3. Usar uma Ferramenta

Cada ferramenta tem seu próprio diretório em `tools/` com README específico:

```bash
# Exemplo: Interpolação GEBCO
cd tools/gebco_interpolation
cat README.md  # Ler instruções
cd scripts
python generate_grid.py
```

## 📚 Documentação

- **Documentação geral**: [`docs/`](docs/)
- **Documentação por ferramenta**: `tools/[nome_ferramenta]/README.md`

### Documentos principais

| Documento | Descrição |
|-----------|-----------|
| [INSTALL.md](docs/INSTALL.md) | Guia detalhado de instalação |
| [QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md) | Referência rápida de comandos |

## 🔧 Estrutura do Projeto

```
ocean-grid-tools/
├── tools/                        # Ferramentas disponíveis
│   ├── gebco_interpolation/      # Interpolação de dados GEBCO
│   ├── grid_editor/              # Editor interativo de grades
│   └── reanalysis_mask/          # Extração de máscaras de reanálises
│       ├── README.md             # Doc específica desta ferramenta
│       ├── src/                  # Código-fonte
│       ├── scripts/              # Scripts executáveis
│       ├── examples/             # Exemplos de uso
│       └── tests/                # Testes unitários
│
├── docs/                         # Documentação geral
│   ├── INSTALL.md
│   ├── QUICK_REFERENCE.md
│   └── ...
│
├── tests/                        # Testes do projeto
├── gebco_2025_sub_ice_topo/      # Dados GEBCO (não versionado)
├── output/                       # Arquivos gerados
│
├── environment.yml               # Ambiente conda
├── requirements.txt              # Dependências Python
├── ocean_mesh_tools.sh           # Script CLI principal
└── README.md                     # Este arquivo
```

## 🎯 Filosofia do Projeto

Este é um projeto **modular** e **pragmático**:

- ✅ Cada ferramenta é independente
- ✅ Documentação objetiva e prática
- ✅ Exemplos didáticos para usuários com Python básico
- ✅ Foco em funcionalidade, não em formalidades

## 🛠️ Tecnologias

- **Python 3.8+**
- **numpy** - Computação numérica
- **scipy** - Interpolação
- **xarray** - Manipulação de dados NetCDF
- **netCDF4** - Leitura de dados GEBCO
- **matplotlib** - Visualização e editor interativo

## 📝 Como Adicionar Nova Ferramenta

1. Criar diretório em `tools/nome_da_ferramenta/`
2. Seguir estrutura padrão: `src/`, `scripts/`, `examples/`
3. Criar README.md sucinto explicando:
   - O que faz
   - Como usar
   - Parâmetros principais
   - Exemplos práticos
4. Atualizar este README principal
5. Adicionar ao environment.yml se houver novas dependências

## 📄 Licença

MIT License - veja [LICENSE](LICENSE)

## 👤 Autor

Projeto pessoal desenvolvido para auxiliar na geração de grades para modelagem oceânica.

## 🔗 Links Úteis

- [GEBCO](https://www.gebco.net/) - General Bathymetric Chart of the Oceans
- [Princeton Ocean Model](https://www.ccpo.odu.edu/~klinck/Reprints/PDF/mellor2004.pdf) - POM Reference
