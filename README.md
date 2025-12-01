# Ocean Grid Tools

Ferramentas para geração de grades retangulares para modelos oceânicos.

## 📋 Sobre

Este é um conjunto de ferramentas (toolkit) para auxiliar na criação e manipulação de grades retangulares utilizadas em modelos oceânicos numéricos. O projeto é modular, permitindo adicionar novas funcionalidades de forma independente.

## 🗂️ Ferramentas Disponíveis

### 1. Interpolação de Dados GEBCO

Interpola dados batimétricos globais do GEBCO para criar grades regulares customizadas.

**Localização**: `tools/gebco_interpolation/`

**Características**:
- ✨ Interpolação de alta qualidade dos dados batimétricos
- 🚀 Processamento paralelo para grandes áreas
- 📐 Espaçamentos diferentes para dx e dy
- 🖱️ Editor interativo para correções manuais
- 📝 Formato ASCII simples (5 colunas: i, j, lon, lat, depth)

**Uso rápido**:
```bash
cd tools/gebco_interpolation/scripts
python generate_grid.py
```

👉 **[Ver documentação completa](tools/gebco_interpolation/README.md)**

---

### 2. [Futuras Ferramentas]

Espaço reservado para novas funcionalidades de geração de grades.

## 🚀 Início Rápido

### 1. Instalação do Ambiente

```bash
# Criar ambiente conda com todas as dependências
conda env create -f environment.yml
conda activate pom
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
│   └── gebco_interpolation/      # Interpolação de dados GEBCO
│       ├── README.md             # Doc específica desta ferramenta
│       ├── src/                  # Código-fonte
│       ├── scripts/              # Scripts executáveis
│       └── examples/             # Exemplos de uso
│
├── docs/                         # Documentação geral
│   ├── INSTALL.md
│   ├── QUICK_REFERENCE.md
│   └── ...
│
├── gebco_2025_sub_ice_topo/      # Dados GEBCO (não versionado)
├── output/                       # Arquivos gerados
│
├── environment.yml               # Ambiente conda
├── requirements.txt              # Dependências Python
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
