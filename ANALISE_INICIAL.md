# ANÁLISE INICIAL - PROJETO BIBLIX

**Data:** 20/10/2025
**Versão:** 1.0
**Status:** Análise de Gap entre Estado Atual e Solução Proposta

---

## 1. RESUMO EXECUTIVO

Este documento apresenta uma análise detalhada do projeto **Biblix** - Sistema de Gestão Inteligente de Empréstimo de Livros, comparando o estado atual da implementação com a solução completa descrita no documento de especificação (Biblix.pdf).

### 1.1. Objetivo do Projeto

Desenvolver uma aplicação web completa para gestão de empréstimos de livros em bibliotecas escolares, comunitárias ou institucionais, com foco em:
- Automatização de processos de cadastro, reserva, empréstimo e devolução
- Interface moderna e responsiva
- Controle de acesso por perfis hierárquicos
- Sistema de relatórios e estatísticas
- Notificações automáticas

### 1.2. Base Tecnológica Atual

O projeto está construído sobre o **DefaultWebApp**, um boilerplate profissional que fornece:
- ✅ Framework: **Python 3.12 + FastAPI**
- ✅ Templates: **Jinja2**
- ✅ Banco de Dados: **SQLite** (com possibilidade de migração para PostgreSQL)
- ✅ Frontend: **HTML5/CSS3 + Bootstrap 5**
- ✅ Autenticação e autorização completa
- ✅ Sistema de validação robusto (15+ validadores)
- ✅ Sistema de fotos de perfil
- ✅ Flash messages e toasts
- ✅ Logger profissional
- ✅ Envio de emails
- ✅ Máscaras de input

### 1.3. Estado Atual vs. Solução Proposta

| Aspecto | Status Atual | Meta Proposta | Gap |
|---------|-------------|---------------|-----|
| **Estrutura Base** | ✅ Completa | Sistema Biblix | Renomeação/Adaptação |
| **Autenticação** | ✅ Completa | Múltiplos perfis Biblix | Adicionar perfis específicos |
| **Models de Dados** | 🟡 Parcial | DER completo | Completar relacionamentos |
| **Funcionalidades CRUD** | 🔴 Mínima | RFs 1-13 | Implementar 13 requisitos |
| **Interfaces** | 🔴 Nenhuma | UI completa Biblix | Criar todas as views |
| **Relatórios** | 🔴 Nenhum | Estatísticas e dashboards | Implementar sistema |

**Legenda:** ✅ Completo | 🟡 Parcial | 🔴 Não iniciado

---

## 2. INVENTÁRIO DO ESTADO ATUAL

### 2.1. Estrutura de Diretórios

```
Biblix/
├── data/                    # ✅ Dados seed em JSON
├── docs/                    # 🔴 Documentação específica Biblix
├── dtos/                    # 🟡 Validadores - faltam DTOs Biblix
├── model/                   # 🟡 Models básicos criados
│   ├── autor_model.py       # ✅ Criado (vazio)
│   ├── categoria_model.py   # ✅ Criado (vazio)
│   ├── configuracao_model.py # ✅ Criado
│   ├── emprestimo_model.py  # 🟡 Criado (incompleto)
│   ├── livro_model.py       # 🟡 Criado (incompleto)
│   ├── reserva_model.py     # 🟡 Criado (incompleto)
│   ├── tarefa_model.py      # ⚠️ Template/Exemplo (remover)
│   └── usuario_model.py     # ✅ Completo
├── repo/                    # 🔴 Repositories Biblix não criados
│   ├── configuracao_repo.py # ✅ Existe
│   ├── tarefa_repo.py       # ⚠️ Template/Exemplo (remover)
│   └── usuario_repo.py      # ✅ Completo
├── routes/                  # 🔴 Rotas Biblix não criadas
│   ├── admin_*.py           # ✅ Base administrativa existe
│   ├── auth_routes.py       # ✅ Autenticação completa
│   ├── perfil_routes.py     # ✅ Perfil de usuário completo
│   ├── public_routes.py     # ✅ Rotas públicas
│   ├── examples_routes.py   # ⚠️ Remover (exemplos)
│   └── tarefas_routes.py    # ⚠️ Template/Exemplo (remover)
├── sql/                     # 🔴 SQLs Biblix não criados
│   ├── configuracao_sql.py  # ✅ Existe
│   ├── tarefa_sql.py        # ⚠️ Template/Exemplo (remover)
│   └── usuario_sql.py       # ✅ Completo
├── static/                  # ✅ Estrutura completa
├── templates/               # 🟡 Base existe, faltam templates Biblix
│   ├── auth/                # ✅ Login, cadastro, recuperação
│   ├── perfil/              # ✅ Perfil de usuário
│   ├── admin/               # ✅ Área administrativa base
│   ├── components/          # ✅ Componentes reutilizáveis
│   ├── macros/              # ✅ Macros de formulário
│   ├── examples/            # ⚠️ Remover (exemplos)
│   └── tarefas/             # ⚠️ Template/Exemplo (remover)
├── tests/                   # 🟡 Estrutura existe, faltam testes Biblix
└── util/                    # ✅ Utilitários completos
```

### 2.2. Models Existentes (Estado Atual)

#### 2.2.1. ✅ **Usuario Model** - COMPLETO
```python
@dataclass
class Usuario:
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    token_redefinicao: Optional[str]
    data_token: Optional[str]
    data_cadastro: Optional[str]
```
**Status:** Pronto para uso. Precisa apenas adicionar perfis específicos Biblix.

#### 2.2.2. 🟡 **Livro Model** - INCOMPLETO
```python
@dataclass
class Livro:
    id_livro: int
    titulo: str
    data_publicacao: datetime
    sinopse: str
```
**Gaps identificados:**
- ❌ Falta relacionamento com Autor (N:N)
- ❌ Falta relacionamento com Categoria (N:N)
- ❌ Falta campo ISBN
- ❌ Falta campo editora
- ❌ Falta campo quantidade_disponivel
- ❌ Falta campo quantidade_total
- ❌ Falta campo capa_url
- ❌ Falta campo status (disponível/indisponível)

