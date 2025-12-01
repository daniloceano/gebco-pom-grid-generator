# 📝 Instruções para Renomear o Repositório no GitHub

O projeto foi renomeado de **gebco-pom-grid-generator** para **RecOM (Rectangular Ocean Mesh Tools)**.

## 🔄 Passos para Atualizar no GitHub

### Opção 1: Renomear o Repositório Existente (Recomendado)

1. **Acessar Configurações do Repositório**
   - Vá para: https://github.com/daniloceano/gebco-pom-grid-generator
   - Clique em **Settings** (Configurações)

2. **Renomear**
   - Na seção "Repository name", altere para: `RecOM`
   - Clique em **Rename**
   - O GitHub redirecionará automaticamente URLs antigas

3. **Atualizar Remote Local**
   ```bash
   # Atualizar URL do remote
   git remote set-url origin https://github.com/daniloceano/RecOM.git
   
   # Verificar
   git remote -v
   ```

4. **Atualizar Descrição do Repositório**
   - Em Settings, altere a descrição para:
   - **"RecOM - Rectangular Ocean Mesh Tools: Ferramentas para geração de grades oceânicas retangulares"**

5. **Atualizar Topics (Tags)**
   - Adicione: `ocean-modeling`, `mesh-generation`, `bathymetry`, `gebco`, `oceanography`, `grid-tools`

### Opção 2: Criar Novo Repositório

Se preferir criar um repositório totalmente novo:

1. **Criar Novo Repositório no GitHub**
   - Nome: `RecOM`
   - Descrição: "RecOM - Rectangular Ocean Mesh Tools: Ferramentas para geração de grades oceânicas retangulares"
   - Público ou Privado (sua escolha)

2. **Atualizar Remote Local**
   ```bash
   # Remover remote antigo
   git remote remove origin
   
   # Adicionar novo remote
   git remote add origin https://github.com/daniloceano/RecOM.git
   
   # Fazer push inicial
   git push -u origin main
   ```

3. **Arquivar Repositório Antigo** (opcional)
   - Vá para o repositório antigo
   - Settings → Archive this repository

## 📦 Commit das Alterações

Antes de fazer push, commite todas as mudanças:

```bash
# Verificar alterações
git status

# Adicionar novos arquivos
git add tests/test_reanalysis_mask.py
git add tools/reanalysis_mask/
git add tools/reanalysis_mask/scripts/apply_mask.py

# Commitar todas as mudanças
git add -A
git commit -m "Renomear projeto para RecOM (Rectangular Ocean Mesh Tools)

- Atualizado nome do projeto em toda documentação
- Renomeado ambiente conda para ocean_mesh_tools
- Atualizado URLs do GitHub
- Adicionado módulo reanalysis_mask completo
- Criado script apply_mask.py separado do grid_editor
- Melhorias na documentação e estrutura do projeto"

# Push para GitHub
git push origin main
```

## 🎯 Benefícios do Novo Nome

- **RecOM** é mais conciso e memorável
- **Rectangular Ocean Mesh** descreve claramente o propósito
- Nome profissional e acadêmico
- Sigla fácil de referenciar em papers e apresentações

## 📚 Próximos Passos

Após renomear:

1. ✅ Atualizar links em documentação externa (se houver)
2. ✅ Informar colaboradores sobre a mudança (se houver)
3. ✅ Atualizar citações em artigos/teses
4. ✅ Criar release tag: `v1.0.0` para marcar a primeira versão oficial

## 🔗 URLs Atualizadas

- **Repositório:** https://github.com/daniloceano/RecOM
- **Clone:** `git clone https://github.com/daniloceano/RecOM.git`

---

**Nota:** O GitHub mantém redirecionamento automático do nome antigo para o novo por tempo indeterminado, mas é recomendado atualizar todos os links.
