# Git Flow - Workflow Padronizado

Este projeto utiliza o **Git Flow**, uma metodologia de branching criada por Vincent Driessen, que organiza o desenvolvimento em branches específicas para diferentes propósitos.

## 📋 Estrutura de Branches

### Branches Principais

- **`main`** (ou `master`): Branch de produção. Contém apenas código estável e testado que está em produção.
- **`develop`**: Branch de desenvolvimento. Contém o código mais recente que foi desenvolvido e está pronto para ser integrado.

### Branches de Suporte

- **`feature/*`**: Branches para desenvolvimento de novas funcionalidades
- **`release/*`**: Branches para preparação de releases
- **`hotfix/*`**: Branches para correções urgentes em produção

## 🚀 Workflow Padronizado

### ⚠️ REGRA IMPORTANTE
**NUNCA faça commits diretamente na branch `main`!** 
Todas as alterações devem ser feitas através de branches de feature, release ou hotfix.

### 1. Desenvolvimento de Features

Para desenvolver uma nova funcionalidade:

```bash
# Certifique-se de estar na branch develop
git checkout develop
git pull origin develop

# Crie uma nova branch de feature
git checkout -b feature/nome-da-feature

# Faça suas alterações e commits
git add .
git commit -m "feat: descrição da feature"

# Envie a branch para o repositório remoto
git push origin feature/nome-da-feature

# Quando a feature estiver completa, faça merge na develop
git checkout develop
git pull origin develop
git merge feature/nome-da-feature
git push origin develop

# Delete a branch local (opcional)
git branch -d feature/nome-da-feature
```

### 2. Preparação de Release

Quando o código na `develop` estiver pronto para produção:

```bash
# Crie uma branch de release
git checkout develop
git pull origin develop
git checkout -b release/1.0.0

# Faça ajustes finais (versionamento, changelog, etc.)
# Não adicione novas features aqui, apenas correções de bugs

# Quando estiver pronto, faça merge na main e develop
git checkout main
git merge release/1.0.0
git tag -a v1.0.0 -m "Release version 1.0.0"
git push origin main --tags

git checkout develop
git merge release/1.0.0
git push origin develop

# Delete a branch de release
git branch -d release/1.0.0
```

### 3. Hotfix (Correções Urgentes)

Para correções urgentes em produção:

```bash
# Crie uma branch de hotfix a partir da main
git checkout main
git pull origin main
git checkout -b hotfix/correcao-urgente

# Faça a correção
git add .
git commit -m "fix: descrição da correção"

# Faça merge na main e develop
git checkout main
git merge hotfix/correcao-urgente
git tag -a v1.0.1 -m "Hotfix version 1.0.1"
git push origin main --tags

git checkout develop
git merge hotfix/correcao-urgente
git push origin develop

# Delete a branch de hotfix
git branch -d hotfix/correcao-urgente
```

## 📝 Convenções de Commit

Seguindo o padrão **Conventional Commits**:

- `feat:` - Nova funcionalidade
- `fix:` - Correção de bug
- `docs:` - Documentação
- `style:` - Formatação, ponto e vírgula, etc (não afeta código)
- `refactor:` - Refatoração de código
- `test:` - Adição ou correção de testes
- `chore:` - Tarefas de build, configuração, etc

Exemplo:
```bash
git commit -m "feat: adiciona autenticação JWT"
git commit -m "fix: corrige validação de email"
git commit -m "docs: atualiza README com instruções de deploy"
```

## 🔒 Proteção da Branch Main

### Configuração Recomendada no GitHub/GitLab

1. Vá em **Settings** → **Branches**
2. Adicione uma regra de proteção para a branch `main`:
   - ✅ Require pull request before merging
   - ✅ Require approvals (1 ou mais)
   - ✅ Require status checks to pass
   - ✅ Do not allow bypassing the above settings

Isso garante que ninguém possa fazer push direto na `main`.

## 📊 Fluxograma Visual

```
main (produção)
  ↑
  | hotfix
  |
  | release
  |
develop (desenvolvimento)
  ↑
  | feature
  |
feature/nova-funcionalidade
```

## 🎯 Resumo Rápido

1. **Desenvolvimento normal**: `develop` → `feature/*` → `develop`
2. **Preparar release**: `develop` → `release/*` → `main` + `develop`
3. **Correção urgente**: `main` → `hotfix/*` → `main` + `develop`
4. **Nunca commite diretamente na `main`!**

## 📚 Referências

- [Git Flow Original (Vincent Driessen)](https://nvie.com/posts/a-successful-git-branching-model/)
- [Conventional Commits](https://www.conventionalcommits.org/)

