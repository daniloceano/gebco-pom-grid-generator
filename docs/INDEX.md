# 🗂️ Índice da Documentação - Ocean Grid Tools

## 📖 Para Novos Usuários

Leia nesta ordem:

1. **[README.md](../README.md)** - Visão geral do projeto
2. **[INSTALL.md](INSTALL.md)** - Instalação do ambiente
3. **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** - Comandos práticos

## 🎯 Uso Rápido

```bash
# 1. Instalar (uma vez)
conda env create -f environment.yml
conda activate pom

# 2. Usar ferramenta GEBCO
cd tools/gebco_interpolation/scripts
python generate_grid.py

# 3. Editar grade
python edit_grid_interactive.py ../../../output/pom_bathymetry_grid.asc
```

## 📚 Documentação

### Documentos Gerais

| Arquivo | Descrição | Quando Ler |
|---------|-----------|------------|
| **[README.md](../README.md)** | Visão geral do pacote de ferramentas | ⭐ Primeiro contato |
| **[INSTALL.md](INSTALL.md)** | Guia de instalação detalhado | ⭐ Na instalação |
| **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** | Referência rápida de uso | ⭐ Uso diário |
| **[INDEX.md](INDEX.md)** | Este arquivo - Navegação | Para encontrar documentos |

### Documentação por Ferramenta

Cada ferramenta tem sua própria documentação em seu diretório:

| Ferramenta | Localização | README |
|------------|-------------|--------|
| **Interpolação GEBCO** | `tools/gebco_interpolation/` | [README](../tools/gebco_interpolation/README.md) |
| *Futuras ferramentas* | `tools/[nome]/` | `tools/[nome]/README.md` |

## 🔧 Estrutura do Projeto

```
ocean-grid-tools/
├── docs/                         # ← Você está aqui
│   ├── INDEX.md                  # Este arquivo
│   ├── INSTALL.md                # Instalação
│   ├── QUICK_REFERENCE.md        # Referência rápida
│   └── ...                       # Outros docs gerais
│
├── tools/                        # Ferramentas disponíveis
│   └── gebco_interpolation/      # Interpolação GEBCO
│       ├── README.md             # Doc específica
│       ├── src/                  # Código-fonte
│       ├── scripts/              # Scripts executáveis
│       └── examples/             # Exemplos
│
├── README.md                     # Doc principal do projeto
└── environment.yml               # Ambiente conda
```

## 📖 Documentos Antigos

Os documentos abaixo são da versão anterior do projeto e serão atualizados:

| Arquivo | Status | Nota |
|---------|--------|------|
| `README_BATHYMETRY_GRID.md` | ⚠️ Desatualizado | Ver novo: `tools/gebco_interpolation/README.md` |
| `PROJECT_SUMMARY.md` | ⚠️ Desatualizado | Ver novo: `README.md` principal |
| `INTERACTIVE_EDITOR.md` | ⚠️ Desatualizado | Conteúdo integrado em `gebco_interpolation/README.md` |

## 🗺️ Navegação Rápida

### Quero instalar o projeto
→ **[INSTALL.md](INSTALL.md)**

### Quero gerar uma grade batimétrica
→ **[tools/gebco_interpolation/README.md](../tools/gebco_interpolation/README.md)**

### Quero editar uma grade manualmente
→ **[QUICK_REFERENCE.md](QUICK_REFERENCE.md)** (seção "Editar Grade")

### Quero entender a estrutura do projeto
→ **[README.md](../README.md)** (seção "Estrutura do Projeto")

### Quero adicionar uma nova ferramenta
→ **[README.md](../README.md)** (seção "Como Adicionar Nova Ferramenta")

### Preciso de exemplos de código
→ **`tools/gebco_interpolation/examples/`**

## 📝 Convenções

### Formato de Grade
- **5 colunas**: i, j, lon, lat, depth
- **Profundidade**: depth > 0 = oceano, depth = 0 = terra
- **Arquivo**: ASCII simples

### Coordenadas
- **Longitude**: valores negativos para oeste
- **Latitude**: valores negativos para sul
- **Exemplo**: Brasil está em (-60, -30) lon, (-35, -5) lat

### Espaçamento
- **Unidade**: graus decimais
- **Padrão**: 0.25° (≈ 28 km no equador)
- **Range típico**: 0.05° a 1.0°

## 🆘 Ajuda Rápida

**Problema: Não sei por onde começar**
→ Leia [README.md](../README.md), depois [INSTALL.md](INSTALL.md)

**Problema: Instalação falhou**
→ Ver [INSTALL.md](INSTALL.md) seção "Troubleshooting"

**Problema: Grade gerada está errada**
→ Use editor interativo (ver [QUICK_REFERENCE.md](QUICK_REFERENCE.md))

**Problema: Processamento muito lento**
→ Ative paralelização em `generate_grid.py`: `USE_PARALLEL = True`

**Problema: Erro de memória**
→ Aumente `GRID_SPACING` ou reduza a área

## 📧 Notas

Este é um **projeto pessoal** para auxiliar pesquisa em oceanografia. A documentação foca em ser **prática e didática**, não em formalidades de projetos open-source.