#### 2.2.3. 🟡 **Emprestimo Model** - INCOMPLETO
```python
@dataclass
class Emprestimo:
    id_emprestimo: int
    id_livro: int
    id_leitor: int
    data_retirada: datetime
    data_devolucao: datetime
```
**Gaps identificados:**
- ❌ Falta campo data_devolucao_prevista
- ❌ Falta campo status (emprestado/devolvido/atrasado)
- ❌ Falta campo id_bibliotecario (quem registrou)
- ❌ Falta campo renovacoes (contador)
- ❌ Falta relacionamentos (livro, leitor, bibliotecário)

#### 2.2.4. 🟡 **Reserva Model** - INCOMPLETO
```python
@dataclass
class Reserva:
    id_reserva: int
    id_livro: int
    id_leitor: int
    data_cadastro: datetime
    data_reserva: datetime
    status: str
    livro: Optional[Livro]
    leitor: Optional[Usuario]
```
**Gaps identificados:**
- ❌ Campo data_reserva deveria ser data_desejada
- ❌ Falta campo data_expiracao
- ❌ Falta campo notificado (boolean)
- ✅ Relacionamentos existem mas precisam ser verificados

#### 2.2.5. 🔴 **Autor Model** - VAZIO
**Deve conter:**
- id
- nome
- biografia
- data_nascimento
- foto_url
- data_cadastro

#### 2.2.6. 🔴 **Categoria Model** - VAZIO
**Deve conter:**
- id
- nome
- descricao
- data_cadastro

### 2.3. Perfis de Usuário

#### Perfis Atuais (util/perfis.py):
```python
class Perfil(str, Enum):
    ADMIN = "Administrador"
    CLIENTE = "Cliente"
    VENDEDOR = "Vendedor"
```

#### Perfis Necessários (conforme PDF):
```python
class Perfil(str, Enum):
    ADMIN = "Administrador"
    BIBLIOTECARIO = "Bibliotecário"
    LEITOR = "Leitor"
    # Usuário Autenticado é uma abstração (qualquer um logado)
    # Anônimo não precisa estar no Enum (não autenticado)
```

**Ações necessárias:**
- ✅ Manter: ADMIN (já existe)
- ❌ Remover: CLIENTE, VENDEDOR (não fazem sentido no Biblix)
- ✅ Adicionar: BIBLIOTECARIO
- ✅ Adicionar: LEITOR

### 2.4. Funcionalidades Existentes (Reutilizáveis)

O boilerplate atual oferece funcionalidades prontas que podem ser reutilizadas:

| Funcionalidade | Status | Uso no Biblix |
|----------------|--------|---------------|
| **Sistema de Login/Logout** | ✅ Completo | Reutilizar diretamente |
| **Cadastro de usuário** | ✅ Completo | Adaptar para perfil Leitor |
| **Recuperação de senha** | ✅ Completo | Reutilizar diretamente |
| **Gerenciamento de perfil** | ✅ Completo | Reutilizar + adicionar campos |
| **Sistema de fotos** | ✅ Completo | Usar para fotos de perfil |
| **Flash messages** | ✅ Completo | Reutilizar para notificações |
| **Validadores** | ✅ 15+ validadores | Adicionar validadores específicos |
| **Máscaras de input** | ✅ Completo | Adicionar máscara ISBN |
| **Components reutilizáveis** | ✅ Modal, Gallery | Reutilizar em views Biblix |
| **Macros de formulário** | ✅ Completo | Reutilizar em forms |
| **Logger** | ✅ Profissional | Usar para auditoria |
| **Email service** | ✅ Integrado | Notificações de empréstimo |
| **Auth decorator** | ✅ Completo | Proteger rotas por perfil |

---

## 3. REQUISITOS FUNCIONAIS - ANÁLISE DE GAP

### 3.1. Requisitos de Alta Prioridade

#### **RF1**: Sistema de perfis hierárquicos
- **Especificação:** Anônimo → Usuário → Leitor/Bibliotecário/Admin
- **Status Atual:** 🟡 Parcial (tem Admin, Cliente, Vendedor)
- **Gap:** Substituir perfis atuais por Leitor, Bibliotecário, Admin
- **Esforço:** 2h

#### **RF2**: Visitantes anônimos podem buscar livros
- **Especificação:** Buscar no acervo, ver detalhes, criar conta, login
- **Status Atual:** 🔴 Não implementado
- **Gap:** Criar view pública de catálogo com busca e filtros
- **Esforço:** 8h

#### **RF3**: Usuários autenticados podem fazer logout
- **Especificação:** Funcionalidade de logout
- **Status Atual:** ✅ Implementado
- **Gap:** Nenhum
- **Esforço:** 0h

#### **RF4**: Leitores podem gerenciar empréstimos e reservas
- **Especificação:**
  - Reservar livros
  - Consultar reservas
  - Cancelar reservas
  - Consultar empréstimos
  - Renovar empréstimos
  - Devolver livros

- **Status Atual:** 🔴 Nenhuma funcionalidade implementada
- **Gap:** Criar todo o módulo de gestão do leitor
- **Esforço:** 24h

#### **RF5**: Bibliotecários podem gerenciar operações
- **Especificação:**
  - Registrar empréstimos
  - Registrar devoluções
  - Consultar reservas
  - Consultar empréstimos
  - Gerenciar livros (CRUD)
  - Gerenciar leitores

- **Status Atual:** 🔴 Nenhuma funcionalidade implementada
- **Gap:** Criar todo o módulo de gestão do bibliotecário
- **Esforço:** 32h

#### **RF6**: Administradores têm controle total
- **Especificação:**
  - Manter bibliotecários (CRUD)
  - Realizar backup
  - Restaurar backup

- **Status Atual:** 🟡 Existe CRUD de usuários admin
- **Gap:** Adicionar funcionalidades de backup/restore
- **Esforço:** 12h

### 3.2. Requisitos de Média Prioridade

#### **RF7**: Alterar senha e perfil
- **Status Atual:** ✅ Implementado (rota /perfil)
- **Gap:** Nenhum
- **Esforço:** 0h

#### **RF8**: Recuperação de senha
- **Status Atual:** ✅ Implementado
- **Gap:** Nenhum
- **Esforço:** 0h

#### **RF9**: Sistema de mensagens internas
- **Especificação:** Leitores e bibliotecários trocam mensagens
- **Status Atual:** 🔴 Não existe
- **Gap:** Criar sistema completo de mensagens
- **Esforço:** 20h

