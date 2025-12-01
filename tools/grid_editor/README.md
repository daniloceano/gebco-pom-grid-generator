# Editor de Grades - RecOM

## O que faz

Editor visual interativo para manipulação manual de grades oceânicas. Permite alternar células entre terra e água com interface gráfica avançada.

**Principais características:**
- 🗺️ **Linha de costa real** via Cartopy (Natural Earth)
- 📊 **Contornos batimétricos** com labels
- 🎨 **Visualização clara**: terra em cinza, oceano em azul
- 🖱️ **Click-to-edit**: Alternar terra ↔ água
- 🔍 **Zoom interativo** com scroll e teclas
- 🧮 **Interpolação automática** IDW quando converte terra → água
- 💾 **Auto-save** com timestamp
- 🔧 **Configurável** via argumentos CLI

## Formato Suportado

Suporta grades no formato ASCII de 5 colunas (POM):
```
i  j  longitude  latitude  depth
```

**Convenção**: depth > 0 = oceano, depth = 0 = terra

## Como usar

### Visualizar Grade (somente leitura)

```bash
# Via ocean_mesh_tools.sh (recomendado)
./ocean_mesh_tools.sh view output/pom_bathymetry_grid.asc

# Salvar figura
./ocean_mesh_tools.sh view output/pom_bathymetry_grid.asc -o mapa.png

# Alta resolução
./ocean_mesh_tools.sh view output/pom_bathymetry_grid.asc -o mapa.png --dpi 600

# Direto (do diretório scripts/)
python visualize_grid.py ../../output/pom_bathymetry_grid.asc
python visualize_grid.py ../../output/pom_bathymetry_grid.asc -o figura.png
```

### Editar Grade (modo interativo)

```bash
# Via ocean_mesh_tools.sh (recomendado)
./ocean_mesh_tools.sh edit output/pom_bathymetry_grid.asc

# Direto (do diretório scripts/)
cd scripts
python edit_grid.py ../../output/pom_bathymetry_grid.asc

# Com opções
python edit_grid.py grade.asc --no-coastline
python edit_grid.py grade.asc --no-contours
```

## Controles

### Mouse
- **Click esquerdo**: Alternar terra/água no ponto clicado
- **Click direito + arrastar**: Mover/pan pelo mapa
- **Scroll up**: Zoom in
- **Scroll down**: Zoom out

### Teclado
- **+** ou **=**: Zoom in
- **-**: Zoom out
- **r**: Reset do zoom
- **g**: Toggle grade de células
- **c**: Toggle linha de costa
- **b**: Toggle contornos batimétricos
- **s**: Salvar modificações
- **q**: Sair

**Nota:** Para aplicar máscaras de reanálise, use o módulo `reanalysis_mask`:
```bash
python tools/reanalysis_mask/scripts/apply_mask.py <grade> <mascara>
```

## Visualização

### Com Cartopy (recomendado)
```
✓ Linha de costa de alta resolução (Natural Earth)
✓ Fronteiras de países
✓ Projeção cartográfica correta
✓ Contornos batimétricos com labels
```

### Sem Cartopy
```
⚠ Linha de costa simplificada (contorno depth=0)
⚠ Visualização básica
```

## Exemplos

### Exemplo 1: Fechar uma baía

1. Abra o editor: `python edit_grid.py grade.asc`
2. Dê zoom na baía (scroll ou tecla +)
3. Clique nas células de água que quer converter para terra
4. Pressione 's' para salvar

### Exemplo 2: Abrir um canal

1. Abra o editor
2. Localize o canal obstruído
3. Clique nas células de terra para converter em água
4. O editor interpolará automaticamente a profundidade
5. Pressione 's' para salvar

### Exemplo 3: Ajuste fino de costa

1. Use 'c' para mostrar/esconder a linha de costa real
2. Compare com a grade
3. Ajuste as células conforme necessário
4. Use 'b' para ver contornos batimétricos
5. Salve quando satisfeito

## Interpolação Automática

Quando você converte terra → água, o editor:

