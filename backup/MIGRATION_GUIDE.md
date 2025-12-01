# Guia de Transição - Nova Estrutura do Projeto

## 🔄 Mudanças na Estrutura

O projeto foi reorganizado de **gerador GEBCO-POM** para **Ocean Grid Tools** - um pacote modular de ferramentas para geração de grades oceânicas.

## 📂 Mapeamento de Diretórios

### Antes (estrutura antiga)
```
POM/
├── src/                          # Código-fonte
│   └── bathymetry_generator.py
├── scripts/                      # Scripts executáveis
│   ├── generate_grid.py
│   ├── edit_grid_interactive.py
│   └── quick_generate.py
├── examples/                     # Exemplos
└── docs/                         # Documentação
```

### Agora (nova estrutura)
```
ocean-grid-tools/
├── tools/                        # Ferramentas modularizadas
│   └── gebco_interpolation/      # ← Funcionalidade GEBCO
│       ├── src/                  # ← Movido de src/
│       ├── scripts/              # ← Movido de scripts/
│       ├── examples/             # ← Movido de examples/
│       └── README.md             # ← Documentação específica
├── docs/                         # Documentação geral
└── README.md                     # Novo README principal
```

## 🔀 Como Usar Agora

### Scripts Antigos → Novos Caminhos

| Script Antigo | Novo Caminho |
|---------------|--------------|
| `scripts/generate_grid.py` | `tools/gebco_interpolation/scripts/generate_grid.py` |
| `scripts/edit_grid_interactive.py` | `tools/gebco_interpolation/scripts/edit_grid_interactive.py` |
| `scripts/quick_generate.py` | `tools/gebco_interpolation/scripts/quick_generate.py` |

### Comandos Antigos → Novos Comandos

| Comando Antigo | Novo Comando |
|----------------|--------------|
| `./scripts/pom.sh setup` | `./ocean-tools.sh env` |
| `./scripts/pom.sh run` | `cd tools/gebco_interpolation/scripts && python generate_grid.py` |
| `./scripts/pom.sh edit <file>` | `./ocean-tools.sh edit <file>` |

### Novo Script Principal

O novo script `ocean-tools.sh` substitui `scripts/pom.sh`:

```bash
./ocean-tools.sh env        # Configurar ambiente
./ocean-tools.sh gebco      # Acessar ferramenta GEBCO
./ocean-tools.sh edit <file> # Editar grade
./ocean-tools.sh help       # Ajuda
```

## 📚 Documentação Atualizada

### Documentos Principais (atualizados)

- ✅ **README.md** - Visão geral do pacote de ferramentas
- ✅ **docs/INSTALL.md** - Instalação com nova estrutura
- ✅ **docs/QUICK_REFERENCE.md** - Referência rápida atualizada
- ✅ **docs/INDEX.md** - Navegação atualizada
- ✅ **tools/gebco_interpolation/README.md** - Documentação específica GEBCO

### Documentos Antigos (preservados)

Os documentos antigos foram renomeados com sufixo `_old`:
- `README_old.md`
- `docs/INSTALL_old.md`
- `docs/QUICK_REFERENCE_old.md`
- `docs/INDEX_old.md`

### Documentos para Atualização Futura

- ⚠️ `docs/README_BATHYMETRY_GRID.md` - Conteúdo duplicado, considerar remover
- ⚠️ `docs/PROJECT_SUMMARY.md` - Desatualizado
- ⚠️ `docs/INTERACTIVE_EDITOR.md` - Conteúdo integrado em `gebco_interpolation/README.md`

## 🎯 Workflow Atualizado

### Workflow Antigo
```bash
# 1. Setup
./scripts/pom.sh setup

# 2. Editar configurações
nano scripts/generate_grid.py

# 3. Executar
./scripts/pom.sh run

# 4. Editar
./scripts/pom.sh edit output/grade.asc
```

### Workflow Novo
```bash
# 1. Setup (uma vez)
./ocean-tools.sh env
conda activate pom

# 2. Entrar no módulo GEBCO
cd tools/gebco_interpolation/scripts

# 3. Editar configurações
nano generate_grid.py

# 4. Executar
python generate_grid.py

# 5. Editar interativamente (da raiz do projeto)
cd ../../..
./ocean-tools.sh edit output/pom_bathymetry_grid.asc
```