#### **RF10**: Bibliotecários gerenciam autores e categorias
- **Especificação:** CRUD de autores e categorias + estatísticas
- **Status Atual:** 🔴 Não implementado
- **Gap:** Criar CRUDs + dashboard de estatísticas
- **Esforço:** 16h

#### **RF11**: Administradores alteram configurações
- **Especificação:** Configurações do sistema + estatísticas
- **Status Atual:** 🟡 Existe configuração_model/repo
- **Gap:** Criar interface de configuração + dashboard admin
- **Esforço:** 12h

### 3.3. Requisitos de Baixa Prioridade

#### **RF12**: Favoritar livros
- **Especificação:** Leitores podem favoritar/desfavoritar
- **Status Atual:** 🔴 Não existe
- **Gap:** Criar tabela favoritos + funcionalidade
- **Esforço:** 6h

#### **RF13**: Moderação de leitores
- **Especificação:** Bibliotecários podem moderar leitores
- **Status Atual:** 🔴 Não existe
- **Gap:** Adicionar campos de status/bloqueio + interface
- **Esforço:** 8h

---

## 4. MODELO DE DADOS - ANÁLISE DE GAP

### 4.1. Diagrama ER Proposto (PDF)

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Usuario   │       │    Livro     │       │    Autor    │
├─────────────┤       ├──────────────┤       ├─────────────┤
│ id          │       │ id           │       │ id          │
│ nome        │◄──┐   │ titulo       │       │ nome        │
│ email       │   │   │ data_pub     │       │ biografia   │
│ senha       │   │   │ sinopse      │       │ data_nasc   │
│ perfil      │   │   └──────────────┘       └─────────────┘
│ ...         │   │         │ ▲                     │ ▲
└─────────────┘   │         │ │                     │ │
                  │         │ │                     │ │
        ┌─────────┴────┐    │ │    ┌───────────────┴─┴──────┐
        │ Emprestimo   │    │ │    │   LivroAutor (N:N)     │
        ├──────────────┤    │ │    ├────────────────────────┤
        │ id           │    │ │    │ id_livro               │
        │ id_livro     │────┘ │    │ id_autor               │
        │ id_leitor    │──────┘    └────────────────────────┘
        │ data_retirada│
        │ data_devoluc │              ┌─────────────┐
        └──────────────┘              │  Categoria  │
                                      ├─────────────┤
        ┌─────────────┐               │ id          │
        │   Reserva   │               │ nome        │
        ├─────────────┤               └─────────────┘
        │ id          │                     │ ▲
        │ id_livro    │────┐                │ │
        │ id_leitor   │───┐│   ┌────────────┴─┴──────────┐
        │ data_reserva│   ││   │  LivroCategoria (N:N)  │
        │ data_desej  │   ││   ├────────────────────────┤
        └─────────────┘   ││   │ id_livro               │
                          ││   │ id_categoria           │
                          ││   └────────────────────────┘
                          │└──────────┘
                          └───────────┘
```

### 4.2. Tabelas a Criar/Modificar

#### 4.2.1. ✅ **Tabela usuario** - EXISTENTE (verificar campos)
```sql
CREATE TABLE usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL,
    data_nascimento TEXT,           -- ADICIONAR
    telefone TEXT,                  -- ADICIONAR
    endereco TEXT,                  -- ADICIONAR
    confirmado INTEGER DEFAULT 1,   -- ADICIONAR (verificação email)
    bloqueado INTEGER DEFAULT 0,    -- ADICIONAR (moderação)
    token_redefinicao TEXT,
    data_token TEXT,
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.2. 🔴 **Tabela autor** - CRIAR
```sql
CREATE TABLE autor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    biografia TEXT,
    data_nascimento TEXT,
    foto_url TEXT,
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.3. 🔴 **Tabela categoria** - CRIAR
```sql
CREATE TABLE categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.4. 🟡 **Tabela livro** - COMPLETAR
```sql
CREATE TABLE livro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    subtitulo TEXT,                         -- ADICIONAR
    isbn TEXT UNIQUE,                        -- ADICIONAR
    editora TEXT,                            -- ADICIONAR
    ano_publicacao INTEGER,                  -- MODIFICAR (era datetime)
    sinopse TEXT,
    capa_url TEXT,                           -- ADICIONAR
    quantidade_total INTEGER DEFAULT 1,      -- ADICIONAR
    quantidade_disponivel INTEGER DEFAULT 1, -- ADICIONAR
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
);
```

#### 4.2.5. 🔴 **Tabela livro_autor** - CRIAR (N:N)
```sql
CREATE TABLE livro_autor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_autor INTEGER NOT NULL,
    FOREIGN KEY (id_livro) REFERENCES livro(id) ON DELETE CASCADE,
    FOREIGN KEY (id_autor) REFERENCES autor(id) ON DELETE CASCADE,
    UNIQUE(id_livro, id_autor)
);
```

#### 4.2.6. 🔴 **Tabela livro_categoria** - CRIAR (N:N)
```sql
CREATE TABLE livro_categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_categoria INTEGER NOT NULL,
    FOREIGN KEY (id_livro) REFERENCES livro(id) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id) ON DELETE CASCADE,
    UNIQUE(id_livro, id_categoria)
);
```

#### 4.2.7. 🟡 **Tabela emprestimo** - COMPLETAR
```sql
CREATE TABLE emprestimo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_leitor INTEGER NOT NULL,
    id_bibliotecario INTEGER,                -- ADICIONAR
    data_emprestimo TEXT NOT NULL,           -- RENOMEAR (era data_retirada)
    data_devolucao_prevista TEXT NOT NULL,   -- ADICIONAR
    data_devolucao_real TEXT,                -- RENOMEAR (era data_devolucao)
    renovacoes INTEGER DEFAULT 0,            -- ADICIONAR
    status TEXT DEFAULT 'ativo',             -- ADICIONAR (ativo/devolvido/atrasado)
    observacoes TEXT,                        -- ADICIONAR
    FOREIGN KEY (id_livro) REFERENCES livro(id),
    FOREIGN KEY (id_leitor) REFERENCES usuario(id),
    FOREIGN KEY (id_bibliotecario) REFERENCES usuario(id)
);
```

