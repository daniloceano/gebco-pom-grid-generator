# Editor Interativo de Grade Batimétrica

## Visão Geral

O editor interativo permite ajustar manualmente a grade batimétrica após a geração automática. Isso é especialmente útil para:

- **Corrigir instabilidades**: Algumas configurações de batimetria podem causar problemas numéricos no modelo POM
- **Ajustar linha de costa**: Fechar canais estreitos ou abrir passagens
- **Modificar ilhas**: Adicionar ou remover pequenas ilhas
- **Refinar detalhes**: Ajustar manualmente pontos específicos

## Características

### Interface Gráfica Interativa

- 🖱️ **Click para editar**: Clique em qualquer ponto para alternar entre terra e água
- 🔍 **Zoom dinâmico**: Use scroll ou teclas +/- para zoom in/out
- 🗺️ **Visualização completa**:
  - Batimetria com cores (shaded relief)
  - Linha de costa em vermelho
  - Grade de células do modelo
- 💾 **Salvamento automático**: Cria backups e versões com timestamp

### Controles

| Ação | Controle |
|------|----------|
| Alternar terra/água | Click esquerdo do mouse |
| Zoom in | `+` ou scroll up |
| Zoom out | `-` ou scroll down |
| Reset zoom | `r` |
| Toggle grade | `g` |
| Toggle linha de costa | `c` |
| Salvar modificações | `s` |
| Sair | `q` ou fechar janela |

## Uso

### Comando Básico

```bash
# Via pom.sh (recomendado)
./scripts/pom.sh edit ../output/pom_bathymetry_grid.asc

# Diretamente
python scripts/edit_grid_interactive.py ../output/pom_bathymetry_grid.asc
```

### Workflow Típico

1. **Gerar grade inicial**:
   ```bash
   ./scripts/pom.sh run
   # ou
   ./scripts/pom.sh quick --region brasil_sul
   ```

2. **Abrir editor**:
   ```bash
   ./scripts/pom.sh edit ../output/pom_bathymetry_grid.asc
   ```

3. **Fazer ajustes**:
   - Use scroll para dar zoom na região problemática
   - Clique nos pontos que precisam ser modificados
   - Use `g` para visualizar a grade se necessário

4. **Salvar**:
   - Pressione `s` para salvar
   - O editor cria:
     - `pom_bathymetry_grid_backup.asc` (primeira vez)
     - `pom_bathymetry_grid_vYYYYMMDD_HHMMSS.asc` (versão com timestamp)
     - `pom_bathymetry_grid.asc` (arquivo principal atualizado)

5. **Sair**:
   - Pressione `q` ou feche a janela
   - Se houver modificações não salvas, será perguntado

## Exemplos de Uso

### Exemplo 1: Fechar um canal estreito

```bash
# Abrir editor
./scripts/pom.sh edit ../output/pom_bathymetry_grid.asc

# No editor:
# 1. Zoom in na região do canal
# 2. Click nos pontos de água para converter em terra
# 3. Pressione 's' para salvar
# 4. Pressione 'q' para sair
```

### Exemplo 2: Remover ilha pequena

```bash
./scripts/pom.sh edit ../output/pom_bathymetry_grid.asc

# No editor:
# 1. Localize a ilha (pontos verdes)
# 2. Click nos pontos de terra para converter em água
# 3. Salvar e sair
```

### Exemplo 3: Ajuste fino da costa

```bash
./scripts/pom.sh edit ../output/pom_bathymetry_grid.asc

# Use 'c' para visualizar melhor a linha de costa
# Use 'g' para ver a grade de células
# Ajuste pontos próximos à costa conforme necessário
```

## Formato dos Arquivos

### Arquivo Original
```
# Grade batimétrica POM
ncols         121
nrows         81
xllcorner     -60.0
yllcorner     -35.0
dx            0.25
dy            0.25
NODATA_value  -9999
   -123.456    -234.567 ...
   ...
```

### Arquivo com Modificações
O editor preserva completamente o formato, adicionando apenas um comentário no cabeçalho:
```
# Grade batimétrica editada - 2025-10-28 14:30:45
ncols         121
nrows         81
...
```

## Segurança

O editor implementa várias proteções:

1. **Backup automático**: Cria `.../pom_bathymetry_grid_backup.asc` antes da primeira edição
2. **Versionamento**: Cada salvamento cria uma cópia com timestamp
3. **Confirmação de saída**: Pergunta antes de sair com modificações não salvas
4. **Validação**: Mantém integridade do formato ASCII

## Dicas e Boas Práticas

### 1. Trabalhe em Zoom
- Sempre dê zoom na região antes de fazer modificações
- Isso garante precisão nos clicks

### 2. Use a Grade
- Ative a visualização da grade (`g`) para ver células individuais
- Útil para ajustes precisos

### 3. Salve Frequentemente
- Pressione `s` após cada conjunto de modificações
- As versões com timestamp servem como histórico

### 4. Verifique a Linha de Costa
- Use `c` para toggle da linha de costa
- Ajuda a identificar problemas

### 5. Compare Versões
Você pode carregar versões antigas para comparar:
```bash
# Versão atual
./scripts/pom.sh edit ../output/pom_bathymetry_grid.asc

# Versão anterior (exemplo)
./scripts/pom.sh edit ../output/pom_bathymetry_grid_v20251028_143045.asc
```

## Limitações Conhecidas

1. **Performance com grades grandes**: Grades muito grandes (>500x500) podem ficar lentas
2. **Zoom extremo**: Em zoom muito alto, a visualização pode perder detalhes
3. **Apenas conversão binária**: O editor só alterna terra/água, não ajusta profundidades específicas

## Resolução de Problemas

### Editor não abre
```bash
# Verificar instalação do matplotlib
conda activate ocean_mesh_tools
python -c "import matplotlib; print(matplotlib.__version__)"

# Se necessário, reinstalar
conda install matplotlib
```

### Arquivo não encontrado
```bash
# Listar arquivos disponíveis
./scripts/pom.sh edit
# Mostrará arquivos em output/
```

### Modificações não salvam
- Verifique permissões do diretório
- Certifique-se de pressionar `s` antes de sair

## Integração com POM

Após editar a grade:

1. **Verificar formato**:
   ```bash
   head -20 ../output/pom_bathymetry_grid.asc
   ```

2. **Testar no modelo**:
   - Use o arquivo editado normalmente no POM
   - O formato permanece 100% compatível

3. **Documentar mudanças**:
   - As versões com timestamp permitem rastrear modificações
   - Anote as razões para mudanças específicas

## Desenvolvimento Futuro

Possíveis melhorias planejadas:

- [ ] Edição de profundidades específicas (não apenas terra/água)
- [ ] Ferramentas de desenho (linha, polígono)
- [ ] Desfazer/refazer (undo/redo)
- [ ] Comparação lado-a-lado de versões
- [ ] Exportação de relatório de modificações

## Suporte

Para problemas ou sugestões:
- Abra uma issue no GitHub: https://github.com/daniloceano/RecOM
- Consulte a documentação principal em `docs/`