## 🔍 O Que Mudou

### Estrutura
✅ Código GEBCO movido para `tools/gebco_interpolation/`
✅ Cada ferramenta tem seu próprio README
✅ Estrutura modular permite adicionar novas ferramentas
✅ Backup da estrutura antiga em `old_structure/`

### Documentação
✅ README principal focado no pacote de ferramentas
✅ Documentação específica por ferramenta
✅ Guias mais sucintos e práticos
✅ Instruções para Copilot em `.copilot-instructions.md`

### Scripts
✅ Novo `ocean-tools.sh` como script mestre
✅ Scripts GEBCO mantidos em `tools/gebco_interpolation/scripts/`
✅ `pom.sh` antigo preservado em `scripts/pom.sh` (backup)

## 🚀 Benefícios da Nova Estrutura

1. **Modularidade**: Fácil adicionar novas ferramentas em `tools/`
2. **Clareza**: Cada ferramenta tem documentação própria
3. **Escalabilidade**: Estrutura preparada para crescimento
4. **Manutenção**: Código organizado por funcionalidade
5. **Didática**: Documentação focada em exemplos práticos

## ➕ Como Adicionar Nova Ferramenta

```bash
# 1. Criar estrutura
mkdir -p tools/nova_ferramenta/{src,scripts,examples}

# 2. Adicionar código
# tools/nova_ferramenta/src/...
# tools/nova_ferramenta/scripts/...

# 3. Criar README
# tools/nova_ferramenta/README.md
#   - O que faz
#   - Como usar
#   - Parâmetros
#   - Exemplos

# 4. Atualizar README principal
# Adicionar em README.md seção "Ferramentas Disponíveis"

# 5. Documentar uso
# Adicionar comandos em ocean-tools.sh se necessário
```

## 📝 Checklist de Migração

Se você tinha trabalhos em andamento:

- [ ] Atualizar imports em scripts personalizados
  ```python
  # Antigo
  sys.path.insert(0, '../src')
  
  # Novo
  sys.path.insert(0, '../tools/gebco_interpolation/src')
  ```

- [ ] Atualizar caminhos de arquivos
  ```python
  # Antigo
  GEBCO_FILE = "../gebco_2025_sub_ice_topo/..."
  OUTPUT_DIR = "../output"
  
  # Novo (de tools/gebco_interpolation/scripts/)
  GEBCO_FILE = "../../../gebco_2025_sub_ice_topo/..."
  OUTPUT_DIR = "../../../output"
  ```

- [ ] Ler nova documentação
  - [ ] README.md principal
  - [ ] docs/QUICK_REFERENCE.md
  - [ ] tools/gebco_interpolation/README.md

- [ ] Testar workflow
  ```bash
  cd tools/gebco_interpolation/scripts
  python generate_grid.py
  ```

## 🆘 Problemas Comuns

### "ModuleNotFoundError: No module named 'bathymetry_generator'"

**Causa**: Executando do diretório errado.

**Solução**:
```bash
cd tools/gebco_interpolation/scripts
python generate_grid.py
```

### "FileNotFoundError: GEBCO file not found"

**Causa**: Caminhos relativos mudaram.

**Solução**: Editar `generate_grid.py`:
```python
GEBCO_FILE = "../../../gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc"
```

### "ocean-tools.sh: command not found"

**Solução**:
```bash
chmod +x ocean-tools.sh
./ocean-tools.sh help
```

## 📞 Referências Rápidas

### Documentação Principal
- **README.md** - Início aqui
- **docs/INSTALL.md** - Instalação
- **docs/QUICK_REFERENCE.md** - Comandos rápidos

### Ferramenta GEBCO
- **tools/gebco_interpolation/README.md** - Documentação completa
- **tools/gebco_interpolation/scripts/generate_grid.py** - Script principal
- **tools/gebco_interpolation/examples/** - Exemplos de uso

### Backup da Estrutura Antiga
- **old_structure/** - Backup completo da estrutura anterior
- **README_old.md** - README antigo
- **docs/*_old.md** - Documentação antiga preservada
