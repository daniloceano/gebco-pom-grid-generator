# GEBCO to POM Grid Generator

Generator de grades batimétricas do GEBCO para o modelo POM (Princeton Ocean Model).

## 📋 Sobre

Este projeto fornece ferramentas para criar grades batimétricas interpoladas a partir dos dados globais do GEBCO para uso no modelo POM. O sistema inclui:

- ✨ Interpolação de alta qualidade dos dados batimétricos
- 🚀 Processamento paralelo para melhor performance
- 📐 Grade regular customizável com espaçamento definido pelo usuário
- 📝 Formato ASCII compatível com POM
- 🖼️ Visualização automática da batimetria
- 🔧 Ambiente conda isolado

## 🗂️ Estrutura do Projeto

```
POM/
├── src/                          # Código-fonte principal
│   ├── __init__.py
│   └── bathymetry_generator.py   # Classe principal (paralelizada)
│
├── scripts/                      # Scripts executáveis
│   ├── generate_grid.py          # Script principal configurável
│   ├── quick_generate.py         # Interface CLI rápida
│   ├── setup_environment.sh      # Instalação do ambiente conda
│   ├── run_pom.sh                # Wrapper de execução
│   └── pom.sh                    # Script mestre
│
├── examples/                     # Exemplos de uso
│   ├── example_basic.py          # Uso básico
│   └── example_advanced.py       # Uso avançado com customizações
│
├── tests/                        # Testes e validação
│   └── test_bathymetry_generator.py
│
├── docs/                         # Documentação completa
│   ├── README.md                 # Documentação principal
│   ├── INSTALL.md                # Guia de instalação
│   ├── QUICK_REFERENCE.md        # Referência rápida
│   └── ...
│
├── output/                       # Diretório para arquivos gerados
│
├── gebco_2025_sub_ice_topo/      # Dados do GEBCO
│   └── GEBCO_2025_sub_ice.nc
│
├── environment.yml               # Configuração do ambiente conda
├── requirements.txt              # Dependências Python
├── .gitignore                    # Arquivos ignorados pelo git
└── LICENSE                       # Licença do projeto
```

## 🚀 Início Rápido

### 1. Instalação

```bash
# Configurar ambiente conda
cd scripts
./setup_environment.sh

# Ou manualmente
conda env create -f environment.yml
conda activate pom
```

### 2. Uso Básico

```bash
# Opção A: Script rápido com CLI
cd scripts
./pom.sh quick --region brasil_sul

# Opção B: Script principal (edite parâmetros no arquivo)
./pom.sh run

# Opção C: Python direto
conda activate pom
python quick_generate.py --help
```

### 3. Exemplos

```bash
# Ver exemplos prontos
cd examples
python example_basic.py
python example_advanced.py
```

## 📖 Documentação

A documentação completa está em `docs/`:

- **[INSTALL.md](docs/INSTALL.md)** - Guia detalhado de instalação
- **[QUICK_REFERENCE.md](docs/QUICK_REFERENCE.md)** - Referência rápida de comandos
- **[README.md](docs/README.md)** - Documentação técnica completa

## 🛠️ Requisitos

- **Conda** (Anaconda ou Miniconda)
- **Python 3.10+**
- **Dependências:** numpy, scipy, xarray, netCDF4, matplotlib

## 💡 Exemplos de Uso

### Interface CLI

```bash
# Região pré-definida
python scripts/quick_generate.py --region brasil_sul

# Região customizada
python scripts/quick_generate.py \
    --lon-min -60 --lon-max -30 \
    --lat-min -35 --lat-max -5 \
    --spacing 0.25

# Com paralelização customizada
python scripts/quick_generate.py \
    --region atlantico_sw \
    --workers 4 \
    --method cubic
```

### API Python

```python
from src.bathymetry_generator import BathymetryGridGenerator

# Criar gerador
gen = BathymetryGridGenerator("gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc", 
                              spacing=0.25, n_workers=4)

# Processar
gen.load_gebco_data()
gen.define_grid_extent(-60, -30, -35, -5)
gen.interpolate_bathymetry(method='linear', parallel=True)
gen.export_to_ascii("output/my_grid.asc")
gen.plot_bathymetry("output/my_grid.png")
gen.cleanup()
```

## 📊 Formato de Saída

Arquivo ASCII com 5 colunas:

```
#  i      j        lon        lat      depth
   1      1   -60.0000   -35.0000      45.32
   2      1   -59.7500   -35.0000     123.45
   ...
```

- **i**: índice da coluna (1 a n_cols)
- **j**: índice da linha (1 a n_rows)  
- **lon**: longitude em graus decimais
- **lat**: latitude em graus decimais
- **depth**: profundidade em metros (positivo = oceano)

## 🔬 Características Técnicas

### Processamento Paralelo

A versão 2.0 inclui suporte a processamento paralelo:

- Divisão automática do trabalho entre múltiplos cores
- Speedup típico de 2-4x em máquinas multi-core
- Configurável via parâmetro `n_workers`

### Métodos de Interpolação

- **linear**: Balanço entre velocidade e qualidade (padrão)
- **nearest**: Mais rápido, menos suave
- **cubic**: Melhor qualidade, mais lento

## 🧪 Testes

```bash
# Executar suite de testes
cd scripts
./pom.sh test

# Ou diretamente
conda activate pom
python tests/test_bathymetry_generator.py
```

## 📝 Citação

Se utilizar este código em publicações científicas, por favor cite:

**Dados GEBCO:**
```
GEBCO Compilation Group (2025) GEBCO 2025 Grid
```

## 🤝 Contribuindo

Contribuições são bem-vindas! Por favor:

1. Fork o projeto
2. Crie uma branch para sua feature
3. Commit suas mudanças
4. Push para a branch
5. Abra um Pull Request

## 📜 Licença

Este projeto é fornecido sob a licença MIT. Veja o arquivo [LICENSE](LICENSE) para detalhes.

## 🔗 Links Úteis

- [GEBCO](https://www.gebco.net/)
- [Modelo POM](http://www.ccpo.odu.edu/POMWEB/)
- [Documentação Xarray](https://docs.xarray.dev/)

## 📞 Suporte

Para questões ou problemas:

1. Consulte a [documentação](docs/)
2. Execute `./scripts/pom.sh test` para diagnóstico
3. Abra uma issue no GitHub

---

**Versão:** 2.0.0  
**Status:** Ativo  
**Última atualização:** Outubro 2025
