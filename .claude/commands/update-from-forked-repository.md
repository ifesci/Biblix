# Update from Forked Repository

Atualiza este repositório fork com as últimas mudanças do repositório original upstream, corrigindo automaticamente problemas comuns nos testes.

## ⚠️ GARANTIA DE SEGURANÇA

**Este comando NUNCA modifica o repositório original (upstream):**

✅ **Operações de LEITURA no upstream:**
- `git fetch upstream` - apenas baixa atualizações
- `git log upstream/main` - apenas consulta commits
- `git merge upstream/main` - usa dados já baixados localmente

✅ **Operações de ESCRITA (apenas no fork local):**
- `git commit` - salva mudanças LOCALMENTE
- `git branch` - cria branches LOCAIS
- `git push origin main` - envia para SEU FORK (não para upstream)

🔒 **Garantias:**
- Nenhum comando faz `git push upstream` (isso nem é possível sem permissões especiais)
- O repositório original permanece intocado
- Apenas seu fork local e remoto são modificados

**Remotes:**
- `origin` = seu fork (repositório do aluno)
- `upstream` = repositório original (DefaultWebApp)

---

## Instruções para Execução

Execute as seguintes fases de forma autônoma e sequencial:

---

## FASE 1: Pré-validação

1. **Verificar estado do repositório**
   ```bash
   git status
   ```
   - Se houver mudanças não commitadas: **ABORTAR** e informar usuário para commitar ou fazer stash primeiro

2. **Verificar configuração de remotes**
   ```bash
   git remote -v
   ```
   - Se `upstream` NÃO estiver configurado:
     - **PERGUNTAR ao usuário**: "Qual é a URL do repositório original (upstream)?"
     - Configurar: `git remote add upstream <URL>`
   - Se `upstream` JÁ estiver configurado:
     - Mostrar URL e confirmar: "Upstream configurado: <URL>"

---

## FASE 2: Análise e Backup

1. **Buscar atualizações do upstream**
   ```bash
   git fetch upstream
   ```

2. **Analisar divergências**
   ```bash
   # Contar commits novos no upstream
   git log --oneline upstream/main --not main | wc -l

   # Contar commits locais não no upstream
   git log --oneline main --not upstream/main | wc -l

   # Encontrar ponto de divergência
   git merge-base main upstream/main
   ```

   Mostrar resumo:
   ```
   📊 Análise de Divergências:
   - X commits novos no upstream
   - Y commits locais únicos
   - Ponto de divergência: <commit-hash>
   ```

3. **Criar branch de backup**
   ```bash
   # Formato: backup-before-update-YYYYMMDD-HHMMSS
   git branch backup-before-update-$(date +%Y%m%d-%H%M%S)
   ```

   Confirmar: "✅ Backup criado: <nome-do-branch>"

---

## FASE 3: Merge

1. **Executar merge**
   ```bash
   git merge upstream/main --no-edit
   ```

2. **Verificar resultado**
   - Se merge foi bem-sucedido: continuar para Fase 4
   - Se houver **CONFLITOS**:
     ```
     ⚠️  CONFLITOS DETECTADOS!

     Arquivos em conflito:
     <listar arquivos>

     Para resolver:
     1. Resolva os conflitos manualmente
     2. git add <arquivos-resolvidos>
     3. git commit
     4. Execute este comando novamente

     Para cancelar: git merge --abort
     ```
     **ABORTAR** e aguardar resolução manual

3. **Mostrar resumo do merge**
   ```bash
   git diff --stat <commit-antes>..HEAD
   ```
   Exemplo:
   ```
   ✅ Merge concluído com sucesso!
   - 117 arquivos alterados
   - 7.146 inserções, 1.373 deleções
   ```

---

## FASE 4: Validação Inteligente

1. **Detectar tipo de projeto**
   - Se existe `requirements.txt` ou `pytest.ini` ou `tests/` com Python → Projeto Python
   - Se existe `package.json` → Projeto Node.js
   - Se existe `pom.xml` → Projeto Java