#### 4.2.8. 🟡 **Tabela reserva** - COMPLETAR
```sql
CREATE TABLE reserva (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_leitor INTEGER NOT NULL,
    data_reserva TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,  -- RENOMEAR
    data_desejada TEXT,                      -- RENOMEAR (era data_reserva)
    data_expiracao TEXT,                     -- ADICIONAR
    status TEXT DEFAULT 'ativa',             -- MANTER (ativa/cancelada/atendida)
    notificado INTEGER DEFAULT 0,            -- ADICIONAR
    FOREIGN KEY (id_livro) REFERENCES livro(id),
    FOREIGN KEY (id_leitor) REFERENCES usuario(id)
);
```

#### 4.2.9. 🔴 **Tabela favoritos** - CRIAR (RF12)
```sql
CREATE TABLE favoritos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_leitor INTEGER NOT NULL,
    data_favoritado TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_livro) REFERENCES livro(id) ON DELETE CASCADE,
    FOREIGN KEY (id_leitor) REFERENCES usuario(id) ON DELETE CASCADE,
    UNIQUE(id_livro, id_leitor)
);
```

#### 4.2.10. 🔴 **Tabela mensagens** - CRIAR (RF9)
```sql
CREATE TABLE mensagem (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_remetente INTEGER NOT NULL,
    id_destinatario INTEGER NOT NULL,
    assunto TEXT NOT NULL,
    corpo TEXT NOT NULL,
    lida INTEGER DEFAULT 0,
    data_envio TEXT DEFAULT CURRENT_TIMESTAMP,
    data_leitura TEXT,
    FOREIGN KEY (id_remetente) REFERENCES usuario(id),
    FOREIGN KEY (id_destinatario) REFERENCES usuario(id)
);
```

### 4.3. Índices Necessários

```sql
-- Performance em buscas frequentes
CREATE INDEX idx_livro_titulo ON livro(titulo);
CREATE INDEX idx_livro_isbn ON livro(isbn);
CREATE INDEX idx_usuario_email ON usuario(email);
CREATE INDEX idx_emprestimo_leitor ON emprestimo(id_leitor);
CREATE INDEX idx_emprestimo_status ON emprestimo(status);
CREATE INDEX idx_reserva_leitor ON reserva(id_leitor);
CREATE INDEX idx_reserva_status ON reserva(status);
CREATE INDEX idx_mensagem_destinatario ON mensagem(id_destinatario, lida);
```

---

## 5. ROTAS E ENDPOINTS - ANÁLISE DE GAP

### 5.1. Rotas Públicas (Anônimo) - RF2

| Endpoint | Método | Funcionalidade | Status |
|----------|--------|----------------|--------|
| `/` | GET | Home pública com catálogo | 🔴 Criar |
| `/livros` | GET | Listagem de livros | 🔴 Criar |
| `/livros/buscar` | GET | Busca no acervo | 🔴 Criar |
| `/livros/{id}` | GET | Detalhes do livro | 🔴 Criar |
| `/cadastro` | GET/POST | Criar conta (Leitor) | 🟡 Adaptar existente |
| `/login` | GET/POST | Login | ✅ Existe |

### 5.2. Rotas de Leitor (Autenticado) - RF4

| Endpoint | Método | Funcionalidade | Status |
|----------|--------|----------------|--------|
| `/leitor/emprestimos` | GET | Listar meus empréstimos | 🔴 Criar |
| `/leitor/emprestimos/{id}/renovar` | POST | Renovar empréstimo | 🔴 Criar |
| `/leitor/emprestimos/{id}/devolver` | POST | Devolver livro | 🔴 Criar |
| `/leitor/reservas` | GET | Listar minhas reservas | 🔴 Criar |
| `/leitor/reservas/criar` | POST | Criar reserva | 🔴 Criar |
| `/leitor/reservas/{id}/cancelar` | POST | Cancelar reserva | 🔴 Criar |
| `/leitor/favoritos` | GET | Listar favoritos | 🔴 Criar |
| `/leitor/favoritos/{id}/adicionar` | POST | Favoritar livro | 🔴 Criar |
| `/leitor/favoritos/{id}/remover` | POST | Desfavoritar livro | 🔴 Criar |
| `/leitor/mensagens` | GET | Listar mensagens | 🔴 Criar |
| `/leitor/mensagens/enviar` | POST | Enviar mensagem | 🔴 Criar |
| `/leitor/mensagens/{id}` | GET | Ler mensagem | 🔴 Criar |

### 5.3. Rotas de Bibliotecário - RF5, RF10

| Endpoint | Método | Funcionalidade | Status |
|----------|--------|----------------|--------|
| `/bibliotecario/emprestimos` | GET | Listar todos empréstimos | 🔴 Criar |
| `/bibliotecario/emprestimos/registrar` | GET/POST | Registrar empréstimo | 🔴 Criar |
| `/bibliotecario/emprestimos/{id}/devolver` | POST | Registrar devolução | 🔴 Criar |
| `/bibliotecario/reservas` | GET | Consultar todas reservas | 🔴 Criar |
| `/bibliotecario/livros` | GET | Listar livros (gestão) | 🔴 Criar |
| `/bibliotecario/livros/cadastrar` | GET/POST | Cadastrar livro | 🔴 Criar |
| `/bibliotecario/livros/{id}/editar` | GET/POST | Editar livro | 🔴 Criar |
| `/bibliotecario/livros/{id}/excluir` | POST | Excluir livro | 🔴 Criar |
| `/bibliotecario/autores` | GET | Listar autores | 🔴 Criar |
| `/bibliotecario/autores/cadastrar` | GET/POST | Cadastrar autor | 🔴 Criar |
| `/bibliotecario/autores/{id}/editar` | GET/POST | Editar autor | 🔴 Criar |
| `/bibliotecario/autores/{id}/excluir` | POST | Excluir autor | 🔴 Criar |
| `/bibliotecario/categorias` | GET | Listar categorias | 🔴 Criar |
| `/bibliotecario/categorias/cadastrar` | GET/POST | Cadastrar categoria | 🔴 Criar |
| `/bibliotecario/categorias/{id}/editar` | GET/POST | Editar categoria | 🔴 Criar |
| `/bibliotecario/categorias/{id}/excluir` | POST | Excluir categoria | 🔴 Criar |
| `/bibliotecario/leitores` | GET | Gerenciar leitores | 🔴 Criar |
| `/bibliotecario/leitores/{id}/moderar` | POST | Moderar leitor | 🔴 Criar |
| `/bibliotecario/estatisticas` | GET | Dashboard de estatísticas | 🔴 Criar |
| `/bibliotecario/mensagens` | GET | Sistema de mensagens | 🔴 Criar |