1. Busca células de água vizinhas (raio de até 5 células)
2. Calcula distância de cada vizinho
3. Aplica IDW (Inverse Distance Weighting):
   ```
   depth = Σ(depth_i * weight_i) / Σ(weight_i)
   onde weight_i = 1 / distance_i²
   ```
4. Usa mínimo de 4 vizinhos para boa interpolação
5. Fallback para 100m se não houver vizinhos

## Salvamento

Arquivos editados são salvos com timestamp:
```
grade.asc               # Original
grade_backup.asc        # Backup automático
grade_edited_20251201_143052.asc  # Versão editada
```

O arquivo salvo mantém:
- Cabeçalho original
- Adiciona linha com timestamp da edição
- Mesmo formato (5 colunas)
- Compatível com ferramentas do pacote

## Requisitos

### Obrigatórios
- numpy
- matplotlib

### Opcionais (recomendados)
- **cartopy** - Para linha de costa real e melhor visualização

```bash
conda install -c conda-forge cartopy
```

## Estrutura de arquivos

```
grid_editor/
├── README.md                    # Este arquivo
├── src/
│   ├── __init__.py
│   └── grid_editor.py           # Classe principal
├── scripts/
│   └── edit_grid.py             # Script wrapper
└── examples/
    └── example_edit.py          # Exemplo de uso
```

## Uso Programático

```python
import sys
sys.path.insert(0, 'tools/grid_editor/src')
from grid_editor import GridEditor

# Criar editor
editor = GridEditor(
    'grade.asc',
    use_cartopy=True,
    show_contours=True
)

# Mostrar interface
editor.show()

# Ou modificar programaticamente
editor.toggle_cell(10, 15)  # Alternar célula i=10, j=15
editor.save()
```

## Diferenças do Editor Antigo

| Recurso | Antigo | Novo |
|---------|--------|------|
| Linha de costa | Contorno simples | Cartopy (real) |
| Terra | Transparente | Cinza claro |
| Oceano | Terrain colormap | Blues (batimetria) |
| Contornos | Apenas costa | Costa + batimetria |
| Localização | gebco_interpolation/ | grid_editor/ (módulo próprio) |
| Reutilizável | Não | Sim (por outras ferramentas) |

## Performance

- **Grids pequenos** (< 100x100): Instantâneo
- **Grids médios** (100x100 a 500x500): < 2 segundos
- **Grids grandes** (> 500x500): 2-5 segundos inicial, depois fluido

Dica: Use zoom para trabalhar em regiões específicas

## Troubleshooting

### "cartopy não encontrado"
```bash
conda activate ocean_mesh_tools
conda install -c conda-forge cartopy
```

### Editor muito lento
- Desative contornos: tecla 'b'
- Desative grade: tecla 'g'
- Use --no-contours ao iniciar

### Linha de costa não aparece
- Verifique se cartopy está instalado
- Tente --no-cartopy para modo simplificado
- Pressione 'c' para toggle

### Interpolação retorna 100m sempre
- Significa que não há células de água próximas
- Defina profundidade manualmente editando o arquivo

## Extensibilidade

Este módulo pode ser usado por outras ferramentas:

```python
# Em outra ferramenta do pacote
from tools.grid_editor.src import GridEditor

editor = GridEditor(my_grid_file)
editor.show()
```

## Testes

Ver `tests/test_grid_editor.py` para testes automatizados.

## Notas Técnicas

### Projeção
- Usa PlateCarree (lat/lon simples) quando com Cartopy
- Adequado para grades regionais e globais

### Colormap
- Terra: Greys (cinza claro)
- Oceano: Blues_r (azul escuro = profundo, claro = raso)
- Range: 0-6000m para oceano

### Contornos
- Batimetria: 500, 1000, 2000, 3000, 4000, 5000, 6000m
- Costa: depth = 0.5m (tolerância para suavidade)

## Referências

- Natural Earth: https://www.naturalearthdata.com/
- Cartopy: https://scitools.org.uk/cartopy/
- IDW Interpolation: https://en.wikipedia.org/wiki/Inverse_distance_weighting
