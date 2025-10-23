# Guia de Publicação no GitHub

Este guia explica como publicar este projeto no GitHub.

## Passo 1: Criar Repositório no GitHub

1. Acesse https://github.com e faça login
2. Clique no botão "+" no canto superior direito
3. Selecione "New repository"
4. Configure o repositório:
   - **Name:** `gebco-pom-grid-generator` (ou outro nome de sua preferência)
   - **Description:** "Generator de grades batimétricas do GEBCO para o modelo POM"
   - **Visibility:** Public (ou Private se preferir)
   - **NÃO** marque "Initialize this repository with a README" (já temos um)
   - **NÃO** adicione .gitignore ou license (já temos)
5. Clique em "Create repository"

## Passo 2: Conectar Repositório Local ao GitHub

Após criar o repositório, você verá instruções. Use os comandos abaixo:

```bash
cd /Users/danilocoutodesouza/Documents/Programs_and_scripts/POM

# Adicionar o remote (substitua SEU_USUARIO pelo seu nome de usuário do GitHub)
git remote add origin https://github.com/SEU_USUARIO/gebco-pom-grid-generator.git

# Renomear branch para 'main' se necessário
git branch -M main

# Push inicial
git push -u origin main
```

## Passo 3: Configurar o Repositório

### Adicionar Topics/Tags

No GitHub, na página do repositório:
1. Clique em "About" (ícone de engrenagem)
2. Adicione topics relevantes:
   - `oceanography`
   - `bathymetry`
   - `gebco`
   - `pom-model`
   - `python`
   - `scientific-computing`
   - `grid-generation`

### Criar Releases

1. Vá em "Releases" > "Create a new release"
2. Tag version: `v2.0.0`
3. Release title: `Version 2.0.0 - Parallel Processing`
4. Descrição:
   ```markdown
   ## GEBCO to POM Grid Generator v2.0.0
   
   Primeira release pública com processamento paralelo.
   
   ### Características
   - ✨ Processamento paralelo para melhor performance
   - 📐 Interpolação de alta qualidade
   - 📝 Formato ASCII compatível com POM
   - 🖼️ Visualização automática
   - 📚 Documentação completa
   
   ### Instalação
   ```bash
   conda env create -f environment.yml
   conda activate pom
   ```
   
   ### Uso Rápido
   ```bash
   cd scripts
   python quick_generate.py --region brasil_sul
   ```
   
   Veja a [documentação completa](README.md) para mais detalhes.
   ```
5. Clique em "Publish release"

## Passo 4: Adicionar README Shields/Badges (Opcional)

Adicione badges ao topo do README.md:

```markdown
[![Python](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![GitHub release](https://img.shields.io/github/v/release/SEU_USUARIO/gebco-pom-grid-generator.svg)](https://github.com/SEU_USUARIO/gebco-pom-grid-generator/releases)
```

## Passo 5: Adicionar Documentação ao GitHub Pages (Opcional)

1. Vá em Settings > Pages
2. Source: "Deploy from a branch"
3. Branch: `main`, folder: `/docs`
4. Save
5. Seu site estará em: `https://SEU_USUARIO.github.io/gebco-pom-grid-generator/`

## Comandos Git Úteis

### Atualizar o repositório após mudanças:

```bash
# Ver status
git status

# Adicionar mudanças
git add .

# Commit
git commit -m "Descrição das mudanças"

# Push
git push
```

### Criar uma nova release:

```bash
# Tag
git tag -a v2.0.1 -m "Versão 2.0.1 - Correções de bugs"

# Push da tag
git push origin v2.0.1
```

### Trabalhar com branches:

```bash
# Criar branch para nova feature
git checkout -b feature/nova-funcionalidade

# Fazer mudanças, commits...

# Voltar para main
git checkout main

# Merge da feature
git merge feature/nova-funcionalidade

# Push
git push
```

## Checklist de Publicação

- [ ] Repositório criado no GitHub
- [ ] Remote adicionado localmente
- [ ] Push inicial realizado
- [ ] Topics/tags configurados
- [ ] Release v2.0.0 criada
- [ ] README verificado no GitHub
- [ ] Badges adicionados (opcional)
- [ ] GitHub Pages configurado (opcional)
- [ ] Colaboradores adicionados (se aplicável)
- [ ] Issues template criado (opcional)
- [ ] GitHub Actions configurado para CI/CD (opcional)

## Próximos Passos

Após publicar:

1. Compartilhe o link do repositório com colaboradores
2. Adicione o link na sua tese/artigos
3. Considere registrar no Zenodo para DOI
4. Submeta para listas de recursos oceanográficos

## Notas Importantes

### Dados GEBCO

O arquivo GEBCO (`*.nc`) é muito grande (~7 GB) e **NÃO** deve ser enviado ao GitHub.
Está no `.gitignore` para evitar problemas.

Os usuários devem baixar o GEBCO separadamente de:
https://www.gebco.net/data_and_products/gridded_bathymetry_data/

### Informações Sensíveis

Verifique que não há:
- Senhas ou tokens
- Caminhos absolutos específicos do seu computador
- Informações pessoais sensíveis

---

**Pronto!** Seu projeto está agora no GitHub e pronto para ser compartilhado com a comunidade científica! 🎉