### 5.4. Rotas de Administrador - RF6, RF11

| Endpoint | Método | Funcionalidade | Status |
|----------|--------|----------------|--------|
| `/admin/bibliotecarios` | GET | Listar bibliotecários | 🔴 Criar |
| `/admin/bibliotecarios/cadastrar` | GET/POST | Cadastrar bibliotecário | 🔴 Criar |
| `/admin/bibliotecarios/{id}/editar` | GET/POST | Editar bibliotecário | 🔴 Criar |
| `/admin/bibliotecarios/{id}/excluir` | POST | Excluir bibliotecário | 🔴 Criar |
| `/admin/configuracoes` | GET/POST | Configurações do sistema | 🟡 Adaptar |
| `/admin/backup` | GET | Página de backup | 🔴 Criar |
| `/admin/backup/executar` | POST | Realizar backup | 🔴 Criar |
| `/admin/backup/restaurar` | POST | Restaurar backup | 🔴 Criar |
| `/admin/estatisticas` | GET | Dashboard administrativo | 🔴 Criar |

### 5.5. Rotas Comuns (Autenticados) - RF7, RF8, RF9

| Endpoint | Método | Funcionalidade | Status |
|----------|--------|----------------|--------|
| `/perfil` | GET | Ver/editar perfil | ✅ Existe |
| `/perfil/alterar-senha` | POST | Alterar senha | ✅ Existe |
| `/perfil/foto` | POST | Upload foto | ✅ Existe |
| `/recuperar-senha` | GET/POST | Recuperação de senha | ✅ Existe |
| `/logout` | GET | Logout | ✅ Existe |

---

## 6. VIEWS E INTERFACES - ANÁLISE DE GAP

### 6.1. Templates a Criar/Adaptar

#### 6.1.1. 🔴 **Templates Públicos** (Anônimo)
```
templates/
├── public/
│   ├── home.html                    # Home com catálogo em destaque
│   ├── catalogo.html                # Listagem completa de livros
│   ├── livro_detalhes.html          # Detalhes de um livro
│   └── sobre.html                   # Sobre a biblioteca
```

#### 6.1.2. 🔴 **Templates de Leitor**
```
templates/
├── leitor/
│   ├── dashboard.html               # Dashboard do leitor
│   ├── meus_emprestimos.html        # Lista de empréstimos
│   ├── minhas_reservas.html         # Lista de reservas
│   ├── favoritos.html               # Livros favoritados
│   ├── mensagens/
│   │   ├── inbox.html               # Caixa de entrada
│   │   ├── ler.html                 # Ler mensagem
│   │   └── enviar.html              # Enviar mensagem
```

#### 6.1.3. 🔴 **Templates de Bibliotecário**
```
templates/
├── bibliotecario/
│   ├── dashboard.html               # Dashboard do bibliotecário
│   ├── emprestimos/
│   │   ├── listar.html              # Todos os empréstimos
│   │   ├── registrar.html           # Registrar novo empréstimo
│   │   └── devolver.html            # Registrar devolução
│   ├── reservas/
│   │   └── listar.html              # Todas as reservas
│   ├── livros/
│   │   ├── listar.html              # Gestão de livros
│   │   ├── cadastrar.html           # Cadastrar livro
│   │   └── editar.html              # Editar livro
│   ├── autores/
│   │   ├── listar.html
│   │   ├── cadastrar.html
│   │   └── editar.html
│   ├── categorias/
│   │   ├── listar.html
│   │   ├── cadastrar.html
│   │   └── editar.html
│   ├── leitores/
│   │   ├── listar.html              # Gerenciar leitores
│   │   └── moderar.html             # Moderar leitor
│   ├── estatisticas.html            # Relatórios e gráficos
│   └── mensagens/
│       ├── inbox.html
│       └── enviar.html
```

#### 6.1.4. 🔴 **Templates de Administrador**
```
templates/
├── admin/
│   ├── dashboard.html               # Dashboard administrativo
│   ├── bibliotecarios/
│   │   ├── listar.html
│   │   ├── cadastrar.html
│   │   └── editar.html
│   ├── backup/
│   │   └── index.html               # Backup e restore
│   ├── configuracoes/
│   │   └── index.html               # Configurações do sistema
│   └── estatisticas.html            # Estatísticas globais
```

#### 6.1.5. ✅ **Templates Reutilizáveis (Já existem)**
```
templates/
├── base_publica.html                # ✅ Layout público
├── base_privada.html                # ✅ Layout autenticado
├── auth/                            # ✅ Login, cadastro, recuperação
├── perfil/                          # ✅ Perfil de usuário
├── components/                      # ✅ Componentes reutilizáveis
│   ├── modal_confirmacao.html
│   ├── modal_crop_imagem.html
│   └── photo_gallery.html
├── macros/                          # ✅ Macros de formulário
│   └── form_fields.html
└── errors/                          # ✅ Páginas de erro
    ├── 404.html
    └── 500.html
```

### 6.2. Componentes Novos a Criar

#### 6.2.1. 🔴 **Card de Livro** (Reutilizável)
```html
<!-- templates/components/card_livro.html -->
Exibir: capa, título, autor(es), categoria, disponibilidade
Ações: Ver detalhes, Reservar, Favoritar
```

#### 6.2.2. 🔴 **Badge de Status** (Macro)
```html
<!-- templates/macros/badges.html -->
- Status de empréstimo: Ativo, Devolvido, Atrasado
- Status de reserva: Ativa, Cancelada, Atendida
- Status de disponibilidade: Disponível, Emprestado, Reservado
```

#### 6.2.3. 🔴 **Tabela de Empréstimos** (Componente)
```html
<!-- templates/components/tabela_emprestimos.html -->
Colunas: Livro, Leitor, Data Empréstimo, Data Prevista, Status, Ações
Filtros: Por status, por período, por leitor
```

