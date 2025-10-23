# Contributing to GEBCO to POM Grid Generator

Obrigado pelo interesse em contribuir! Este documento fornece diretrizes para contribuições.

## Como Contribuir

### Reportar Bugs

Se você encontrou um bug:

1. Verifique se já não existe uma issue sobre o problema
2. Abra uma nova issue incluindo:
   - Descrição clara do problema
   - Passos para reproduzir
   - Comportamento esperado vs. observado
   - Versão do Python e sistema operacional
   - Logs relevantes

### Sugerir Melhorias

Para sugestões de novas funcionalidades:

1. Abra uma issue descrevendo:
   - O problema que a funcionalidade resolveria
   - Como você imagina que deveria funcionar
   - Exemplos de uso

### Pull Requests

1. Fork o repositório
2. Crie uma branch para sua feature (`git checkout -b feature/MinhaFeature`)
3. Faça commit das suas mudanças (`git commit -m 'Adiciona MinhaFeature'`)
4. Push para a branch (`git push origin feature/MinhaFeature`)
5. Abra um Pull Request

#### Checklist para Pull Requests

- [ ] Código segue o estilo do projeto
- [ ] Comentários adicionados onde necessário
- [ ] Documentação atualizada
- [ ] Testes adicionados/atualizados
- [ ] Todos os testes passam
- [ ] CHANGELOG.md atualizado

## Estilo de Código

- Seguir PEP 8 para código Python
- Docstrings no formato NumPy
- Comentários em português para facilitar uso por pesquisadores brasileiros
- Type hints onde apropriado

## Testes

Antes de submeter um PR:

```bash
cd scripts
./pom.sh test
```

## Dúvidas?

Abra uma issue com a tag `question`.

Obrigado por contribuir! 🎉