2. **Para Projetos Python:**

   a. Executar testes:
   ```bash
   python -m pytest tests/ -v --tb=short
   ```

   b. Capturar resultados:
   - Total de testes
   - Testes passando
   - Testes falhando
   - Tipos de erros

3. **Se todos os testes passarem:**
   - Pular para Fase 6 (Finalização)

4. **Se houver testes falhando:**
   - Continuar para Fase 5 (Correção Automática)

---

## FASE 5: Correção Automática de Testes (Python)

### Estratégia de Correção Automática

Analise os erros dos testes e aplique correções genéricas:

### 5.1 Verificar arquivo conftest.py

```bash
# Verificar se conftest.py existe
ls tests/conftest.py
```

### 5.2 Analisar tipos de erros comuns

**Tipo 1: ValidationError - Campos obrigatórios faltando**
- Sintoma: `ValidationError`, `field required`, campos faltando em DTOs
- Exemplo: "perfil is required", "campo X is missing"
- Ação: Identificar qual campo está faltando e adicionar nas fixtures e testes

**Tipo 2: Problemas de isolamento entre testes**
- Sintoma: Testes passam individualmente mas falham em conjunto
- Exemplo: "expected 0 but got 3", dados de outros testes aparecendo
- Ação: Adicionar limpeza de banco de dados entre testes

**Tipo 3: Rate limiter bloqueando testes**
- Sintoma: "muitas tentativas", "rate limit exceeded", "aguarde"
- Ação: Adicionar limpeza de rate limiters entre testes

### 5.3 Aplicar Correções

**Correção A: Adicionar limpeza de banco de dados**

Se detectar problemas de isolamento, adicionar em `tests/conftest.py`:

```python
@pytest.fixture(scope="function", autouse=True)
def limpar_banco_dados():
    """Limpa o banco de dados antes de cada teste"""
    from util.db_util import get_connection
    import sqlite3

    with get_connection() as conn:
        cursor = conn.cursor()
        # Tentar limpar cada tabela, ignorando se não existir
        try:
            cursor.execute("DELETE FROM tarefa")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("DELETE FROM usuario")
        except sqlite3.OperationalError:
            pass
        try:
            cursor.execute("DELETE FROM configuracao")
        except sqlite3.OperationalError:
            pass

    yield
```

**Correção B: Adicionar limpeza de rate limiters**

Se detectar rate limiting, adicionar em `tests/conftest.py`:

```python
@pytest.fixture(scope="function", autouse=True)
def limpar_rate_limiter():
    """Limpa o rate limiter antes de cada teste para evitar bloqueios"""
    from routes.auth_routes import login_limiter, cadastro_limiter, esqueci_senha_limiter

    login_limiter.limpar()
    cadastro_limiter.limpar()
    esqueci_senha_limiter.limpar()
    yield
    login_limiter.limpar()
    cadastro_limiter.limpar()
    esqueci_senha_limiter.limpar()
```

**Correção C: Atualizar fixtures com campos obrigatórios**

Se detectar ValidationError por campo faltando (ex: "perfil"):

1. Buscar fixture `criar_usuario` em conftest.py
2. Adicionar parâmetro com default:
   ```python
   def _criar_usuario(nome: str, email: str, senha: str, perfil: str = "Cliente"):
   ```
3. Adicionar campo no POST:
   ```python
   response = client.post("/cadastrar", data={
       "perfil": perfil,  # <-- Adicionar
       "nome": nome,
       "email": email,
       "senha": senha,
       "confirmar_senha": senha
   })
   ```

4. Buscar todos os testes que fazem POST para cadastro e adicionar campo faltando

**Correção D: Corrigir testes específicos**

Procurar padrões como:
- `assert tarefas[0].titulo == ...` → mudar para `assert titulo in [t.titulo for t in tarefas]`
- Testes assumindo posição específica → usar verificação de presença

### 5.4 Re-executar testes

Após cada correção:
```bash
python -m pytest tests/ -v --tb=short
```

Repetir até testes passarem ou não haver mais correções automáticas possíveis.

### 5.5 Relatório de correções