---

## 7. VALIDADORES E DTOs - ANÁLISE DE GAP

### 7.1. Validadores Existentes (Reutilizáveis)

✅ **Já disponíveis em dtos/validators.py:**
- `validar_email()`
- `validar_senha_forte()`
- `validar_string_obrigatoria()`
- `validar_comprimento()`
- `validar_data()`
- `validar_data_futura()`
- `validar_data_passada()`
- `validar_inteiro_positivo()`
- `validar_decimal_positivo()`

### 7.2. Validadores a Adicionar

#### 7.2.1. 🔴 **Validador de ISBN**
```python
def validar_isbn():
    """Valida ISBN-10 ou ISBN-13"""
    def validador(v: str) -> str:
        # Implementar validação de ISBN
        pass
    return validador
```

#### 7.2.2. 🔴 **Validador de Data de Publicação**
```python
def validar_ano_publicacao():
    """Valida ano entre 1000 e ano atual"""
    def validador(v: int) -> int:
        ano_atual = datetime.now().year
        if not (1000 <= v <= ano_atual):
            raise ValueError(f"Ano deve estar entre 1000 e {ano_atual}")
        return v
    return validador
```

### 7.3. DTOs a Criar

#### 7.3.1. 🔴 **Livro DTOs**
```python
# dtos/livro_dto.py
class LivroCriarDTO(BaseModel):
    titulo: str
    subtitulo: Optional[str]
    isbn: Optional[str]
    editora: Optional[str]
    ano_publicacao: int
    sinopse: str
    quantidade_total: int
    autores: List[int]  # IDs dos autores
    categorias: List[int]  # IDs das categorias
    # Validadores específicos

class LivroAlterarDTO(BaseModel):
    # Campos editáveis
    pass

class LivroFiltroDTO(BaseModel):
    # Para busca e filtros
    titulo: Optional[str]
    autor: Optional[str]
    categoria: Optional[int]
    ano_inicio: Optional[int]
    ano_fim: Optional[int]
```

#### 7.3.2. 🔴 **Emprestimo DTOs**
```python
# dtos/emprestimo_dto.py
class EmprestimoCriarDTO(BaseModel):
    id_livro: int
    id_leitor: int
    prazo_dias: int = 14  # Configurável
    # Validadores

class EmprestimoRenovarDTO(BaseModel):
    id_emprestimo: int
    # Validação: limite de renovações

class EmprestimoDevolverDTO(BaseModel):
    id_emprestimo: int
    observacoes: Optional[str]
```

#### 7.3.3. 🔴 **Reserva DTOs**
```python
# dtos/reserva_dto.py
class ReservaCriarDTO(BaseModel):
    id_livro: int
    data_desejada: Optional[date]
    # Validadores

class ReservaCancelarDTO(BaseModel):
    id_reserva: int
    motivo: Optional[str]
```

#### 7.3.4. 🔴 **Autor e Categoria DTOs**
```python
# dtos/autor_dto.py
class AutorCriarDTO(BaseModel):
    nome: str
    biografia: Optional[str]
    data_nascimento: Optional[date]

# dtos/categoria_dto.py
class CategoriaCriarDTO(BaseModel):
    nome: str
    descricao: Optional[str]
```

#### 7.3.5. 🔴 **Mensagem DTO**
```python
# dtos/mensagem_dto.py
class MensagemEnviarDTO(BaseModel):
    id_destinatario: int
    assunto: str
    corpo: str
    # Validadores
```

---

## 8. ESTATÍSTICAS E RELATÓRIOS

### 8.1. Dashboard do Leitor

**Indicadores necessários:**
- 📊 Empréstimos ativos (quantidade)
- 📊 Empréstimos próximos ao vencimento
- 📊 Empréstimos atrasados (se houver)
- 📊 Reservas ativas
- 📊 Histórico de leituras (total)
- 📊 Livros favoritos (quantidade)

**Queries SQL a implementar:**
```sql
-- Empréstimos ativos do leitor
SELECT COUNT(*) FROM emprestimo
WHERE id_leitor = ? AND status = 'ativo';

-- Empréstimos próximos ao vencimento (3 dias)
SELECT * FROM emprestimo
WHERE id_leitor = ?
  AND status = 'ativo'
  AND date(data_devolucao_prevista) BETWEEN date('now') AND date('now', '+3 days');

-- etc.
```

### 8.2. Dashboard do Bibliotecário

**Indicadores necessários:**
- 📊 Empréstimos ativos (total)
- 📊 Empréstimos atrasados (total)
- 📊 Devoluções do dia
- 📊 Reservas pendentes
- 📊 Livros mais emprestados (top 10)
- 📊 Leitores mais ativos (top 10)
- 📊 Livros indisponíveis
- 📊 Gráfico de empréstimos por mês

### 8.3. Dashboard do Administrador

**Indicadores necessários:**
- 📊 Total de livros no acervo
- 📊 Total de leitores cadastrados
- 📊 Total de empréstimos (histórico)
- 📊 Taxa de ocupação do acervo
- 📊 Gráfico de crescimento (leitores, empréstimos)
- 📊 Estatísticas por categoria
- 📊 Relatório de backup (último, próximo)

---

## 9. SISTEMA DE NOTIFICAÇÕES

### 9.1. Emails a Implementar (util/email_service.py)

#### ✅ **Já existem (reutilizar):**
- `enviar_email_boas_vindas()` - Após cadastro
- `enviar_email_recuperacao_senha()` - Recuperação de senha

#### 🔴 **A criar:**

```python
def enviar_email_emprestimo_confirmado(email, nome, livro, data_devolucao):
    """Confirmação de empréstimo"""
    pass

def enviar_email_devolucao_proxima(email, nome, livro, dias_restantes):
    """Lembrete de devolução (3 dias antes)"""
    pass

def enviar_email_emprestimo_atrasado(email, nome, livro, dias_atraso):
    """Notificação de atraso"""
    pass

def enviar_email_reserva_disponivel(email, nome, livro):
    """Livro reservado está disponível"""
    pass

def enviar_email_reserva_cancelada(email, nome, livro, motivo):
    """Reserva cancelada"""
    pass
```

