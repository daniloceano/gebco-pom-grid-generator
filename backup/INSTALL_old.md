# Guia de Instalação - Gerador de Grade Batimétrica POM

## Pré-requisitos

Antes de começar, você precisa ter instalado:

### 1. Anaconda ou Miniconda

**Por que Conda?**
- Gerencia dependências complexas de forma eficiente
- Evita conflitos entre pacotes científicos
- Isola ambientes de diferentes projetos

**Download:**
- Anaconda (completo, ~500 MB): https://www.anaconda.com/download
- Miniconda (mínimo, ~50 MB): https://docs.conda.io/en/latest/miniconda.html

**Verificar instalação:**
```bash
conda --version
```

### 2. Dados GEBCO

Certifique-se de que o arquivo NetCDF do GEBCO está na pasta correta:
```
gebco_2025_sub_ice_topo/GEBCO_2025_sub_ice.nc
```

## Instalação Rápida

### Método 1: Script Automático (Recomendado)

```bash
# Tornar o script executável
chmod +x setup_environment.sh

# Executar instalação
./setup_environment.sh
```

Este script irá:
1. ✓ Verificar se conda está instalado
2. ✓ Criar ambiente conda chamado "pom"
3. ✓ Instalar Python 3.10
4. ✓ Instalar todas as dependências (numpy, scipy, xarray, netCDF4, matplotlib)
5. ✓ Validar a instalação

### Método 2: Arquivo de Ambiente Conda

```bash
# Criar ambiente a partir do arquivo YAML
conda env create -f environment.yml

# Ativar ambiente
conda activate pom

# Verificar instalação
python test_bathymetry_generator.py
```

### Método 3: Manual

```bash
# Criar ambiente
conda create -n pom python=3.10 -y

# Ativar ambiente
conda activate pom

# Instalar dependências via conda-forge
conda install -c conda-forge numpy scipy xarray netcdf4 matplotlib -y

# Ou via pip
pip install -r requirements.txt

# Testar instalação
python test_bathymetry_generator.py
```

## Uso do Ambiente

### Ativar o Ambiente

Sempre que for trabalhar no projeto:

```bash
conda activate pom
```

Você verá `(pom)` no início do prompt do terminal.

### Executar Scripts

#### Opção 1: Com ambiente ativado manualmente

```bash
conda activate pom
python create_pom_bathymetry_grid.py
```

#### Opção 2: Usar script wrapper (automatiza ativação)

```bash
# Tornar executável
chmod +x run_pom.sh

# Executar qualquer script
./run_pom.sh create_pom_bathymetry_grid.py
./run_pom.sh quick_generate_grid.py --help
./run_pom.sh test_bathymetry_generator.py
```

### Desativar o Ambiente

Quando terminar de trabalhar:

```bash
conda deactivate
```

## Verificação da Instalação

Execute o script de teste para verificar se tudo está funcionando:

```bash
conda activate pom
python test_bathymetry_generator.py
```

Saída esperada:
```
======================================================================
 TESTE 1: Verificação de Dependências
======================================================================

Módulos obrigatórios:
  ✓ numpy           1.24.3     - Manipulação de arrays numéricos
  ✓ scipy           1.11.2     - Interpolação científica
  ✓ xarray          2023.8.0   - Leitura de dados NetCDF
  ✓ netCDF4         1.6.4      - Suporte NetCDF

Módulos opcionais:
  ✓ matplotlib      3.7.2      - Visualização de dados

✓ Todas as dependências obrigatórias estão instaladas!

[... outros testes ...]

======================================================================
 ✓ TODOS OS TESTES PASSARAM!
======================================================================
```

## Solução de Problemas

### Erro: "conda: command not found"

**Problema:** Conda não está no PATH

**Solução:**
```bash
# Adicionar conda ao PATH (ajuste o caminho conforme sua instalação)
export PATH="$HOME/anaconda3/bin:$PATH"

# Ou para Miniconda
export PATH="$HOME/miniconda3/bin:$PATH"

# Para tornar permanente, adicione ao ~/.zshrc ou ~/.bashrc
echo 'export PATH="$HOME/anaconda3/bin:$PATH"' >> ~/.zshrc
source ~/.zshrc
```

### Erro: "environment already exists"

**Problema:** Ambiente "pom" já existe

**Solução 1:** Remover e recriar
```bash
conda env remove -n pom
./setup_environment.sh
```

**Solução 2:** Atualizar ambiente existente
```bash
conda activate pom
conda env update -f environment.yml --prune
```

### Erro: "Solving environment: failed"

**Problema:** Conflito de dependências

**Solução:**
```bash
# Limpar cache do conda
conda clean --all

# Tentar criar ambiente novamente
./setup_environment.sh

# Se ainda falhar, usar pip
conda create -n pom python=3.10 -y
conda activate pom
pip install -r requirements.txt
```

### Erro ao carregar arquivo GEBCO

**Problema:** Arquivo NetCDF muito grande, pouca memória

**Solução:**
- Use uma região menor (LON/LAT mais restrita)
- Aumente o espaçamento da grade
- Feche outros programas para liberar memória
- Use um computador com mais RAM

### Script muito lento

**Problema:** Interpolação demora muito

**Solução:**
```python
# No script, use:
INTERPOLATION_METHOD = 'linear'  # Mais rápido que 'cubic'
GRID_SPACING = 0.5  # Maior = mais rápido

# Ou reduza a área:
LON_MIN, LON_MAX = -50.0, -40.0  # Área menor
LAT_MIN, LAT_MAX = -30.0, -20.0
```

## Atualizando o Ambiente

### Atualizar pacotes

```bash
conda activate pom

# Atualizar todos os pacotes
conda update --all

# Ou atualizar pacote específico
conda update numpy
```

### Adicionar novos pacotes

```bash
conda activate pom

# Via conda
conda install nome-do-pacote

# Via pip
pip install nome-do-pacote
```

### Exportar ambiente (para compartilhar)

```bash
conda activate pom

# Exportar para arquivo
conda env export > environment_export.yml

# Outros usuários podem recriar com:
# conda env create -f environment_export.yml
```

## Desinstalação

Para remover completamente o ambiente:

```bash
# Desativar se estiver ativo
conda deactivate

# Remover ambiente
conda env remove -n pom

# Confirmar remoção
conda env list
```

## Comandos Úteis

```bash
# Listar todos os ambientes conda
conda env list

# Ver pacotes instalados no ambiente
conda activate pom
conda list

# Informações sobre o ambiente
conda info

# Limpar cache (liberar espaço)
conda clean --all

# Criar atalho para ativação rápida (adicione ao ~/.zshrc)
alias pom="conda activate pom"
```

## Próximos Passos

Após a instalação bem-sucedida:

1. ✓ Leia o [README_BATHYMETRY_GRID.md](README_BATHYMETRY_GRID.md)
2. ✓ Configure os parâmetros em `create_pom_bathymetry_grid.py`
3. ✓ Execute: `python create_pom_bathymetry_grid.py`
4. ✓ Verifique a saída e visualização
5. ✓ Use a grade no modelo POM

## Suporte

Se encontrar problemas:

1. Execute `python test_bathymetry_generator.py` para diagnóstico
2. Verifique se o ambiente está ativado: `conda info --envs`
3. Consulte a documentação do conda: https://docs.conda.io/
4. Entre em contato com o desenvolvedor

---

**Última atualização:** Outubro 2025  
**Versão:** 1.0