Listar todas as correções aplicadas:
```
🔧 Correções Automáticas Aplicadas:
✅ Adicionada limpeza de banco de dados em conftest.py
✅ Adicionada limpeza de rate limiters em conftest.py
✅ Atualizada fixture criar_usuario com campo 'perfil'
✅ Corrigidos 7 testes em test_auth.py
✅ Corrigido 1 teste em test_tarefas.py
```

---

## FASE 6: Finalização

1. **Verificar estado final dos testes**
   ```bash
   python -m pytest tests/ -v --tb=short
   ```

   Mostrar:
   ```
   📊 Resultado Final dos Testes:
   ✅ 49 de 49 testes passando (100%)
   ```

   Ou se ainda houver falhas:
   ```
   ⚠️  Alguns testes ainda falhando:
   ❌ 3 de 49 testes falhando

   Estes testes requerem correção manual.
   ```

2. **Criar commit automático**

   Se houve correções nos testes:
   ```bash
   git add tests/
   git commit -m "merge: atualizar fork com upstream e corrigir testes

   - Integrados X commits do repositório upstream
   - Corrigidos Y arquivos de teste
   - Todos os testes passando

   🤖 Generated with [Claude Code](https://claude.com/claude-code)

   Co-Authored-By: Claude <noreply@anthropic.com>"
   ```

   Se não houve correções:
   ```bash
   # Merge já foi commitado automaticamente pelo git merge
   ```

3. **Pergunta opcional: Push automático**

   **PERGUNTAR**: "Fazer push para origin agora? (s/N)"
   - Default: **N** (Não)
   - Se "s" ou "sim": `git push origin main`
   - Se "n" ou "não": informar comando: `git push origin main`

---

## RELATÓRIO FINAL

Ao concluir todas as fases, apresentar relatório completo:

```
═══════════════════════════════════════════════════════════
🎉 ATUALIZAÇÃO DO FORK CONCLUÍDA COM SUCESSO!
═══════════════════════════════════════════════════════════

📥 INTEGRAÇÃO:
   • 28 commits do upstream integrados
   • 117 arquivos modificados
   • 7.146 inserções, 1.373 deleções

🔧 CORREÇÕES AUTOMÁTICAS:
   • Limpeza de banco de dados adicionada
   • Limpeza de rate limiters adicionada
   • 8 testes corrigidos

✅ TESTES:
   • Antes: 30/49 passando (61%)
   • Depois: 49/49 passando (100%)

💾 BACKUP:
   • Branch de segurança: backup-before-update-20251020-085200
   • Para reverter: git reset --hard backup-before-update-20251020-085200

📦 PRÓXIMOS PASSOS:
   1. Revisar mudanças integradas
   2. Testar aplicação manualmente se necessário
   3. Push para repositório: git push origin main

═══════════════════════════════════════════════════════════
```

---

## COMPORTAMENTO AUTÔNOMO

**Minimizar perguntas:**
- Apenas perguntar URL do upstream se não existir
- Apenas perguntar sobre push no final
- Todo o resto é automático com decisões sensatas

**Segurança:**
- Sempre criar backup antes de qualquer alteração
- Abortar se houver mudanças não commitadas
- Abortar se houver conflitos (correção manual)
- Nunca forçar push
- NUNCA modifica o repositório upstream (apenas leitura)
- APENAS escreve no fork local (origin), nunca no upstream

**Inteligência:**
- Detectar tipo de projeto automaticamente
- Aplicar correções baseadas em padrões conhecidos
- Adaptar estratégia conforme erros encontrados

**Transparência:**
- Mostrar cada passo executado
- Listar todas as correções aplicadas
- Fornecer relatório detalhado final
- Indicar comandos de rollback

---

## TRATAMENTO DE ERROS

Se qualquer comando falhar:
1. Mostrar erro detalhado
2. Indicar em qual fase falhou
3. Fornecer comando de rollback: `git reset --hard backup-before-update-...`
4. Sugerir ações corretivas

---

**IMPORTANTE**: Execute todas as fases sequencialmente sem parar, exceto quando:
- Houver mudanças não commitadas (Fase 1)
- Houver conflitos de merge (Fase 3)
- Perguntas obrigatórias (upstream URL, push final)

Seja autônomo, inteligente e transparente!