### 9.2. Notificações In-App (Flash Messages)

**Já implementado** ✅ - Reutilizar:
- `informar_sucesso()`
- `informar_erro()`
- `informar_aviso()`
- `informar_info()`

---

## 10. SISTEMA DE BACKUP (RF6)

### 10.1. Funcionalidades Necessárias

#### 🔴 **Criar módulo util/backup_util.py:**

```python
def realizar_backup() -> str:
    """
    Realiza backup do banco de dados.
    Returns: caminho do arquivo de backup
    """
    # Copiar database.db para backups/backup_YYYYMMDD_HHMMSS.db
    # Compactar (zip)
    # Retornar caminho
    pass

def listar_backups() -> List[dict]:
    """
    Lista todos os backups disponíveis.
    Returns: [{nome, data, tamanho, caminho}]
    """
    pass

def restaurar_backup(caminho: str):
    """
    Restaura um backup.
    CUIDADO: Sobrescreve o banco atual!
    """
    # Validar arquivo
    # Parar aplicação (se possível) ou avisar
    # Copiar backup para database.db
    # Reiniciar aplicação
    pass

def excluir_backups_antigos(dias: int = 30):
    """Remove backups com mais de X dias"""
    pass
```

#### 🔴 **Criar job agendado (opcional):**
```python
# util/scheduler.py
# Usar APScheduler para backup automático diário
```

---

## 11. CONFIGURAÇÕES DO SISTEMA (RF11)

### 11.1. Configurações Necessárias

#### 🟡 **Expandir tabela configuracao:**

```sql
-- Adicionar configs específicas Biblix
INSERT INTO configuracao (chave, valor) VALUES
('biblix_prazo_emprestimo_dias', '14'),
('biblix_limite_renovacoes', '2'),
('biblix_dias_aviso_devolucao', '3'),
('biblix_dias_expiracao_reserva', '7'),
('biblix_permitir_renovacao', 'true'),
('biblix_permitir_reserva', 'true'),
('biblix_emprestimos_simultaneos_leitor', '3'),
('biblix_backup_automatico', 'true'),
('biblix_backup_horario', '02:00'),
('biblix_email_notificacoes', 'true'),
('biblix_biblioteca_nome', 'Biblioteca'),
('biblix_biblioteca_email', 'biblioteca@example.com'),
('biblix_biblioteca_telefone', '(00) 0000-0000'),
('biblix_biblioteca_endereco', '');
```

#### 🔴 **Interface de configuração:**
- Template: `admin/configuracoes/index.html`
- Formulário para editar cada configuração
- Validação de tipos (int, bool, string)
- Cache das configurações (util/config_cache.py - já existe)

---

## 12. LIMPEZA DO CÓDIGO BASE

### 12.1. Arquivos/Módulos a Remover

#### ⚠️ **Templates de exemplo (remover):**
```
templates/examples/       # Todos os exemplos
templates/tarefas/        # CRUD de exemplo
```

#### ⚠️ **Rotas de exemplo (remover):**
```
routes/examples_routes.py # Exemplos
routes/tarefas_routes.py  # CRUD de exemplo
```

#### ⚠️ **Models/Repos de exemplo (remover):**
```
model/tarefa_model.py
repo/tarefa_repo.py
sql/tarefa_sql.py
dtos/tarefa_dto.py
```

#### ⚠️ **Atualizar main.py:**
- Remover imports de exemplos
- Remover criação de tabela tarefa
- Remover include de routers de exemplo

---

## 13. ESTIMATIVA DE ESFORÇO

### 13.1. Resumo por Componente

| Componente | Esforço (horas) | Prioridade | Dependências |
|------------|-----------------|------------|--------------|
| **1. Ajuste de Perfis** | 2h | Alta | - |
| **2. Modelos de Dados** | 8h | Alta | - |
| **3. SQL Scripts** | 6h | Alta | Models |
| **4. Repositories** | 12h | Alta | SQLs |
| **5. DTOs e Validadores** | 8h | Alta | Models |
| **6. Rotas Públicas** | 8h | Alta | Repos |
| **7. Rotas de Leitor** | 24h | Alta | Repos |
| **8. Rotas de Bibliotecário** | 32h | Alta | Repos |
| **9. Rotas de Administrador** | 12h | Alta | Repos |
| **10. Templates Públicos** | 12h | Média | Rotas |
| **11. Templates de Leitor** | 16h | Média | Rotas |
| **12. Templates de Bibliotecário** | 24h | Média | Rotas |
| **13. Templates de Admin** | 8h | Média | Rotas |
| **14. Sistema de Mensagens** | 20h | Média | Repos |
| **15. Estatísticas e Dashboards** | 16h | Média | Repos |
| **16. Sistema de Backup** | 12h | Média | - |
| **17. Sistema de Notificações Email** | 8h | Baixa | - |
| **18. Favoritos** | 6h | Baixa | Repos |
| **19. Testes** | 24h | Alta | Tudo |
| **20. Documentação** | 8h | Média | Tudo |
| **21. Ajustes e Refinamentos** | 16h | Média | Tudo |

**TOTAL ESTIMADO: 262 horas (~6-7 semanas em tempo integral)**

### 13.2. Divisão em Sprints (Sugestão)

#### **Sprint 1 (40h) - Fundação**
- Ajuste de perfis
- Modelos de dados completos
- SQL scripts
- Repositories básicos
- DTOs e validadores

**Entrega:** Backend básico funcionando

#### **Sprint 2 (40h) - Funcionalidades de Leitor**
- Rotas de leitor
- Templates de leitor
- Sistema de reservas
- Sistema de favoritos

**Entrega:** Leitor pode gerenciar empréstimos e reservas

#### **Sprint 3 (48h) - Funcionalidades de Bibliotecário**
- Rotas de bibliotecário
- Templates de bibliotecário
- CRUD de livros, autores, categorias
- Gestão de empréstimos e devoluções

**Entrega:** Bibliotecário pode gerenciar todo o acervo

#### **Sprint 4 (32h) - Funcionalidades Administrativas**
- Rotas de admin
- Templates de admin
- Sistema de backup
- Configurações do sistema

**Entrega:** Admin tem controle total do sistema

#### **Sprint 5 (32h) - Funcionalidades Complementares**
- Sistema de mensagens
- Estatísticas e dashboards
- Notificações por email
- Área pública (catálogo)

**Entrega:** Sistema completo com todos os RFs

#### **Sprint 6 (40h) - Qualidade**
- Testes automatizados
- Correções de bugs
- Refinamentos de UX
- Documentação
- Otimizações de performance

**Entrega:** Sistema pronto para produção

#### **Sprint 7 (30h) - Polimento Final**
- Ajustes finais
- Deploy
- Treinamento
- Migração de dados (se houver)

**Entrega:** Sistema em produção

---

## 14. PRÓXIMOS PASSOS RECOMENDADOS

### 14.1. Ordem de Implementação Sugerida

1. **Começar pelo backend (prioridade alta):**
   - ✅ Ajustar perfis em util/perfis.py
   - ✅ Completar todos os models
   - ✅ Criar todos os SQL scripts
   - ✅ Implementar repositories
   - ✅ Criar DTOs e validadores

2. **Implementar funcionalidades core:**
   - ✅ Rotas e templates de leitor (empréstimos, reservas)
   - ✅ Rotas e templates de bibliotecário (gestão)
   - ✅ Rotas e templates de admin

3. **Adicionar funcionalidades complementares:**
   - ✅ Sistema de mensagens
   - ✅ Estatísticas
   - ✅ Backup
   - ✅ Notificações

4. **Área pública:**
   - ✅ Catálogo público
   - ✅ Busca de livros
   - ✅ Detalhes de livro

5. **Qualidade:**
   - ✅ Testes automatizados
   - ✅ Documentação
   - ✅ Refinamentos

### 14.2. Decisões Técnicas Necessárias

#### 🤔 **Definir antes de começar:**

1. **Prazo padrão de empréstimo:** 14 dias? 7 dias? 30 dias?
2. **Limite de renovações:** 0, 1, 2, ilimitado?
3. **Limite de empréstimos simultâneos por leitor:** 3? 5? ilimitado?
4. **Prazo de expiração de reserva:** 7 dias? Sem expiração?
5. **Envio de email:** Apenas lembretes ou todas as ações?
6. **Backup:** Automático diário? Manual? Horário?
7. **Multas por atraso:** Implementar? Apenas avisar?
8. **Fotos de livros:** Upload ou apenas URL?
9. **Autores:** Permitir cadastro rápido ao criar livro?
10. **Categorias:** Hierarquizadas (pais/filhos) ou planas?

---

## 15. RISCOS E DESAFIOS

### 15.1. Riscos Identificados

| Risco | Probabilidade | Impacto | Mitigação |
|-------|---------------|---------|-----------|
| **Mudança de requisitos** | Média | Alto | Documentar bem e usar sprints curtas |
| **Complexidade de relacionamentos N:N** | Baixa | Médio | Usar padrão já estabelecido no projeto |
| **Performance com muitos livros** | Média | Médio | Criar índices, paginação |
| **Gestão de estoque de livros** | Alta | Alto | Implementar transações atomicas |
| **Notificações por email não chegam** | Média | Baixo | Testar com múltiplos provedores |
| **Backup falhar** | Baixa | Alto | Implementar logs e validação |
| **Usuários não entenderem interface** | Média | Médio | UX simples, feedbacks claros |

### 15.2. Desafios Técnicos

1. **Controle de estoque de livros:**
   - Garantir que quantidade_disponivel nunca fique negativa
   - Usar transações SQL para atomicidade

2. **Reservas automáticas:**
   - Quando livro é devolvido, notificar próximo da fila de reserva
   - Implementar sistema de fila (FIFO)

3. **Cálculo de atrasos:**
   - Job diário para marcar empréstimos como atrasados
   - Envio de emails de lembrete

4. **Performance de busca:**
   - Implementar busca full-text ou usar LIKE otimizado
   - Considerar índices compostos

5. **Auditoria:**
   - Registrar quem fez cada ação (created_by, updated_by)
   - Log de operações críticas

---

## 16. CONSIDERAÇÕES FINAIS

### 16.1. Pontos Fortes do Projeto Atual

✅ **Infraestrutura sólida:** O DefaultWebApp fornece base excelente
✅ **Padrões definidos:** Arquitetura clara e bem documentada
✅ **Componentes reutilizáveis:** Economia de tempo significativa
✅ **Segurança:** Sistema de autenticação robusto
✅ **Validação:** Framework de validação completo
✅ **UI/UX:** Bootstrap + componentes prontos

### 16.2. Principais Gaps

🔴 **Funcionalidades de negócio:** 90% não implementadas
🔴 **Interfaces específicas:** 100% a criar
🟡 **Modelos de dados:** 40% completo
✅ **Base técnica:** 95% pronta

### 16.3. Viabilidade do Projeto

✅ **VIÁVEL** - O projeto é completamente viável e bem estruturado.

**Motivos:**
1. Base tecnológica sólida e madura
2. Requisitos bem definidos no PDF
3. Escopo controlado e realista
4. Equipe tem domínio das tecnologias
5. Riscos identificados e mitigáveis
6. Tempo estimado razoável (6-7 semanas)

### 16.4. Recomendação Final

**Recomenda-se proceder com a implementação seguindo:**

1. ✅ Usar abordagem incremental (sprints)
2. ✅ Começar pelo backend (base sólida)
3. ✅ Implementar funcionalidades core primeiro
4. ✅ Testar continuamente
5. ✅ Documentar durante o desenvolvimento
6. ✅ Fazer demos ao final de cada sprint

---

## APÊNDICES

### Apêndice A: Checklist de Implementação

Criar arquivo separado: `docs/CHECKLIST.md`

### Apêndice B: Padrões de Código

Seguir padrões já estabelecidos no DefaultWebApp (ver README.md e CLAUDE.md)

### Apêndice C: Diagrama de Classes

Criar após completar os models

### Apêndice D: Dicionário de Dados

Criar durante a implementação dos SQLs

---

**FIM DA ANÁLISE INICIAL**

---

**Elaborado por:** Claude Code (Anthropic)
**Revisão:** Aguardando validação da equipe
**Próxima etapa:** Criação do GUIA.md com passo a passo de implementação
