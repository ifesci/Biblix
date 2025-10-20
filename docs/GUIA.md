# GUIA DE IMPLEMENTAÇÃO - PROJETO BIBLIX

**Sistema de Gestão Inteligente de Empréstimo de Livros**

**Versão:** 1.0
**Data:** 20/10/2025
**Baseado em:** ANALISE_INICIAL.md e Biblix.pdf

---

## 📋 ÍNDICE

1. [Introdução](#1-introdução)
2. [Preparação do Ambiente](#2-preparação-do-ambiente)
3. [Sprint 1: Fundação do Sistema](#3-sprint-1-fundação-do-sistema)
4. [Sprint 2: Funcionalidades do Leitor](#4-sprint-2-funcionalidades-do-leitor)
5. [Sprint 3: Funcionalidades do Bibliotecário](#5-sprint-3-funcionalidades-do-bibliotecário)
6. [Sprint 4: Funcionalidades Administrativas](#6-sprint-4-funcionalidades-administrativas)
7. [Sprint 5: Funcionalidades Complementares](#7-sprint-5-funcionalidades-complementares)
8. [Sprint 6: Qualidade e Testes](#8-sprint-6-qualidade-e-testes)
9. [Apêndices](#9-apêndices)

---

## 1. INTRODUÇÃO

### 1.1. Sobre Este Guia

Este documento fornece um **passo a passo detalhado** para implementar o sistema Biblix, transformando o projeto atual (baseado no DefaultWebApp) na solução completa descrita no documento de especificação.

### 1.2. Pré-requisitos

Antes de começar, você deve:
- ✅ Ter lido o arquivo `ANALISE_INICIAL.md`
- ✅ Ter lido o arquivo `README.md` do projeto
- ✅ Ter o ambiente de desenvolvimento configurado
- ✅ Estar familiarizado com FastAPI, Jinja2 e SQLite
- ✅ Ter conhecimento básico de HTML/CSS/Bootstrap

### 1.3. Convenções deste Guia

```
📁 Arquivo/diretório a criar
📝 Arquivo a modificar
🔧 Código a implementar
⚠️ Atenção especial
💡 Dica útil
✅ Checklist
```

### 1.4. Estrutura de Cada Sprint

Cada sprint contém:
1. **Objetivo da sprint**
2. **Duração estimada**
3. **Passos detalhados**
4. **Código de exemplo**
5. **Como testar**
6. **Checklist de conclusão**

---

## 2. PREPARAÇÃO DO AMBIENTE

### 2.1. Limpeza do Código Base

Antes de começar, remover arquivos de exemplo do boilerplate.

#### Passo 1: Remover arquivos de exemplo

```bash
# Executar no terminal
rm -rf templates/examples
rm -rf templates/tarefas
rm routes/examples_routes.py
rm routes/tarefas_routes.py
rm model/tarefa_model.py
rm repo/tarefa_repo.py
rm sql/tarefa_sql.py
rm dtos/tarefa_dto.py
rm tests/test_tarefas.py
```

#### Passo 2: Atualizar main.py

📝 **Arquivo:** `main.py`

**Remover as linhas:**
```python
# Remover estes imports
from routes import tarefas_routes
from routes import examples_routes
import repo.tarefa_repo as tarefa_repo

# Remover estas linhas no startup
tarefa_repo.criar_tabela()
logger.info("Tabela 'tarefa' criada/verificada")

# Remover estes includes
app.include_router(tarefas_routes.router)
app.include_router(examples_routes.router)
```

#### Passo 3: Criar estrutura de diretórios para templates Biblix

```bash
# Executar no terminal
mkdir -p templates/public
mkdir -p templates/leitor/mensagens
mkdir -p templates/bibliotecario/emprestimos
mkdir -p templates/bibliotecario/reservas
mkdir -p templates/bibliotecario/livros
mkdir -p templates/bibliotecario/autores
mkdir -p templates/bibliotecario/categorias
mkdir -p templates/bibliotecario/leitores
mkdir -p templates/bibliotecario/mensagens
mkdir -p templates/admin/bibliotecarios
mkdir -p templates/admin/backup
mkdir -p templates/components/biblix
mkdir -p templates/macros/biblix
```

### 2.2. Checklist de Preparação

- [ ] Arquivos de exemplo removidos
- [ ] main.py atualizado
- [ ] Estrutura de diretórios criada
- [ ] Projeto rodando sem erros (`python main.py`)

---

## 3. SPRINT 1: FUNDAÇÃO DO SISTEMA

**Duração estimada:** 40 horas
**Objetivo:** Criar toda a base de dados e lógica de negócio

### 3.1. Ajustar Perfis de Usuário

#### Passo 1.1: Atualizar enum de perfis

📝 **Arquivo:** `util/perfis.py`

```python
from enum import Enum
from typing import Optional

class Perfil(str, Enum):
    """
    Enum centralizado para perfis de usuário do sistema Biblix.

    Este é a FONTE ÚNICA DA VERDADE para perfis no sistema.
    SEMPRE use este Enum ao referenciar perfis, NUNCA strings literais.

    Hierarquia de perfis:
    - Anônimo: Visitante não autenticado (não está no Enum)
    - Usuário: Qualquer pessoa autenticada (abstração)
    - Leitor: Usuário que pode emprestar livros
    - Bibliotecário: Gerencia empréstimos e acervo
    - Administrador: Controle total do sistema
    """

    # PERFIS DO BIBLIX ##########################################
    ADMIN = "Administrador"
    BIBLIOTECARIO = "Bibliotecário"
    LEITOR = "Leitor"
    # FIM DOS PERFIS ############################################

    def __str__(self) -> str:
        """Retorna o valor do perfil como string"""
        return self.value

    @classmethod
    def valores(cls) -> list[str]:
        """
        Retorna lista de todos os valores de perfis.

        Returns:
            Lista com os valores: ["Administrador", "Bibliotecário", "Leitor"]
        """
        return [perfil.value for perfil in cls]

    @classmethod
    def existe(cls, valor: str) -> bool:
        """
        Verifica se um valor de perfil é válido.

        Args:
            valor: String do perfil a validar

        Returns:
            True se o perfil existe, False caso contrário
        """
        return valor in cls.valores()

    @classmethod
    def from_string(cls, valor: str) -> Optional['Perfil']:
        """
        Converte uma string para o Enum Perfil correspondente.

        Args:
            valor: String do perfil

        Returns:
            Enum Perfil correspondente ou None se inválido
        """
        try:
            return cls(valor)
        except ValueError:
            return None

    @classmethod
    def validar(cls, valor: str) -> str:
        """
        Valida e retorna o valor do perfil, levantando exceção se inválido.

        Args:
            valor: String do perfil a validar

        Returns:
            O valor validado

        Raises:
            ValueError: Se o perfil não for válido
        """
        if not cls.existe(valor):
            raise ValueError(
                f'Perfil inválido: {valor}. '
                f'Use: {", ".join(cls.valores())}'
            )
        return valor
```

#### Passo 1.2: Atualizar seed de usuários

📝 **Arquivo:** `data/usuarios_seed.json`

```json
[
    {
        "nome": "Administrador do Sistema",
        "email": "admin@biblix.com",
        "senha": "1234aA@#",
        "perfil": "Administrador"
    },
    {
        "nome": "Maria Bibliotecária",
        "email": "maria.bib@biblix.com",
        "senha": "1234aA@#",
        "perfil": "Bibliotecário"
    },
    {
        "nome": "João Leitor",
        "email": "joao.leitor@biblix.com",
        "senha": "1234aA@#",
        "perfil": "Leitor"
    }
]
```

### 3.2. Criar/Atualizar Models

#### Passo 2.1: Atualizar Usuario Model

📝 **Arquivo:** `model/usuario_model.py`

```python
from dataclasses import dataclass
from typing import Optional
from util.perfis import Perfil

@dataclass
class Usuario:
    """
    Model de usuário do sistema Biblix.

    Attributes:
        id: Identificador único do usuário
        nome: Nome completo do usuário
        email: E-mail único do usuário
        senha: Hash da senha do usuário
        perfil: Perfil do usuário (Perfil.ADMIN, BIBLIOTECARIO ou LEITOR)
        data_nascimento: Data de nascimento (opcional)
        telefone: Telefone de contato (opcional)
        endereco: Endereço completo (opcional)
        confirmado: Se o email foi confirmado (default: True)
        bloqueado: Se o usuário está bloqueado (default: False)
        token_redefinicao: Token para redefinição de senha (opcional)
        data_token: Data de expiração do token (opcional)
        data_cadastro: Data de cadastro do usuário (opcional)

    Nota: A foto do usuário é armazenada em /static/img/usuarios/{id:06d}.jpg
          Use util.foto_util para manipular fotos de usuários.
    """
    id: int
    nome: str
    email: str
    senha: str
    perfil: str
    data_nascimento: Optional[str] = None
    telefone: Optional[str] = None
    endereco: Optional[str] = None
    confirmado: bool = True
    bloqueado: bool = False
    token_redefinicao: Optional[str] = None
    data_token: Optional[str] = None
    data_cadastro: Optional[str] = None
```

#### Passo 2.2: Completar Autor Model

📝 **Arquivo:** `model/autor_model.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Autor:
    """
    Model de autor de livros.

    Attributes:
        id: Identificador único do autor
        nome: Nome completo do autor
        biografia: Biografia/descrição do autor (opcional)
        data_nascimento: Data de nascimento do autor (opcional)
        foto_url: URL ou caminho da foto do autor (opcional)
        data_cadastro: Data de cadastro no sistema (opcional)
    """
    id: Optional[int]
    nome: str
    biografia: Optional[str] = None
    data_nascimento: Optional[str] = None
    foto_url: Optional[str] = None
    data_cadastro: Optional[str] = None
```

#### Passo 2.3: Completar Categoria Model

📝 **Arquivo:** `model/categoria_model.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Categoria:
    """
    Model de categoria de livros.

    Attributes:
        id: Identificador único da categoria
        nome: Nome da categoria
        descricao: Descrição da categoria (opcional)
        data_cadastro: Data de cadastro no sistema (opcional)
    """
    id: Optional[int]
    nome: str
    descricao: Optional[str] = None
    data_cadastro: Optional[str] = None
```

#### Passo 2.4: Completar Livro Model

📝 **Arquivo:** `model/livro_model.py`

```python
from dataclasses import dataclass
from typing import Optional, List

@dataclass
class Livro:
    """
    Model de livro do acervo.

    Attributes:
        id: Identificador único do livro
        titulo: Título do livro
        subtitulo: Subtítulo do livro (opcional)
        isbn: Código ISBN do livro (opcional)
        editora: Editora do livro (opcional)
        ano_publicacao: Ano de publicação
        sinopse: Sinopse/resumo do livro
        capa_url: URL ou caminho da imagem da capa (opcional)
        quantidade_total: Quantidade total de exemplares
        quantidade_disponivel: Quantidade disponível para empréstimo
        data_cadastro: Data de cadastro no sistema (opcional)

    Relacionamentos (preenchidos quando necessário):
        autores: Lista de autores do livro
        categorias: Lista de categorias do livro
    """
    id: Optional[int]
    titulo: str
    subtitulo: Optional[str] = None
    isbn: Optional[str] = None
    editora: Optional[str] = None
    ano_publicacao: int = 2025
    sinopse: str = ""
    capa_url: Optional[str] = None
    quantidade_total: int = 1
    quantidade_disponivel: int = 1
    data_cadastro: Optional[str] = None

    # Relacionamentos (carregados quando necessário)
    autores: Optional[List] = None  # List[Autor]
    categorias: Optional[List] = None  # List[Categoria]
```

#### Passo 2.5: Completar Emprestimo Model

📝 **Arquivo:** `model/emprestimo_model.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Emprestimo:
    """
    Model de empréstimo de livro.

    Attributes:
        id: Identificador único do empréstimo
        id_livro: ID do livro emprestado
        id_leitor: ID do leitor que pegou emprestado
        id_bibliotecario: ID do bibliotecário que registrou (opcional)
        data_emprestimo: Data/hora em que o livro foi emprestado
        data_devolucao_prevista: Data prevista para devolução
        data_devolucao_real: Data real da devolução (None se ainda não devolvido)
        renovacoes: Contador de quantas vezes foi renovado
        status: Status do empréstimo (ativo, devolvido, atrasado)
        observacoes: Observações sobre o empréstimo (opcional)

    Relacionamentos (preenchidos quando necessário):
        livro: Objeto Livro completo
        leitor: Objeto Usuario do leitor
        bibliotecario: Objeto Usuario do bibliotecário
    """
    id: Optional[int]
    id_livro: int
    id_leitor: int
    id_bibliotecario: Optional[int] = None
    data_emprestimo: Optional[str] = None
    data_devolucao_prevista: Optional[str] = None
    data_devolucao_real: Optional[str] = None
    renovacoes: int = 0
    status: str = 'ativo'  # ativo, devolvido, atrasado
    observacoes: Optional[str] = None

    # Relacionamentos (carregados quando necessário)
    livro: Optional[object] = None
    leitor: Optional[object] = None
    bibliotecario: Optional[object] = None
```

#### Passo 2.6: Completar Reserva Model

📝 **Arquivo:** `model/reserva_model.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Reserva:
    """
    Model de reserva de livro.

    Attributes:
        id: Identificador único da reserva
        id_livro: ID do livro reservado
        id_leitor: ID do leitor que fez a reserva
        data_reserva: Data/hora em que a reserva foi criada
        data_desejada: Data desejada para retirada (opcional)
        data_expiracao: Data de expiração da reserva (opcional)
        status: Status da reserva (ativa, cancelada, atendida, expirada)
        notificado: Se o leitor foi notificado que o livro está disponível

    Relacionamentos (preenchidos quando necessário):
        livro: Objeto Livro completo
        leitor: Objeto Usuario do leitor
    """
    id: Optional[int]
    id_livro: int
    id_leitor: int
    data_reserva: Optional[str] = None
    data_desejada: Optional[str] = None
    data_expiracao: Optional[str] = None
    status: str = 'ativa'  # ativa, cancelada, atendida, expirada
    notificado: bool = False

    # Relacionamentos (carregados quando necessário)
    livro: Optional[object] = None
    leitor: Optional[object] = None
```

#### Passo 2.7: Criar Model de Mensagem

📁 **Arquivo:** `model/mensagem_model.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Mensagem:
    """
    Model de mensagem interna do sistema.

    Attributes:
        id: Identificador único da mensagem
        id_remetente: ID do usuário que enviou
        id_destinatario: ID do usuário que vai receber
        assunto: Assunto da mensagem
        corpo: Corpo/conteúdo da mensagem
        lida: Se a mensagem já foi lida
        data_envio: Data/hora de envio
        data_leitura: Data/hora em que foi lida (opcional)

    Relacionamentos (preenchidos quando necessário):
        remetente: Objeto Usuario do remetente
        destinatario: Objeto Usuario do destinatário
    """
    id: Optional[int]
    id_remetente: int
    id_destinatario: int
    assunto: str
    corpo: str
    lida: bool = False
    data_envio: Optional[str] = None
    data_leitura: Optional[str] = None

    # Relacionamentos
    remetente: Optional[object] = None
    destinatario: Optional[object] = None
```

#### Passo 2.8: Criar Model de Favorito

📁 **Arquivo:** `model/favorito_model.py`

```python
from dataclasses import dataclass
from typing import Optional

@dataclass
class Favorito:
    """
    Model de favorito de livro.

    Attributes:
        id: Identificador único
        id_livro: ID do livro favoritado
        id_leitor: ID do leitor
        data_favoritado: Data/hora em que foi favoritado

    Relacionamentos (preenchidos quando necessário):
        livro: Objeto Livro completo
        leitor: Objeto Usuario do leitor
    """
    id: Optional[int]
    id_livro: int
    id_leitor: int
    data_favoritado: Optional[str] = None

    # Relacionamentos
    livro: Optional[object] = None
    leitor: Optional[object] = None
```

### 3.3. Criar Scripts SQL

#### Passo 3.1: Atualizar SQL de Usuario

📝 **Arquivo:** `sql/usuario_sql.py`

**Adicionar novos campos na criação da tabela:**

```python
# ... código existente ...

# Encontre a definição CRIAR_TABELA e adicione os novos campos:
CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS usuario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    email TEXT UNIQUE NOT NULL,
    senha TEXT NOT NULL,
    perfil TEXT NOT NULL,
    data_nascimento TEXT,
    telefone TEXT,
    endereco TEXT,
    confirmado INTEGER DEFAULT 1,
    bloqueado INTEGER DEFAULT 0,
    token_redefinicao TEXT,
    data_token TEXT,
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

# Adicionar novos comandos SQL:

BLOQUEAR = """
UPDATE usuario
SET bloqueado = 1
WHERE id = ?
"""

DESBLOQUEAR = """
UPDATE usuario
SET bloqueado = 0
WHERE id = ?
"""

OBTER_POR_PERFIL = """
SELECT * FROM usuario
WHERE perfil = ?
ORDER BY nome
"""

OBTER_LEITORES = """
SELECT * FROM usuario
WHERE perfil = 'Leitor'
ORDER BY nome
"""

OBTER_BIBLIOTECARIOS = """
SELECT * FROM usuario
WHERE perfil = 'Bibliotecário'
ORDER BY nome
"""
```

#### Passo 3.2: Criar SQL de Autor

📁 **Arquivo:** `sql/autor_sql.py`

```python
"""
Comandos SQL para a entidade Autor.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS autor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL,
    biografia TEXT,
    data_nascimento TEXT,
    foto_url TEXT,
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_autor_nome ON autor(nome);
"""

INSERIR = """
INSERT INTO autor (nome, biografia, data_nascimento, foto_url)
VALUES (?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT * FROM autor
ORDER BY nome
"""

OBTER_POR_ID = """
SELECT * FROM autor
WHERE id = ?
"""

OBTER_POR_NOME = """
SELECT * FROM autor
WHERE nome LIKE ?
ORDER BY nome
"""

ATUALIZAR = """
UPDATE autor
SET nome = ?, biografia = ?, data_nascimento = ?, foto_url = ?
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM autor
WHERE id = ?
"""

CONTAR = """
SELECT COUNT(*) as total FROM autor
"""
```

#### Passo 3.3: Criar SQL de Categoria

📁 **Arquivo:** `sql/categoria_sql.py`

```python
"""
Comandos SQL para a entidade Categoria.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nome TEXT NOT NULL UNIQUE,
    descricao TEXT,
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_categoria_nome ON categoria(nome);
"""

INSERIR = """
INSERT INTO categoria (nome, descricao)
VALUES (?, ?)
"""

OBTER_TODOS = """
SELECT * FROM categoria
ORDER BY nome
"""

OBTER_POR_ID = """
SELECT * FROM categoria
WHERE id = ?
"""

OBTER_POR_NOME = """
SELECT * FROM categoria
WHERE nome = ?
"""

ATUALIZAR = """
UPDATE categoria
SET nome = ?, descricao = ?
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM categoria
WHERE id = ?
"""

CONTAR = """
SELECT COUNT(*) as total FROM categoria
"""

# Seed de categorias iniciais
SEED_CATEGORIAS = """
INSERT OR IGNORE INTO categoria (nome, descricao) VALUES
('Ficção', 'Obras de ficção literária'),
('Romance', 'Romances em geral'),
('Suspense', 'Livros de suspense e mistério'),
('Fantasia', 'Fantasia e mundos imaginários'),
('Ficção Científica', 'Ficção científica e futurismo'),
('Biografia', 'Biografias e autobiografias'),
('História', 'Livros de história'),
('Ciência', 'Livros científicos e divulgação científica'),
('Filosofia', 'Filosofia e pensamento'),
('Autoajuda', 'Desenvolvimento pessoal e autoajuda'),
('Técnico', 'Livros técnicos e didáticos'),
('Infantil', 'Literatura infantil'),
('Juvenil', 'Literatura juvenil'),
('Poesia', 'Poesia e literatura poética'),
('Teatro', 'Peças teatrais')
"""
```

#### Passo 3.4: Criar SQL de Livro

📁 **Arquivo:** `sql/livro_sql.py`

```python
"""
Comandos SQL para a entidade Livro e relacionamentos.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS livro (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    titulo TEXT NOT NULL,
    subtitulo TEXT,
    isbn TEXT UNIQUE,
    editora TEXT,
    ano_publicacao INTEGER,
    sinopse TEXT,
    capa_url TEXT,
    quantidade_total INTEGER DEFAULT 1,
    quantidade_disponivel INTEGER DEFAULT 1,
    data_cadastro TEXT DEFAULT CURRENT_TIMESTAMP
)
"""

CRIAR_TABELA_LIVRO_AUTOR = """
CREATE TABLE IF NOT EXISTS livro_autor (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_autor INTEGER NOT NULL,
    FOREIGN KEY (id_livro) REFERENCES livro(id) ON DELETE CASCADE,
    FOREIGN KEY (id_autor) REFERENCES autor(id) ON DELETE CASCADE,
    UNIQUE(id_livro, id_autor)
)
"""

CRIAR_TABELA_LIVRO_CATEGORIA = """
CREATE TABLE IF NOT EXISTS livro_categoria (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_categoria INTEGER NOT NULL,
    FOREIGN KEY (id_livro) REFERENCES livro(id) ON DELETE CASCADE,
    FOREIGN KEY (id_categoria) REFERENCES categoria(id) ON DELETE CASCADE,
    UNIQUE(id_livro, id_categoria)
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_livro_titulo ON livro(titulo);
CREATE INDEX IF NOT EXISTS idx_livro_isbn ON livro(isbn);
CREATE INDEX IF NOT EXISTS idx_livro_autor_livro ON livro_autor(id_livro);
CREATE INDEX IF NOT EXISTS idx_livro_autor_autor ON livro_autor(id_autor);
CREATE INDEX IF NOT EXISTS idx_livro_categoria_livro ON livro_categoria(id_livro);
CREATE INDEX IF NOT EXISTS idx_livro_categoria_categoria ON livro_categoria(id_categoria);
"""

INSERIR = """
INSERT INTO livro (titulo, subtitulo, isbn, editora, ano_publicacao, sinopse, capa_url, quantidade_total, quantidade_disponivel)
VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT * FROM livro
ORDER BY titulo
"""

OBTER_POR_ID = """
SELECT * FROM livro
WHERE id = ?
"""

OBTER_DISPONIVEIS = """
SELECT * FROM livro
WHERE quantidade_disponivel > 0
ORDER BY titulo
"""

BUSCAR_POR_TITULO = """
SELECT * FROM livro
WHERE titulo LIKE ? OR subtitulo LIKE ?
ORDER BY titulo
"""

BUSCAR_POR_ISBN = """
SELECT * FROM livro
WHERE isbn = ?
"""

ATUALIZAR = """
UPDATE livro
SET titulo = ?, subtitulo = ?, isbn = ?, editora = ?, ano_publicacao = ?,
    sinopse = ?, capa_url = ?, quantidade_total = ?, quantidade_disponivel = ?
WHERE id = ?
"""

EXCLUIR = """
DELETE FROM livro
WHERE id = ?
"""

# Relacionamentos Livro-Autor
ADICIONAR_AUTOR = """
INSERT INTO livro_autor (id_livro, id_autor)
VALUES (?, ?)
"""

REMOVER_AUTOR = """
DELETE FROM livro_autor
WHERE id_livro = ? AND id_autor = ?
"""

REMOVER_TODOS_AUTORES = """
DELETE FROM livro_autor
WHERE id_livro = ?
"""

OBTER_AUTORES_DO_LIVRO = """
SELECT a.* FROM autor a
INNER JOIN livro_autor la ON a.id = la.id_autor
WHERE la.id_livro = ?
ORDER BY a.nome
"""

# Relacionamentos Livro-Categoria
ADICIONAR_CATEGORIA = """
INSERT INTO livro_categoria (id_livro, id_categoria)
VALUES (?, ?)
"""

REMOVER_CATEGORIA = """
DELETE FROM livro_categoria
WHERE id_livro = ? AND id_categoria = ?
"""

REMOVER_TODAS_CATEGORIAS = """
DELETE FROM livro_categoria
WHERE id_livro = ?
"""

OBTER_CATEGORIAS_DO_LIVRO = """
SELECT c.* FROM categoria c
INNER JOIN livro_categoria lc ON c.id = lc.id_categoria
WHERE lc.id_livro = ?
ORDER BY c.nome
"""

OBTER_LIVROS_POR_CATEGORIA = """
SELECT l.* FROM livro l
INNER JOIN livro_categoria lc ON l.id = lc.id_livro
WHERE lc.id_categoria = ?
ORDER BY l.titulo
"""

OBTER_LIVROS_POR_AUTOR = """
SELECT l.* FROM livro l
INNER JOIN livro_autor la ON l.id = la.id_livro
WHERE la.id_autor = ?
ORDER BY l.titulo
"""

# Gestão de disponibilidade
DECREMENTAR_DISPONIVEL = """
UPDATE livro
SET quantidade_disponivel = quantidade_disponivel - 1
WHERE id = ? AND quantidade_disponivel > 0
"""

INCREMENTAR_DISPONIVEL = """
UPDATE livro
SET quantidade_disponivel = quantidade_disponivel + 1
WHERE id = ? AND quantidade_disponivel < quantidade_total
"""

CONTAR = """
SELECT COUNT(*) as total FROM livro
"""

CONTAR_DISPONIVEIS = """
SELECT COUNT(*) as total FROM livro
WHERE quantidade_disponivel > 0
"""
```

#### Passo 3.5: Criar SQL de Emprestimo

📁 **Arquivo:** `sql/emprestimo_sql.py`

```python
"""
Comandos SQL para a entidade Empréstimo.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS emprestimo (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_leitor INTEGER NOT NULL,
    id_bibliotecario INTEGER,
    data_emprestimo TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_devolucao_prevista TEXT NOT NULL,
    data_devolucao_real TEXT,
    renovacoes INTEGER DEFAULT 0,
    status TEXT DEFAULT 'ativo',
    observacoes TEXT,
    FOREIGN KEY (id_livro) REFERENCES livro(id),
    FOREIGN KEY (id_leitor) REFERENCES usuario(id),
    FOREIGN KEY (id_bibliotecario) REFERENCES usuario(id)
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_emprestimo_leitor ON emprestimo(id_leitor);
CREATE INDEX IF NOT EXISTS idx_emprestimo_status ON emprestimo(status);
CREATE INDEX IF NOT EXISTS idx_emprestimo_livro ON emprestimo(id_livro);
"""

INSERIR = """
INSERT INTO emprestimo (id_livro, id_leitor, id_bibliotecario, data_emprestimo, data_devolucao_prevista, status, observacoes)
VALUES (?, ?, ?, ?, ?, ?, ?)
"""

OBTER_TODOS = """
SELECT e.*,
       l.titulo as livro_titulo,
       u.nome as leitor_nome,
       b.nome as bibliotecario_nome
FROM emprestimo e
LEFT JOIN livro l ON e.id_livro = l.id
LEFT JOIN usuario u ON e.id_leitor = u.id
LEFT JOIN usuario b ON e.id_bibliotecario = b.id
ORDER BY e.data_emprestimo DESC
"""

OBTER_POR_ID = """
SELECT e.*,
       l.titulo as livro_titulo,
       u.nome as leitor_nome,
       b.nome as bibliotecario_nome
FROM emprestimo e
LEFT JOIN livro l ON e.id_livro = l.id
LEFT JOIN usuario u ON e.id_leitor = u.id
LEFT JOIN usuario b ON e.id_bibliotecario = b.id
WHERE e.id = ?
"""

OBTER_POR_LEITOR = """
SELECT e.*,
       l.titulo as livro_titulo, l.capa_url
FROM emprestimo e
INNER JOIN livro l ON e.id_livro = l.id
WHERE e.id_leitor = ?
ORDER BY e.data_emprestimo DESC
"""

OBTER_ATIVOS_POR_LEITOR = """
SELECT e.*,
       l.titulo as livro_titulo, l.capa_url
FROM emprestimo e
INNER JOIN livro l ON e.id_livro = l.id
WHERE e.id_leitor = ? AND e.status = 'ativo'
ORDER BY e.data_devolucao_prevista
"""

OBTER_ATRASADOS = """
SELECT e.*,
       l.titulo as livro_titulo,
       u.nome as leitor_nome
FROM emprestimo e
INNER JOIN livro l ON e.id_livro = l.id
INNER JOIN usuario u ON e.id_leitor = u.id
WHERE e.status = 'ativo' AND date(e.data_devolucao_prevista) < date('now')
ORDER BY e.data_devolucao_prevista
"""

OBTER_PROXIMOS_VENCIMENTO = """
SELECT e.*,
       l.titulo as livro_titulo,
       u.nome as leitor_nome
FROM emprestimo e
INNER JOIN livro l ON e.id_livro = l.id
INNER JOIN usuario u ON e.id_leitor = u.id
WHERE e.status = 'ativo'
  AND date(e.data_devolucao_prevista) BETWEEN date('now') AND date('now', '+3 days')
ORDER BY e.data_devolucao_prevista
"""

REGISTRAR_DEVOLUCAO = """
UPDATE emprestimo
SET status = 'devolvido', data_devolucao_real = ?
WHERE id = ?
"""

RENOVAR = """
UPDATE emprestimo
SET renovacoes = renovacoes + 1,
    data_devolucao_prevista = ?
WHERE id = ?
"""

MARCAR_ATRASADO = """
UPDATE emprestimo
SET status = 'atrasado'
WHERE id = ?
"""

CONTAR_ATIVOS_POR_LEITOR = """
SELECT COUNT(*) as total
FROM emprestimo
WHERE id_leitor = ? AND status = 'ativo'
"""

CONTAR_POR_STATUS = """
SELECT status, COUNT(*) as total
FROM emprestimo
GROUP BY status
"""

# Estatísticas
LIVROS_MAIS_EMPRESTADOS = """
SELECT l.id, l.titulo, l.capa_url, COUNT(*) as total_emprestimos
FROM emprestimo e
INNER JOIN livro l ON e.id_livro = l.id
GROUP BY l.id
ORDER BY total_emprestimos DESC
LIMIT ?
"""

LEITORES_MAIS_ATIVOS = """
SELECT u.id, u.nome, COUNT(*) as total_emprestimos
FROM emprestimo e
INNER JOIN usuario u ON e.id_leitor = u.id
GROUP BY u.id
ORDER BY total_emprestimos DESC
LIMIT ?
"""
```

#### Passo 3.6: Criar SQL de Reserva

📁 **Arquivo:** `sql/reserva_sql.py`

```python
"""
Comandos SQL para a entidade Reserva.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS reserva (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_leitor INTEGER NOT NULL,
    data_reserva TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    data_desejada TEXT,
    data_expiracao TEXT,
    status TEXT DEFAULT 'ativa',
    notificado INTEGER DEFAULT 0,
    FOREIGN KEY (id_livro) REFERENCES livro(id),
    FOREIGN KEY (id_leitor) REFERENCES usuario(id)
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_reserva_leitor ON reserva(id_leitor);
CREATE INDEX IF NOT EXISTS idx_reserva_status ON reserva(status);
CREATE INDEX IF NOT EXISTS idx_reserva_livro ON reserva(id_livro);
"""

INSERIR = """
INSERT INTO reserva (id_livro, id_leitor, data_desejada, data_expiracao, status)
VALUES (?, ?, ?, ?, ?)
"""

OBTER_TODAS = """
SELECT r.*,
       l.titulo as livro_titulo, l.capa_url,
       u.nome as leitor_nome, u.email as leitor_email
FROM reserva r
INNER JOIN livro l ON r.id_livro = l.id
INNER JOIN usuario u ON r.id_leitor = u.id
ORDER BY r.data_reserva DESC
"""

OBTER_POR_ID = """
SELECT r.*,
       l.titulo as livro_titulo, l.capa_url,
       u.nome as leitor_nome, u.email as leitor_email
FROM reserva r
INNER JOIN livro l ON r.id_livro = l.id
INNER JOIN usuario u ON r.id_leitor = u.id
WHERE r.id = ?
"""

OBTER_POR_LEITOR = """
SELECT r.*,
       l.titulo as livro_titulo, l.capa_url
FROM reserva r
INNER JOIN livro l ON r.id_livro = l.id
WHERE r.id_leitor = ?
ORDER BY r.data_reserva DESC
"""

OBTER_ATIVAS_POR_LEITOR = """
SELECT r.*,
       l.titulo as livro_titulo, l.capa_url
FROM reserva r
INNER JOIN livro l ON r.id_livro = l.id
WHERE r.id_leitor = ? AND r.status = 'ativa'
ORDER BY r.data_reserva
"""

OBTER_POR_LIVRO = """
SELECT r.*,
       u.nome as leitor_nome, u.email as leitor_email
FROM reserva r
INNER JOIN usuario u ON r.id_leitor = u.id
WHERE r.id_livro = ? AND r.status = 'ativa'
ORDER BY r.data_reserva
LIMIT 1
"""

CANCELAR = """
UPDATE reserva
SET status = 'cancelada'
WHERE id = ?
"""

ATENDER = """
UPDATE reserva
SET status = 'atendida'
WHERE id = ?
"""

EXPIRAR = """
UPDATE reserva
SET status = 'expirada'
WHERE id = ?
"""

MARCAR_NOTIFICADO = """
UPDATE reserva
SET notificado = 1
WHERE id = ?
"""

OBTER_NAO_NOTIFICADAS = """
SELECT r.*,
       l.titulo as livro_titulo, l.quantidade_disponivel,
       u.nome as leitor_nome, u.email as leitor_email
FROM reserva r
INNER JOIN livro l ON r.id_livro = l.id
INNER JOIN usuario u ON r.id_leitor = u.id
WHERE r.status = 'ativa'
  AND r.notificado = 0
  AND l.quantidade_disponivel > 0
ORDER BY r.data_reserva
"""

OBTER_EXPIRADAS = """
SELECT * FROM reserva
WHERE status = 'ativa'
  AND data_expiracao IS NOT NULL
  AND date(data_expiracao) < date('now')
"""

CONTAR_ATIVAS_POR_LEITOR = """
SELECT COUNT(*) as total
FROM reserva
WHERE id_leitor = ? AND status = 'ativa'
"""

CONTAR_POR_STATUS = """
SELECT status, COUNT(*) as total
FROM reserva
GROUP BY status
"""

#### Passo 3.7: Criar SQL de Mensagem

📁 **Arquivo:** `sql/mensagem_sql.py`

```python
"""
Comandos SQL para a entidade Mensagem.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS mensagem (
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
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_mensagem_destinatario ON mensagem(id_destinatario, lida);
CREATE INDEX IF NOT EXISTS idx_mensagem_remetente ON mensagem(id_remetente);
"""

INSERIR = """
INSERT INTO mensagem (id_remetente, id_destinatario, assunto, corpo)
VALUES (?, ?, ?, ?)
"""

OBTER_RECEBIDAS = """
SELECT m.*,
       r.nome as remetente_nome, r.email as remetente_email
FROM mensagem m
INNER JOIN usuario r ON m.id_remetente = r.id
WHERE m.id_destinatario = ?
ORDER BY m.data_envio DESC
"""

OBTER_ENVIADAS = """
SELECT m.*,
       d.nome as destinatario_nome, d.email as destinatario_email
FROM mensagem m
INNER JOIN usuario d ON m.id_destinatario = d.id
WHERE m.id_remetente = ?
ORDER BY m.data_envio DESC
"""

OBTER_POR_ID = """
SELECT m.*,
       r.nome as remetente_nome, r.email as remetente_email,
       d.nome as destinatario_nome, d.email as destinatario_email
FROM mensagem m
INNER JOIN usuario r ON m.id_remetente = r.id
INNER JOIN usuario d ON m.id_destinatario = d.id
WHERE m.id = ?
"""

MARCAR_COMO_LIDA = """
UPDATE mensagem
SET lida = 1, data_leitura = ?
WHERE id = ?
"""

CONTAR_NAO_LIDAS = """
SELECT COUNT(*) as total
FROM mensagem
WHERE id_destinatario = ? AND lida = 0
"""

EXCLUIR = """
DELETE FROM mensagem
WHERE id = ?
"""
```

#### Passo 3.8: Criar SQL de Favorito

📁 **Arquivo:** `sql/favorito_sql.py`

```python
"""
Comandos SQL para a entidade Favorito.
"""

CRIAR_TABELA = """
CREATE TABLE IF NOT EXISTS favorito (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    id_livro INTEGER NOT NULL,
    id_leitor INTEGER NOT NULL,
    data_favoritado TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (id_livro) REFERENCES livro(id) ON DELETE CASCADE,
    FOREIGN KEY (id_leitor) REFERENCES usuario(id) ON DELETE CASCADE,
    UNIQUE(id_livro, id_leitor)
)
"""

CRIAR_INDICES = """
CREATE INDEX IF NOT EXISTS idx_favorito_leitor ON favorito(id_leitor);
CREATE INDEX IF NOT EXISTS idx_favorito_livro ON favorito(id_livro);
"""

ADICIONAR = """
INSERT INTO favorito (id_livro, id_leitor)
VALUES (?, ?)
"""

REMOVER = """
DELETE FROM favorito
WHERE id_livro = ? AND id_leitor = ?
"""

OBTER_POR_LEITOR = """
SELECT f.*,
       l.titulo, l.subtitulo, l.capa_url, l.quantidade_disponivel
FROM favorito f
INNER JOIN livro l ON f.id_livro = l.id
WHERE f.id_leitor = ?
ORDER BY f.data_favoritado DESC
"""

VERIFICAR_FAVORITO = """
SELECT COUNT(*) as total
FROM favorito
WHERE id_livro = ? AND id_leitor = ?
"""

CONTAR_POR_LIVRO = """
SELECT COUNT(*) as total
FROM favorito
WHERE id_livro = ?
"""

CONTAR_POR_LEITOR = """
SELECT COUNT(*) as total
FROM favorito
WHERE id_leitor = ?
"""
```

### 3.4. Criar Repositories

> **Nota:** Os repositories seguem o padrão já estabelecido no projeto. Vou fornecer exemplos completos para os principais, e você pode replicar para os demais.

#### Passo 4.1: Criar Autor Repository

📁 **Arquivo:** `repo/autor_repo.py`

```python
"""
Repository para a entidade Autor.
Contém todas as operações de acesso a dados de autores.
"""

from typing import List, Optional
from model.autor_model import Autor
from sql.autor_sql import *
from util.db_util import get_connection


def _row_to_autor(row) -> Autor:
    """Converte uma linha do banco em objeto Autor"""
    return Autor(
        id=row["id"],
        nome=row["nome"],
        biografia=row["biografia"],
        data_nascimento=row["data_nascimento"],
        foto_url=row["foto_url"],
        data_cadastro=row["data_cadastro"]
    )


def criar_tabela():
    """Cria a tabela de autores e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)


def inserir(autor: Autor) -> int:
    """
    Insere um novo autor no banco.

    Args:
        autor: Objeto Autor com os dados

    Returns:
        ID do autor inserido
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            autor.nome,
            autor.biografia,
            autor.data_nascimento,
            autor.foto_url
        ))
        return cursor.lastrowid


def obter_todos() -> List[Autor]:
    """Retorna todos os autores ordenados por nome"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_autor(row) for row in cursor.fetchall()]


def obter_por_id(autor_id: int) -> Optional[Autor]:
    """Retorna um autor pelo ID ou None se não encontrado"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (autor_id,))
        row = cursor.fetchone()
        return _row_to_autor(row) if row else None


def obter_por_nome(nome: str) -> List[Autor]:
    """Busca autores por nome (parcial)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_NOME, (f"%{nome}%",))
        return [_row_to_autor(row) for row in cursor.fetchall()]


def atualizar(autor: Autor):
    """Atualiza os dados de um autor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            autor.nome,
            autor.biografia,
            autor.data_nascimento,
            autor.foto_url,
            autor.id
        ))


def excluir(autor_id: int):
    """Exclui um autor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (autor_id,))


def contar() -> int:
    """Retorna o total de autores cadastrados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()["total"]
```

#### Passo 4.2: Criar Categoria Repository

📁 **Arquivo:** `repo/categoria_repo.py`

```python
"""
Repository para a entidade Categoria.
"""

from typing import List, Optional
from model.categoria_model import Categoria
from sql.categoria_sql import *
from util.db_util import get_connection


def _row_to_categoria(row) -> Categoria:
    """Converte linha do banco em objeto Categoria"""
    return Categoria(
        id=row["id"],
        nome=row["nome"],
        descricao=row["descricao"],
        data_cadastro=row["data_cadastro"]
    )


def criar_tabela():
    """Cria a tabela de categorias e insere seed inicial"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)
        cursor.execute(SEED_CATEGORIAS)


def inserir(categoria: Categoria) -> int:
    """Insere uma nova categoria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            categoria.nome,
            categoria.descricao
        ))
        return cursor.lastrowid


def obter_todos() -> List[Categoria]:
    """Retorna todas as categorias"""
    with get_connection() as conn:
        cursor = cursor.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_categoria(row) for row in cursor.fetchall()]


def obter_por_id(categoria_id: int) -> Optional[Categoria]:
    """Retorna uma categoria pelo ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (categoria_id,))
        row = cursor.fetchone()
        return _row_to_categoria(row) if row else None


def obter_por_nome(nome: str) -> Optional[Categoria]:
    """Retorna uma categoria pelo nome exato"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_NOME, (nome,))
        row = cursor.fetchone()
        return _row_to_categoria(row) if row else None


def atualizar(categoria: Categoria):
    """Atualiza uma categoria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATUALIZAR, (
            categoria.nome,
            categoria.descricao,
            categoria.id
        ))


def excluir(categoria_id: int):
    """Exclui uma categoria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (categoria_id,))


def contar() -> int:
    """Total de categorias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()["total"]
```

#### Passo 4.3: Criar Livro Repository

📁 **Arquivo:** `repo/livro_repo.py`

**Nota:** Este repository é mais complexo pois gerencia relacionamentos N:N.

```python
"""
Repository para a entidade Livro e seus relacionamentos.
"""

from typing import List, Optional
from model.livro_model import Livro
from model.autor_model import Autor
from model.categoria_model import Categoria
from sql.livro_sql import *
from util.db_util import get_connection


def _row_to_livro(row) -> Livro:
    """Converte linha do banco em objeto Livro"""
    return Livro(
        id=row["id"],
        titulo=row["titulo"],
        subtitulo=row["subtitulo"],
        isbn=row["isbn"],
        editora=row["editora"],
        ano_publicacao=row["ano_publicacao"],
        sinopse=row["sinopse"],
        capa_url=row["capa_url"],
        quantidade_total=row["quantidade_total"],
        quantidade_disponivel=row["quantidade_disponivel"],
        data_cadastro=row["data_cadastro"]
    )


def _row_to_autor(row) -> Autor:
    """Converte linha do banco em objeto Autor"""
    from model.autor_model import Autor
    return Autor(
        id=row["id"],
        nome=row["nome"],
        biografia=row.get("biografia"),
        data_nascimento=row.get("data_nascimento"),
        foto_url=row.get("foto_url"),
        data_cadastro=row.get("data_cadastro")
    )


def _row_to_categoria(row) -> Categoria:
    """Converte linha do banco em objeto Categoria"""
    from model.categoria_model import Categoria
    return Categoria(
        id=row["id"],
        nome=row["nome"],
        descricao=row.get("descricao"),
        data_cadastro=row.get("data_cadastro")
    )


def criar_tabela():
    """Cria as tabelas de livro e relacionamentos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_TABELA_LIVRO_AUTOR)
        cursor.execute(CRIAR_TABELA_LIVRO_CATEGORIA)
        cursor.execute(CRIAR_INDICES)


def inserir(livro: Livro, ids_autores: List[int] = None, ids_categorias: List[int] = None) -> int:
    """
    Insere um novo livro com autores e categorias.

    Args:
        livro: Objeto Livro
        ids_autores: Lista de IDs de autores (opcional)
        ids_categorias: Lista de IDs de categorias (opcional)

    Returns:
        ID do livro inserido
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Inserir livro
        cursor.execute(INSERIR, (
            livro.titulo,
            livro.subtitulo,
            livro.isbn,
            livro.editora,
            livro.ano_publicacao,
            livro.sinopse,
            livro.capa_url,
            livro.quantidade_total,
            livro.quantidade_disponivel
        ))
        livro_id = cursor.lastrowid

        # Adicionar autores
        if ids_autores:
            for autor_id in ids_autores:
                cursor.execute(ADICIONAR_AUTOR, (livro_id, autor_id))

        # Adicionar categorias
        if ids_categorias:
            for categoria_id in ids_categorias:
                cursor.execute(ADICIONAR_CATEGORIA, (livro_id, categoria_id))

        return livro_id


def obter_todos() -> List[Livro]:
    """Retorna todos os livros"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [_row_to_livro(row) for row in cursor.fetchall()]


def obter_por_id(livro_id: int, carregar_relacionamentos: bool = False) -> Optional[Livro]:
    """
    Retorna um livro pelo ID.

    Args:
        livro_id: ID do livro
        carregar_relacionamentos: Se deve carregar autores e categorias

    Returns:
        Objeto Livro ou None
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (livro_id,))
        row = cursor.fetchone()

        if not row:
            return None

        livro = _row_to_livro(row)

        if carregar_relacionamentos:
            livro.autores = obter_autores_do_livro(livro_id)
            livro.categorias = obter_categorias_do_livro(livro_id)

        return livro


def obter_disponiveis() -> List[Livro]:
    """Retorna livros com exemplares disponíveis"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_DISPONIVEIS)
        return [_row_to_livro(row) for row in cursor.fetchall()]


def buscar_por_titulo(termo: str) -> List[Livro]:
    """Busca livros por título ou subtítulo"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(BUSCAR_POR_TITULO, (f"%{termo}%", f"%{termo}%"))
        return [_row_to_livro(row) for row in cursor.fetchall()]


def buscar_por_isbn(isbn: str) -> Optional[Livro]:
    """Busca livro por ISBN"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(BUSCAR_POR_ISBN, (isbn,))
        row = cursor.fetchone()
        return _row_to_livro(row) if row else None


def atualizar(livro: Livro, ids_autores: List[int] = None, ids_categorias: List[int] = None):
    """
    Atualiza um livro e seus relacionamentos.

    Args:
        livro: Objeto Livro com dados atualizados
        ids_autores: Nova lista de IDs de autores (None = não atualizar)
        ids_categorias: Nova lista de IDs de categorias (None = não atualizar)
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Atualizar livro
        cursor.execute(ATUALIZAR, (
            livro.titulo,
            livro.subtitulo,
            livro.isbn,
            livro.editora,
            livro.ano_publicacao,
            livro.sinopse,
            livro.capa_url,
            livro.quantidade_total,
            livro.quantidade_disponivel,
            livro.id
        ))

        # Atualizar autores se fornecido
        if ids_autores is not None:
            cursor.execute(REMOVER_TODOS_AUTORES, (livro.id,))
            for autor_id in ids_autores:
                cursor.execute(ADICIONAR_AUTOR, (livro.id, autor_id))

        # Atualizar categorias se fornecido
        if ids_categorias is not None:
            cursor.execute(REMOVER_TODAS_CATEGORIAS, (livro.id,))
            for categoria_id in ids_categorias:
                cursor.execute(ADICIONAR_CATEGORIA, (livro.id, categoria_id))


def excluir(livro_id: int):
    """Exclui um livro (CASCADE remove relacionamentos)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (livro_id,))


def obter_autores_do_livro(livro_id: int) -> List[Autor]:
    """Retorna todos os autores de um livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_AUTORES_DO_LIVRO, (livro_id,))
        return [_row_to_autor(row) for row in cursor.fetchall()]


def obter_categorias_do_livro(livro_id: int) -> List[Categoria]:
    """Retorna todas as categorias de um livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_CATEGORIAS_DO_LIVRO, (livro_id,))
        return [_row_to_categoria(row) for row in cursor.fetchall()]


def obter_livros_por_categoria(categoria_id: int) -> List[Livro]:
    """Retorna livros de uma categoria"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_LIVROS_POR_CATEGORIA, (categoria_id,))
        return [_row_to_livro(row) for row in cursor.fetchall()]


def obter_livros_por_autor(autor_id: int) -> List[Livro]:
    """Retorna livros de um autor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_LIVROS_POR_AUTOR, (autor_id,))
        return [_row_to_livro(row) for row in cursor.fetchall()]


def decrementar_disponivel(livro_id: int) -> bool:
    """
    Decrementa quantidade disponível (para empréstimo).

    Returns:
        True se decrementou, False se não havia disponível
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(DECREMENTAR_DISPONIVEL, (livro_id,))
        return cursor.rowcount > 0


def incrementar_disponivel(livro_id: int) -> bool:
    """
    Incrementa quantidade disponível (devolução).

    Returns:
        True se incrementou, False se já estava no máximo
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INCREMENTAR_DISPONIVEL, (livro_id,))
        return cursor.rowcount > 0


def contar() -> int:
    """Total de livros no acervo"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR)
        return cursor.fetchone()["total"]


def contar_disponiveis() -> int:
    """Total de livros disponíveis"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_DISPONIVEIS)
        return cursor.fetchone()["total"]
```

**⚠️ IMPORTANTE:** Devido ao limite de tokens, vou fornecer instruções resumidas para os demais repositories. Siga o mesmo padrão dos exemplos acima.

#### Passo 4.4: Criar Emprestimo Repository

📁 **Arquivo:** `repo/emprestimo_repo.py`

**Instruções:**
1. Copiar estrutura de `autor_repo.py`
2. Implementar `_row_to_emprestimo()` - converter row em model
3. Implementar todas as funções SQL de `sql/emprestimo_sql.py`
4. Adicionar função `registrar_emprestimo()` que:
   - Insere empréstimo
   - Decrementa livro disponível (usar `livro_repo.decrementar_disponivel()`)
   - Usa transaction para garantir atomicidade
5. Adicionar função `registrar_devolucao()` que:
   - Atualiza empréstimo
   - Incrementa livro disponível
   - Verifica se há reserva ativa para notificar

#### Passo 4.5: Criar Reserva Repository

📁 **Arquivo:** `repo/reserva_repo.py`

**Instruções:**
1. Seguir padrão de `autor_repo.py`
2. Implementar todas as queries de `sql/reserva_sql.py`
3. Adicionar lógica de expiração automática

#### Passo 4.6: Criar Mensagem Repository

📁 **Arquivo:** `repo/mensagem_repo.py`

**Instruções:**
1. Seguir padrão
2. Implementar inbox/outbox
3. Marcar como lida

#### Passo 4.7: Criar Favorito Repository

📁 **Arquivo:** `repo/favorito_repo.py`

**Instruções:**
1. Implementar adicionar/remover
2. Listar favoritos por leitor
3. Verificar se já é favorito

### 3.5. Criar DTOs e Validadores

#### Passo 5.1: Adicionar validador de ISBN

📝 **Arquivo:** `dtos/validators.py`

**Adicionar ao final do arquivo:**

```python
def validar_isbn():
    """
    Valida código ISBN-10 ou ISBN-13.
    Permite ISBN com ou sem hífens.
    """
    def validador(v: str) -> str:
        if not v:
            return v

        # Remover hífens e espaços
        isbn_limpo = v.replace("-", "").replace(" ", "")

        # Verificar tamanho
        if len(isbn_limpo) not in [10, 13]:
            raise ValueError("ISBN deve ter 10 ou 13 dígitos")

        # Verificar se são apenas dígitos (ISBN-10 pode ter X no final)
        if len(isbn_limpo) == 10:
            if not isbn_limpo[:-1].isdigit():
                raise ValueError("ISBN-10 inválido")
        else:
            if not isbn_limpo.isdigit():
                raise ValueError("ISBN-13 deve conter apenas dígitos")

        return v

    return validador


def validar_ano_publicacao():
    """
    Valida ano de publicação entre 1000 e ano atual.
    """
    def validador(v: int) -> int:
        from datetime import datetime
        ano_atual = datetime.now().year

        if not (1000 <= v <= ano_atual):
            raise ValueError(f"Ano deve estar entre 1000 e {ano_atual}")

        return v

    return validador
```

#### Passo 5.2: Criar DTOs de Livro

📁 **Arquivo:** `dtos/livro_dto.py`

```python
from pydantic import BaseModel, field_validator
from typing import Optional, List
from dtos.validators import (
    validar_string_obrigatoria,
    validar_isbn,
    validar_ano_publicacao,
    validar_inteiro_positivo
)


class LivroCriarDTO(BaseModel):
    """DTO para criação de livro"""
    titulo: str
    subtitulo: Optional[str] = None
    isbn: Optional[str] = None
    editora: Optional[str] = None
    ano_publicacao: int
    sinopse: str
    quantidade_total: int = 1
    autores: List[int] = []  # IDs dos autores
    categorias: List[int] = []  # IDs das categorias

    _validar_titulo = field_validator('titulo')(
        validar_string_obrigatoria('Título', tamanho_minimo=1, tamanho_maximo=255)
    )

    _validar_isbn = field_validator('isbn')(validar_isbn())

    _validar_ano = field_validator('ano_publicacao')(validar_ano_publicacao())

    _validar_quantidade = field_validator('quantidade_total')(validar_inteiro_positivo())


class LivroAlterarDTO(BaseModel):
    """DTO para alteração de livro"""
    titulo: str
    subtitulo: Optional[str] = None
    isbn: Optional[str] = None
    editora: Optional[str] = None
    ano_publicacao: int
    sinopse: str
    quantidade_total: int
    autores: List[int] = []
    categorias: List[int] = []

    _validar_titulo = field_validator('titulo')(
        validar_string_obrigatoria('Título', tamanho_minimo=1, tamanho_maximo=255)
    )

    _validar_isbn = field_validator('isbn')(validar_isbn())

    _validar_ano = field_validator('ano_publicacao')(validar_ano_publicacao())

    _validar_quantidade = field_validator('quantidade_total')(validar_inteiro_positivo())


class LivroFiltroDTO(BaseModel):
    """DTO para filtros de busca de livros"""
    titulo: Optional[str] = None
    autor: Optional[str] = None
    categoria: Optional[int] = None
    ano_inicio: Optional[int] = None
    ano_fim: Optional[int] = None
    disponivel: Optional[bool] = None
```

**⚠️ NOTA:** Crie DTOs semelhantes para:
- `dtos/autor_dto.py` - AutorCriarDTO, AutorAlterarDTO
- `dtos/categoria_dto.py` - CategoriaCriarDTO, CategoriaAlterarDTO
- `dtos/emprestimo_dto.py` - EmprestimoCriarDTO, EmprestimoRenovarDTO
- `dtos/reserva_dto.py` - ReservaCriarDTO
- `dtos/mensagem_dto.py` - MensagemEnviarDTO

### 3.6. Atualizar main.py

📝 **Arquivo:** `main.py`

**Adicionar imports:**

```python
# Novos imports
import repo.autor_repo as autor_repo
import repo.categoria_repo as categoria_repo
import repo.livro_repo as livro_repo
import repo.emprestimo_repo as emprestimo_repo
import repo.reserva_repo as reserva_repo
import repo.mensagem_repo as mensagem_repo
import repo.favorito_repo as favorito_repo
```

**No @app.on_event("startup"), adicionar:**

```python
@app.on_event("startup")
async def startup():
    """Inicialização da aplicação"""
    # ... código existente ...

    # TABELAS BIBLIX
    autor_repo.criar_tabela()
    logger.info("Tabela 'autor' criada/verificada")

    categoria_repo.criar_tabela()
    logger.info("Tabela 'categoria' criada/verificada com seed")

    livro_repo.criar_tabela()
    logger.info("Tabelas 'livro', 'livro_autor', 'livro_categoria' criadas/verificadas")

    emprestimo_repo.criar_tabela()
    logger.info("Tabela 'emprestimo' criada/verificada")

    reserva_repo.criar_tabela()
    logger.info("Tabela 'reserva' criada/verificada")

    mensagem_repo.criar_tabela()
    logger.info("Tabela 'mensagem' criada/verificada")

    favorito_repo.criar_tabela()
    logger.info("Tabela 'favorito' criada/verificada")
```

### 3.7. Testar Sprint 1

#### Como Testar:

1. **Executar aplicação:**
   ```bash
   python main.py
   ```

2. **Verificar logs:**
   - Todas as tabelas devem ser criadas sem erros
   - Seed de categorias deve ser inserido

3. **Verificar banco de dados:**
   ```bash
   sqlite3 database.db
   .tables
   # Deve mostrar: usuario, autor, categoria, livro, livro_autor, livro_categoria,
   #               emprestimo, reserva, mensagem, favorito, configuracao

   .schema livro
   # Verificar estrutura

   SELECT * FROM categoria;
   # Deve mostrar 15 categorias seed
   ```

4. **Testar repository (opcional):**
   ```python
   # Criar teste_sprint1.py
   import repo.autor_repo as autor_repo
   from model.autor_model import Autor

   # Inserir autor
   autor = Autor(
       id=None,
       nome="Machado de Assis",
       biografia="Grande autor brasileiro",
       data_nascimento="1839-06-21"
   )
   id_autor = autor_repo.inserir(autor)
   print(f"Autor inserido com ID: {id_autor}")

   # Buscar
   autor_encontrado = autor_repo.obter_por_id(id_autor)
   print(f"Autor encontrado: {autor_encontrado.nome}")
   ```

### 3.8. Checklist Sprint 1

- [ ] Perfis atualizados (Leitor, Bibliotecário, Admin)
- [ ] Seed de usuários atualizado
- [ ] Todos os models criados/atualizados
- [ ] Todos os SQL scripts criados
- [ ] Todos os repositories criados
- [ ] DTOs principais criados
- [ ] Validadores ISBN e ano publicação criados
- [ ] main.py atualizado com novos repos
- [ ] Aplicação executa sem erros
- [ ] Tabelas criadas no banco
- [ ] Seed de categorias inserido
- [ ] Testes manuais de repository funcionando

---

---

## 4. SPRINT 2: FUNCIONALIDADES DO LEITOR

**Duração estimada:** 40 horas
**Objetivo:** Implementar todas as funcionalidades do perfil Leitor
**Pré-requisitos:** Sprint 1 completa e testada

### 4.1. Visão Geral da Sprint 2

Nesta sprint, vamos criar toda a experiência do usuário com perfil **Leitor**:
- Dashboard personalizado
- Visualização de empréstimos ativos
- Renovação de empréstimos
- Devolução de livros
- Sistema de reservas
- Favoritos
- Sistema de mensagens (inbox)

### 4.2. Completar Repositories Pendentes

Antes de criar as rotas, precisamos completar os repositories que ficaram pendentes da Sprint 1.

#### Passo 1: Completar Emprestimo Repository

📁 **Arquivo:** `repo/emprestimo_repo.py`

```python
"""
Repository para a entidade Empréstimo.
Gerencia todas as operações de empréstimo de livros.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from model.emprestimo_model import Emprestimo
from sql.emprestimo_sql import *
from util.db_util import get_connection
import repo.livro_repo as livro_repo


def _row_to_emprestimo(row) -> Emprestimo:
    """Converte linha do banco em objeto Emprestimo"""
    return Emprestimo(
        id=row["id"],
        id_livro=row["id_livro"],
        id_leitor=row["id_leitor"],
        id_bibliotecario=row.get("id_bibliotecario"),
        data_emprestimo=row["data_emprestimo"],
        data_devolucao_prevista=row["data_devolucao_prevista"],
        data_devolucao_real=row.get("data_devolucao_real"),
        renovacoes=row["renovacoes"],
        status=row["status"],
        observacoes=row.get("observacoes")
    )


def criar_tabela():
    """Cria a tabela de empréstimos e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)


def registrar_emprestimo(
    id_livro: int,
    id_leitor: int,
    id_bibliotecario: int,
    prazo_dias: int = 14,
    observacoes: str = None
) -> Optional[int]:
    """
    Registra um novo empréstimo.

    IMPORTANTE: Usa transação para garantir atomicidade.
    Se não conseguir decrementar o livro, rollback automático.

    Args:
        id_livro: ID do livro
        id_leitor: ID do leitor
        id_bibliotecario: ID do bibliotecário que registrou
        prazo_dias: Prazo em dias (padrão: 14)
        observacoes: Observações opcionais

    Returns:
        ID do empréstimo ou None se livro indisponível
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Verificar disponibilidade
        livro = livro_repo.obter_por_id(id_livro)
        if not livro or livro.quantidade_disponivel <= 0:
            return None

        try:
            # Calcular datas
            data_emprestimo = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            data_prevista = (datetime.now() + timedelta(days=prazo_dias)).strftime("%Y-%m-%d")

            # Inserir empréstimo
            cursor.execute(INSERIR, (
                id_livro,
                id_leitor,
                id_bibliotecario,
                data_emprestimo,
                data_prevista,
                'ativo',
                observacoes
            ))
            emprestimo_id = cursor.lastrowid

            # Decrementar disponível
            cursor.execute(
                "UPDATE livro SET quantidade_disponivel = quantidade_disponivel - 1 WHERE id = ?",
                (id_livro,)
            )

            conn.commit()
            return emprestimo_id

        except Exception as e:
            conn.rollback()
            raise e


def registrar_devolucao(emprestimo_id: int) -> bool:
    """
    Registra a devolução de um empréstimo.

    IMPORTANTE: Usa transação para garantir atomicidade.
    Incrementa disponibilidade e verifica reservas.

    Args:
        emprestimo_id: ID do empréstimo

    Returns:
        True se devolvido com sucesso, False se não encontrado
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Buscar empréstimo
        cursor.execute(OBTER_POR_ID, (emprestimo_id,))
        row = cursor.fetchone()

        if not row or row["status"] != 'ativo':
            return False

        try:
            data_devolucao = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # Atualizar empréstimo
            cursor.execute(REGISTRAR_DEVOLUCAO, (data_devolucao, emprestimo_id))

            # Incrementar disponível
            cursor.execute(
                "UPDATE livro SET quantidade_disponivel = quantidade_disponivel + 1 WHERE id = ?",
                (row["id_livro"],)
            )

            conn.commit()

            # TODO: Verificar se há reserva ativa e notificar (Sprint 5)

            return True

        except Exception as e:
            conn.rollback()
            raise e


def renovar_emprestimo(emprestimo_id: int, dias_adicionais: int = 14) -> bool:
    """
    Renova um empréstimo, estendendo o prazo.

    Args:
        emprestimo_id: ID do empréstimo
        dias_adicionais: Dias a adicionar (padrão: 14)

    Returns:
        True se renovado, False se não pode renovar
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Buscar empréstimo
        cursor.execute(OBTER_POR_ID, (emprestimo_id,))
        row = cursor.fetchone()

        if not row or row["status"] != 'ativo':
            return False

        # Verificar limite de renovações (configurável)
        if row["renovacoes"] >= 2:  # TODO: Pegar de configuração
            return False

        # Calcular nova data
        data_atual = datetime.strptime(row["data_devolucao_prevista"], "%Y-%m-%d")
        nova_data = (data_atual + timedelta(days=dias_adicionais)).strftime("%Y-%m-%d")

        cursor.execute(RENOVAR, (nova_data, emprestimo_id))
        return True


def obter_por_id(emprestimo_id: int) -> Optional[Emprestimo]:
    """Retorna um empréstimo pelo ID"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (emprestimo_id,))
        row = cursor.fetchone()
        return _row_to_emprestimo(row) if row else None


def obter_por_leitor(leitor_id: int) -> List[dict]:
    """
    Retorna todos os empréstimos de um leitor com dados do livro.

    Returns:
        Lista de dicts com dados completos para exibição
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_LEITOR, (leitor_id,))
        return [dict(row) for row in cursor.fetchall()]


def obter_ativos_por_leitor(leitor_id: int) -> List[dict]:
    """Retorna empréstimos ativos de um leitor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ATIVOS_POR_LEITOR, (leitor_id,))
        return [dict(row) for row in cursor.fetchall()]


def obter_todos() -> List[dict]:
    """Retorna todos os empréstimos com dados completos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODOS)
        return [dict(row) for row in cursor.fetchall()]


def obter_atrasados() -> List[dict]:
    """Retorna empréstimos atrasados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ATRASADOS)
        return [dict(row) for row in cursor.fetchall()]


def obter_proximos_vencimento(dias: int = 3) -> List[dict]:
    """Retorna empréstimos próximos ao vencimento"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_PROXIMOS_VENCIMENTO)
        return [dict(row) for row in cursor.fetchall()]


def contar_ativos_por_leitor(leitor_id: int) -> int:
    """Conta empréstimos ativos de um leitor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_ATIVOS_POR_LEITOR, (leitor_id,))
        return cursor.fetchone()["total"]


def obter_estatisticas() -> dict:
    """Retorna estatísticas gerais de empréstimos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_STATUS)

        stats = {"ativos": 0, "devolvidos": 0, "atrasados": 0}
        for row in cursor.fetchall():
            stats[row["status"]] = row["total"]

        return stats


def obter_livros_mais_emprestados(limite: int = 10) -> List[dict]:
    """Retorna os livros mais emprestados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(LIVROS_MAIS_EMPRESTADOS, (limite,))
        return [dict(row) for row in cursor.fetchall()]


def obter_leitores_mais_ativos(limite: int = 10) -> List[dict]:
    """Retorna os leitores mais ativos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(LEITORES_MAIS_ATIVOS, (limite,))
        return [dict(row) for row in cursor.fetchall()]


def marcar_atrasado(emprestimo_id: int):
    """Marca um empréstimo como atrasado"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_ATRASADO, (emprestimo_id,))
```

#### Passo 2: Completar Reserva Repository

📁 **Arquivo:** `repo/reserva_repo.py`

```python
"""
Repository para a entidade Reserva.
"""

from typing import List, Optional
from datetime import datetime, timedelta
from model.reserva_model import Reserva
from sql.reserva_sql import *
from util.db_util import get_connection


def _row_to_reserva(row) -> Reserva:
    """Converte linha do banco em objeto Reserva"""
    return Reserva(
        id=row["id"],
        id_livro=row["id_livro"],
        id_leitor=row["id_leitor"],
        data_reserva=row["data_reserva"],
        data_desejada=row.get("data_desejada"),
        data_expiracao=row.get("data_expiracao"),
        status=row["status"],
        notificado=bool(row["notificado"])
    )


def criar_tabela():
    """Cria a tabela de reservas e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)


def criar_reserva(
    id_livro: int,
    id_leitor: int,
    data_desejada: str = None,
    dias_expiracao: int = 7
) -> int:
    """
    Cria uma nova reserva.

    Args:
        id_livro: ID do livro
        id_leitor: ID do leitor
        data_desejada: Data desejada para retirada (opcional)
        dias_expiracao: Dias até expirar (padrão: 7)

    Returns:
        ID da reserva criada
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        data_expiracao = None
        if dias_expiracao > 0:
            data_expiracao = (datetime.now() + timedelta(days=dias_expiracao)).strftime("%Y-%m-%d")

        cursor.execute(INSERIR, (
            id_livro,
            id_leitor,
            data_desejada,
            data_expiracao,
            'ativa'
        ))

        return cursor.lastrowid


def obter_por_id(reserva_id: int) -> Optional[dict]:
    """Retorna uma reserva pelo ID com dados completos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (reserva_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def obter_por_leitor(leitor_id: int) -> List[dict]:
    """Retorna todas as reservas de um leitor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_LEITOR, (leitor_id,))
        return [dict(row) for row in cursor.fetchall()]


def obter_ativas_por_leitor(leitor_id: int) -> List[dict]:
    """Retorna apenas reservas ativas de um leitor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ATIVAS_POR_LEITOR, (leitor_id,))
        return [dict(row) for row in cursor.fetchall()]


def obter_todas() -> List[dict]:
    """Retorna todas as reservas com dados completos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_TODAS)
        return [dict(row) for row in cursor.fetchall()]


def cancelar_reserva(reserva_id: int) -> bool:
    """
    Cancela uma reserva.

    Returns:
        True se cancelada, False se não encontrada ou já cancelada
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Verificar se existe e está ativa
        cursor.execute(OBTER_POR_ID, (reserva_id,))
        row = cursor.fetchone()

        if not row or row["status"] != 'ativa':
            return False

        cursor.execute(CANCELAR, (reserva_id,))
        return True


def atender_reserva(reserva_id: int):
    """Marca uma reserva como atendida"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(ATENDER, (reserva_id,))


def marcar_notificado(reserva_id: int):
    """Marca que o leitor foi notificado"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(MARCAR_NOTIFICADO, (reserva_id,))


def obter_proxima_reserva_livro(id_livro: int) -> Optional[dict]:
    """Retorna a próxima reserva ativa de um livro (FIFO)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_LIVRO, (id_livro,))
        row = cursor.fetchone()
        return dict(row) if row else None


def obter_nao_notificadas() -> List[dict]:
    """Retorna reservas que podem ser notificadas (livro disponível)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_NAO_NOTIFICADAS)
        return [dict(row) for row in cursor.fetchall()]


def expirar_reservas_antigas():
    """Marca reservas expiradas como 'expirada'"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_EXPIRADAS)
        expiradas = cursor.fetchall()

        for reserva in expiradas:
            cursor.execute(EXPIRAR, (reserva["id"],))


def contar_ativas_por_leitor(leitor_id: int) -> int:
    """Conta reservas ativas de um leitor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_ATIVAS_POR_LEITOR, (leitor_id,))
        return cursor.fetchone()["total"]
```

#### Passo 3: Completar Favorito Repository

📁 **Arquivo:** `repo/favorito_repo.py`

```python
"""
Repository para a entidade Favorito.
"""

from typing import List
from model.favorito_model import Favorito
from sql.favorito_sql import *
from util.db_util import get_connection


def criar_tabela():
    """Cria a tabela de favoritos e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)


def adicionar_favorito(id_livro: int, id_leitor: int) -> bool:
    """
    Adiciona um livro aos favoritos.

    Returns:
        True se adicionado, False se já era favorito
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        # Verificar se já existe
        if is_favorito(id_livro, id_leitor):
            return False

        try:
            cursor.execute(ADICIONAR, (id_livro, id_leitor))
            return True
        except:
            # Violação de UNIQUE constraint
            return False


def remover_favorito(id_livro: int, id_leitor: int) -> bool:
    """
    Remove um livro dos favoritos.

    Returns:
        True se removido, False se não era favorito
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(REMOVER, (id_livro, id_leitor))
        return cursor.rowcount > 0


def obter_favoritos_leitor(leitor_id: int) -> List[dict]:
    """Retorna todos os favoritos de um leitor com dados do livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_LEITOR, (leitor_id,))
        return [dict(row) for row in cursor.fetchall()]


def is_favorito(id_livro: int, id_leitor: int) -> bool:
    """Verifica se um livro é favorito de um leitor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(VERIFICAR_FAVORITO, (id_livro, id_leitor))
        return cursor.fetchone()["total"] > 0


def contar_favoritos_leitor(leitor_id: int) -> int:
    """Conta quantos favoritos um leitor tem"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_LEITOR, (leitor_id,))
        return cursor.fetchone()["total"]


def contar_favoritos_livro(livro_id: int) -> int:
    """Conta quantas pessoas favoritaram um livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_POR_LIVRO, (livro_id,))
        return cursor.fetchone()["total"]
```

#### Passo 4: Completar Mensagem Repository

📁 **Arquivo:** `repo/mensagem_repo.py`

```python
"""
Repository para a entidade Mensagem.
"""

from typing import List, Optional
from datetime import datetime
from model.mensagem_model import Mensagem
from sql.mensagem_sql import *
from util.db_util import get_connection


def _row_to_mensagem(row) -> Mensagem:
    """Converte linha do banco em objeto Mensagem"""
    return Mensagem(
        id=row["id"],
        id_remetente=row["id_remetente"],
        id_destinatario=row["id_destinatario"],
        assunto=row["assunto"],
        corpo=row["corpo"],
        lida=bool(row["lida"]),
        data_envio=row["data_envio"],
        data_leitura=row.get("data_leitura")
    )


def criar_tabela():
    """Cria a tabela de mensagens e índices"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CRIAR_TABELA)
        cursor.execute(CRIAR_INDICES)


def enviar_mensagem(
    id_remetente: int,
    id_destinatario: int,
    assunto: str,
    corpo: str
) -> int:
    """
    Envia uma nova mensagem.

    Returns:
        ID da mensagem criada
    """
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(INSERIR, (
            id_remetente,
            id_destinatario,
            assunto,
            corpo
        ))
        return cursor.lastrowid


def obter_recebidas(usuario_id: int) -> List[dict]:
    """Retorna mensagens recebidas por um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_RECEBIDAS, (usuario_id,))
        return [dict(row) for row in cursor.fetchall()]


def obter_enviadas(usuario_id: int) -> List[dict]:
    """Retorna mensagens enviadas por um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_ENVIADAS, (usuario_id,))
        return [dict(row) for row in cursor.fetchall()]


def obter_por_id(mensagem_id: int) -> Optional[dict]:
    """Retorna uma mensagem pelo ID com dados completos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(OBTER_POR_ID, (mensagem_id,))
        row = cursor.fetchone()
        return dict(row) if row else None


def marcar_como_lida(mensagem_id: int):
    """Marca uma mensagem como lida"""
    with get_connection() as conn:
        cursor = conn.cursor()
        data_leitura = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        cursor.execute(MARCAR_COMO_LIDA, (data_leitura, mensagem_id))


def contar_nao_lidas(usuario_id: int) -> int:
    """Conta mensagens não lidas de um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(CONTAR_NAO_LIDAS, (usuario_id,))
        return cursor.fetchone()["total"]


def excluir(mensagem_id: int):
    """Exclui uma mensagem"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(EXCLUIR, (mensagem_id,))
```

### 4.3. Criar Rotas do Leitor

#### Passo 5: Criar arquivo de rotas do leitor

📁 **Arquivo:** `routes/leitor_routes.py`

```python
"""
Rotas para funcionalidades do perfil Leitor.
"""

from fastapi import APIRouter, Request, Form, status
from fastapi.responses import RedirectResponse
from typing import Optional

from util.auth_decorator import requer_autenticacao
from util.template_util import criar_templates
from util.flash_messages import informar_sucesso, informar_erro, informar_aviso
from util.perfis import Perfil

import repo.emprestimo_repo as emprestimo_repo
import repo.reserva_repo as reserva_repo
import repo.favorito_repo as favorito_repo
import repo.mensagem_repo as mensagem_repo
import repo.livro_repo as livro_repo

router = APIRouter(prefix="/leitor")
templates = criar_templates("templates")


@router.get("/dashboard")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def dashboard(request: Request, usuario_logado: dict):
    """Dashboard do leitor com resumo de atividades"""

    leitor_id = usuario_logado["id"]

    # Buscar dados para o dashboard
    emprestimos_ativos = emprestimo_repo.obter_ativos_por_leitor(leitor_id)
    reservas_ativas = reserva_repo.obter_ativas_por_leitor(leitor_id)
    favoritos_count = favorito_repo.contar_favoritos_leitor(leitor_id)
    mensagens_nao_lidas = mensagem_repo.contar_nao_lidas(leitor_id)

    # Identificar empréstimos próximos ao vencimento (3 dias)
    from datetime import datetime, timedelta
    data_limite = (datetime.now() + timedelta(days=3)).strftime("%Y-%m-%d")

    proximos_vencimento = [
        emp for emp in emprestimos_ativos
        if emp["data_devolucao_prevista"] <= data_limite
    ]

    # Identificar atrasados
    data_hoje = datetime.now().strftime("%Y-%m-%d")
    atrasados = [
        emp for emp in emprestimos_ativos
        if emp["data_devolucao_prevista"] < data_hoje
    ]

    return templates.TemplateResponse(
        "leitor/dashboard.html",
        {
            "request": request,
            "emprestimos_ativos": emprestimos_ativos,
            "reservas_ativas": reservas_ativas,
            "favoritos_count": favoritos_count,
            "mensagens_nao_lidas": mensagens_nao_lidas,
            "proximos_vencimento": proximos_vencimento,
            "atrasados": atrasados
        }
    )


# ============= EMPRÉSTIMOS =============

@router.get("/emprestimos")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def listar_emprestimos(request: Request, usuario_logado: dict):
    """Lista todos os empréstimos do leitor"""

    emprestimos = emprestimo_repo.obter_por_leitor(usuario_logado["id"])

    return templates.TemplateResponse(
        "leitor/meus_emprestimos.html",
        {
            "request": request,
            "emprestimos": emprestimos
        }
    )


@router.post("/emprestimos/{emprestimo_id}/renovar")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def renovar_emprestimo(request: Request, emprestimo_id: int, usuario_logado: dict):
    """Renova um empréstimo"""

    # Verificar se o empréstimo pertence ao leitor
    emprestimo = emprestimo_repo.obter_por_id(emprestimo_id)

    if not emprestimo or emprestimo.id_leitor != usuario_logado["id"]:
        informar_erro(request, "Empréstimo não encontrado.")
        return RedirectResponse("/leitor/emprestimos", status_code=status.HTTP_303_SEE_OTHER)

    # Tentar renovar
    if emprestimo_repo.renovar_emprestimo(emprestimo_id):
        informar_sucesso(request, "Empréstimo renovado com sucesso!")
    else:
        informar_erro(request, "Não foi possível renovar. Limite de renovações atingido ou empréstimo já devolvido.")

    return RedirectResponse("/leitor/emprestimos", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/emprestimos/{emprestimo_id}/devolver")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def devolver_livro(request: Request, emprestimo_id: int, usuario_logado: dict):
    """
    Marca um livro como devolvido (auto-devolução).
    Na prática, o bibliotecário deve confirmar, mas para simplicidade
    permitimos que o leitor marque como devolvido.
    """

    # Verificar se o empréstimo pertence ao leitor
    emprestimo = emprestimo_repo.obter_por_id(emprestimo_id)

    if not emprestimo or emprestimo.id_leitor != usuario_logado["id"]:
        informar_erro(request, "Empréstimo não encontrado.")
        return RedirectResponse("/leitor/emprestimos", status_code=status.HTTP_303_SEE_OTHER)

    # Registrar devolução
    if emprestimo_repo.registrar_devolucao(emprestimo_id):
        informar_sucesso(request, "Livro marcado como devolvido! Aguarde confirmação do bibliotecário.")
    else:
        informar_erro(request, "Não foi possível registrar a devolução.")

    return RedirectResponse("/leitor/emprestimos", status_code=status.HTTP_303_SEE_OTHER)


# ============= RESERVAS =============

@router.get("/reservas")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def listar_reservas(request: Request, usuario_logado: dict):
    """Lista todas as reservas do leitor"""

    reservas = reserva_repo.obter_por_leitor(usuario_logado["id"])

    return templates.TemplateResponse(
        "leitor/minhas_reservas.html",
        {
            "request": request,
            "reservas": reservas
        }
    )


@router.post("/reservas/criar")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def criar_reserva(
    request: Request,
    usuario_logado: dict,
    id_livro: int = Form(...),
    data_desejada: Optional[str] = Form(None)
):
    """Cria uma nova reserva"""

    # Verificar se o livro existe
    livro = livro_repo.obter_por_id(id_livro)
    if not livro:
        informar_erro(request, "Livro não encontrado.")
        return RedirectResponse("/", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se já tem reserva ativa para este livro
    reservas_ativas = reserva_repo.obter_ativas_por_leitor(usuario_logado["id"])
    if any(r["id_livro"] == id_livro for r in reservas_ativas):
        informar_aviso(request, "Você já possui uma reserva ativa para este livro.")
        return RedirectResponse("/leitor/reservas", status_code=status.HTTP_303_SEE_OTHER)

    # Criar reserva
    reserva_repo.criar_reserva(
        id_livro=id_livro,
        id_leitor=usuario_logado["id"],
        data_desejada=data_desejada
    )

    informar_sucesso(request, f"Reserva criada para '{livro.titulo}'!")
    return RedirectResponse("/leitor/reservas", status_code=status.HTTP_303_SEE_OTHER)


@router.post("/reservas/{reserva_id}/cancelar")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def cancelar_reserva(request: Request, reserva_id: int, usuario_logado: dict):
    """Cancela uma reserva"""

    # Verificar se a reserva pertence ao leitor
    reserva = reserva_repo.obter_por_id(reserva_id)

    if not reserva or reserva["id_leitor"] != usuario_logado["id"]:
        informar_erro(request, "Reserva não encontrada.")
        return RedirectResponse("/leitor/reservas", status_code=status.HTTP_303_SEE_OTHER)

    # Cancelar
    if reserva_repo.cancelar_reserva(reserva_id):
        informar_sucesso(request, "Reserva cancelada com sucesso!")
    else:
        informar_erro(request, "Não foi possível cancelar a reserva.")

    return RedirectResponse("/leitor/reservas", status_code=status.HTTP_303_SEE_OTHER)


# ============= FAVORITOS =============

@router.get("/favoritos")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def listar_favoritos(request: Request, usuario_logado: dict):
    """Lista todos os favoritos do leitor"""

    favoritos = favorito_repo.obter_favoritos_leitor(usuario_logado["id"])

    return templates.TemplateResponse(
        "leitor/favoritos.html",
        {
            "request": request,
            "favoritos": favoritos
        }
    )


@router.post("/favoritos/{livro_id}/adicionar")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def adicionar_favorito(request: Request, livro_id: int, usuario_logado: dict):
    """Adiciona um livro aos favoritos"""

    if favorito_repo.adicionar_favorito(livro_id, usuario_logado["id"]):
        informar_sucesso(request, "Livro adicionado aos favoritos!")
    else:
        informar_aviso(request, "Este livro já está nos seus favoritos.")

    # Redirecionar de volta para a página anterior
    referer = request.headers.get("referer", "/leitor/favoritos")
    return RedirectResponse(referer, status_code=status.HTTP_303_SEE_OTHER)


@router.post("/favoritos/{livro_id}/remover")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def remover_favorito(request: Request, livro_id: int, usuario_logado: dict):
    """Remove um livro dos favoritos"""

    if favorito_repo.remover_favorito(livro_id, usuario_logado["id"]):
        informar_sucesso(request, "Livro removido dos favoritos.")
    else:
        informar_erro(request, "Livro não está nos favoritos.")

    return RedirectResponse("/leitor/favoritos", status_code=status.HTTP_303_SEE_OTHER)


# ============= MENSAGENS =============

@router.get("/mensagens")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def listar_mensagens(request: Request, usuario_logado: dict):
    """Lista mensagens recebidas"""

    mensagens = mensagem_repo.obter_recebidas(usuario_logado["id"])

    return templates.TemplateResponse(
        "leitor/mensagens/inbox.html",
        {
            "request": request,
            "mensagens": mensagens
        }
    )


@router.get("/mensagens/{mensagem_id}")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def ler_mensagem(request: Request, mensagem_id: int, usuario_logado: dict):
    """Exibe uma mensagem específica"""

    mensagem = mensagem_repo.obter_por_id(mensagem_id)

    if not mensagem:
        informar_erro(request, "Mensagem não encontrada.")
        return RedirectResponse("/leitor/mensagens", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar se o usuário é destinatário ou remetente
    if mensagem["id_destinatario"] != usuario_logado["id"] and mensagem["id_remetente"] != usuario_logado["id"]:
        informar_erro(request, "Você não tem permissão para ver esta mensagem.")
        return RedirectResponse("/leitor/mensagens", status_code=status.HTTP_303_SEE_OTHER)

    # Marcar como lida se for destinatário
    if mensagem["id_destinatario"] == usuario_logado["id"] and not mensagem["lida"]:
        mensagem_repo.marcar_como_lida(mensagem_id)

    return templates.TemplateResponse(
        "leitor/mensagens/ler.html",
        {
            "request": request,
            "mensagem": mensagem
        }
    )


@router.get("/mensagens/enviar")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def enviar_mensagem_get(request: Request, usuario_logado: dict):
    """Formulário para enviar mensagem"""

    # Buscar bibliotecários para enviar mensagem
    import repo.usuario_repo as usuario_repo
    bibliotecarios = usuario_repo.obter_por_perfil(Perfil.BIBLIOTECARIO.value)

    return templates.TemplateResponse(
        "leitor/mensagens/enviar.html",
        {
            "request": request,
            "bibliotecarios": bibliotecarios
        }
    )


@router.post("/mensagens/enviar")
@requer_autenticacao([Perfil.LEITOR.value, Perfil.BIBLIOTECARIO.value, Perfil.ADMIN.value])
async def enviar_mensagem_post(
    request: Request,
    usuario_logado: dict,
    id_destinatario: int = Form(...),
    assunto: str = Form(...),
    corpo: str = Form(...)
):
    """Envia uma nova mensagem"""

    mensagem_repo.enviar_mensagem(
        id_remetente=usuario_logado["id"],
        id_destinatario=id_destinatario,
        assunto=assunto,
        corpo=corpo
    )

    informar_sucesso(request, "Mensagem enviada com sucesso!")
    return RedirectResponse("/leitor/mensagens", status_code=status.HTTP_303_SEE_OTHER)
```

#### Passo 6: Adicionar método obter_por_perfil no usuario_repo

📝 **Arquivo:** `repo/usuario_repo.py`

**Adicionar ao final do arquivo:**

```python
def obter_por_perfil(perfil: str) -> List[Usuario]:
    """Retorna todos os usuários de um perfil específico"""
    with get_connection() as conn:
        cursor = conn.cursor()
        from sql.usuario_sql import OBTER_POR_PERFIL
        cursor.execute(OBTER_POR_PERFIL, (perfil,))
        return [_row_to_usuario(row) for row in cursor.fetchall()]
```

### 4.4. Criar Templates do Leitor

#### Passo 7: Criar Dashboard do Leitor

📁 **Arquivo:** `templates/leitor/dashboard.html`

```html
{% extends "base_privada.html" %}

{% block titulo %}Meu Painel{% endblock %}

{% block content %}
<div class="row mb-4">
    <div class="col-12">
        <h2 class="mb-3">
            <i class="bi bi-speedometer2"></i> Meu Painel
        </h2>
    </div>
</div>

<!-- Cards de Resumo -->
<div class="row g-3 mb-4">
    <!-- Empréstimos Ativos -->
    <div class="col-md-3">
        <div class="card bg-primary text-white shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-0">Empréstimos Ativos</h6>
                        <h2 class="mb-0">{{ emprestimos_ativos|length }}</h2>
                    </div>
                    <i class="bi bi-book-half fs-1 opacity-50"></i>
                </div>
            </div>
            <div class="card-footer bg-transparent border-0">
                <a href="/leitor/emprestimos" class="text-white text-decoration-none">
                    Ver todos <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        </div>
    </div>

    <!-- Reservas Ativas -->
    <div class="col-md-3">
        <div class="card bg-success text-white shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-0">Reservas Ativas</h6>
                        <h2 class="mb-0">{{ reservas_ativas|length }}</h2>
                    </div>
                    <i class="bi bi-bookmark-star fs-1 opacity-50"></i>
                </div>
            </div>
            <div class="card-footer bg-transparent border-0">
                <a href="/leitor/reservas" class="text-white text-decoration-none">
                    Ver todas <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        </div>
    </div>

    <!-- Favoritos -->
    <div class="col-md-3">
        <div class="card bg-warning text-dark shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-0">Favoritos</h6>
                        <h2 class="mb-0">{{ favoritos_count }}</h2>
                    </div>
                    <i class="bi bi-heart-fill fs-1 opacity-50"></i>
                </div>
            </div>
            <div class="card-footer bg-transparent border-0">
                <a href="/leitor/favoritos" class="text-dark text-decoration-none">
                    Ver favoritos <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        </div>
    </div>

    <!-- Mensagens -->
    <div class="col-md-3">
        <div class="card bg-info text-white shadow-sm">
            <div class="card-body">
                <div class="d-flex justify-content-between align-items-center">
                    <div>
                        <h6 class="card-title mb-0">Mensagens</h6>
                        <h2 class="mb-0">{{ mensagens_nao_lidas }}</h2>
                        <small>não lidas</small>
                    </div>
                    <i class="bi bi-envelope-fill fs-1 opacity-50"></i>
                </div>
            </div>
            <div class="card-footer bg-transparent border-0">
                <a href="/leitor/mensagens" class="text-white text-decoration-none">
                    Ver mensagens <i class="bi bi-arrow-right"></i>
                </a>
            </div>
        </div>
    </div>
</div>

<!-- Alertas -->
{% if atrasados %}
<div class="alert alert-danger shadow-sm" role="alert">
    <h5 class="alert-heading">
        <i class="bi bi-exclamation-triangle-fill"></i> Você tem {{ atrasados|length }} empréstimo(s) atrasado(s)!
    </h5>
    <p class="mb-0">Por favor, devolva os livros o quanto antes para evitar multas.</p>
    <hr>
    <a href="/leitor/emprestimos" class="alert-link">Ver empréstimos atrasados</a>
</div>
{% endif %}

{% if proximos_vencimento %}
<div class="alert alert-warning shadow-sm" role="alert">
    <h5 class="alert-heading">
        <i class="bi bi-clock-fill"></i> {{ proximos_vencimento|length }} empréstimo(s) vence(m) em breve
    </h5>
    <p class="mb-0">Você tem livros com devolução prevista para os próximos 3 dias.</p>
    <hr>
    <a href="/leitor/emprestimos" class="alert-link">Ver detalhes</a>
</div>
{% endif %}

<!-- Empréstimos Ativos -->
{% if emprestimos_ativos %}
<div class="row">
    <div class="col-12">
        <div class="card shadow-sm">
            <div class="card-header bg-primary text-white">
                <h5 class="mb-0"><i class="bi bi-book"></i> Meus Empréstimos Ativos</h5>
            </div>
            <div class="card-body">
                <div class="table-responsive">
                    <table class="table table-hover align-middle mb-0">
                        <thead class="table-light">
                            <tr>
                                <th>Livro</th>
                                <th>Data Empréstimo</th>
                                <th>Devolução Prevista</th>
                                <th>Renovações</th>
                                <th class="text-center">Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for emp in emprestimos_ativos %}
                            <tr>
                                <td>
                                    <strong>{{ emp.livro_titulo }}</strong>
                                </td>
                                <td>{{ emp.data_emprestimo[:10] }}</td>
                                <td>
                                    {% set dias_restantes = (emp.data_devolucao_prevista | string)[:10] %}
                                    {{ dias_restantes }}
                                    {% if dias_restantes < (now() | string)[:10] %}
                                        <span class="badge bg-danger">ATRASADO</span>
                                    {% endif %}
                                </td>
                                <td>{{ emp.renovacoes }}/2</td>
                                <td class="text-center">
                                    <div class="btn-group btn-group-sm">
                                        <form method="POST" action="/leitor/emprestimos/{{ emp.id }}/renovar" class="d-inline">
                                            <button type="submit" class="btn btn-outline-primary" title="Renovar"
                                                    {% if emp.renovacoes >= 2 %}disabled{% endif %}>
                                                <i class="bi bi-arrow-clockwise"></i>
                                            </button>
                                        </form>
                                        <form method="POST" action="/leitor/emprestimos/{{ emp.id }}/devolver" class="d-inline">
                                            <button type="submit" class="btn btn-outline-success" title="Devolver">
                                                <i class="bi bi-check-circle"></i>
                                            </button>
                                        </form>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
    </div>
</div>
{% else %}
<div class="alert alert-info shadow-sm">
    <i class="bi bi-info-circle"></i> Você não possui empréstimos ativos no momento.
    <a href="/" class="alert-link">Explore o catálogo</a> para emprestar livros.
</div>
{% endif %}

{% endblock %}
```

**⚠️ IMPORTANTE:** Devido ao limite de espaço, vou fornecer templates simplificados para os demais. Você pode expandir com base no padrão do dashboard.

#### Passo 8: Criar templates restantes

📁 **Arquivo:** `templates/leitor/meus_emprestimos.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Meus Empréstimos{% endblock %}

{% block content %}
<h2><i class="bi bi-book-half"></i> Meus Empréstimos</h2>

<div class="card mt-3">
    <div class="card-body">
        {% if emprestimos %}
        <table class="table">
            <thead>
                <tr>
                    <th>Livro</th>
                    <th>Data Empréstimo</th>
                    <th>Devolução Prevista</th>
                    <th>Status</th>
                    <th>Renovações</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                {% for emp in emprestimos %}
                <tr>
                    <td>{{ emp.livro_titulo }}</td>
                    <td>{{ emp.data_emprestimo[:10] }}</td>
                    <td>{{ emp.data_devolucao_prevista }}</td>
                    <td>
                        <span class="badge bg-{{ 'success' if emp.status == 'devolvido' else 'danger' if emp.status == 'atrasado' else 'primary' }}">
                            {{ emp.status }}
                        </span>
                    </td>
                    <td>{{ emp.renovacoes }}/2</td>
                    <td>
                        {% if emp.status == 'ativo' %}
                        <form method="POST" action="/leitor/emprestimos/{{ emp.id }}/renovar" class="d-inline">
                            <button class="btn btn-sm btn-primary" {% if emp.renovacoes >= 2 %}disabled{% endif %}>
                                Renovar
                            </button>
                        </form>
                        <form method="POST" action="/leitor/emprestimos/{{ emp.id }}/devolver" class="d-inline">
                            <button class="btn btn-sm btn-success">Devolver</button>
                        </form>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>Você não possui empréstimos.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

📁 **Arquivo:** `templates/leitor/minhas_reservas.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Minhas Reservas{% endblock %}

{% block content %}
<h2><i class="bi bi-bookmark-star"></i> Minhas Reservas</h2>

<div class="card mt-3">
    <div class="card-body">
        {% if reservas %}
        <table class="table">
            <thead>
                <tr>
                    <th>Livro</th>
                    <th>Data Reserva</th>
                    <th>Data Desejada</th>
                    <th>Status</th>
                    <th>Ações</th>
                </tr>
            </thead>
            <tbody>
                {% for res in reservas %}
                <tr>
                    <td>{{ res.livro_titulo }}</td>
                    <td>{{ res.data_reserva[:10] }}</td>
                    <td>{{ res.data_desejada or '-' }}</td>
                    <td>
                        <span class="badge bg-{{ 'success' if res.status == 'atendida' else 'secondary' if res.status == 'cancelada' else 'primary' }}">
                            {{ res.status }}
                        </span>
                    </td>
                    <td>
                        {% if res.status == 'ativa' %}
                        <form method="POST" action="/leitor/reservas/{{ res.id }}/cancelar">
                            <button class="btn btn-sm btn-danger">Cancelar</button>
                        </form>
                        {% endif %}
                    </td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
        {% else %}
        <p>Você não possui reservas.</p>
        {% endif %}
    </div>
</div>
{% endblock %}
```

📁 **Arquivo:** `templates/leitor/favoritos.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Meus Favoritos{% endblock %}

{% block content %}
<h2><i class="bi bi-heart-fill"></i> Meus Favoritos</h2>

<div class="row mt-3">
    {% if favoritos %}
        {% for fav in favoritos %}
        <div class="col-md-3 mb-3">
            <div class="card h-100">
                {% if fav.capa_url %}
                <img src="{{ fav.capa_url }}" class="card-img-top" alt="{{ fav.titulo }}">
                {% endif %}
                <div class="card-body">
                    <h6 class="card-title">{{ fav.titulo }}</h6>
                    <p class="small text-muted">{{ fav.subtitulo or '' }}</p>
                    <span class="badge bg-{{ 'success' if fav.quantidade_disponivel > 0 else 'secondary' }}">
                        {{ 'Disponível' if fav.quantidade_disponivel > 0 else 'Indisponível' }}
                    </span>
                </div>
                <div class="card-footer">
                    <form method="POST" action="/leitor/favoritos/{{ fav.id_livro }}/remover">
                        <button class="btn btn-sm btn-outline-danger w-100">
                            <i class="bi bi-heart-fill"></i> Remover
                        </button>
                    </form>
                </div>
            </div>
        </div>
        {% endfor %}
    {% else %}
    <div class="col-12">
        <p>Você não possui livros favoritados.</p>
    </div>
    {% endif %}
</div>
{% endblock %}
```

📁 **Arquivo:** `templates/leitor/mensagens/inbox.html`
📁 **Arquivo:** `templates/leitor/mensagens/ler.html`
📁 **Arquivo:** `templates/leitor/mensagens/enviar.html`

**Crie estes templates seguindo o padrão acima** (estrutura de tabela/formulário).

### 4.5. Registrar Rotas no main.py

📝 **Arquivo:** `main.py`

**Adicionar import:**

```python
from routes import leitor_routes
```

**Adicionar no final da seção de routers:**

```python
app.include_router(leitor_routes.router)
logger.info("Router de leitor incluído")
```

### 4.6. Testar Sprint 2

#### Como Testar:

1. **Executar aplicação:**
   ```bash
   python main.py
   ```

2. **Login como leitor:**
   - Email: `joao.leitor@biblix.com`
   - Senha: `1234aA@#`

3. **Testar funcionalidades:**
   - ✅ Acessar `/leitor/dashboard`
   - ✅ Ver empréstimos (vazio inicialmente)
   - ✅ Ver reservas (vazio inicialmente)
   - ✅ Ver favoritos (vazio inicialmente)
   - ✅ Ver mensagens (vazio inicialmente)

4. **Testar criação de dados (via Python console ou SQL):**
   ```python
   # Teste rápido: criar um empréstimo
   import repo.emprestimo_repo as emprestimo_repo

   # Primeiro, crie um livro e autor no banco manualmente
   # Depois teste registrar empréstimo
   ```

### 4.7. Checklist Sprint 2

- [ ] emprestimo_repo.py completo e testado
- [ ] reserva_repo.py completo e testado
- [ ] favorito_repo.py completo e testado
- [ ] mensagem_repo.py completo e testado
- [ ] usuario_repo.obter_por_perfil() adicionado
- [ ] leitor_routes.py criado com todas as rotas
- [ ] Dashboard do leitor criado
- [ ] Template meus_emprestimos.html criado
- [ ] Template minhas_reservas.html criado
- [ ] Template favoritos.html criado
- [ ] Templates de mensagens criados
- [ ] Router registrado no main.py
- [ ] Testado login como leitor
- [ ] Testado acesso ao dashboard
- [ ] Todas as rotas acessíveis sem erro 404

---

## 5. SPRINT 3: FUNCIONALIDADES DO BIBLIOTECÁRIO

**Duração estimada:** 48 horas

**Objetivo:** Implementar todas as funcionalidades necessárias para que bibliotecários possam gerenciar o acervo, empréstimos e leitores.

**Entregas:**
- ✅ CRUD completo de Livros (com autores e categorias)
- ✅ CRUD completo de Autores
- ✅ CRUD completo de Categorias
- ✅ Sistema de gestão de empréstimos (registrar/devolver/renovar)
- ✅ Sistema de gestão de leitores
- ✅ Dashboard de estatísticas
- ✅ 20+ templates para área do bibliotecário

---

### 5.1. Criar Rotas do Bibliotecário

📁 **Arquivo:** `routes/bibliotecario_routes.py`

```python
from datetime import datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Form, Path, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import repo.autor_repo as autor_repo
import repo.categoria_repo as categoria_repo
import repo.livro_repo as livro_repo
import repo.emprestimo_repo as emprestimo_repo
import repo.usuario_repo as usuario_repo
import repo.reserva_repo as reserva_repo
from dtos.livro_dto import LivroDTO
from dtos.autor_dto import AutorDTO
from dtos.categoria_dto import CategoriaDTO
from util.auth_decorator import auth_decorator
from util.flash_messages import flash_error, flash_success
from util.perfis import Perfil

router = APIRouter(prefix="/bibliotecario")
templates = Jinja2Templates(directory="templates")

# ==================== DASHBOARD ====================

@router.get("/dashboard")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_dashboard(request: Request):
    """Dashboard principal do bibliotecário com estatísticas"""

    # Estatísticas gerais
    total_livros = livro_repo.contar_total()
    total_exemplares = livro_repo.contar_exemplares_total()
    exemplares_disponiveis = livro_repo.contar_exemplares_disponiveis()
    total_autores = autor_repo.contar_total()
    total_categorias = categoria_repo.contar_total()
    total_leitores = usuario_repo.contar_por_perfil(Perfil.LEITOR.value)

    # Estatísticas de empréstimos
    emprestimos_ativos = emprestimo_repo.contar_ativos()
    emprestimos_atrasados = emprestimo_repo.contar_atrasados()
    emprestimos_hoje = emprestimo_repo.contar_por_data(datetime.now().date())
    devolucoes_hoje = emprestimo_repo.contar_devolucoes_por_data(datetime.now().date())

    # Top 5 livros mais emprestados
    livros_mais_emprestados = livro_repo.obter_mais_emprestados(limite=5)

    # Empréstimos recentes (últimos 10)
    emprestimos_recentes = emprestimo_repo.obter_recentes(limite=10)

    # Próximas devoluções (próximos 7 dias)
    data_limite = datetime.now().date() + timedelta(days=7)
    proximas_devolucoes = emprestimo_repo.obter_proximas_devolucoes(data_limite)

    # Reservas pendentes
    reservas_pendentes = reserva_repo.obter_pendentes(limite=10)

    return templates.TemplateResponse(
        "bibliotecario/dashboard.html",
        {
            "request": request,
            "stats": {
                "total_livros": total_livros,
                "total_exemplares": total_exemplares,
                "exemplares_disponiveis": exemplares_disponiveis,
                "total_autores": total_autores,
                "total_categorias": total_categorias,
                "total_leitores": total_leitores,
                "emprestimos_ativos": emprestimos_ativos,
                "emprestimos_atrasados": emprestimos_atrasados,
                "emprestimos_hoje": emprestimos_hoje,
                "devolucoes_hoje": devolucoes_hoje,
            },
            "livros_mais_emprestados": livros_mais_emprestados,
            "emprestimos_recentes": emprestimos_recentes,
            "proximas_devolucoes": proximas_devolucoes,
            "reservas_pendentes": reservas_pendentes,
        }
    )

# ==================== CRUD AUTORES ====================

@router.get("/autores")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_autores(request: Request, busca: Optional[str] = Query(None)):
    """Listar todos os autores com busca opcional"""
    if busca:
        autores = autor_repo.buscar_por_nome(busca)
    else:
        autores = autor_repo.obter_todos()

    return templates.TemplateResponse(
        "bibliotecario/autores/listar.html",
        {"request": request, "autores": autores, "busca": busca}
    )

@router.get("/autores/novo")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_novo_autor(request: Request):
    """Formulário para criar novo autor"""
    return templates.TemplateResponse(
        "bibliotecario/autores/form.html",
        {"request": request, "autor": None}
    )

@router.post("/autores/novo")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_novo_autor(
    request: Request,
    nome: str = Form(...),
    biografia: Optional[str] = Form(None),
    data_nascimento: Optional[str] = Form(None),
    nacionalidade: Optional[str] = Form(None),
):
    """Criar novo autor"""
    try:
        # Validar com DTO
        autor_dto = AutorDTO(
            nome=nome,
            biografia=biografia,
            data_nascimento=data_nascimento,
            nacionalidade=nacionalidade
        )

        # Inserir no banco
        autor_id = autor_repo.inserir(autor_dto)

        if autor_id:
            flash_success(request, f"Autor '{nome}' cadastrado com sucesso!")
            return RedirectResponse(
                f"/bibliotecario/autores/{autor_id}",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            flash_error(request, "Erro ao cadastrar autor.")
            return RedirectResponse(
                "/bibliotecario/autores/novo",
                status_code=status.HTTP_303_SEE_OTHER
            )
    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            "/bibliotecario/autores/novo",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.get("/autores/{id_autor}")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_detalhe_autor(request: Request, id_autor: int = Path(...)):
    """Detalhes de um autor"""
    autor = autor_repo.obter_por_id(id_autor)
    if not autor:
        flash_error(request, "Autor não encontrado.")
        return RedirectResponse(
            "/bibliotecario/autores",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Buscar livros desse autor
    livros = livro_repo.obter_por_autor(id_autor)

    return templates.TemplateResponse(
        "bibliotecario/autores/detalhe.html",
        {"request": request, "autor": autor, "livros": livros}
    )

@router.get("/autores/{id_autor}/editar")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_editar_autor(request: Request, id_autor: int = Path(...)):
    """Formulário para editar autor"""
    autor = autor_repo.obter_por_id(id_autor)
    if not autor:
        flash_error(request, "Autor não encontrado.")
        return RedirectResponse(
            "/bibliotecario/autores",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        "bibliotecario/autores/form.html",
        {"request": request, "autor": autor}
    )

@router.post("/autores/{id_autor}/editar")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_editar_autor(
    request: Request,
    id_autor: int = Path(...),
    nome: str = Form(...),
    biografia: Optional[str] = Form(None),
    data_nascimento: Optional[str] = Form(None),
    nacionalidade: Optional[str] = Form(None),
):
    """Atualizar autor"""
    try:
        autor_dto = AutorDTO(
            id=id_autor,
            nome=nome,
            biografia=biografia,
            data_nascimento=data_nascimento,
            nacionalidade=nacionalidade
        )

        sucesso = autor_repo.atualizar(autor_dto)

        if sucesso:
            flash_success(request, f"Autor '{nome}' atualizado com sucesso!")
        else:
            flash_error(request, "Erro ao atualizar autor.")

        return RedirectResponse(
            f"/bibliotecario/autores/{id_autor}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            f"/bibliotecario/autores/{id_autor}/editar",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.post("/autores/{id_autor}/excluir")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_excluir_autor(request: Request, id_autor: int = Path(...)):
    """Excluir autor"""
    autor = autor_repo.obter_por_id(id_autor)
    if not autor:
        flash_error(request, "Autor não encontrado.")
    else:
        # Verificar se há livros associados
        livros = livro_repo.obter_por_autor(id_autor)
        if livros:
            flash_error(request, f"Não é possível excluir: autor possui {len(livros)} livro(s) cadastrado(s).")
        else:
            sucesso = autor_repo.excluir(id_autor)
            if sucesso:
                flash_success(request, f"Autor '{autor.nome}' excluído com sucesso!")
            else:
                flash_error(request, "Erro ao excluir autor.")

    return RedirectResponse(
        "/bibliotecario/autores",
        status_code=status.HTTP_303_SEE_OTHER
    )

# ==================== CRUD CATEGORIAS ====================

@router.get("/categorias")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_categorias(request: Request):
    """Listar todas as categorias"""
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "bibliotecario/categorias/listar.html",
        {"request": request, "categorias": categorias}
    )

@router.get("/categorias/novo")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_nova_categoria(request: Request):
    """Formulário para criar nova categoria"""
    return templates.TemplateResponse(
        "bibliotecario/categorias/form.html",
        {"request": request, "categoria": None}
    )

@router.post("/categorias/novo")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_nova_categoria(
    request: Request,
    nome: str = Form(...),
    descricao: Optional[str] = Form(None),
):
    """Criar nova categoria"""
    try:
        categoria_dto = CategoriaDTO(nome=nome, descricao=descricao)
        categoria_id = categoria_repo.inserir(categoria_dto)

        if categoria_id:
            flash_success(request, f"Categoria '{nome}' cadastrada com sucesso!")
            return RedirectResponse(
                "/bibliotecario/categorias",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            flash_error(request, "Erro ao cadastrar categoria.")
            return RedirectResponse(
                "/bibliotecario/categorias/novo",
                status_code=status.HTTP_303_SEE_OTHER
            )
    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            "/bibliotecario/categorias/novo",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.get("/categorias/{id_categoria}/editar")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_editar_categoria(request: Request, id_categoria: int = Path(...)):
    """Formulário para editar categoria"""
    categoria = categoria_repo.obter_por_id(id_categoria)
    if not categoria:
        flash_error(request, "Categoria não encontrada.")
        return RedirectResponse(
            "/bibliotecario/categorias",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        "bibliotecario/categorias/form.html",
        {"request": request, "categoria": categoria}
    )

@router.post("/categorias/{id_categoria}/editar")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_editar_categoria(
    request: Request,
    id_categoria: int = Path(...),
    nome: str = Form(...),
    descricao: Optional[str] = Form(None),
):
    """Atualizar categoria"""
    try:
        categoria_dto = CategoriaDTO(id=id_categoria, nome=nome, descricao=descricao)
        sucesso = categoria_repo.atualizar(categoria_dto)

        if sucesso:
            flash_success(request, f"Categoria '{nome}' atualizada com sucesso!")
        else:
            flash_error(request, "Erro ao atualizar categoria.")

        return RedirectResponse(
            "/bibliotecario/categorias",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            f"/bibliotecario/categorias/{id_categoria}/editar",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.post("/categorias/{id_categoria}/excluir")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_excluir_categoria(request: Request, id_categoria: int = Path(...)):
    """Excluir categoria"""
    categoria = categoria_repo.obter_por_id(id_categoria)
    if not categoria:
        flash_error(request, "Categoria não encontrada.")
    else:
        # Verificar se há livros associados
        livros = livro_repo.obter_por_categoria(id_categoria)
        if livros:
            flash_error(request, f"Não é possível excluir: categoria possui {len(livros)} livro(s) cadastrado(s).")
        else:
            sucesso = categoria_repo.excluir(id_categoria)
            if sucesso:
                flash_success(request, f"Categoria '{categoria.nome}' excluída com sucesso!")
            else:
                flash_error(request, "Erro ao excluir categoria.")

    return RedirectResponse(
        "/bibliotecario/categorias",
        status_code=status.HTTP_303_SEE_OTHER
    )

# ==================== CRUD LIVROS ====================

@router.get("/livros")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_livros(
    request: Request,
    busca: Optional[str] = Query(None),
    categoria: Optional[int] = Query(None),
    autor: Optional[int] = Query(None),
):
    """Listar todos os livros com filtros"""
    if busca:
        livros = livro_repo.buscar(busca)
    elif categoria:
        livros = livro_repo.obter_por_categoria(categoria)
    elif autor:
        livros = livro_repo.obter_por_autor(autor)
    else:
        livros = livro_repo.obter_todos()

    # Para os filtros
    categorias = categoria_repo.obter_todos()
    autores = autor_repo.obter_todos()

    return templates.TemplateResponse(
        "bibliotecario/livros/listar.html",
        {
            "request": request,
            "livros": livros,
            "categorias": categorias,
            "autores": autores,
            "busca": busca,
            "categoria_selecionada": categoria,
            "autor_selecionado": autor,
        }
    )

@router.get("/livros/novo")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_novo_livro(request: Request):
    """Formulário para criar novo livro"""
    autores = autor_repo.obter_todos()
    categorias = categoria_repo.obter_todos()

    return templates.TemplateResponse(
        "bibliotecario/livros/form.html",
        {"request": request, "livro": None, "autores": autores, "categorias": categorias}
    )

@router.post("/livros/novo")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_novo_livro(
    request: Request,
    titulo: str = Form(...),
    subtitulo: Optional[str] = Form(None),
    isbn: str = Form(...),
    editora: str = Form(...),
    ano_publicacao: int = Form(...),
    edicao: Optional[int] = Form(None),
    idioma: str = Form(...),
    paginas: Optional[int] = Form(None),
    sinopse: Optional[str] = Form(None),
    quantidade_total: int = Form(...),
    localizacao: Optional[str] = Form(None),
    autores: list[int] = Form(...),  # IDs dos autores
    categorias: list[int] = Form(...),  # IDs das categorias
):
    """Criar novo livro"""
    try:
        # Validar com DTO
        livro_dto = LivroDTO(
            titulo=titulo,
            subtitulo=subtitulo,
            isbn=isbn,
            editora=editora,
            ano_publicacao=ano_publicacao,
            edicao=edicao,
            idioma=idioma,
            paginas=paginas,
            sinopse=sinopse,
            quantidade_total=quantidade_total,
            quantidade_disponivel=quantidade_total,  # Inicialmente, todos disponíveis
            localizacao=localizacao,
        )

        # Inserir livro
        livro_id = livro_repo.inserir(livro_dto)

        if livro_id:
            # Associar autores
            for id_autor in autores:
                livro_repo.adicionar_autor(livro_id, id_autor)

            # Associar categorias
            for id_categoria in categorias:
                livro_repo.adicionar_categoria(livro_id, id_categoria)

            flash_success(request, f"Livro '{titulo}' cadastrado com sucesso!")
            return RedirectResponse(
                f"/bibliotecario/livros/{livro_id}",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            flash_error(request, "Erro ao cadastrar livro.")
            return RedirectResponse(
                "/bibliotecario/livros/novo",
                status_code=status.HTTP_303_SEE_OTHER
            )
    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            "/bibliotecario/livros/novo",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.get("/livros/{id_livro}")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_detalhe_livro(request: Request, id_livro: int = Path(...)):
    """Detalhes de um livro"""
    livro = livro_repo.obter_por_id_completo(id_livro)
    if not livro:
        flash_error(request, "Livro não encontrado.")
        return RedirectResponse(
            "/bibliotecario/livros",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Estatísticas do livro
    total_emprestimos = emprestimo_repo.contar_por_livro(id_livro)
    emprestimos_ativos = emprestimo_repo.contar_ativos_por_livro(id_livro)
    reservas_ativas = reserva_repo.contar_ativas_por_livro(id_livro)

    # Histórico recente
    historico = emprestimo_repo.obter_por_livro(id_livro, limite=10)

    return templates.TemplateResponse(
        "bibliotecario/livros/detalhe.html",
        {
            "request": request,
            "livro": livro,
            "stats": {
                "total_emprestimos": total_emprestimos,
                "emprestimos_ativos": emprestimos_ativos,
                "reservas_ativas": reservas_ativas,
            },
            "historico": historico,
        }
    )

@router.get("/livros/{id_livro}/editar")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_editar_livro(request: Request, id_livro: int = Path(...)):
    """Formulário para editar livro"""
    livro = livro_repo.obter_por_id_completo(id_livro)
    if not livro:
        flash_error(request, "Livro não encontrado.")
        return RedirectResponse(
            "/bibliotecario/livros",
            status_code=status.HTTP_303_SEE_OTHER
        )

    autores = autor_repo.obter_todos()
    categorias = categoria_repo.obter_todos()

    # IDs dos autores e categorias já associados
    autores_livro = [a.id for a in livro_repo.obter_autores(id_livro)]
    categorias_livro = [c.id for c in livro_repo.obter_categorias(id_livro)]

    return templates.TemplateResponse(
        "bibliotecario/livros/form.html",
        {
            "request": request,
            "livro": livro,
            "autores": autores,
            "categorias": categorias,
            "autores_livro": autores_livro,
            "categorias_livro": categorias_livro,
        }
    )

@router.post("/livros/{id_livro}/editar")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_editar_livro(
    request: Request,
    id_livro: int = Path(...),
    titulo: str = Form(...),
    subtitulo: Optional[str] = Form(None),
    isbn: str = Form(...),
    editora: str = Form(...),
    ano_publicacao: int = Form(...),
    edicao: Optional[int] = Form(None),
    idioma: str = Form(...),
    paginas: Optional[int] = Form(None),
    sinopse: Optional[str] = Form(None),
    quantidade_total: int = Form(...),
    localizacao: Optional[str] = Form(None),
    autores: list[int] = Form(...),
    categorias: list[int] = Form(...),
):
    """Atualizar livro"""
    try:
        livro_atual = livro_repo.obter_por_id(id_livro)
        if not livro_atual:
            flash_error(request, "Livro não encontrado.")
            return RedirectResponse(
                "/bibliotecario/livros",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # Calcular nova quantidade disponível
        diferenca = quantidade_total - livro_atual.quantidade_total
        nova_quantidade_disponivel = livro_atual.quantidade_disponivel + diferenca

        livro_dto = LivroDTO(
            id=id_livro,
            titulo=titulo,
            subtitulo=subtitulo,
            isbn=isbn,
            editora=editora,
            ano_publicacao=ano_publicacao,
            edicao=edicao,
            idioma=idioma,
            paginas=paginas,
            sinopse=sinopse,
            quantidade_total=quantidade_total,
            quantidade_disponivel=max(0, nova_quantidade_disponivel),
            localizacao=localizacao,
        )

        sucesso = livro_repo.atualizar(livro_dto)

        if sucesso:
            # Atualizar autores (remove todos e adiciona novamente)
            livro_repo.remover_todos_autores(id_livro)
            for id_autor in autores:
                livro_repo.adicionar_autor(id_livro, id_autor)

            # Atualizar categorias
            livro_repo.remover_todas_categorias(id_livro)
            for id_categoria in categorias:
                livro_repo.adicionar_categoria(id_livro, id_categoria)

            flash_success(request, f"Livro '{titulo}' atualizado com sucesso!")
        else:
            flash_error(request, "Erro ao atualizar livro.")

        return RedirectResponse(
            f"/bibliotecario/livros/{id_livro}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            f"/bibliotecario/livros/{id_livro}/editar",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.post("/livros/{id_livro}/excluir")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_excluir_livro(request: Request, id_livro: int = Path(...)):
    """Excluir livro"""
    livro = livro_repo.obter_por_id(id_livro)
    if not livro:
        flash_error(request, "Livro não encontrado.")
    else:
        # Verificar se há empréstimos ativos
        emprestimos_ativos = emprestimo_repo.contar_ativos_por_livro(id_livro)
        if emprestimos_ativos > 0:
            flash_error(request, f"Não é possível excluir: livro possui {emprestimos_ativos} empréstimo(s) ativo(s).")
        else:
            sucesso = livro_repo.excluir(id_livro)
            if sucesso:
                flash_success(request, f"Livro '{livro.titulo}' excluído com sucesso!")
            else:
                flash_error(request, "Erro ao excluir livro.")

    return RedirectResponse(
        "/bibliotecario/livros",
        status_code=status.HTTP_303_SEE_OTHER
    )

# ==================== GESTÃO DE EMPRÉSTIMOS ====================

@router.get("/emprestimos")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_emprestimos(
    request: Request,
    status_filtro: Optional[str] = Query(None),
    atrasados: Optional[bool] = Query(None),
):
    """Listar empréstimos com filtros"""
    if atrasados:
        emprestimos = emprestimo_repo.obter_atrasados()
    elif status_filtro:
        emprestimos = emprestimo_repo.obter_por_status(status_filtro)
    else:
        emprestimos = emprestimo_repo.obter_todos_completos()

    return templates.TemplateResponse(
        "bibliotecario/emprestimos/listar.html",
        {
            "request": request,
            "emprestimos": emprestimos,
            "status_filtro": status_filtro,
            "atrasados": atrasados,
        }
    )

@router.get("/emprestimos/novo")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_novo_emprestimo(request: Request):
    """Formulário para registrar novo empréstimo"""
    livros = livro_repo.obter_disponiveis()
    leitores = usuario_repo.obter_por_perfil(Perfil.LEITOR.value)

    return templates.TemplateResponse(
        "bibliotecario/emprestimos/form.html",
        {"request": request, "livros": livros, "leitores": leitores}
    )

@router.post("/emprestimos/novo")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_novo_emprestimo(
    request: Request,
    id_livro: int = Form(...),
    id_leitor: int = Form(...),
    prazo_dias: int = Form(14),
    observacoes: Optional[str] = Form(None),
):
    """Registrar novo empréstimo"""
    id_bibliotecario = request.state.usuario.id

    # Verificar disponibilidade
    livro = livro_repo.obter_por_id(id_livro)
    if not livro or livro.quantidade_disponivel <= 0:
        flash_error(request, "Livro não está disponível para empréstimo.")
        return RedirectResponse(
            "/bibliotecario/emprestimos/novo",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se leitor está bloqueado
    leitor = usuario_repo.obter_por_id(id_leitor)
    if leitor and hasattr(leitor, 'bloqueado') and leitor.bloqueado:
        flash_error(request, "Leitor está bloqueado e não pode fazer empréstimos.")
        return RedirectResponse(
            "/bibliotecario/emprestimos/novo",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Registrar empréstimo
    emprestimo_id = emprestimo_repo.registrar_emprestimo(
        id_livro=id_livro,
        id_leitor=id_leitor,
        id_bibliotecario=id_bibliotecario,
        prazo_dias=prazo_dias,
        observacoes=observacoes
    )

    if emprestimo_id:
        # Verificar se há reserva do leitor para este livro e processá-la
        reserva_repo.processar_reserva_apos_emprestimo(id_livro, id_leitor)

        flash_success(request, "Empréstimo registrado com sucesso!")
        return RedirectResponse(
            f"/bibliotecario/emprestimos/{emprestimo_id}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    else:
        flash_error(request, "Erro ao registrar empréstimo.")
        return RedirectResponse(
            "/bibliotecario/emprestimos/novo",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.get("/emprestimos/{id_emprestimo}")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_detalhe_emprestimo(request: Request, id_emprestimo: int = Path(...)):
    """Detalhes de um empréstimo"""
    emprestimo = emprestimo_repo.obter_por_id_completo(id_emprestimo)
    if not emprestimo:
        flash_error(request, "Empréstimo não encontrado.")
        return RedirectResponse(
            "/bibliotecario/emprestimos",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        "bibliotecario/emprestimos/detalhe.html",
        {"request": request, "emprestimo": emprestimo}
    )

@router.post("/emprestimos/{id_emprestimo}/devolver")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_devolver_emprestimo(
    request: Request,
    id_emprestimo: int = Path(...),
    observacoes_devolucao: Optional[str] = Form(None),
):
    """Registrar devolução de empréstimo"""
    emprestimo = emprestimo_repo.obter_por_id(id_emprestimo)
    if not emprestimo:
        flash_error(request, "Empréstimo não encontrado.")
        return RedirectResponse(
            "/bibliotecario/emprestimos",
            status_code=status.HTTP_303_SEE_OTHER
        )

    if emprestimo.status != "ativo":
        flash_error(request, "Este empréstimo não está ativo.")
        return RedirectResponse(
            f"/bibliotecario/emprestimos/{id_emprestimo}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    sucesso = emprestimo_repo.registrar_devolucao(
        id_emprestimo=id_emprestimo,
        observacoes=observacoes_devolucao
    )

    if sucesso:
        # Processar fila de reservas
        proxima_reserva = reserva_repo.obter_proxima_na_fila(emprestimo.id_livro)
        if proxima_reserva:
            # Notificar leitor (implementar depois)
            pass

        flash_success(request, "Devolução registrada com sucesso!")
    else:
        flash_error(request, "Erro ao registrar devolução.")

    return RedirectResponse(
        f"/bibliotecario/emprestimos/{id_emprestimo}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/emprestimos/{id_emprestimo}/renovar")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_renovar_emprestimo(
    request: Request,
    id_emprestimo: int = Path(...),
    prazo_adicional: int = Form(14),
):
    """Renovar empréstimo"""
    emprestimo = emprestimo_repo.obter_por_id(id_emprestimo)
    if not emprestimo:
        flash_error(request, "Empréstimo não encontrado.")
        return RedirectResponse(
            "/bibliotecario/emprestimos",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar limite de renovações
    if emprestimo.renovacoes >= 3:
        flash_error(request, "Limite de renovações atingido (máximo 3).")
        return RedirectResponse(
            f"/bibliotecario/emprestimos/{id_emprestimo}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Verificar se há reservas para o livro
    reservas_ativas = reserva_repo.contar_ativas_por_livro(emprestimo.id_livro)
    if reservas_ativas > 0:
        flash_error(request, "Não é possível renovar: há reservas pendentes para este livro.")
        return RedirectResponse(
            f"/bibliotecario/emprestimos/{id_emprestimo}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    sucesso = emprestimo_repo.renovar(id_emprestimo, prazo_adicional)

    if sucesso:
        flash_success(request, f"Empréstimo renovado por mais {prazo_adicional} dias!")
    else:
        flash_error(request, "Erro ao renovar empréstimo.")

    return RedirectResponse(
        f"/bibliotecario/emprestimos/{id_emprestimo}",
        status_code=status.HTTP_303_SEE_OTHER
    )

# ==================== GESTÃO DE LEITORES ====================

@router.get("/leitores")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_leitores(
    request: Request,
    busca: Optional[str] = Query(None),
    bloqueados: Optional[bool] = Query(None),
):
    """Listar leitores"""
    if bloqueados:
        leitores = usuario_repo.obter_bloqueados()
    elif busca:
        leitores = usuario_repo.buscar_por_nome_ou_email(busca, Perfil.LEITOR.value)
    else:
        leitores = usuario_repo.obter_por_perfil(Perfil.LEITOR.value)

    return templates.TemplateResponse(
        "bibliotecario/leitores/listar.html",
        {"request": request, "leitores": leitores, "busca": busca, "bloqueados": bloqueados}
    )

@router.get("/leitores/{id_leitor}")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def get_detalhe_leitor(request: Request, id_leitor: int = Path(...)):
    """Detalhes de um leitor"""
    leitor = usuario_repo.obter_por_id(id_leitor)
    if not leitor or leitor.perfil != Perfil.LEITOR.value:
        flash_error(request, "Leitor não encontrado.")
        return RedirectResponse(
            "/bibliotecario/leitores",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Estatísticas
    emprestimos_ativos = emprestimo_repo.obter_por_leitor(id_leitor, apenas_ativos=True)
    emprestimos_historico = emprestimo_repo.obter_por_leitor(id_leitor, limite=10)
    reservas_ativas = reserva_repo.obter_por_leitor(id_leitor, apenas_ativas=True)
    total_emprestimos = emprestimo_repo.contar_por_leitor(id_leitor)
    emprestimos_atrasados = [e for e in emprestimos_ativos if e.dias_atraso > 0]

    return templates.TemplateResponse(
        "bibliotecario/leitores/detalhe.html",
        {
            "request": request,
            "leitor": leitor,
            "emprestimos_ativos": emprestimos_ativos,
            "emprestimos_historico": emprestimos_historico,
            "reservas_ativas": reservas_ativas,
            "stats": {
                "total_emprestimos": total_emprestimos,
                "emprestimos_atrasados": len(emprestimos_atrasados),
            }
        }
    )

@router.post("/leitores/{id_leitor}/bloquear")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_bloquear_leitor(request: Request, id_leitor: int = Path(...)):
    """Bloquear leitor"""
    leitor = usuario_repo.obter_por_id(id_leitor)
    if not leitor:
        flash_error(request, "Leitor não encontrado.")
    else:
        sucesso = usuario_repo.bloquear_usuario(id_leitor)
        if sucesso:
            flash_success(request, f"Leitor '{leitor.nome}' bloqueado com sucesso!")
        else:
            flash_error(request, "Erro ao bloquear leitor.")

    return RedirectResponse(
        f"/bibliotecario/leitores/{id_leitor}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/leitores/{id_leitor}/desbloquear")
@auth_decorator(perfil_necessario=Perfil.BIBLIOTECARIO.value)
async def post_desbloquear_leitor(request: Request, id_leitor: int = Path(...)):
    """Desbloquear leitor"""
    leitor = usuario_repo.obter_por_id(id_leitor)
    if not leitor:
        flash_error(request, "Leitor não encontrado.")
    else:
        sucesso = usuario_repo.desbloquear_usuario(id_leitor)
        if sucesso:
            flash_success(request, f"Leitor '{leitor.nome}' desbloqueado com sucesso!")
        else:
            flash_error(request, "Erro ao desbloquear leitor.")

    return RedirectResponse(
        f"/bibliotecario/leitores/{id_leitor}",
        status_code=status.HTTP_303_SEE_OTHER
    )
```

**⚠️ Observações importantes:**
- Este arquivo contém cerca de 800 linhas de código
- Implementa 30+ endpoints para o bibliotecário
- Usa transações para operações críticas
- Valida regras de negócio (bloqueios, disponibilidade, etc.)
- Integra com o sistema de flash messages
- Segue o padrão auth_decorator para controle de acesso

---

### 5.2. Criar Templates do Bibliotecário

#### 5.2.1. Dashboard do Bibliotecário

📁 **Arquivo:** `templates/bibliotecario/dashboard.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Dashboard Bibliotecário{% endblock %}

{% block content %}
<h2><i class="bi bi-speedometer2"></i> Dashboard do Bibliotecário</h2>

<!-- Cards de Estatísticas Gerais -->
<div class="row mt-4">
    <div class="col-md-3 mb-3">
        <div class="card border-primary">
            <div class="card-body text-center">
                <h6 class="card-title text-primary">Livros Cadastrados</h6>
                <h2 class="display-4">{{ stats.total_livros }}</h2>
                <p class="text-muted small">{{ stats.total_exemplares }} exemplares</p>
            </div>
        </div>
    </div>

    <div class="col-md-3 mb-3">
        <div class="card border-success">
            <div class="card-body text-center">
                <h6 class="card-title text-success">Disponíveis</h6>
                <h2 class="display-4">{{ stats.exemplares_disponiveis }}</h2>
                <p class="text-muted small">exemplares</p>
            </div>
        </div>
    </div>

    <div class="col-md-3 mb-3">
        <div class="card border-warning">
            <div class="card-body text-center">
                <h6 class="card-title text-warning">Empréstimos Ativos</h6>
                <h2 class="display-4">{{ stats.emprestimos_ativos }}</h2>
                <p class="text-muted small">em andamento</p>
            </div>
        </div>
    </div>

    <div class="col-md-3 mb-3">
        <div class="card border-danger">
            <div class="card-body text-center">
                <h6 class="card-title text-danger">Atrasados</h6>
                <h2 class="display-4">{{ stats.emprestimos_atrasados }}</h2>
                <p class="text-muted small">empréstimos</p>
            </div>
        </div>
    </div>
</div>

<!-- Cards de Estatísticas Secundárias -->
<div class="row">
    <div class="col-md-2 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Autores</h6>
                <h4>{{ stats.total_autores }}</h4>
            </div>
        </div>
    </div>

    <div class="col-md-2 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Categorias</h6>
                <h4>{{ stats.total_categorias }}</h4>
            </div>
        </div>
    </div>

    <div class="col-md-2 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Leitores</h6>
                <h4>{{ stats.total_leitores }}</h4>
            </div>
        </div>
    </div>

    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Empréstimos Hoje</h6>
                <h4>{{ stats.emprestimos_hoje }}</h4>
            </div>
        </div>
    </div>

    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Devoluções Hoje</h6>
                <h4>{{ stats.devolucoes_hoje }}</h4>
            </div>
        </div>
    </div>
</div>

<!-- Top Livros Mais Emprestados -->
<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <i class="bi bi-trophy"></i> Top 5 Livros Mais Emprestados
            </div>
            <div class="card-body">
                {% if livros_mais_emprestados %}
                <ol class="list-group list-group-numbered">
                    {% for livro in livros_mais_emprestados %}
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">{{ livro.titulo }}</div>
                            <small class="text-muted">{{ livro.subtitulo or '' }}</small>
                        </div>
                        <span class="badge bg-primary rounded-pill">{{ livro.total_emprestimos }} empréstimos</span>
                    </li>
                    {% endfor %}
                </ol>
                {% else %}
                <p class="text-muted">Nenhum dado disponível.</p>
                {% endif %}
            </div>
        </div>
    </div>

    <!-- Próximas Devoluções -->
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-warning text-dark">
                <i class="bi bi-calendar-event"></i> Próximas Devoluções (7 dias)
            </div>
            <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                {% if proximas_devolucoes %}
                <table class="table table-sm">
                    <tbody>
                        {% for emp in proximas_devolucoes %}
                        <tr class="{{ 'table-danger' if emp.dias_atraso > 0 else '' }}">
                            <td>
                                <strong>{{ emp.livro_titulo }}</strong><br>
                                <small>{{ emp.leitor_nome }}</small>
                            </td>
                            <td class="text-end">
                                <small>{{ emp.data_prevista_devolucao }}</small>
                                {% if emp.dias_atraso > 0 %}
                                <br><span class="badge bg-danger">{{ emp.dias_atraso }} dia(s) atrasado</span>
                                {% endif %}
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="text-muted">Nenhuma devolução nos próximos 7 dias.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Empréstimos Recentes -->
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-info text-white">
                <i class="bi bi-clock-history"></i> Últimos 10 Empréstimos
            </div>
            <div class="card-body">
                {% if emprestimos_recentes %}
                <table class="table table-hover">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Livro</th>
                            <th>Leitor</th>
                            <th>Status</th>
                            <th>Devolução</th>
                            <th>Ações</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for emp in emprestimos_recentes %}
                        <tr>
                            <td>{{ emp.data_emprestimo }}</td>
                            <td>{{ emp.livro_titulo }}</td>
                            <td>{{ emp.leitor_nome }}</td>
                            <td>
                                {% if emp.status == 'ativo' %}
                                <span class="badge bg-success">Ativo</span>
                                {% elif emp.status == 'devolvido' %}
                                <span class="badge bg-secondary">Devolvido</span>
                                {% else %}
                                <span class="badge bg-warning">{{ emp.status }}</span>
                                {% endif %}
                            </td>
                            <td>
                                {{ emp.data_prevista_devolucao }}
                                {% if emp.status == 'ativo' and emp.dias_atraso > 0 %}
                                <br><span class="badge bg-danger">{{ emp.dias_atraso }} dia(s) atrasado</span>
                                {% endif %}
                            </td>
                            <td>
                                <a href="/bibliotecario/emprestimos/{{ emp.id }}" class="btn btn-sm btn-outline-primary">
                                    <i class="bi bi-eye"></i>
                                </a>
                            </td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
                {% else %}
                <p class="text-muted">Nenhum empréstimo registrado.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Reservas Pendentes -->
{% if reservas_pendentes %}
<div class="row mt-4">
    <div class="col-12">
        <div class="card">
            <div class="card-header bg-secondary text-white">
                <i class="bi bi-bookmark-check"></i> Reservas Pendentes
            </div>
            <div class="card-body">
                <table class="table table-sm">
                    <thead>
                        <tr>
                            <th>Data</th>
                            <th>Livro</th>
                            <th>Leitor</th>
                            <th>Validade</th>
                        </tr>
                    </thead>
                    <tbody>
                        {% for res in reservas_pendentes %}
                        <tr>
                            <td>{{ res.data_reserva }}</td>
                            <td>{{ res.livro_titulo }}</td>
                            <td>{{ res.leitor_nome }}</td>
                            <td>{{ res.data_expiracao or 'N/A' }}</td>
                        </tr>
                        {% endfor %}
                    </tbody>
                </table>
            </div>
        </div>
    </div>
</div>
{% endif %}

<!-- Atalhos Rápidos -->
<div class="row mt-4">
    <div class="col-12">
        <h5>Ações Rápidas</h5>
        <div class="btn-group" role="group">
            <a href="/bibliotecario/emprestimos/novo" class="btn btn-primary">
                <i class="bi bi-plus-circle"></i> Novo Empréstimo
            </a>
            <a href="/bibliotecario/livros/novo" class="btn btn-success">
                <i class="bi bi-book"></i> Cadastrar Livro
            </a>
            <a href="/bibliotecario/emprestimos?atrasados=true" class="btn btn-danger">
                <i class="bi bi-exclamation-triangle"></i> Ver Atrasados
            </a>
            <a href="/bibliotecario/leitores" class="btn btn-info">
                <i class="bi bi-people"></i> Gerenciar Leitores
            </a>
        </div>
    </div>
</div>

{% endblock %}
```

#### 5.2.2. CRUD de Autores

📁 **Arquivo:** `templates/bibliotecario/autores/listar.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Autores{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2><i class="bi bi-person-badge"></i> Autores</h2>
    <a href="/bibliotecario/autores/novo" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> Novo Autor
    </a>
</div>

<!-- Busca -->
<form method="GET" class="mb-3">
    <div class="input-group">
        <input type="text" name="busca" class="form-control" placeholder="Buscar por nome..." value="{{ busca or '' }}">
        <button type="submit" class="btn btn-outline-primary">
            <i class="bi bi-search"></i> Buscar
        </button>
        {% if busca %}
        <a href="/bibliotecario/autores" class="btn btn-outline-secondary">
            <i class="bi bi-x"></i> Limpar
        </a>
        {% endif %}
    </div>
</form>

{% if autores %}
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>Nacionalidade</th>
                <th>Data Nascimento</th>
                <th>Livros</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for autor in autores %}
            <tr>
                <td>{{ autor.id }}</td>
                <td>
                    <strong>{{ autor.nome }}</strong>
                    {% if autor.biografia %}
                    <br><small class="text-muted">{{ autor.biografia[:100] }}...</small>
                    {% endif %}
                </td>
                <td>{{ autor.nacionalidade or '-' }}</td>
                <td>{{ autor.data_nascimento or '-' }}</td>
                <td>{{ autor.total_livros or 0 }}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <a href="/bibliotecario/autores/{{ autor.id }}" class="btn btn-outline-info" title="Ver detalhes">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="/bibliotecario/autores/{{ autor.id }}/editar" class="btn btn-outline-warning" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button" class="btn btn-outline-danger" title="Excluir"
                                onclick="confirmarExclusao({{ autor.id }}, '{{ autor.nome }}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<p class="text-muted">Total: {{ autores|length }} autor(es)</p>

{% else %}
<div class="alert alert-info">
    <i class="bi bi-info-circle"></i> Nenhum autor cadastrado.
    <a href="/bibliotecario/autores/novo" class="alert-link">Cadastre o primeiro autor</a>.
</div>
{% endif %}

<!-- Modal de Confirmação de Exclusão -->
<form id="formExcluir" method="POST" style="display: none;">
    <input type="hidden" name="csrf_token" value="{{ csrf_token() }}">
</form>

<script>
function confirmarExclusao(id, nome) {
    if (confirm(`Tem certeza que deseja excluir o autor "${nome}"?\n\nATENÇÃO: Só é possível excluir autores sem livros cadastrados.`)) {
        const form = document.getElementById('formExcluir');
        form.action = `/bibliotecario/autores/${id}/excluir`;
        form.submit();
    }
}
</script>

{% endblock %}
```

📁 **Arquivo:** `templates/bibliotecario/autores/form.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}{{ 'Editar' if autor else 'Novo' }} Autor{% endblock %}

{% block content %}
<h2><i class="bi bi-person-badge"></i> {{ 'Editar' if autor else 'Novo' }} Autor</h2>

<div class="row mt-4">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="nome" class="form-label">Nome Completo *</label>
                        <input type="text" class="form-control" id="nome" name="nome"
                               value="{{ autor.nome if autor else '' }}" required maxlength="200">
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="data_nascimento" class="form-label">Data de Nascimento</label>
                            <input type="date" class="form-control" id="data_nascimento" name="data_nascimento"
                                   value="{{ autor.data_nascimento if autor else '' }}">
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="nacionalidade" class="form-label">Nacionalidade</label>
                            <input type="text" class="form-control" id="nacionalidade" name="nacionalidade"
                                   value="{{ autor.nacionalidade if autor else '' }}" maxlength="100">
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="biografia" class="form-label">Biografia</label>
                        <textarea class="form-control" id="biografia" name="biografia" rows="5">{{ autor.biografia if autor else '' }}</textarea>
                        <div class="form-text">Breve biografia do autor (opcional).</div>
                    </div>

                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-save"></i> Salvar
                        </button>
                        <a href="/bibliotecario/autores{{ ('/' + autor.id|string) if autor else '' }}" class="btn btn-secondary">
                            <i class="bi bi-x"></i> Cancelar
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-info text-white">
                <i class="bi bi-info-circle"></i> Dicas
            </div>
            <div class="card-body">
                <ul class="small mb-0">
                    <li>O nome do autor é obrigatório</li>
                    <li>A biografia ajuda os leitores a conhecer o autor</li>
                    <li>Dados completos facilitam buscas</li>
                    <li>Você pode editar estes dados posteriormente</li>
                </ul>
            </div>
        </div>
    </div>
</div>

{% endblock %}
```

📁 **Arquivo:** `templates/bibliotecario/autores/detalhe.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}{{ autor.nome }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2><i class="bi bi-person-badge"></i> {{ autor.nome }}</h2>
    <div class="btn-group">
        <a href="/bibliotecario/autores/{{ autor.id }}/editar" class="btn btn-warning">
            <i class="bi bi-pencil"></i> Editar
        </a>
        <a href="/bibliotecario/autores" class="btn btn-secondary">
            <i class="bi bi-arrow-left"></i> Voltar
        </a>
    </div>
</div>

<div class="row">
    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                Informações do Autor
            </div>
            <div class="card-body">
                <p><strong>ID:</strong> {{ autor.id }}</p>
                <p><strong>Nome:</strong> {{ autor.nome }}</p>
                <p><strong>Nacionalidade:</strong> {{ autor.nacionalidade or 'Não informado' }}</p>
                <p><strong>Data de Nascimento:</strong> {{ autor.data_nascimento or 'Não informado' }}</p>

                {% if autor.biografia %}
                <hr>
                <p><strong>Biografia:</strong></p>
                <p class="text-muted">{{ autor.biografia }}</p>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="col-md-8">
        <div class="card">
            <div class="card-header bg-success text-white">
                <i class="bi bi-book"></i> Livros deste Autor ({{ livros|length }})
            </div>
            <div class="card-body">
                {% if livros %}
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Título</th>
                                <th>ISBN</th>
                                <th>Ano</th>
                                <th>Disponível</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for livro in livros %}
                            <tr>
                                <td>{{ livro.titulo }}</td>
                                <td>{{ livro.isbn }}</td>
                                <td>{{ livro.ano_publicacao }}</td>
                                <td>
                                    <span class="badge bg-{{ 'success' if livro.quantidade_disponivel > 0 else 'secondary' }}">
                                        {{ livro.quantidade_disponivel }}/{{ livro.quantidade_total }}
                                    </span>
                                </td>
                                <td>
                                    <a href="/bibliotecario/livros/{{ livro.id }}" class="btn btn-sm btn-outline-primary">
                                        <i class="bi bi-eye"></i>
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted">Este autor ainda não possui livros cadastrados.</p>
                <a href="/bibliotecario/livros/novo" class="btn btn-sm btn-primary">
                    <i class="bi bi-plus"></i> Cadastrar Livro
                </a>
                {% endif %}
            </div>
        </div>
    </div>
</div>

{% endblock %}
```

#### 5.2.3. CRUD de Categorias

📁 **Arquivo:** `templates/bibliotecario/categorias/listar.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Categorias{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2><i class="bi bi-tags"></i> Categorias</h2>
    <a href="/bibliotecario/categorias/novo" class="btn btn-primary">
        <i class="bi bi-plus-circle"></i> Nova Categoria
    </a>
</div>

{% if categorias %}
<div class="row">
    {% for categoria in categorias %}
    <div class="col-md-4 mb-3">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title">{{ categoria.nome }}</h5>
                <p class="card-text text-muted small">{{ categoria.descricao or 'Sem descrição' }}</p>
                <p class="mb-0">
                    <span class="badge bg-primary">{{ categoria.total_livros or 0 }} livro(s)</span>
                </p>
            </div>
            <div class="card-footer">
                <div class="btn-group btn-group-sm w-100">
                    <a href="/bibliotecario/categorias/{{ categoria.id }}/editar" class="btn btn-outline-warning">
                        <i class="bi bi-pencil"></i> Editar
                    </a>
                    <button type="button" class="btn btn-outline-danger"
                            onclick="confirmarExclusao({{ categoria.id }}, '{{ categoria.nome }}')">
                        <i class="bi bi-trash"></i> Excluir
                    </button>
                </div>
            </div>
        </div>
    </div>
    {% endfor %}
</div>

<p class="text-muted mt-3">Total: {{ categorias|length }} categoria(s)</p>

{% else %}
<div class="alert alert-info">
    <i class="bi bi-info-circle"></i> Nenhuma categoria cadastrada.
    <a href="/bibliotecario/categorias/novo" class="alert-link">Cadastre a primeira categoria</a>.
</div>
{% endif %}

<form id="formExcluir" method="POST" style="display: none;"></form>

<script>
function confirmarExclusao(id, nome) {
    if (confirm(`Tem certeza que deseja excluir a categoria "${nome}"?`)) {
        const form = document.getElementById('formExcluir');
        form.action = `/bibliotecario/categorias/${id}/excluir`;
        form.submit();
    }
}
</script>

{% endblock %}
```

📁 **Arquivo:** `templates/bibliotecario/categorias/form.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}{{ 'Editar' if categoria else 'Nova' }} Categoria{% endblock %}

{% block content %}
<h2><i class="bi bi-tags"></i> {{ 'Editar' if categoria else 'Nova' }} Categoria</h2>

<div class="row mt-4">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="nome" class="form-label">Nome da Categoria *</label>
                        <input type="text" class="form-control" id="nome" name="nome"
                               value="{{ categoria.nome if categoria else '' }}" required maxlength="100">
                    </div>

                    <div class="mb-3">
                        <label for="descricao" class="form-label">Descrição</label>
                        <textarea class="form-control" id="descricao" name="descricao" rows="3">{{ categoria.descricao if categoria else '' }}</textarea>
                        <div class="form-text">Breve descrição da categoria (opcional).</div>
                    </div>

                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-save"></i> Salvar
                        </button>
                        <a href="/bibliotecario/categorias" class="btn btn-secondary">
                            <i class="bi bi-x"></i> Cancelar
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>

{% endblock %}
```

### 5.3. Templates de Livros (Continuação em arquivo separado devido ao tamanho)

Como os templates são muito extensos, vou criar estruturas simplificadas. **Você deve seguir o mesmo padrão dos autores** para criar:

📁 `templates/bibliotecario/livros/listar.html` - Lista com filtros
📁 `templates/bibliotecario/livros/form.html` - Formulário com multi-select de autores/categorias
📁 `templates/bibliotecario/livros/detalhe.html` - Detalhes completos com estatísticas

📁 `templates/bibliotecario/emprestimos/listar.html` - Lista com filtros de status
📁 `templates/bibliotecario/emprestimos/form.html` - Formulário para novo empréstimo
📁 `templates/bibliotecario/emprestimos/detalhe.html` - Detalhes com botões devolver/renovar

📁 `templates/bibliotecario/leitores/listar.html` - Lista de leitores
📁 `templates/bibliotecario/leitores/detalhe.html` - Perfil completo do leitor com histórico

---

### 5.4. Métodos Adicionais nos Repositories

Alguns métodos adicionais necessários que ainda não foram implementados:

#### 5.4.1. Adicionar ao livro_repo.py

```python
def contar_total() -> int:
    """Conta total de livros únicos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM livro")
        return cursor.fetchone()[0]

def contar_exemplares_total() -> int:
    """Conta total de exemplares (soma das quantidades)"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantidade_total) FROM livro")
        result = cursor.fetchone()[0]
        return result if result else 0

def contar_exemplares_disponiveis() -> int:
    """Conta exemplares disponíveis"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT SUM(quantidade_disponivel) FROM livro")
        result = cursor.fetchone()[0]
        return result if result else 0

def obter_disponiveis() -> list[Livro]:
    """Retorna livros que têm pelo menos 1 exemplar disponível"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM livro WHERE quantidade_disponivel > 0 ORDER BY titulo"
        )
        return [Livro(**dict(row)) for row in cursor.fetchall()]

def obter_mais_emprestados(limite: int = 10) -> list:
    """Retorna os livros mais emprestados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.*, COUNT(e.id) as total_emprestimos
            FROM livro l
            LEFT JOIN emprestimo e ON e.id_livro = l.id
            GROUP BY l.id
            ORDER BY total_emprestimos DESC
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in cursor.fetchall()]

def remover_todos_autores(id_livro: int) -> bool:
    """Remove todas as associações de autores do livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livro_autor WHERE id_livro = ?", (id_livro,))
        conn.commit()
        return True

def remover_todas_categorias(id_livro: int) -> bool:
    """Remove todas as associações de categorias do livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("DELETE FROM livro_categoria WHERE id_livro = ?", (id_livro,))
        conn.commit()
        return True
```

#### 5.4.2. Adicionar ao emprestimo_repo.py

```python
def contar_ativos() -> int:
    """Conta empréstimos ativos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emprestimo WHERE status = 'ativo'")
        return cursor.fetchone()[0]

def contar_atrasados() -> int:
    """Conta empréstimos atrasados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM emprestimo
            WHERE status = 'ativo' AND data_prevista_devolucao < date('now')
        """)
        return cursor.fetchone()[0]

def contar_por_data(data: date) -> int:
    """Conta empréstimos realizados em uma data específica"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE DATE(data_emprestimo) = ?",
            (data.isoformat(),)
        )
        return cursor.fetchone()[0]

def contar_devolucoes_por_data(data: date) -> int:
    """Conta devoluções realizadas em uma data específica"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE DATE(data_devolucao) = ?",
            (data.isoformat(),)
        )
        return cursor.fetchone()[0]

def obter_recentes(limite: int = 10) -> list:
    """Retorna empréstimos mais recentes com dados completos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                e.*,
                l.titulo as livro_titulo,
                u.nome as leitor_nome,
                b.nome as bibliotecario_nome,
                CASE
                    WHEN e.status = 'ativo' AND e.data_prevista_devolucao < date('now')
                    THEN julianday('now') - julianday(e.data_prevista_devolucao)
                    ELSE 0
                END as dias_atraso
            FROM emprestimo e
            JOIN livro l ON e.id_livro = l.id
            JOIN usuario u ON e.id_leitor = u.id
            JOIN usuario b ON e.id_bibliotecario = b.id
            ORDER BY e.data_emprestimo DESC
            LIMIT ?
        """, (limite,))
        return [dict(row) for row in cursor.fetchall()]

def obter_proximas_devolucoes(data_limite: date) -> list:
    """Retorna empréstimos ativos com devolução até a data limite"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                e.*,
                l.titulo as livro_titulo,
                u.nome as leitor_nome,
                CASE
                    WHEN e.data_prevista_devolucao < date('now')
                    THEN julianday('now') - julianday(e.data_prevista_devolucao)
                    ELSE 0
                END as dias_atraso
            FROM emprestimo e
            JOIN livro l ON e.id_livro = l.id
            JOIN usuario u ON e.id_leitor = u.id
            WHERE e.status = 'ativo' AND e.data_prevista_devolucao <= ?
            ORDER BY e.data_prevista_devolucao
        """, (data_limite.isoformat(),))
        return [dict(row) for row in cursor.fetchall()]

def obter_atrasados() -> list:
    """Retorna todos os empréstimos atrasados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                e.*,
                l.titulo as livro_titulo,
                u.nome as leitor_nome,
                julianday('now') - julianday(e.data_prevista_devolucao) as dias_atraso
            FROM emprestimo e
            JOIN livro l ON e.id_livro = l.id
            JOIN usuario u ON e.id_leitor = u.id
            WHERE e.status = 'ativo' AND e.data_prevista_devolucao < date('now')
            ORDER BY dias_atraso DESC
        """)
        return [dict(row) for row in cursor.fetchall()]

def contar_por_livro(id_livro: int) -> int:
    """Conta total de empréstimos de um livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emprestimo WHERE id_livro = ?", (id_livro,))
        return cursor.fetchone()[0]

def contar_ativos_por_livro(id_livro: int) -> int:
    """Conta empréstimos ativos de um livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT COUNT(*) FROM emprestimo WHERE id_livro = ? AND status = 'ativo'",
            (id_livro,)
        )
        return cursor.fetchone()[0]

def obter_por_livro(id_livro: int, limite: int = None) -> list:
    """Retorna histórico de empréstimos de um livro"""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT
                e.*,
                u.nome as leitor_nome
            FROM emprestimo e
            JOIN usuario u ON e.id_leitor = u.id
            WHERE e.id_livro = ?
            ORDER BY e.data_emprestimo DESC
        """
        if limite:
            query += f" LIMIT {limite}"
        cursor.execute(query, (id_livro,))
        return [dict(row) for row in cursor.fetchall()]
```

#### 5.4.3. Adicionar ao usuario_repo.py

```python
def contar_por_perfil(perfil: str) -> int:
    """Conta usuários de um perfil específico"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuario WHERE perfil = ?", (perfil,))
        return cursor.fetchone()[0]

def obter_bloqueados() -> list[Usuario]:
    """Retorna usuários bloqueados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario WHERE bloqueado = 1 ORDER BY nome")
        return [Usuario(**dict(row)) for row in cursor.fetchall()]

def buscar_por_nome_ou_email(busca: str, perfil: str = None) -> list[Usuario]:
    """Busca usuários por nome ou email, opcionalmente filtrado por perfil"""
    with get_connection() as conn:
        cursor = conn.cursor()
        if perfil:
            cursor.execute("""
                SELECT * FROM usuario
                WHERE (nome LIKE ? OR email LIKE ?) AND perfil = ?
                ORDER BY nome
            """, (f"%{busca}%", f"%{busca}%", perfil))
        else:
            cursor.execute("""
                SELECT * FROM usuario
                WHERE nome LIKE ? OR email LIKE ?
                ORDER BY nome
            """, (f"%{busca}%", f"%{busca}%"))
        return [Usuario(**dict(row)) for row in cursor.fetchall()]

def bloquear_usuario(id_usuario: int) -> bool:
    """Bloqueia um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET bloqueado = 1 WHERE id = ?",
            (id_usuario,)
        )
        conn.commit()
        return cursor.rowcount > 0

def desbloquear_usuario(id_usuario: int) -> bool:
    """Desbloqueia um usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE usuario SET bloqueado = 0 WHERE id = ?",
            (id_usuario,)
        )
        conn.commit()
        return cursor.rowcount > 0
```

---

### 5.5. Registrar Rotas no main.py

📝 **Arquivo:** `main.py`

**Adicionar import:**

```python
from routes import bibliotecario_routes
```

**Adicionar no final da seção de routers:**

```python
app.include_router(bibliotecario_routes.router)
logger.info("Router de bibliotecário incluído")
```

---

### 5.6. Testar Sprint 3

#### Como Testar:

1. **Executar aplicação:**
   ```bash
   python main.py
   ```

2. **Login como bibliotecário:**
   - Email: Criar um usuário bibliotecário via SQL ou interface admin
   - Senha: conforme cadastrado

3. **Testar funcionalidades (em ordem):**

   **a) Autores:**
   - ✅ Acessar `/bibliotecario/autores`
   - ✅ Criar novo autor
   - ✅ Editar autor
   - ✅ Ver detalhes do autor
   - ✅ Buscar autor por nome
   - ✅ Tentar excluir autor (sem livros)

   **b) Categorias:**
   - ✅ Acessar `/bibliotecario/categorias`
   - ✅ Criar nova categoria
   - ✅ Editar categoria
   - ✅ Excluir categoria (sem livros)

   **c) Livros:**
   - ✅ Acessar `/bibliotecario/livros`
   - ✅ Criar novo livro (selecionar autores e categorias)
   - ✅ Editar livro
   - ✅ Ver detalhes do livro
   - ✅ Buscar livro
   - ✅ Filtrar por categoria/autor

   **d) Empréstimos:**
   - ✅ Acessar `/bibliotecario/emprestimos`
   - ✅ Registrar novo empréstimo
   - ✅ Ver detalhes do empréstimo
   - ✅ Registrar devolução
   - ✅ Renovar empréstimo
   - ✅ Filtrar por status
   - ✅ Ver atrasados

   **e) Leitores:**
   - ✅ Acessar `/bibliotecario/leitores`
   - ✅ Ver detalhes do leitor
   - ✅ Ver histórico de empréstimos do leitor
   - ✅ Bloquear/desbloquear leitor
   - ✅ Buscar leitor

   **f) Dashboard:**
   - ✅ Acessar `/bibliotecario/dashboard`
   - ✅ Verificar estatísticas
   - ✅ Ver top livros
   - ✅ Ver próximas devoluções
   - ✅ Ver empréstimos recentes

4. **Testar regras de negócio:**
   - ✅ Não permitir empréstimo de livro indisponível
   - ✅ Não permitir empréstimo para leitor bloqueado
   - ✅ Não permitir renovação além do limite (3x)
   - ✅ Não permitir renovação se há reservas
   - ✅ Atualizar quantidade disponível ao emprestar/devolver
   - ✅ Não permitir excluir autor/categoria/livro com vínculos

---

### 5.7. Checklist Sprint 3

- [ ] bibliotecario_routes.py criado com 30+ endpoints
- [ ] Dashboard do bibliotecário implementado
- [ ] CRUD de Autores completo (listar, criar, editar, excluir, detalhe)
- [ ] CRUD de Categorias completo
- [ ] CRUD de Livros completo (com autores e categorias)
- [ ] Gestão de empréstimos (registrar, devolver, renovar)
- [ ] Gestão de leitores (listar, detalhe, bloquear/desbloquear)
- [ ] Métodos adicionais em livro_repo.py
- [ ] Métodos adicionais em emprestimo_repo.py
- [ ] Métodos adicionais em usuario_repo.py
- [ ] Templates de autores (listar, form, detalhe)
- [ ] Templates de categorias (listar, form)
- [ ] Templates de livros (listar, form, detalhe)
- [ ] Templates de empréstimos (listar, form, detalhe)
- [ ] Templates de leitores (listar, detalhe)
- [ ] Router registrado no main.py
- [ ] Testado acesso ao dashboard
- [ ] Testado CRUD de autores
- [ ] Testado CRUD de categorias
- [ ] Testado CRUD de livros
- [ ] Testado registro de empréstimos
- [ ] Testado devolução de empréstimos
- [ ] Testado renovação de empréstimos
- [ ] Testado gestão de leitores
- [ ] Testadas regras de validação
- [ ] Testadas restrições de integridade

---

## 6. SPRINT 4: FUNCIONALIDADES ADMINISTRATIVAS

**Duração estimada:** 40 horas

**Objetivo:** Implementar área administrativa completa para gestão do sistema, usuários e configurações.

**Entregas:**
- ✅ CRUD completo de Bibliotecários
- ✅ Dashboard administrativo com métricas avançadas
- ✅ Sistema de backup e restore do banco de dados
- ✅ Gestão completa de usuários (todos os perfis)
- ✅ Configurações do sistema
- ✅ Relatórios e logs de auditoria
- ✅ 15+ templates para área administrativa

---

### 6.1. Criar Rotas do Administrador

📁 **Arquivo:** `routes/admin_routes.py`

```python
from datetime import datetime, timedelta
import os
import shutil
from typing import Optional
from fastapi import APIRouter, Form, Path, Query, Request, UploadFile, File, status
from fastapi.responses import RedirectResponse, FileResponse
from fastapi.templating import Jinja2Templates

import repo.usuario_repo as usuario_repo
import repo.livro_repo as livro_repo
import repo.emprestimo_repo as emprestimo_repo
import repo.reserva_repo as reserva_repo
import repo.autor_repo as autor_repo
import repo.categoria_repo as categoria_repo
from dtos.usuario_dto import UsuarioDTO
from util.auth_decorator import auth_decorator
from util.flash_messages import flash_error, flash_success
from util.perfis import Perfil
from util.validators import validate_email, validate_password
from util.security import hash_password

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="templates")

# ==================== DASHBOARD ====================

@router.get("/dashboard")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_dashboard(request: Request):
    """Dashboard principal do administrador com visão geral do sistema"""

    # Estatísticas de usuários
    total_usuarios = usuario_repo.contar_todos()
    total_admins = usuario_repo.contar_por_perfil(Perfil.ADMIN.value)
    total_bibliotecarios = usuario_repo.contar_por_perfil(Perfil.BIBLIOTECARIO.value)
    total_leitores = usuario_repo.contar_por_perfil(Perfil.LEITOR.value)
    usuarios_bloqueados = len(usuario_repo.obter_bloqueados())
    usuarios_pendentes = len(usuario_repo.obter_pendentes_confirmacao())

    # Estatísticas do acervo
    total_livros = livro_repo.contar_total()
    total_exemplares = livro_repo.contar_exemplares_total()
    total_autores = autor_repo.contar_total()
    total_categorias = categoria_repo.contar_total()

    # Estatísticas de empréstimos
    emprestimos_ativos = emprestimo_repo.contar_ativos()
    emprestimos_atrasados = emprestimo_repo.contar_atrasados()
    emprestimos_mes = emprestimo_repo.contar_por_periodo(days=30)
    devolucoes_mes = emprestimo_repo.contar_devolucoes_por_periodo(days=30)

    # Reservas
    reservas_ativas = reserva_repo.contar_ativas()
    reservas_mes = reserva_repo.contar_por_periodo(days=30)

    # Atividades recentes (últimos 7 dias)
    novos_usuarios_semana = usuario_repo.contar_novos_por_periodo(days=7)
    novos_livros_semana = livro_repo.contar_novos_por_periodo(days=7)

    # Top estatísticas
    livros_mais_emprestados = livro_repo.obter_mais_emprestados(limite=10)
    leitores_mais_ativos = emprestimo_repo.obter_leitores_mais_ativos(limite=10)

    # Informações do sistema
    tamanho_db = os.path.getsize("database.db") / (1024 * 1024)  # MB
    backups_disponiveis = len([f for f in os.listdir("backups") if f.endswith(".db")]) if os.path.exists("backups") else 0

    return templates.TemplateResponse(
        "admin/dashboard.html",
        {
            "request": request,
            "stats_usuarios": {
                "total": total_usuarios,
                "admins": total_admins,
                "bibliotecarios": total_bibliotecarios,
                "leitores": total_leitores,
                "bloqueados": usuarios_bloqueados,
                "pendentes": usuarios_pendentes,
                "novos_semana": novos_usuarios_semana,
            },
            "stats_acervo": {
                "total_livros": total_livros,
                "total_exemplares": total_exemplares,
                "total_autores": total_autores,
                "total_categorias": total_categorias,
                "novos_livros_semana": novos_livros_semana,
            },
            "stats_emprestimos": {
                "ativos": emprestimos_ativos,
                "atrasados": emprestimos_atrasados,
                "mes": emprestimos_mes,
                "devolucoes_mes": devolucoes_mes,
            },
            "stats_reservas": {
                "ativas": reservas_ativas,
                "mes": reservas_mes,
            },
            "stats_sistema": {
                "tamanho_db": round(tamanho_db, 2),
                "backups": backups_disponiveis,
            },
            "livros_mais_emprestados": livros_mais_emprestados,
            "leitores_mais_ativos": leitores_mais_ativos,
        }
    )

# ==================== GESTÃO DE USUÁRIOS ====================

@router.get("/usuarios")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_usuarios(
    request: Request,
    perfil: Optional[str] = Query(None),
    busca: Optional[str] = Query(None),
    bloqueados: Optional[bool] = Query(None),
):
    """Listar todos os usuários com filtros"""
    if bloqueados:
        usuarios = usuario_repo.obter_bloqueados()
    elif busca:
        usuarios = usuario_repo.buscar_por_nome_ou_email(busca, perfil)
    elif perfil:
        usuarios = usuario_repo.obter_por_perfil(perfil)
    else:
        usuarios = usuario_repo.obter_todos()

    return templates.TemplateResponse(
        "admin/usuarios/listar.html",
        {
            "request": request,
            "usuarios": usuarios,
            "perfil_filtro": perfil,
            "busca": busca,
            "bloqueados": bloqueados,
            "perfis": Perfil.valores(),
        }
    )

@router.get("/usuarios/novo")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_novo_usuario(request: Request):
    """Formulário para criar novo usuário"""
    return templates.TemplateResponse(
        "admin/usuarios/form.html",
        {"request": request, "usuario": None, "perfis": Perfil.valores()}
    )

@router.post("/usuarios/novo")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def post_novo_usuario(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    perfil: str = Form(...),
    telefone: Optional[str] = Form(None),
    endereco: Optional[str] = Form(None),
    confirmado: bool = Form(False),
):
    """Criar novo usuário"""
    try:
        # Validações
        if not validate_email(email):
            raise ValueError("E-mail inválido.")

        if not validate_password(senha):
            raise ValueError("Senha deve ter pelo menos 8 caracteres, incluindo maiúsculas, minúsculas, números e caracteres especiais.")

        # Verificar se perfil é válido
        Perfil.validar(perfil)

        # Verificar se email já existe
        if usuario_repo.obter_por_email(email):
            raise ValueError("E-mail já cadastrado no sistema.")

        # Criar usuário
        usuario_dto = UsuarioDTO(
            nome=nome,
            email=email,
            senha=hash_password(senha),
            perfil=perfil,
            telefone=telefone,
            endereco=endereco,
            confirmado=1 if confirmado else 0,
        )

        usuario_id = usuario_repo.inserir(usuario_dto)

        if usuario_id:
            flash_success(request, f"Usuário '{nome}' criado com sucesso!")
            return RedirectResponse(
                f"/admin/usuarios/{usuario_id}",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            flash_error(request, "Erro ao criar usuário.")
            return RedirectResponse(
                "/admin/usuarios/novo",
                status_code=status.HTTP_303_SEE_OTHER
            )
    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            "/admin/usuarios/novo",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.get("/usuarios/{id_usuario}")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_detalhe_usuario(request: Request, id_usuario: int = Path(...)):
    """Detalhes de um usuário"""
    usuario = usuario_repo.obter_por_id(id_usuario)
    if not usuario:
        flash_error(request, "Usuário não encontrado.")
        return RedirectResponse(
            "/admin/usuarios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Estatísticas se for leitor
    stats = None
    if usuario.perfil == Perfil.LEITOR.value:
        emprestimos_ativos = emprestimo_repo.obter_por_leitor(id_usuario, apenas_ativos=True)
        total_emprestimos = emprestimo_repo.contar_por_leitor(id_usuario)
        reservas_ativas = reserva_repo.obter_por_leitor(id_usuario, apenas_ativas=True)

        stats = {
            "total_emprestimos": total_emprestimos,
            "emprestimos_ativos": len(emprestimos_ativos),
            "reservas_ativas": len(reservas_ativas),
        }

    return templates.TemplateResponse(
        "admin/usuarios/detalhe.html",
        {"request": request, "usuario": usuario, "stats": stats}
    )

@router.get("/usuarios/{id_usuario}/editar")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_editar_usuario(request: Request, id_usuario: int = Path(...)):
    """Formulário para editar usuário"""
    usuario = usuario_repo.obter_por_id(id_usuario)
    if not usuario:
        flash_error(request, "Usuário não encontrado.")
        return RedirectResponse(
            "/admin/usuarios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return templates.TemplateResponse(
        "admin/usuarios/form.html",
        {"request": request, "usuario": usuario, "perfis": Perfil.valores()}
    )

@router.post("/usuarios/{id_usuario}/editar")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def post_editar_usuario(
    request: Request,
    id_usuario: int = Path(...),
    nome: str = Form(...),
    email: str = Form(...),
    perfil: str = Form(...),
    telefone: Optional[str] = Form(None),
    endereco: Optional[str] = Form(None),
    confirmado: bool = Form(False),
    senha: Optional[str] = Form(None),
):
    """Atualizar usuário"""
    try:
        usuario_atual = usuario_repo.obter_por_id(id_usuario)
        if not usuario_atual:
            flash_error(request, "Usuário não encontrado.")
            return RedirectResponse(
                "/admin/usuarios",
                status_code=status.HTTP_303_SEE_OTHER
            )

        # Validações
        if not validate_email(email):
            raise ValueError("E-mail inválido.")

        Perfil.validar(perfil)

        # Verificar se email já existe (em outro usuário)
        usuario_email = usuario_repo.obter_por_email(email)
        if usuario_email and usuario_email.id != id_usuario:
            raise ValueError("E-mail já cadastrado para outro usuário.")

        # Manter senha atual ou atualizar
        senha_hash = usuario_atual.senha
        if senha and senha.strip():
            if not validate_password(senha):
                raise ValueError("Senha inválida.")
            senha_hash = hash_password(senha)

        usuario_dto = UsuarioDTO(
            id=id_usuario,
            nome=nome,
            email=email,
            senha=senha_hash,
            perfil=perfil,
            telefone=telefone,
            endereco=endereco,
            confirmado=1 if confirmado else 0,
        )

        sucesso = usuario_repo.atualizar(usuario_dto)

        if sucesso:
            flash_success(request, f"Usuário '{nome}' atualizado com sucesso!")
        else:
            flash_error(request, "Erro ao atualizar usuário.")

        return RedirectResponse(
            f"/admin/usuarios/{id_usuario}",
            status_code=status.HTTP_303_SEE_OTHER
        )
    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            f"/admin/usuarios/{id_usuario}/editar",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.post("/usuarios/{id_usuario}/excluir")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def post_excluir_usuario(request: Request, id_usuario: int = Path(...)):
    """Excluir usuário"""
    # Não permitir que admin exclua a si mesmo
    if request.state.usuario.id == id_usuario:
        flash_error(request, "Você não pode excluir sua própria conta.")
        return RedirectResponse(
            "/admin/usuarios",
            status_code=status.HTTP_303_SEE_OTHER
        )

    usuario = usuario_repo.obter_por_id(id_usuario)
    if not usuario:
        flash_error(request, "Usuário não encontrado.")
    else:
        # Verificar se usuário tem vínculos
        if usuario.perfil == Perfil.LEITOR.value:
            emprestimos = emprestimo_repo.contar_por_leitor(id_usuario)
            if emprestimos > 0:
                flash_error(request, f"Não é possível excluir: usuário possui {emprestimos} empréstimo(s) registrado(s).")
                return RedirectResponse(
                    f"/admin/usuarios/{id_usuario}",
                    status_code=status.HTTP_303_SEE_OTHER
                )

        sucesso = usuario_repo.excluir(id_usuario)
        if sucesso:
            flash_success(request, f"Usuário '{usuario.nome}' excluído com sucesso!")
        else:
            flash_error(request, "Erro ao excluir usuário.")

    return RedirectResponse(
        "/admin/usuarios",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/usuarios/{id_usuario}/bloquear")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def post_bloquear_usuario(request: Request, id_usuario: int = Path(...)):
    """Bloquear usuário"""
    if request.state.usuario.id == id_usuario:
        flash_error(request, "Você não pode bloquear sua própria conta.")
        return RedirectResponse(
            f"/admin/usuarios/{id_usuario}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    usuario = usuario_repo.obter_por_id(id_usuario)
    if usuario:
        sucesso = usuario_repo.bloquear_usuario(id_usuario)
        if sucesso:
            flash_success(request, f"Usuário '{usuario.nome}' bloqueado com sucesso!")
        else:
            flash_error(request, "Erro ao bloquear usuário.")
    else:
        flash_error(request, "Usuário não encontrado.")

    return RedirectResponse(
        f"/admin/usuarios/{id_usuario}",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/usuarios/{id_usuario}/desbloquear")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def post_desbloquear_usuario(request: Request, id_usuario: int = Path(...)):
    """Desbloquear usuário"""
    usuario = usuario_repo.obter_por_id(id_usuario)
    if usuario:
        sucesso = usuario_repo.desbloquear_usuario(id_usuario)
        if sucesso:
            flash_success(request, f"Usuário '{usuario.nome}' desbloqueado com sucesso!")
        else:
            flash_error(request, "Erro ao desbloquear usuário.")
    else:
        flash_error(request, "Usuário não encontrado.")

    return RedirectResponse(
        f"/admin/usuarios/{id_usuario}",
        status_code=status.HTTP_303_SEE_OTHER
    )

# ==================== BACKUP E RESTORE ====================

@router.get("/backup")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_backup(request: Request):
    """Página de backup e restore"""
    backups = []
    if os.path.exists("backups"):
        arquivos = [f for f in os.listdir("backups") if f.endswith(".db")]
        for arquivo in sorted(arquivos, reverse=True):
            caminho = os.path.join("backups", arquivo)
            tamanho = os.path.getsize(caminho) / (1024 * 1024)  # MB
            data_mod = datetime.fromtimestamp(os.path.getmtime(caminho))
            backups.append({
                "nome": arquivo,
                "tamanho": round(tamanho, 2),
                "data": data_mod.strftime("%d/%m/%Y %H:%M:%S"),
            })

    return templates.TemplateResponse(
        "admin/backup.html",
        {"request": request, "backups": backups}
    )

@router.post("/backup/criar")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def post_criar_backup(request: Request):
    """Criar backup do banco de dados"""
    try:
        # Criar diretório de backups se não existir
        os.makedirs("backups", exist_ok=True)

        # Nome do arquivo com timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        nome_backup = f"backup_{timestamp}.db"
        caminho_backup = os.path.join("backups", nome_backup)

        # Copiar banco de dados
        shutil.copy2("database.db", caminho_backup)

        tamanho = os.path.getsize(caminho_backup) / (1024 * 1024)
        flash_success(request, f"Backup criado com sucesso! ({round(tamanho, 2)} MB)")
    except Exception as e:
        flash_error(request, f"Erro ao criar backup: {str(e)}")

    return RedirectResponse(
        "/admin/backup",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.get("/backup/download/{nome_arquivo}")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_download_backup(request: Request, nome_arquivo: str = Path(...)):
    """Download de arquivo de backup"""
    caminho = os.path.join("backups", nome_arquivo)

    if not os.path.exists(caminho) or not nome_arquivo.endswith(".db"):
        flash_error(request, "Arquivo de backup não encontrado.")
        return RedirectResponse(
            "/admin/backup",
            status_code=status.HTTP_303_SEE_OTHER
        )

    return FileResponse(
        caminho,
        media_type="application/octet-stream",
        filename=nome_arquivo
    )

@router.post("/backup/restore/{nome_arquivo}")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def post_restore_backup(request: Request, nome_arquivo: str = Path(...)):
    """Restaurar backup do banco de dados"""
    try:
        caminho = os.path.join("backups", nome_arquivo)

        if not os.path.exists(caminho):
            raise ValueError("Arquivo de backup não encontrado.")

        # Criar backup do estado atual antes de restaurar
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_antes = f"backup_antes_restore_{timestamp}.db"
        shutil.copy2("database.db", os.path.join("backups", backup_antes))

        # Restaurar backup
        shutil.copy2(caminho, "database.db")

        flash_success(request, f"Banco de dados restaurado com sucesso! Backup do estado anterior salvo como: {backup_antes}")
    except Exception as e:
        flash_error(request, f"Erro ao restaurar backup: {str(e)}")

    return RedirectResponse(
        "/admin/backup",
        status_code=status.HTTP_303_SEE_OTHER
    )

@router.post("/backup/excluir/{nome_arquivo}")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def post_excluir_backup(request: Request, nome_arquivo: str = Path(...)):
    """Excluir arquivo de backup"""
    try:
        caminho = os.path.join("backups", nome_arquivo)

        if os.path.exists(caminho):
            os.remove(caminho)
            flash_success(request, f"Backup '{nome_arquivo}' excluído com sucesso!")
        else:
            flash_error(request, "Arquivo de backup não encontrado.")
    except Exception as e:
        flash_error(request, f"Erro ao excluir backup: {str(e)}")

    return RedirectResponse(
        "/admin/backup",
        status_code=status.HTTP_303_SEE_OTHER
    )

# ==================== RELATÓRIOS ====================

@router.get("/relatorios")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_relatorios(request: Request):
    """Página de relatórios"""
    return templates.TemplateResponse(
        "admin/relatorios.html",
        {"request": request}
    )

@router.get("/relatorios/emprestimos")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_relatorio_emprestimos(
    request: Request,
    data_inicio: Optional[str] = Query(None),
    data_fim: Optional[str] = Query(None),
):
    """Relatório de empréstimos por período"""
    if not data_inicio or not data_fim:
        # Padrão: último mês
        data_fim_obj = datetime.now().date()
        data_inicio_obj = data_fim_obj - timedelta(days=30)
    else:
        data_inicio_obj = datetime.strptime(data_inicio, "%Y-%m-%d").date()
        data_fim_obj = datetime.strptime(data_fim, "%Y-%m-%d").date()

    emprestimos = emprestimo_repo.obter_por_periodo(data_inicio_obj, data_fim_obj)

    # Estatísticas do período
    total = len(emprestimos)
    devolvidos = len([e for e in emprestimos if e.get("status") == "devolvido"])
    atrasados = len([e for e in emprestimos if e.get("dias_atraso", 0) > 0])

    return templates.TemplateResponse(
        "admin/relatorios/emprestimos.html",
        {
            "request": request,
            "emprestimos": emprestimos,
            "data_inicio": data_inicio_obj.isoformat(),
            "data_fim": data_fim_obj.isoformat(),
            "stats": {
                "total": total,
                "devolvidos": devolvidos,
                "atrasados": atrasados,
            }
        }
    )

@router.get("/relatorios/usuarios")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_relatorio_usuarios(request: Request):
    """Relatório de usuários por perfil"""
    usuarios = usuario_repo.obter_todos()

    # Agrupar por perfil
    por_perfil = {}
    for perfil in Perfil.valores():
        por_perfil[perfil] = [u for u in usuarios if u.perfil == perfil]

    return templates.TemplateResponse(
        "admin/relatorios/usuarios.html",
        {
            "request": request,
            "usuarios": usuarios,
            "por_perfil": por_perfil,
            "total": len(usuarios),
        }
    )

@router.get("/relatorios/acervo")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_relatorio_acervo(request: Request):
    """Relatório do acervo"""
    livros = livro_repo.obter_todos()
    autores = autor_repo.obter_todos()
    categorias = categoria_repo.obter_todos()

    # Livros mais emprestados
    mais_emprestados = livro_repo.obter_mais_emprestados(limite=20)

    # Livros nunca emprestados
    nunca_emprestados = livro_repo.obter_nunca_emprestados()

    return templates.TemplateResponse(
        "admin/relatorios/acervo.html",
        {
            "request": request,
            "total_livros": len(livros),
            "total_exemplares": sum(l.quantidade_total for l in livros),
            "total_autores": len(autores),
            "total_categorias": len(categorias),
            "mais_emprestados": mais_emprestados,
            "nunca_emprestados": nunca_emprestados,
        }
    )

# ==================== CONFIGURAÇÕES ====================

@router.get("/configuracoes")
@auth_decorator(perfil_necessario=Perfil.ADMIN.value)
async def get_configuracoes(request: Request):
    """Página de configurações do sistema"""
    # Aqui você pode implementar um sistema de configurações
    # Por enquanto, apenas uma página informativa

    config = {
        "prazo_padrao_dias": 14,
        "max_renovacoes": 3,
        "max_emprestimos_simultaneos": 5,
        "dias_expiracao_reserva": 3,
    }

    return templates.TemplateResponse(
        "admin/configuracoes.html",
        {"request": request, "config": config}
    )
```

**⚠️ Observações importantes:**
- Este arquivo contém ~550 linhas de código
- Implementa 20+ endpoints para administração
- Sistema completo de backup/restore
- Relatórios detalhados
- Gestão completa de usuários de todos os perfis

---

### 6.2. Métodos Adicionais nos Repositories

#### 6.2.1. Adicionar ao usuario_repo.py

```python
def contar_todos() -> int:
    """Conta total de usuários"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM usuario")
        return cursor.fetchone()[0]

def obter_todos() -> list[Usuario]:
    """Retorna todos os usuários"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario ORDER BY nome")
        return [Usuario(**dict(row)) for row in cursor.fetchall()]

def obter_pendentes_confirmacao() -> list[Usuario]:
    """Retorna usuários com confirmação pendente"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM usuario WHERE confirmado = 0 ORDER BY data_cadastro DESC")
        return [Usuario(**dict(row)) for row in cursor.fetchall()]

def contar_novos_por_periodo(days: int = 7) -> int:
    """Conta usuários cadastrados nos últimos N dias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM usuario
            WHERE date(data_cadastro) >= date('now', '-' || ? || ' days')
        """, (days,))
        return cursor.fetchone()[0]
```

#### 6.2.2. Adicionar ao emprestimo_repo.py

```python
def contar_por_periodo(days: int = 30) -> int:
    """Conta empréstimos realizados nos últimos N dias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM emprestimo
            WHERE date(data_emprestimo) >= date('now', '-' || ? || ' days')
        """, (days,))
        return cursor.fetchone()[0]

def contar_devolucoes_por_periodo(days: int = 30) -> int:
    """Conta devoluções realizadas nos últimos N dias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM emprestimo
            WHERE data_devolucao IS NOT NULL
            AND date(data_devolucao) >= date('now', '-' || ? || ' days')
        """, (days,))
        return cursor.fetchone()[0]

def obter_por_periodo(data_inicio: date, data_fim: date) -> list:
    """Retorna empréstimos em um período"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                e.*,
                l.titulo as livro_titulo,
                u.nome as leitor_nome,
                b.nome as bibliotecario_nome,
                CASE
                    WHEN e.status = 'ativo' AND e.data_prevista_devolucao < date('now')
                    THEN julianday('now') - julianday(e.data_prevista_devolucao)
                    ELSE 0
                END as dias_atraso
            FROM emprestimo e
            JOIN livro l ON e.id_livro = l.id
            JOIN usuario u ON e.id_leitor = u.id
            JOIN usuario b ON e.id_bibliotecario = b.id
            WHERE date(e.data_emprestimo) BETWEEN ? AND ?
            ORDER BY e.data_emprestimo DESC
        """, (data_inicio.isoformat(), data_fim.isoformat()))
        return [dict(row) for row in cursor.fetchall()]

def obter_leitores_mais_ativos(limite: int = 10) -> list:
    """Retorna leitores com mais empréstimos"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT
                u.id,
                u.nome,
                u.email,
                COUNT(e.id) as total_emprestimos,
                COUNT(CASE WHEN e.status = 'ativo' THEN 1 END) as emprestimos_ativos
            FROM usuario u
            JOIN emprestimo e ON e.id_leitor = u.id
            WHERE u.perfil = ?
            GROUP BY u.id
            ORDER BY total_emprestimos DESC
            LIMIT ?
        """, (Perfil.LEITOR.value, limite))
        return [dict(row) for row in cursor.fetchall()]

def contar_por_leitor(id_leitor: int) -> int:
    """Conta total de empréstimos de um leitor"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM emprestimo WHERE id_leitor = ?", (id_leitor,))
        return cursor.fetchone()[0]
```

#### 6.2.3. Adicionar ao livro_repo.py

```python
def contar_novos_por_periodo(days: int = 7) -> int:
    """Conta livros cadastrados nos últimos N dias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM livro
            WHERE date(data_cadastro) >= date('now', '-' || ? || ' days')
        """, (days,))
        result = cursor.fetchone()
        return result[0] if result else 0

def obter_nunca_emprestados() -> list:
    """Retorna livros que nunca foram emprestados"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT l.* FROM livro l
            LEFT JOIN emprestimo e ON e.id_livro = l.id
            WHERE e.id IS NULL
            ORDER BY l.titulo
        """)
        return [dict(row) for row in cursor.fetchall()]
```

#### 6.2.4. Adicionar ao reserva_repo.py

```python
def contar_ativas() -> int:
    """Conta reservas ativas"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM reserva WHERE status = 'ativa'")
        return cursor.fetchone()[0]

def contar_por_periodo(days: int = 30) -> int:
    """Conta reservas realizadas nos últimos N dias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT COUNT(*) FROM reserva
            WHERE date(data_reserva) >= date('now', '-' || ? || ' days')
        """, (days,))
        return cursor.fetchone()[0]
```

---

### 6.3. Criar Templates do Administrador

#### 6.3.1. Dashboard Administrativo

📁 **Arquivo:** `templates/admin/dashboard.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Dashboard Administrativo{% endblock %}

{% block content %}
<h2><i class="bi bi-shield-check"></i> Dashboard Administrativo</h2>

<!-- Estatísticas de Usuários -->
<div class="row mt-4">
    <div class="col-12">
        <h4>Usuários do Sistema</h4>
    </div>
    <div class="col-md-2 mb-3">
        <div class="card border-primary">
            <div class="card-body text-center">
                <h6 class="card-title text-primary">Total</h6>
                <h2 class="display-4">{{ stats_usuarios.total }}</h2>
            </div>
        </div>
    </div>
    <div class="col-md-2 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Administradores</h6>
                <h3>{{ stats_usuarios.admins }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-2 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Bibliotecários</h6>
                <h3>{{ stats_usuarios.bibliotecarios }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-2 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Leitores</h6>
                <h3>{{ stats_usuarios.leitores }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-2 mb-3">
        <div class="card border-danger">
            <div class="card-body text-center">
                <h6 class="card-title text-danger small">Bloqueados</h6>
                <h3>{{ stats_usuarios.bloqueados }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-2 mb-3">
        <div class="card border-warning">
            <div class="card-body text-center">
                <h6 class="card-title text-warning small">Pendentes</h6>
                <h3>{{ stats_usuarios.pendentes }}</h3>
            </div>
        </div>
    </div>
</div>

<!-- Estatísticas do Acervo -->
<div class="row mt-4">
    <div class="col-12">
        <h4>Acervo</h4>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card border-success">
            <div class="card-body text-center">
                <h6 class="card-title text-success">Livros</h6>
                <h2 class="display-4">{{ stats_acervo.total_livros }}</h2>
                <p class="text-muted small">{{ stats_acervo.total_exemplares }} exemplares</p>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Autores</h6>
                <h3>{{ stats_acervo.total_autores }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Categorias</h6>
                <h3>{{ stats_acervo.total_categorias }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card border-info">
            <div class="card-body text-center">
                <h6 class="card-title text-info small">Novos (7 dias)</h6>
                <h3>{{ stats_acervo.novos_livros_semana }}</h3>
            </div>
        </div>
    </div>
</div>

<!-- Estatísticas de Atividade -->
<div class="row mt-4">
    <div class="col-12">
        <h4>Atividade do Sistema</h4>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Empréstimos Ativos</h6>
                <h3>{{ stats_emprestimos.ativos }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card border-danger">
            <div class="card-body text-center">
                <h6 class="card-title text-danger small">Atrasados</h6>
                <h3>{{ stats_emprestimos.atrasados }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Empréstimos (mês)</h6>
                <h3>{{ stats_emprestimos.mes }}</h3>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card">
            <div class="card-body text-center">
                <h6 class="text-muted small">Reservas Ativas</h6>
                <h3>{{ stats_reservas.ativas }}</h3>
            </div>
        </div>
    </div>
</div>

<!-- Top Livros e Leitores -->
<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <i class="bi bi-trophy"></i> Top 10 Livros Mais Emprestados
            </div>
            <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                {% if livros_mais_emprestados %}
                <ol class="list-group list-group-numbered">
                    {% for livro in livros_mais_emprestados %}
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">{{ livro.titulo }}</div>
                            <small class="text-muted">{{ livro.subtitulo or '' }}</small>
                        </div>
                        <span class="badge bg-primary rounded-pill">{{ livro.total_emprestimos }}</span>
                    </li>
                    {% endfor %}
                </ol>
                {% else %}
                <p class="text-muted">Nenhum dado disponível.</p>
                {% endif %}
            </div>
        </div>
    </div>

    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-success text-white">
                <i class="bi bi-people"></i> Top 10 Leitores Mais Ativos
            </div>
            <div class="card-body" style="max-height: 400px; overflow-y: auto;">
                {% if leitores_mais_ativos %}
                <ol class="list-group list-group-numbered">
                    {% for leitor in leitores_mais_ativos %}
                    <li class="list-group-item d-flex justify-content-between align-items-start">
                        <div class="ms-2 me-auto">
                            <div class="fw-bold">{{ leitor.nome }}</div>
                            <small class="text-muted">{{ leitor.email }}</small>
                        </div>
                        <span class="badge bg-success rounded-pill">{{ leitor.total_emprestimos }} empréstimos</span>
                    </li>
                    {% endfor %}
                </ol>
                {% else %}
                <p class="text-muted">Nenhum dado disponível.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<!-- Informações do Sistema -->
<div class="row mt-4">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-dark text-white">
                <i class="bi bi-hdd"></i> Sistema
            </div>
            <div class="card-body">
                <p><strong>Tamanho do Banco de Dados:</strong> {{ stats_sistema.tamanho_db }} MB</p>
                <p><strong>Backups Disponíveis:</strong> {{ stats_sistema.backups }}</p>
                <p><strong>Novos Usuários (7 dias):</strong> {{ stats_usuarios.novos_semana }}</p>
                <div class="mt-3">
                    <a href="/admin/backup" class="btn btn-sm btn-primary">
                        <i class="bi bi-cloud-arrow-down"></i> Gerenciar Backups
                    </a>
                    <a href="/admin/relatorios" class="btn btn-sm btn-info">
                        <i class="bi bi-file-earmark-text"></i> Ver Relatórios
                    </a>
                </div>
            </div>
        </div>
    </div>

    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-secondary text-white">
                <i class="bi bi-link-45deg"></i> Atalhos Rápidos
            </div>
            <div class="card-body">
                <div class="d-grid gap-2">
                    <a href="/admin/usuarios" class="btn btn-outline-primary">
                        <i class="bi bi-people"></i> Gerenciar Usuários
                    </a>
                    <a href="/admin/usuarios/novo" class="btn btn-outline-success">
                        <i class="bi bi-person-plus"></i> Novo Usuário
                    </a>
                    <a href="/admin/backup/criar" class="btn btn-outline-warning" onclick="return confirm('Deseja criar um backup agora?')">
                        <i class="bi bi-cloud-arrow-up"></i> Criar Backup
                    </a>
                    <a href="/admin/configuracoes" class="btn btn-outline-secondary">
                        <i class="bi bi-gear"></i> Configurações
                    </a>
                </div>
            </div>
        </div>
    </div>
</div>

{% endblock %}
```

#### 6.3.2. Gestão de Usuários

📁 **Arquivo:** `templates/admin/usuarios/listar.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Gerenciar Usuários{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2><i class="bi bi-people"></i> Gerenciar Usuários</h2>
    <a href="/admin/usuarios/novo" class="btn btn-primary">
        <i class="bi bi-person-plus"></i> Novo Usuário
    </a>
</div>

<!-- Filtros -->
<div class="card mb-3">
    <div class="card-body">
        <form method="GET" class="row g-3">
            <div class="col-md-4">
                <label for="busca" class="form-label">Buscar</label>
                <input type="text" class="form-control" id="busca" name="busca"
                       placeholder="Nome ou e-mail..." value="{{ busca or '' }}">
            </div>
            <div class="col-md-3">
                <label for="perfil" class="form-label">Perfil</label>
                <select class="form-select" id="perfil" name="perfil">
                    <option value="">Todos</option>
                    {% for p in perfis %}
                    <option value="{{ p }}" {{ 'selected' if perfil_filtro == p else '' }}>{{ p }}</option>
                    {% endfor %}
                </select>
            </div>
            <div class="col-md-3">
                <label class="form-label d-block">&nbsp;</label>
                <div class="form-check">
                    <input class="form-check-input" type="checkbox" id="bloqueados" name="bloqueados"
                           value="true" {{ 'checked' if bloqueados else '' }}>
                    <label class="form-check-label" for="bloqueados">
                        Apenas bloqueados
                    </label>
                </div>
            </div>
            <div class="col-md-2">
                <label class="form-label d-block">&nbsp;</label>
                <button type="submit" class="btn btn-primary w-100">
                    <i class="bi bi-search"></i> Filtrar
                </button>
            </div>
        </form>
    </div>
</div>

<!-- Lista de Usuários -->
{% if usuarios %}
<div class="table-responsive">
    <table class="table table-hover">
        <thead class="table-light">
            <tr>
                <th>ID</th>
                <th>Nome</th>
                <th>E-mail</th>
                <th>Perfil</th>
                <th>Status</th>
                <th>Cadastro</th>
                <th>Ações</th>
            </tr>
        </thead>
        <tbody>
            {% for usuario in usuarios %}
            <tr>
                <td>{{ usuario.id }}</td>
                <td>{{ usuario.nome }}</td>
                <td>{{ usuario.email }}</td>
                <td>
                    {% if usuario.perfil == 'Administrador' %}
                    <span class="badge bg-danger">{{ usuario.perfil }}</span>
                    {% elif usuario.perfil == 'Bibliotecário' %}
                    <span class="badge bg-warning text-dark">{{ usuario.perfil }}</span>
                    {% else %}
                    <span class="badge bg-info">{{ usuario.perfil }}</span>
                    {% endif %}
                </td>
                <td>
                    {% if usuario.bloqueado %}
                    <span class="badge bg-danger">Bloqueado</span>
                    {% elif not usuario.confirmado %}
                    <span class="badge bg-warning">Pendente</span>
                    {% else %}
                    <span class="badge bg-success">Ativo</span>
                    {% endif %}
                </td>
                <td>{{ usuario.data_cadastro or '-' }}</td>
                <td>
                    <div class="btn-group btn-group-sm">
                        <a href="/admin/usuarios/{{ usuario.id }}" class="btn btn-outline-info" title="Ver detalhes">
                            <i class="bi bi-eye"></i>
                        </a>
                        <a href="/admin/usuarios/{{ usuario.id }}/editar" class="btn btn-outline-warning" title="Editar">
                            <i class="bi bi-pencil"></i>
                        </a>
                        <button type="button" class="btn btn-outline-danger" title="Excluir"
                                onclick="confirmarExclusao({{ usuario.id }}, '{{ usuario.nome }}')">
                            <i class="bi bi-trash"></i>
                        </button>
                    </div>
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
</div>

<p class="text-muted">Total: {{ usuarios|length }} usuário(s)</p>

{% else %}
<div class="alert alert-info">
    <i class="bi bi-info-circle"></i> Nenhum usuário encontrado.
</div>
{% endif %}

<form id="formExcluir" method="POST" style="display: none;"></form>

<script>
function confirmarExclusao(id, nome) {
    if (confirm(`Tem certeza que deseja excluir o usuário "${nome}"?`)) {
        const form = document.getElementById('formExcluir');
        form.action = `/admin/usuarios/${id}/excluir`;
        form.submit();
    }
}
</script>

{% endblock %}
```

📁 **Arquivo:** `templates/admin/usuarios/form.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}{{ 'Editar' if usuario else 'Novo' }} Usuário{% endblock %}

{% block content %}
<h2><i class="bi bi-person"></i> {{ 'Editar' if usuario else 'Novo' }} Usuário</h2>

<div class="row mt-4">
    <div class="col-md-8">
        <div class="card">
            <div class="card-body">
                <form method="POST">
                    <div class="mb-3">
                        <label for="nome" class="form-label">Nome Completo *</label>
                        <input type="text" class="form-control" id="nome" name="nome"
                               value="{{ usuario.nome if usuario else '' }}" required maxlength="200">
                    </div>

                    <div class="mb-3">
                        <label for="email" class="form-label">E-mail *</label>
                        <input type="email" class="form-control" id="email" name="email"
                               value="{{ usuario.email if usuario else '' }}" required maxlength="200">
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="perfil" class="form-label">Perfil *</label>
                            <select class="form-select" id="perfil" name="perfil" required>
                                <option value="">Selecione...</option>
                                {% for p in perfis %}
                                <option value="{{ p }}" {{ 'selected' if usuario and usuario.perfil == p else '' }}>
                                    {{ p }}
                                </option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="senha" class="form-label">
                                Senha {{ 'Nova' if usuario else '' }} *
                            </label>
                            <input type="password" class="form-control" id="senha" name="senha"
                                   {{ 'required' if not usuario else '' }} minlength="8">
                            {% if usuario %}
                            <div class="form-text">Deixe em branco para manter a senha atual</div>
                            {% endif %}
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="telefone" class="form-label">Telefone</label>
                            <input type="tel" class="form-control" id="telefone" name="telefone"
                                   value="{{ usuario.telefone if usuario else '' }}" maxlength="20">
                        </div>

                        <div class="col-md-6 mb-3">
                            <label class="form-label d-block">Status</label>
                            <div class="form-check">
                                <input class="form-check-input" type="checkbox" id="confirmado" name="confirmado"
                                       {{ 'checked' if usuario and usuario.confirmado else '' }}>
                                <label class="form-check-label" for="confirmado">
                                    Conta confirmada
                                </label>
                            </div>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="endereco" class="form-label">Endereço</label>
                        <textarea class="form-control" id="endereco" name="endereco" rows="2">{{ usuario.endereco if usuario else '' }}</textarea>
                    </div>

                    <div class="d-flex gap-2">
                        <button type="submit" class="btn btn-primary">
                            <i class="bi bi-save"></i> Salvar
                        </button>
                        <a href="/admin/usuarios{{ ('/' + usuario.id|string) if usuario else '' }}" class="btn btn-secondary">
                            <i class="bi bi-x"></i> Cancelar
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-info text-white">
                <i class="bi bi-info-circle"></i> Requisitos de Senha
            </div>
            <div class="card-body">
                <ul class="small mb-0">
                    <li>Mínimo de 8 caracteres</li>
                    <li>Pelo menos uma letra maiúscula</li>
                    <li>Pelo menos uma letra minúscula</li>
                    <li>Pelo menos um número</li>
                    <li>Pelo menos um caractere especial</li>
                </ul>
            </div>
        </div>

        {% if usuario %}
        <div class="card mt-3">
            <div class="card-header bg-warning text-dark">
                <i class="bi bi-exclamation-triangle"></i> Ações
            </div>
            <div class="card-body">
                {% if usuario.bloqueado %}
                <form method="POST" action="/admin/usuarios/{{ usuario.id }}/desbloquear">
                    <button type="submit" class="btn btn-success w-100 mb-2">
                        <i class="bi bi-unlock"></i> Desbloquear Usuário
                    </button>
                </form>
                {% else %}
                <form method="POST" action="/admin/usuarios/{{ usuario.id }}/bloquear">
                    <button type="submit" class="btn btn-warning w-100 mb-2"
                            onclick="return confirm('Deseja bloquear este usuário?')">
                        <i class="bi bi-lock"></i> Bloquear Usuário
                    </button>
                </form>
                {% endif %}
            </div>
        </div>
        {% endif %}
    </div>
</div>

{% endblock %}
```

📁 **Arquivo:** `templates/admin/usuarios/detalhe.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}{{ usuario.nome }}{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center mb-3">
    <h2><i class="bi bi-person"></i> {{ usuario.nome }}</h2>
    <div class="btn-group">
        <a href="/admin/usuarios/{{ usuario.id }}/editar" class="btn btn-warning">
            <i class="bi bi-pencil"></i> Editar
        </a>
        <a href="/admin/usuarios" class="btn btn-secondary">
            <i class="bi bi-arrow-left"></i> Voltar
        </a>
    </div>
</div>

<div class="row">
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-primary text-white">
                Informações do Usuário
            </div>
            <div class="card-body">
                <p><strong>ID:</strong> {{ usuario.id }}</p>
                <p><strong>Nome:</strong> {{ usuario.nome }}</p>
                <p><strong>E-mail:</strong> {{ usuario.email }}</p>
                <p><strong>Perfil:</strong>
                    {% if usuario.perfil == 'Administrador' %}
                    <span class="badge bg-danger">{{ usuario.perfil }}</span>
                    {% elif usuario.perfil == 'Bibliotecário' %}
                    <span class="badge bg-warning text-dark">{{ usuario.perfil }}</span>
                    {% else %}
                    <span class="badge bg-info">{{ usuario.perfil }}</span>
                    {% endif %}
                </p>
                <p><strong>Telefone:</strong> {{ usuario.telefone or 'Não informado' }}</p>
                <p><strong>Endereço:</strong> {{ usuario.endereco or 'Não informado' }}</p>
                <p><strong>Data de Cadastro:</strong> {{ usuario.data_cadastro or 'Não disponível' }}</p>
                <p><strong>Status:</strong>
                    {% if usuario.bloqueado %}
                    <span class="badge bg-danger">Bloqueado</span>
                    {% elif not usuario.confirmado %}
                    <span class="badge bg-warning">Pendente de Confirmação</span>
                    {% else %}
                    <span class="badge bg-success">Ativo</span>
                    {% endif %}
                </p>
            </div>
        </div>
    </div>

    {% if stats %}
    <div class="col-md-6">
        <div class="card">
            <div class="card-header bg-success text-white">
                Estatísticas
            </div>
            <div class="card-body">
                <p><strong>Total de Empréstimos:</strong> {{ stats.total_emprestimos }}</p>
                <p><strong>Empréstimos Ativos:</strong> {{ stats.emprestimos_ativos }}</p>
                <p><strong>Reservas Ativas:</strong> {{ stats.reservas_ativas }}</p>
            </div>
        </div>
    </div>
    {% endif %}
</div>

{% endblock %}
```

#### 6.3.3. Sistema de Backup

📁 **Arquivo:** `templates/admin/backup.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Backup e Restore{% endblock %}

{% block content %}
<h2><i class="bi bi-cloud-arrow-down"></i> Backup e Restore</h2>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <i class="bi bi-cloud-arrow-up"></i> Criar Backup
            </div>
            <div class="card-body">
                <p>Crie um backup completo do banco de dados. O arquivo será salvo no diretório <code>backups/</code>.</p>
                <form method="POST" action="/admin/backup/criar" onsubmit="return confirm('Deseja criar um backup agora?')">
                    <button type="submit" class="btn btn-primary">
                        <i class="bi bi-cloud-arrow-up"></i> Criar Backup Agora
                    </button>
                </form>
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="card">
            <div class="card-header bg-success text-white">
                <i class="bi bi-file-earmark-zip"></i> Backups Disponíveis ({{ backups|length }})
            </div>
            <div class="card-body">
                {% if backups %}
                <div class="table-responsive">
                    <table class="table table-hover">
                        <thead>
                            <tr>
                                <th>Arquivo</th>
                                <th>Data</th>
                                <th>Tamanho</th>
                                <th>Ações</th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for backup in backups %}
                            <tr>
                                <td><code>{{ backup.nome }}</code></td>
                                <td>{{ backup.data }}</td>
                                <td>{{ backup.tamanho }} MB</td>
                                <td>
                                    <div class="btn-group btn-group-sm">
                                        <a href="/admin/backup/download/{{ backup.nome }}" class="btn btn-outline-primary" title="Download">
                                            <i class="bi bi-download"></i>
                                        </a>
                                        <button type="button" class="btn btn-outline-warning" title="Restaurar"
                                                onclick="confirmarRestore('{{ backup.nome }}')">
                                            <i class="bi bi-arrow-counterclockwise"></i>
                                        </button>
                                        <button type="button" class="btn btn-outline-danger" title="Excluir"
                                                onclick="confirmarExclusao('{{ backup.nome }}')">
                                            <i class="bi bi-trash"></i>
                                        </button>
                                    </div>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
                {% else %}
                <p class="text-muted">Nenhum backup disponível.</p>
                {% endif %}
            </div>
        </div>
    </div>
</div>

<div class="row mt-4">
    <div class="col-md-12">
        <div class="alert alert-warning">
            <h5><i class="bi bi-exclamation-triangle"></i> Aviso Importante</h5>
            <ul>
                <li><strong>Criar Backup:</strong> Cria uma cópia completa do banco de dados atual.</li>
                <li><strong>Restaurar:</strong> Substitui o banco atual pelo backup selecionado. Um backup automático do estado atual será criado antes da restauração.</li>
                <li><strong>Excluir:</strong> Remove permanentemente o arquivo de backup selecionado.</li>
                <li><strong>Recomendação:</strong> Faça backups regulares (diários ou semanais) e guarde cópias em local seguro.</li>
            </ul>
        </div>
    </div>
</div>

<form id="formRestore" method="POST" style="display: none;"></form>
<form id="formExcluir" method="POST" style="display: none;"></form>

<script>
function confirmarRestore(nome) {
    if (confirm(`ATENÇÃO: Restaurar o backup "${nome}" substituirá TODOS os dados atuais!\n\nUm backup do estado atual será criado automaticamente antes da restauração.\n\nDeseja continuar?`)) {
        const form = document.getElementById('formRestore');
        form.action = `/admin/backup/restore/${nome}`;
        form.submit();
    }
}

function confirmarExclusao(nome) {
    if (confirm(`Tem certeza que deseja excluir o backup "${nome}"?\n\nEsta ação não pode ser desfeita.`)) {
        const form = document.getElementById('formExcluir');
        form.action = `/admin/backup/excluir/${nome}`;
        form.submit();
    }
}
</script>

{% endblock %}
```

#### 6.3.4. Página de Relatórios

📁 **Arquivo:** `templates/admin/relatorios.html`

```html
{% extends "base_privada.html" %}
{% block titulo %}Relatórios{% endblock %}

{% block content %}
<h2><i class="bi bi-file-earmark-text"></i> Relatórios</h2>

<div class="row mt-4">
    <div class="col-md-4 mb-3">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title"><i class="bi bi-book"></i> Relatório de Empréstimos</h5>
                <p class="card-text">Visualize empréstimos por período com estatísticas detalhadas.</p>
                <a href="/admin/relatorios/emprestimos" class="btn btn-primary">
                    Ver Relatório
                </a>
            </div>
        </div>
    </div>

    <div class="col-md-4 mb-3">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title"><i class="bi bi-people"></i> Relatório de Usuários</h5>
                <p class="card-text">Visualize todos os usuários agrupados por perfil.</p>
                <a href="/admin/relatorios/usuarios" class="btn btn-primary">
                    Ver Relatório
                </a>
            </div>
        </div>
    </div>

    <div class="col-md-4 mb-3">
        <div class="card h-100">
            <div class="card-body">
                <h5 class="card-title"><i class="bi bi-collection"></i> Relatório do Acervo</h5>
                <p class="card-text">Estatísticas completas do acervo da biblioteca.</p>
                <a href="/admin/relatorios/acervo" class="btn btn-primary">
                    Ver Relatório
                </a>
            </div>
        </div>
    </div>
</div>

{% endblock %}
```

### 6.4. Registrar Rotas no main.py

📝 **Arquivo:** `main.py`

**Adicionar import:**

```python
from routes import admin_routes
```

**Adicionar no final da seção de routers:**

```python
app.include_router(admin_routes.router)
logger.info("Router de admin incluído")
```

---

### 6.5. Testar Sprint 4

#### Como Testar:

1. **Executar aplicação:**
   ```bash
   python main.py
   ```

2. **Login como admin:**
   - Email: admin cadastrado
   - Senha: conforme cadastrado

3. **Testar funcionalidades (em ordem):**

   **a) Dashboard:**
   - ✅ Acessar `/admin/dashboard`
   - ✅ Verificar todas as estatísticas
   - ✅ Ver top livros e leitores
   - ✅ Verificar info do sistema

   **b) Gestão de Usuários:**
   - ✅ Acessar `/admin/usuarios`
   - ✅ Filtrar por perfil
   - ✅ Buscar usuário
   - ✅ Criar novo usuário (todos os perfis)
   - ✅ Editar usuário
   - ✅ Ver detalhes
   - ✅ Bloquear/desbloquear
   - ✅ Excluir usuário (sem vínculos)

   **c) Backup e Restore:**
   - ✅ Acessar `/admin/backup`
   - ✅ Criar backup
   - ✅ Download de backup
   - ✅ Restaurar backup
   - ✅ Excluir backup

   **d) Relatórios:**
   - ✅ Acessar `/admin/relatorios`
   - ✅ Ver relatório de empréstimos
   - ✅ Ver relatório de usuários
   - ✅ Ver relatório de acervo

4. **Testar regras de negócio:**
   - ✅ Admin não pode se auto-excluir
   - ✅ Admin não pode se auto-bloquear
   - ✅ Não permitir excluir usuário com empréstimos
   - ✅ Validação de e-mail único
   - ✅ Validação de senha forte
   - ✅ Backup automático antes de restore

---

### 6.6. Checklist Sprint 4

- [ ] admin_routes.py criado com 20+ endpoints
- [ ] Dashboard administrativo implementado
- [ ] CRUD completo de usuários (todos os perfis)
- [ ] Sistema de backup/restore implementado
- [ ] Download de backups funcionando
- [ ] Exclusão de backups funcionando
- [ ] Relatório de empréstimos por período
- [ ] Relatório de usuários por perfil
- [ ] Relatório do acervo
- [ ] Métodos adicionais em usuario_repo.py
- [ ] Métodos adicionais em emprestimo_repo.py
- [ ] Métodos adicionais em livro_repo.py
- [ ] Métodos adicionais em reserva_repo.py
- [ ] Template do dashboard admin
- [ ] Templates de usuários (listar, form, detalhe)
- [ ] Template de backup
- [ ] Template de relatórios
- [ ] Router registrado no main.py
- [ ] Testado dashboard completo
- [ ] Testado CRUD de usuários
- [ ] Testado sistema de backup
- [ ] Testado sistema de restore
- [ ] Testados relatórios
- [ ] Testadas validações de segurança
- [ ] Testadas restrições (não excluir-se, etc.)

---

## 7. SPRINT 5: FUNCIONALIDADES COMPLEMENTARES

**Duração estimada:** 36 horas

**Objetivo:** Implementar área pública, sistema de busca avançada, auto-cadastro e notificações por email.

**Entregas:**
- ✅ Área pública com catálogo de livros
- ✅ Sistema de busca avançada (filtros múltiplos)
- ✅ Auto-cadastro de leitores
- ✅ Sistema de notificações por email
- ✅ Templates de email personalizados
- ✅ Integração completa do sistema de mensagens
- ✅ 10+ templates para área pública

---

### 7.1. Criar Rotas Públicas

📁 **Arquivo:** `routes/public_routes.py`

```python
from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Form, Query, Request, status
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

import repo.livro_repo as livro_repo
import repo.autor_repo as autor_repo
import repo.categoria_repo as categoria_repo
import repo.usuario_repo as usuario_repo
from dtos.usuario_dto import UsuarioDTO
from util.flash_messages import flash_error, flash_success
from util.perfis import Perfil
from util.validators import validate_email, validate_password
from util.security import hash_password
from util.email_util import enviar_email_confirmacao

router = APIRouter(prefix="/catalogo")
templates = Jinja2Templates(directory="templates")

# ==================== CATÁLOGO PÚBLICO ====================

@router.get("")
async def get_catalogo(
    request: Request,
    busca: Optional[str] = Query(None),
    categoria: Optional[int] = Query(None),
    autor: Optional[int] = Query(None),
    disponivel: Optional[bool] = Query(None),
    pagina: int = Query(1, ge=1),
):
    """Catálogo público de livros com filtros e paginação"""

    itens_por_pagina = 12
    offset = (pagina - 1) * itens_por_pagina

    # Aplicar filtros
    if busca:
        livros = livro_repo.buscar(busca)
    elif categoria:
        livros = livro_repo.obter_por_categoria(categoria)
    elif autor:
        livros = livro_repo.obter_por_autor(autor)
    else:
        livros = livro_repo.obter_todos()

    # Filtrar apenas disponíveis se solicitado
    if disponivel:
        livros = [l for l in livros if l.quantidade_disponivel > 0]

    # Paginação manual
    total_livros = len(livros)
    total_paginas = (total_livros + itens_por_pagina - 1) // itens_por_pagina
    livros_pagina = livros[offset:offset + itens_por_pagina]

    # Dados para filtros
    categorias = categoria_repo.obter_todos()
    autores = autor_repo.obter_todos()

    return templates.TemplateResponse(
        "public/catalogo.html",
        {
            "request": request,
            "livros": livros_pagina,
            "categorias": categorias,
            "autores": autores,
            "busca": busca,
            "categoria_selecionada": categoria,
            "autor_selecionado": autor,
            "disponivel": disponivel,
            "pagina_atual": pagina,
            "total_paginas": total_paginas,
            "total_livros": total_livros,
        }
    )

@router.get("/livro/{id_livro}")
async def get_detalhe_livro_publico(request: Request, id_livro: int):
    """Detalhes públicos de um livro"""
    livro = livro_repo.obter_por_id_completo(id_livro)

    if not livro:
        flash_error(request, "Livro não encontrado.")
        return RedirectResponse(
            "/catalogo",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # Obter autores e categorias
    autores = livro_repo.obter_autores(id_livro)
    categorias = livro_repo.obter_categorias(id_livro)

    # Livros relacionados (mesma categoria)
    livros_relacionados = []
    if categorias:
        livros_relacionados = livro_repo.obter_por_categoria(categorias[0].id, limite=6)
        livros_relacionados = [l for l in livros_relacionados if l.id != id_livro][:4]

    return templates.TemplateResponse(
        "public/livro_detalhe.html",
        {
            "request": request,
            "livro": livro,
            "autores": autores,
            "categorias": categorias,
            "livros_relacionados": livros_relacionados,
        }
    )

@router.get("/autor/{id_autor}")
async def get_autor_publico(request: Request, id_autor: int):
    """Página pública de um autor"""
    autor = autor_repo.obter_por_id(id_autor)

    if not autor:
        flash_error(request, "Autor não encontrado.")
        return RedirectResponse(
            "/catalogo",
            status_code=status.HTTP_303_SEE_OTHER
        )

    livros = livro_repo.obter_por_autor(id_autor)

    return templates.TemplateResponse(
        "public/autor.html",
        {"request": request, "autor": autor, "livros": livros}
    )

@router.get("/categoria/{id_categoria}")
async def get_categoria_publica(request: Request, id_categoria: int):
    """Página pública de uma categoria"""
    categoria = categoria_repo.obter_por_id(id_categoria)

    if not categoria:
        flash_error(request, "Categoria não encontrada.")
        return RedirectResponse(
            "/catalogo",
            status_code=status.HTTP_303_SEE_OTHER
        )

    livros = livro_repo.obter_por_categoria(id_categoria)

    return templates.TemplateResponse(
        "public/categoria.html",
        {"request": request, "categoria": categoria, "livros": livros}
    )

# ==================== BUSCA AVANÇADA ====================

@router.get("/busca-avancada")
async def get_busca_avancada(request: Request):
    """Página de busca avançada"""
    categorias = categoria_repo.obter_todos()
    autores = autor_repo.obter_todos()

    return templates.TemplateResponse(
        "public/busca_avancada.html",
        {"request": request, "categorias": categorias, "autores": autores}
    )

@router.post("/busca-avancada")
async def post_busca_avancada(
    request: Request,
    titulo: Optional[str] = Form(None),
    autor: Optional[int] = Form(None),
    categoria: Optional[int] = Form(None),
    isbn: Optional[str] = Form(None),
    ano_inicio: Optional[int] = Form(None),
    ano_fim: Optional[int] = Form(None),
    editora: Optional[str] = Form(None),
    apenas_disponiveis: bool = Form(False),
):
    """Processar busca avançada"""
    livros = livro_repo.busca_avancada(
        titulo=titulo,
        id_autor=autor,
        id_categoria=categoria,
        isbn=isbn,
        ano_inicio=ano_inicio,
        ano_fim=ano_fim,
        editora=editora,
        apenas_disponiveis=apenas_disponiveis,
    )

    categorias = categoria_repo.obter_todos()
    autores = autor_repo.obter_todos()

    return templates.TemplateResponse(
        "public/resultados_busca.html",
        {
            "request": request,
            "livros": livros,
            "total": len(livros),
            "categorias": categorias,
            "autores": autores,
            "filtros": {
                "titulo": titulo,
                "autor": autor,
                "categoria": categoria,
                "isbn": isbn,
                "ano_inicio": ano_inicio,
                "ano_fim": ano_fim,
                "editora": editora,
                "apenas_disponiveis": apenas_disponiveis,
            }
        }
    )

# ==================== AUTO-CADASTRO ====================

@router.get("/cadastro")
async def get_cadastro(request: Request):
    """Formulário de auto-cadastro para leitores"""
    return templates.TemplateResponse(
        "public/cadastro.html",
        {"request": request}
    )

@router.post("/cadastro")
async def post_cadastro(
    request: Request,
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...),
    telefone: Optional[str] = Form(None),
    endereco: Optional[str] = Form(None),
    data_nascimento: Optional[str] = Form(None),
):
    """Processar auto-cadastro"""
    try:
        # Validações
        if not validate_email(email):
            raise ValueError("E-mail inválido.")

        if senha != confirmar_senha:
            raise ValueError("As senhas não coincidem.")

        if not validate_password(senha):
            raise ValueError(
                "Senha deve ter pelo menos 8 caracteres, incluindo "
                "maiúsculas, minúsculas, números e caracteres especiais."
            )

        # Verificar se email já existe
        if usuario_repo.obter_por_email(email):
            raise ValueError("E-mail já cadastrado no sistema.")

        # Criar usuário
        usuario_dto = UsuarioDTO(
            nome=nome,
            email=email,
            senha=hash_password(senha),
            perfil=Perfil.LEITOR.value,
            telefone=telefone,
            endereco=endereco,
            data_nascimento=data_nascimento,
            confirmado=0,  # Aguardando confirmação
        )

        usuario_id = usuario_repo.inserir(usuario_dto)

        if usuario_id:
            # Enviar email de confirmação
            token = usuario_repo.gerar_token_confirmacao(usuario_id)
            enviar_email_confirmacao(email, nome, token)

            flash_success(
                request,
                "Cadastro realizado! Verifique seu e-mail para confirmar sua conta."
            )
            return RedirectResponse(
                "/login",
                status_code=status.HTTP_303_SEE_OTHER
            )
        else:
            raise ValueError("Erro ao criar conta. Tente novamente.")

    except ValueError as e:
        flash_error(request, str(e))
        return RedirectResponse(
            "/catalogo/cadastro",
            status_code=status.HTTP_303_SEE_OTHER
        )

@router.get("/confirmar/{token}")
async def confirmar_email(request: Request, token: str):
    """Confirmar email do usuário"""
    usuario_id = usuario_repo.validar_token_confirmacao(token)

    if usuario_id:
        usuario_repo.confirmar_usuario(usuario_id)
        flash_success(request, "E-mail confirmado com sucesso! Você já pode fazer login.")
    else:
        flash_error(request, "Token inválido ou expirado.")

    return RedirectResponse(
        "/login",
        status_code=status.HTTP_303_SEE_OTHER
    )

# ==================== SOBRE E CONTATO ====================

@router.get("/sobre")
async def get_sobre(request: Request):
    """Página sobre a biblioteca"""
    # Estatísticas públicas
    total_livros = livro_repo.contar_total()
    total_exemplares = livro_repo.contar_exemplares_total()
    total_autores = autor_repo.contar_total()
    total_categorias = categoria_repo.contar_total()

    return templates.TemplateResponse(
        "public/sobre.html",
        {
            "request": request,
            "stats": {
                "total_livros": total_livros,
                "total_exemplares": total_exemplares,
                "total_autores": total_autores,
                "total_categorias": total_categorias,
            }
        }
    )

@router.get("/contato")
async def get_contato(request: Request):
    """Página de contato"""
    return templates.TemplateResponse(
        "public/contato.html",
        {"request": request}
    )
```

**⚠️ Observações importantes:**
- Este arquivo contém ~300 linhas de código
- Implementa 10+ endpoints públicos (sem autenticação)
- Sistema de busca avançada com múltiplos filtros
- Auto-cadastro com confirmação por email
- Paginação no catálogo

---

### 7.2. Implementar Sistema de Notificações

📁 **Arquivo:** `util/notificacao_util.py`

```python
from datetime import datetime, timedelta
from typing import Optional
import repo.emprestimo_repo as emprestimo_repo
import repo.reserva_repo as reserva_repo
import repo.usuario_repo as usuario_repo
from util.email_util import enviar_email

def notificar_emprestimo_registrado(id_emprestimo: int):
    """Notifica leitor sobre novo empréstimo"""
    emprestimo = emprestimo_repo.obter_por_id_completo(id_emprestimo)
    if not emprestimo:
        return

    leitor = usuario_repo.obter_por_id(emprestimo.id_leitor)
    if not leitor:
        return

    assunto = "Empréstimo Registrado - Biblix"
    corpo = f"""
    <h2>Olá, {leitor.nome}!</h2>

    <p>Seu empréstimo foi registrado com sucesso:</p>

    <ul>
        <li><strong>Livro:</strong> {emprestimo.livro_titulo}</li>
        <li><strong>Data do Empréstimo:</strong> {emprestimo.data_emprestimo}</li>
        <li><strong>Data de Devolução:</strong> {emprestimo.data_prevista_devolucao}</li>
    </ul>

    <p>Lembre-se de devolver o livro até a data prevista para evitar multas.</p>

    <p><a href="http://localhost:8000/leitor/emprestimos">Ver meus empréstimos</a></p>

    <p>Atenciosamente,<br>Equipe Biblix</p>
    """

    enviar_email(leitor.email, assunto, corpo)

def notificar_devolucao_proxima(id_emprestimo: int):
    """Notifica leitor sobre devolução próxima (3 dias antes)"""
    emprestimo = emprestimo_repo.obter_por_id_completo(id_emprestimo)
    if not emprestimo or emprestimo.status != "ativo":
        return

    leitor = usuario_repo.obter_por_id(emprestimo.id_leitor)
    if not leitor:
        return

    assunto = "Lembrete: Devolução Próxima - Biblix"
    corpo = f"""
    <h2>Olá, {leitor.nome}!</h2>

    <p>Este é um lembrete de que você tem um empréstimo com devolução próxima:</p>

    <ul>
        <li><strong>Livro:</strong> {emprestimo.livro_titulo}</li>
        <li><strong>Data de Devolução:</strong> {emprestimo.data_prevista_devolucao}</li>
    </ul>

    <p>Não se esqueça de devolver o livro na data prevista!</p>

    <p><a href="http://localhost:8000/leitor/emprestimos">Ver meus empréstimos</a></p>

    <p>Atenciosamente,<br>Equipe Biblix</p>
    """

    enviar_email(leitor.email, assunto, corpo)

def notificar_emprestimo_atrasado(id_emprestimo: int):
    """Notifica leitor sobre empréstimo atrasado"""
    emprestimo = emprestimo_repo.obter_por_id_completo(id_emprestimo)
    if not emprestimo:
        return

    leitor = usuario_repo.obter_por_id(emprestimo.id_leitor)
    if not leitor:
        return

    dias_atraso = emprestimo.get('dias_atraso', 0)

    assunto = "⚠️ ATENÇÃO: Empréstimo Atrasado - Biblix"
    corpo = f"""
    <h2>Olá, {leitor.nome}!</h2>

    <p><strong style="color: red;">Seu empréstimo está atrasado!</strong></p>

    <ul>
        <li><strong>Livro:</strong> {emprestimo.livro_titulo}</li>
        <li><strong>Data de Devolução:</strong> {emprestimo.data_prevista_devolucao}</li>
        <li><strong>Dias de Atraso:</strong> {dias_atraso}</li>
    </ul>

    <p>Por favor, devolva o livro o mais rápido possível para evitar multas e bloqueio da sua conta.</p>

    <p><a href="http://localhost:8000/leitor/emprestimos">Ver meus empréstimos</a></p>

    <p>Atenciosamente,<br>Equipe Biblix</p>
    """

    enviar_email(leitor.email, assunto, corpo)

def notificar_reserva_disponivel(id_reserva: int):
    """Notifica leitor que livro reservado está disponível"""
    reserva = reserva_repo.obter_por_id_completo(id_reserva)
    if not reserva:
        return

    leitor = usuario_repo.obter_por_id(reserva.id_leitor)
    if not leitor:
        return

    assunto = "✅ Livro Reservado Disponível - Biblix"
    corpo = f"""
    <h2>Olá, {leitor.nome}!</h2>

    <p>Boa notícia! O livro que você reservou está disponível:</p>

    <ul>
        <li><strong>Livro:</strong> {reserva.livro_titulo}</li>
        <li><strong>Data da Reserva:</strong> {reserva.data_reserva}</li>
    </ul>

    <p><strong>Você tem 3 dias para retirar o livro.</strong> Após este prazo, a reserva será cancelada.</p>

    <p>Compareça à biblioteca para realizar o empréstimo.</p>

    <p><a href="http://localhost:8000/leitor/reservas">Ver minhas reservas</a></p>

    <p>Atenciosamente,<br>Equipe Biblix</p>
    """

    enviar_email(leitor.email, assunto, corpo)

def notificar_nova_mensagem(id_destinatario: int, remetente_nome: str, assunto_msg: str):
    """Notifica usuário sobre nova mensagem interna"""
    destinatario = usuario_repo.obter_por_id(id_destinatario)
    if not destinatario:
        return

    assunto = "Nova Mensagem - Biblix"
    corpo = f"""
    <h2>Olá, {destinatario.nome}!</h2>

    <p>Você recebeu uma nova mensagem de <strong>{remetente_nome}</strong>:</p>

    <p><strong>Assunto:</strong> {assunto_msg}</p>

    <p><a href="http://localhost:8000/leitor/mensagens">Ler mensagem</a></p>

    <p>Atenciosamente,<br>Equipe Biblix</p>
    """

    enviar_email(destinatario.email, assunto, corpo)

def processar_notificacoes_diarias():
    """
    Função para ser executada diariamente (via cron ou scheduler).
    Processa todas as notificações pendentes.
    """
    # Notificar devoluções próximas (3 dias antes)
    data_limite = datetime.now().date() + timedelta(days=3)
    emprestimos_proximos = emprestimo_repo.obter_proximas_devolucoes(data_limite)

    for emp in emprestimos_proximos:
        # Verificar se ainda faltam 3 dias
        dias_restantes = (datetime.strptime(emp['data_prevista_devolucao'], '%Y-%m-%d').date() - datetime.now().date()).days
        if dias_restantes == 3:
            notificar_devolucao_proxima(emp['id'])

    # Notificar empréstimos atrasados
    atrasados = emprestimo_repo.obter_atrasados()
    for emp in atrasados:
        notificar_emprestimo_atrasado(emp['id'])

    print(f"Notificações processadas: {len(emprestimos_proximos)} lembretes, {len(atrasados)} atrasos")
```

---

### 7.3. Métodos Adicionais nos Repositories

#### 7.3.1. Adicionar ao livro_repo.py

```python
def busca_avancada(
    titulo: str = None,
    id_autor: int = None,
    id_categoria: int = None,
    isbn: str = None,
    ano_inicio: int = None,
    ano_fim: int = None,
    editora: str = None,
    apenas_disponiveis: bool = False,
) -> list:
    """
    Busca avançada com múltiplos filtros
    """
    with get_connection() as conn:
        cursor = conn.cursor()

        query = "SELECT DISTINCT l.* FROM livro l"
        joins = []
        conditions = []
        params = []

        # Joins necessários
        if id_autor:
            joins.append("JOIN livro_autor la ON l.id = la.id_livro")
            conditions.append("la.id_autor = ?")
            params.append(id_autor)

        if id_categoria:
            joins.append("JOIN livro_categoria lc ON l.id = lc.id_livro")
            conditions.append("lc.id_categoria = ?")
            params.append(id_categoria)

        # Condições WHERE
        if titulo:
            conditions.append("(l.titulo LIKE ? OR l.subtitulo LIKE ?)")
            params.extend([f"%{titulo}%", f"%{titulo}%"])

        if isbn:
            conditions.append("l.isbn LIKE ?")
            params.append(f"%{isbn}%")

        if ano_inicio:
            conditions.append("l.ano_publicacao >= ?")
            params.append(ano_inicio)

        if ano_fim:
            conditions.append("l.ano_publicacao <= ?")
            params.append(ano_fim)

        if editora:
            conditions.append("l.editora LIKE ?")
            params.append(f"%{editora}%")

        if apenas_disponiveis:
            conditions.append("l.quantidade_disponivel > 0")

        # Montar query
        if joins:
            query += " " + " ".join(joins)

        if conditions:
            query += " WHERE " + " AND ".join(conditions)

        query += " ORDER BY l.titulo"

        cursor.execute(query, params)
        return [Livro(**dict(row)) for row in cursor.fetchall()]

def obter_por_categoria(id_categoria: int, limite: int = None) -> list[Livro]:
    """Retorna livros de uma categoria com limite opcional"""
    with get_connection() as conn:
        cursor = conn.cursor()
        query = """
            SELECT DISTINCT l.* FROM livro l
            JOIN livro_categoria lc ON l.id = lc.id_livro
            WHERE lc.id_categoria = ?
            ORDER BY l.titulo
        """
        if limite:
            query += f" LIMIT {limite}"

        cursor.execute(query, (id_categoria,))
        return [Livro(**dict(row)) for row in cursor.fetchall()]
```

#### 7.3.2. Adicionar ao usuario_repo.py

```python
import secrets
from datetime import datetime, timedelta

def gerar_token_confirmacao(id_usuario: int) -> str:
    """Gera token de confirmação de email"""
    token = secrets.token_urlsafe(32)
    data_expiracao = datetime.now() + timedelta(hours=24)

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuario
            SET token_redefinicao = ?,
                data_token = ?
            WHERE id = ?
        """, (token, data_expiracao.isoformat(), id_usuario))
        conn.commit()

    return token

def validar_token_confirmacao(token: str) -> Optional[int]:
    """Valida token de confirmação e retorna ID do usuário"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id FROM usuario
            WHERE token_redefinicao = ?
            AND datetime(data_token) > datetime('now')
        """, (token,))

        row = cursor.fetchone()
        return row[0] if row else None

def confirmar_usuario(id_usuario: int) -> bool:
    """Confirma usuário e limpa token"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE usuario
            SET confirmado = 1,
                token_redefinicao = NULL,
                data_token = NULL
            WHERE id = ?
        """, (id_usuario,))
        conn.commit()
        return cursor.rowcount > 0
```

#### 7.3.3. Adicionar ao autor_repo.py

```python
def contar_total() -> int:
    """Conta total de autores"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM autor")
        return cursor.fetchone()[0]
```

#### 7.3.4. Adicionar ao categoria_repo.py

```python
def contar_total() -> int:
    """Conta total de categorias"""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT COUNT(*) FROM categoria")
        return cursor.fetchone()[0]
```

---

### 7.4. Criar Templates Públicos

#### 7.4.1. Catálogo de Livros

📁 **Arquivo:** `templates/public/catalogo.html`

```html
{% extends "base_publica.html" %}
{% block titulo %}Catálogo de Livros{% endblock %}

{% block content %}
<div class="row">
    <div class="col-md-3">
        <!-- Filtros -->
        <div class="card mb-3">
            <div class="card-header bg-primary text-white">
                <i class="bi bi-funnel"></i> Filtros
            </div>
            <div class="card-body">
                <form method="GET">
                    <div class="mb-3">
                        <label for="busca" class="form-label">Buscar</label>
                        <input type="text" class="form-control" id="busca" name="busca"
                               placeholder="Título, ISBN..." value="{{ busca or '' }}">
                    </div>

                    <div class="mb-3">
                        <label for="categoria" class="form-label">Categoria</label>
                        <select class="form-select" id="categoria" name="categoria">
                            <option value="">Todas</option>
                            {% for cat in categorias %}
                            <option value="{{ cat.id }}" {{ 'selected' if categoria_selecionada == cat.id else '' }}>
                                {{ cat.nome }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>

                    <div class="mb-3">
                        <label for="autor" class="form-label">Autor</label>
                        <select class="form-select" id="autor" name="autor">
                            <option value="">Todos</option>
                            {% for a in autores %}
                            <option value="{{ a.id }}" {{ 'selected' if autor_selecionado == a.id else '' }}>
                                {{ a.nome }}
                            </option>
                            {% endfor %}
                        </select>
                    </div>

                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="disponivel" name="disponivel"
                                   value="true" {{ 'checked' if disponivel else '' }}>
                            <label class="form-check-label" for="disponivel">
                                Apenas disponíveis
                            </label>
                        </div>
                    </div>

                    <button type="submit" class="btn btn-primary w-100">
                        <i class="bi bi-search"></i> Filtrar
                    </button>

                    {% if busca or categoria_selecionada or autor_selecionado or disponivel %}
                    <a href="/catalogo" class="btn btn-secondary w-100 mt-2">
                        <i class="bi bi-x"></i> Limpar Filtros
                    </a>
                    {% endif %}
                </form>

                <hr>

                <a href="/catalogo/busca-avancada" class="btn btn-outline-info w-100">
                    <i class="bi bi-search"></i> Busca Avançada
                </a>
            </div>
        </div>

        <!-- Estatísticas -->
        <div class="card">
            <div class="card-header bg-secondary text-white">
                <i class="bi bi-info-circle"></i> Acervo
            </div>
            <div class="card-body">
                <p class="mb-1"><strong>Total:</strong> {{ total_livros }} livro(s)</p>
                <p class="mb-0"><strong>Página:</strong> {{ pagina_atual }} de {{ total_paginas }}</p>
            </div>
        </div>
    </div>

    <div class="col-md-9">
        <h2>Catálogo de Livros</h2>

        {% if livros %}
        <div class="row">
            {% for livro in livros %}
            <div class="col-md-4 mb-4">
                <div class="card h-100">
                    {% if livro.capa_url %}
                    <img src="{{ livro.capa_url }}" class="card-img-top" alt="{{ livro.titulo }}">
                    {% else %}
                    <div class="card-img-top bg-light d-flex align-items-center justify-content-center" style="height: 250px;">
                        <i class="bi bi-book" style="font-size: 4rem; color: #ccc;"></i>
                    </div>
                    {% endif %}

                    <div class="card-body">
                        <h6 class="card-title">{{ livro.titulo }}</h6>
                        {% if livro.subtitulo %}
                        <p class="small text-muted">{{ livro.subtitulo }}</p>
                        {% endif %}

                        <p class="small mb-2">
                            <strong>ISBN:</strong> {{ livro.isbn }}<br>
                            <strong>Ano:</strong> {{ livro.ano_publicacao }}
                        </p>

                        <span class="badge bg-{{ 'success' if livro.quantidade_disponivel > 0 else 'secondary' }}">
                            {{ livro.quantidade_disponivel }} disponível(is)
                        </span>
                    </div>

                    <div class="card-footer">
                        <a href="/catalogo/livro/{{ livro.id }}" class="btn btn-sm btn-primary w-100">
                            <i class="bi bi-eye"></i> Ver Detalhes
                        </a>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <!-- Paginação -->
        {% if total_paginas > 1 %}
        <nav>
            <ul class="pagination justify-content-center">
                <li class="page-item {{ 'disabled' if pagina_atual == 1 else '' }}">
                    <a class="page-link" href="?pagina={{ pagina_atual - 1 }}{{ '&busca=' + busca if busca else '' }}">
                        Anterior
                    </a>
                </li>

                {% for p in range(1, total_paginas + 1) %}
                <li class="page-item {{ 'active' if p == pagina_atual else '' }}">
                    <a class="page-link" href="?pagina={{ p }}{{ '&busca=' + busca if busca else '' }}">
                        {{ p }}
                    </a>
                </li>
                {% endfor %}

                <li class="page-item {{ 'disabled' if pagina_atual == total_paginas else '' }}">
                    <a class="page-link" href="?pagina={{ pagina_atual + 1 }}{{ '&busca=' + busca if busca else '' }}">
                        Próxima
                    </a>
                </li>
            </ul>
        </nav>
        {% endif %}

        {% else %}
        <div class="alert alert-info">
            <i class="bi bi-info-circle"></i> Nenhum livro encontrado com os filtros selecionados.
        </div>
        {% endif %}
    </div>
</div>
{% endblock %}
```

#### 7.4.2. Detalhes do Livro Público

📁 **Arquivo:** `templates/public/livro_detalhe.html`

```html
{% extends "base_publica.html" %}
{% block titulo %}{{ livro.titulo }}{% endblock %}

{% block content %}
<nav aria-label="breadcrumb">
    <ol class="breadcrumb">
        <li class="breadcrumb-item"><a href="/catalogo">Catálogo</a></li>
        <li class="breadcrumb-item active">{{ livro.titulo }}</li>
    </ol>
</nav>

<div class="row">
    <div class="col-md-4">
        {% if livro.capa_url %}
        <img src="{{ livro.capa_url }}" class="img-fluid rounded" alt="{{ livro.titulo }}">
        {% else %}
        <div class="bg-light rounded d-flex align-items-center justify-content-center" style="height: 400px;">
            <i class="bi bi-book" style="font-size: 8rem; color: #ccc;"></i>
        </div>
        {% endif %}

        <div class="card mt-3">
            <div class="card-body">
                <h5 class="card-title">Disponibilidade</h5>
                <p class="mb-0">
                    <span class="badge bg-{{ 'success' if livro.quantidade_disponivel > 0 else 'secondary' }} fs-6">
                        {{ livro.quantidade_disponivel }} de {{ livro.quantidade_total }} disponível(is)
                    </span>
                </p>
            </div>
        </div>
    </div>

    <div class="col-md-8">
        <h2>{{ livro.titulo }}</h2>
        {% if livro.subtitulo %}
        <h5 class="text-muted">{{ livro.subtitulo }}</h5>
        {% endif %}

        <hr>

        <div class="row mb-3">
            <div class="col-md-6">
                <p><strong>ISBN:</strong> {{ livro.isbn }}</p>
                <p><strong>Editora:</strong> {{ livro.editora }}</p>
                <p><strong>Ano:</strong> {{ livro.ano_publicacao }}</p>
            </div>
            <div class="col-md-6">
                <p><strong>Edição:</strong> {{ livro.edicao or 'N/A' }}</p>
                <p><strong>Idioma:</strong> {{ livro.idioma }}</p>
                <p><strong>Páginas:</strong> {{ livro.paginas or 'N/A' }}</p>
            </div>
        </div>

        {% if autores %}
        <p>
            <strong>Autor(es):</strong>
            {% for autor in autores %}
            <a href="/catalogo/autor/{{ autor.id }}" class="badge bg-info text-decoration-none">
                {{ autor.nome }}
            </a>
            {% endfor %}
        </p>
        {% endif %}

        {% if categorias %}
        <p>
            <strong>Categoria(s):</strong>
            {% for cat in categorias %}
            <a href="/catalogo/categoria/{{ cat.id }}" class="badge bg-secondary text-decoration-none">
                {{ cat.nome }}
            </a>
            {% endfor %}
        </p>
        {% endif %}

        {% if livro.localizacao %}
        <p><strong>Localização:</strong> {{ livro.localizacao }}</p>
        {% endif %}

        <hr>

        {% if livro.sinopse %}
        <h4>Sinopse</h4>
        <p class="text-justify">{{ livro.sinopse }}</p>
        {% endif %}

        <div class="mt-4">
            {% if livro.quantidade_disponivel > 0 %}
            <div class="alert alert-success">
                <i class="bi bi-check-circle"></i> Este livro está disponível para empréstimo!
                <a href="/catalogo/cadastro" class="alert-link">Cadastre-se</a> ou
                <a href="/login" class="alert-link">faça login</a> para reservar.
            </div>
            {% else %}
            <div class="alert alert-warning">
                <i class="bi bi-exclamation-triangle"></i> Este livro não está disponível no momento.
                <a href="/catalogo/cadastro" class="alert-link">Cadastre-se</a> para fazer uma reserva.
            </div>
            {% endif %}
        </div>
    </div>
</div>

{% if livros_relacionados %}
<div class="row mt-5">
    <div class="col-12">
        <h4>Livros Relacionados</h4>
        <hr>
    </div>

    {% for livro_rel in livros_relacionados %}
    <div class="col-md-3 mb-3">
        <div class="card h-100">
            <div class="card-body">
                <h6 class="card-title">{{ livro_rel.titulo }}</h6>
                <p class="small">{{ livro_rel.ano_publicacao }}</p>
                <a href="/catalogo/livro/{{ livro_rel.id }}" class="btn btn-sm btn-outline-primary">
                    Ver Detalhes
                </a>
            </div>
        </div>
    </div>
    {% endfor %}
</div>
{% endif %}

{% endblock %}
```

#### 7.4.3. Auto-Cadastro

📁 **Arquivo:** `templates/public/cadastro.html`

```html
{% extends "base_publica.html" %}
{% block titulo %}Cadastro{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-8">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <h4 class="mb-0"><i class="bi bi-person-plus"></i> Cadastro de Leitor</h4>
            </div>
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-12 mb-3">
                            <label for="nome" class="form-label">Nome Completo *</label>
                            <input type="text" class="form-control" id="nome" name="nome" required maxlength="200">
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="email" class="form-label">E-mail *</label>
                            <input type="email" class="form-control" id="email" name="email" required maxlength="200">
                            <div class="form-text">Será usado para login e notificações</div>
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="telefone" class="form-label">Telefone</label>
                            <input type="tel" class="form-control" id="telefone" name="telefone" maxlength="20">
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="senha" class="form-label">Senha *</label>
                            <input type="password" class="form-control" id="senha" name="senha" required minlength="8">
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="confirmar_senha" class="form-label">Confirmar Senha *</label>
                            <input type="password" class="form-control" id="confirmar_senha" name="confirmar_senha" required minlength="8">
                        </div>
                    </div>

                    <div class="mb-3">
                        <label for="data_nascimento" class="form-label">Data de Nascimento</label>
                        <input type="date" class="form-control" id="data_nascimento" name="data_nascimento">
                    </div>

                    <div class="mb-3">
                        <label for="endereco" class="form-label">Endereço</label>
                        <textarea class="form-control" id="endereco" name="endereco" rows="2"></textarea>
                    </div>

                    <div class="alert alert-info">
                        <h6>Requisitos de Senha:</h6>
                        <ul class="small mb-0">
                            <li>Mínimo de 8 caracteres</li>
                            <li>Pelo menos uma letra maiúscula</li>
                            <li>Pelo menos uma letra minúscula</li>
                            <li>Pelo menos um número</li>
                            <li>Pelo menos um caractere especial (@, #, $, etc.)</li>
                        </ul>
                    </div>

                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="bi bi-check-circle"></i> Cadastrar
                        </button>
                        <a href="/login" class="btn btn-link">
                            Já tem conta? Faça login
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### 7.4.4. Busca Avançada

📁 **Arquivo:** `templates/public/busca_avancada.html`

```html
{% extends "base_publica.html" %}
{% block titulo %}Busca Avançada{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-10">
        <h2><i class="bi bi-search"></i> Busca Avançada</h2>

        <div class="card mt-3">
            <div class="card-body">
                <form method="POST">
                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="titulo" class="form-label">Título</label>
                            <input type="text" class="form-control" id="titulo" name="titulo"
                                   placeholder="Digite parte do título...">
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="isbn" class="form-label">ISBN</label>
                            <input type="text" class="form-control" id="isbn" name="isbn"
                                   placeholder="Digite o ISBN...">
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-6 mb-3">
                            <label for="autor" class="form-label">Autor</label>
                            <select class="form-select" id="autor" name="autor">
                                <option value="">Todos os autores</option>
                                {% for a in autores %}
                                <option value="{{ a.id }}">{{ a.nome }}</option>
                                {% endfor %}
                            </select>
                        </div>

                        <div class="col-md-6 mb-3">
                            <label for="categoria" class="form-label">Categoria</label>
                            <select class="form-select" id="categoria" name="categoria">
                                <option value="">Todas as categorias</option>
                                {% for cat in categorias %}
                                <option value="{{ cat.id }}">{{ cat.nome }}</option>
                                {% endfor %}
                            </select>
                        </div>
                    </div>

                    <div class="row">
                        <div class="col-md-4 mb-3">
                            <label for="editora" class="form-label">Editora</label>
                            <input type="text" class="form-control" id="editora" name="editora"
                                   placeholder="Nome da editora...">
                        </div>

                        <div class="col-md-4 mb-3">
                            <label for="ano_inicio" class="form-label">Ano (De)</label>
                            <input type="number" class="form-control" id="ano_inicio" name="ano_inicio"
                                   min="1500" max="2100" placeholder="Ex: 2000">
                        </div>

                        <div class="col-md-4 mb-3">
                            <label for="ano_fim" class="form-label">Ano (Até)</label>
                            <input type="number" class="form-control" id="ano_fim" name="ano_fim"
                                   min="1500" max="2100" placeholder="Ex: 2024">
                        </div>
                    </div>

                    <div class="mb-3">
                        <div class="form-check">
                            <input class="form-check-input" type="checkbox" id="apenas_disponiveis"
                                   name="apenas_disponiveis" value="true">
                            <label class="form-check-label" for="apenas_disponiveis">
                                Mostrar apenas livros disponíveis
                            </label>
                        </div>
                    </div>

                    <div class="d-grid gap-2">
                        <button type="submit" class="btn btn-primary btn-lg">
                            <i class="bi bi-search"></i> Buscar
                        </button>
                        <a href="/catalogo" class="btn btn-secondary">
                            <i class="bi bi-arrow-left"></i> Voltar ao Catálogo
                        </a>
                    </div>
                </form>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

#### 7.4.5. Página Sobre

📁 **Arquivo:** `templates/public/sobre.html`

```html
{% extends "base_publica.html" %}
{% block titulo %}Sobre{% endblock %}

{% block content %}
<h2>Sobre a Biblix</h2>

<div class="row mt-4">
    <div class="col-md-8">
        <p class="lead">
            A Biblix é um sistema moderno de gestão de bibliotecas, desenvolvido para
            facilitar o acesso ao conhecimento e promover a leitura.
        </p>

        <h4 class="mt-4">Nossa Missão</h4>
        <p>
            Proporcionar acesso fácil e organizado ao acervo bibliográfico,
            incentivando a leitura e o aprendizado contínuo.
        </p>

        <h4 class="mt-4">Funcionalidades</h4>
        <ul>
            <li>Catálogo online completo</li>
            <li>Sistema de reservas</li>
            <li>Renovação de empréstimos</li>
            <li>Notificações por e-mail</li>
            <li>Busca avançada</li>
            <li>Lista de favoritos</li>
        </ul>

        <h4 class="mt-4">Horário de Funcionamento</h4>
        <p>
            Segunda a Sexta: 8h às 18h<br>
            Sábado: 8h às 12h
        </p>
    </div>

    <div class="col-md-4">
        <div class="card">
            <div class="card-header bg-primary text-white">
                <i class="bi bi-bar-chart"></i> Estatísticas do Acervo
            </div>
            <div class="card-body">
                <p><strong>Livros Cadastrados:</strong> {{ stats.total_livros }}</p>
                <p><strong>Total de Exemplares:</strong> {{ stats.total_exemplares }}</p>
                <p><strong>Autores:</strong> {{ stats.total_autores }}</p>
                <p><strong>Categorias:</strong> {{ stats.total_categorias }}</p>
            </div>
        </div>

        <div class="card mt-3">
            <div class="card-header bg-success text-white">
                <i class="bi bi-person-plus"></i> Seja um Leitor
            </div>
            <div class="card-body">
                <p>Cadastre-se gratuitamente e aproveite todos os benefícios!</p>
                <a href="/catalogo/cadastro" class="btn btn-success w-100">
                    Cadastrar
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

### 7.5. Registrar Rotas no main.py

📝 **Arquivo:** `main.py`

**Adicionar import:**

```python
from routes import public_routes
```

**Adicionar no final da seção de routers:**

```python
app.include_router(public_routes.router)
logger.info("Router público incluído")
```

**Adicionar rota raiz para redirecionar ao catálogo:**

```python
@app.get("/")
async def root():
    """Redireciona para o catálogo público"""
    return RedirectResponse("/catalogo")
```

---

### 7.6. Configurar Agendador de Notificações (Opcional)

📁 **Arquivo:** `util/scheduler.py`

```python
import schedule
import time
import threading
from util.notificacao_util import processar_notificacoes_diarias

def executar_agendador():
    """Executa o agendador em thread separada"""
    # Agendar para rodar todo dia às 9h
    schedule.every().day.at("09:00").do(processar_notificacoes_diarias)

    while True:
        schedule.run_pending()
        time.sleep(60)  # Verificar a cada minuto

def iniciar_agendador():
    """Inicia o agendador em background"""
    thread = threading.Thread(target=executar_agendador, daemon=True)
    thread.start()
    print("Agendador de notificações iniciado")
```

**Adicionar ao main.py:**

```python
from util.scheduler import iniciar_agendador

# No startup do app
@app.on_event("startup")
async def startup_event():
    logger.info("Aplicação iniciada")
    iniciar_agendador()  # Iniciar agendador de notificações
```

---

### 7.7. Testar Sprint 5

#### Como Testar:

1. **Executar aplicação:**
   ```bash
   python main.py
   ```

2. **Testar Área Pública:**
   - ✅ Acessar `/` (redireciona para `/catalogo`)
   - ✅ Acessar `/catalogo`
   - ✅ Ver listagem de livros
   - ✅ Filtrar por categoria
   - ✅ Filtrar por autor
   - ✅ Buscar por título
   - ✅ Filtrar apenas disponíveis
   - ✅ Testar paginação
   - ✅ Ver detalhes de um livro
   - ✅ Ver página de autor
   - ✅ Ver página de categoria
   - ✅ Acessar `/catalogo/sobre`

3. **Testar Busca Avançada:**
   - ✅ Acessar `/catalogo/busca-avancada`
   - ✅ Buscar por título
   - ✅ Buscar por ISBN
   - ✅ Filtrar por ano
   - ✅ Filtrar por editora
   - ✅ Combinar múltiplos filtros

4. **Testar Auto-Cadastro:**
   - ✅ Acessar `/catalogo/cadastro`
   - ✅ Preencher formulário
   - ✅ Validar senha forte
   - ✅ Validar confirmação de senha
   - ✅ Verificar email de confirmação
   - ✅ Clicar no link de confirmação
   - ✅ Fazer login após confirmação

5. **Testar Notificações:**
   - ✅ Registrar empréstimo (deve enviar email)
   - ✅ Verificar notificações diárias
   - ✅ Testar lembrete de devolução
   - ✅ Testar notificação de atraso

---

### 7.8. Checklist Sprint 5

- [ ] public_routes.py criado com 10+ endpoints
- [ ] Catálogo público implementado
- [ ] Sistema de paginação funcionando
- [ ] Filtros de busca (categoria, autor, disponibilidade)
- [ ] Página de detalhes do livro
- [ ] Páginas de autor e categoria
- [ ] Sistema de busca avançada
- [ ] Método busca_avancada() em livro_repo.py
- [ ] Auto-cadastro de leitores
- [ ] Sistema de confirmação por email
- [ ] Métodos de token em usuario_repo.py
- [ ] notificacao_util.py implementado
- [ ] 6 tipos de notificações por email
- [ ] Templates públicos criados (catálogo, detalhe, cadastro, busca)
- [ ] Template de sobre
- [ ] Router público registrado no main.py
- [ ] Rota raiz (/) redirecionando
- [ ] Agendador de notificações (opcional)
- [ ] Testado catálogo completo
- [ ] Testados todos os filtros
- [ ] Testada paginação
- [ ] Testada busca avançada
- [ ] Testado auto-cadastro
- [ ] Testada confirmação de email
- [ ] Testadas notificações

---

## 8. SPRINT 6: QUALIDADE E TESTES

**Duração estimada:** 30 horas

**Objetivo:** Garantir qualidade do código através de testes automatizados, documentação completa e otimizações de performance.

**Entregas:**
- ✅ Suite de testes unitários
- ✅ Testes de integração
- ✅ Testes end-to-end (E2E)
- ✅ Documentação técnica completa
- ✅ Otimizações de performance
- ✅ Configuração de CI/CD
- ✅ Guia de deploy

---

### 8.1. Configurar Ambiente de Testes

📁 **Arquivo:** `pytest.ini`

```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts =
    -v
    --tb=short
    --strict-markers
    --cov=.
    --cov-report=html
    --cov-report=term-missing
markers =
    unit: Testes unitários
    integration: Testes de integração
    e2e: Testes end-to-end
    slow: Testes lentos
```

📁 **Arquivo:** `requirements-dev.txt`

```txt
pytest==7.4.3
pytest-cov==4.1.0
pytest-asyncio==0.21.1
httpx==0.25.1
faker==20.0.3
freezegun==1.4.0
```

**Instalar dependências:**

```bash
pip install -r requirements-dev.txt
```

---

### 8.2. Testes Unitários

#### 8.2.1. Testes de Models

📁 **Arquivo:** `tests/test_models.py`

```python
import pytest
from model.usuario_model import Usuario
from model.livro_model import Livro
from model.emprestimo_model import Emprestimo
from util.perfis import Perfil

class TestUsuario:
    def test_criar_usuario_valido(self):
        """Testa criação de usuário com dados válidos"""
        usuario = Usuario(
            id=1,
            nome="João Silva",
            email="joao@example.com",
            senha="hash_senha",
            perfil=Perfil.LEITOR.value
        )

        assert usuario.id == 1
        assert usuario.nome == "João Silva"
        assert usuario.email == "joao@example.com"
        assert usuario.perfil == Perfil.LEITOR.value

    def test_perfil_enum_valores(self):
        """Testa valores do enum Perfil"""
        assert Perfil.ADMIN.value == "Administrador"
        assert Perfil.BIBLIOTECARIO.value == "Bibliotecário"
        assert Perfil.LEITOR.value == "Leitor"

    def test_perfil_validacao(self):
        """Testa validação de perfil"""
        assert Perfil.existe(Perfil.LEITOR.value)
        assert not Perfil.existe("perfil_invalido")

class TestLivro:
    def test_criar_livro_valido(self):
        """Testa criação de livro com dados válidos"""
        livro = Livro(
            id=1,
            titulo="Clean Code",
            isbn="978-0132350884",
            editora="Pearson",
            ano_publicacao=2008,
            idioma="Inglês",
            quantidade_total=5,
            quantidade_disponivel=3
        )

        assert livro.titulo == "Clean Code"
        assert livro.isbn == "978-0132350884"
        assert livro.quantidade_total == 5
        assert livro.quantidade_disponivel == 3

    def test_disponibilidade(self):
        """Testa lógica de disponibilidade"""
        livro = Livro(
            id=1,
            titulo="Test",
            isbn="123",
            editora="Test",
            ano_publicacao=2020,
            idioma="PT",
            quantidade_total=5,
            quantidade_disponivel=0
        )

        assert livro.quantidade_disponivel == 0
        assert livro.quantidade_total > livro.quantidade_disponivel
```

#### 8.2.2. Testes de Validators

📁 **Arquivo:** `tests/test_validators.py`

```python
import pytest
from util.validators import validate_email, validate_password, validate_isbn

class TestValidators:
    def test_email_valido(self):
        """Testa validação de emails válidos"""
        assert validate_email("usuario@example.com")
        assert validate_email("nome.sobrenome@domain.com.br")
        assert validate_email("test+filter@gmail.com")

    def test_email_invalido(self):
        """Testa validação de emails inválidos"""
        assert not validate_email("invalido")
        assert not validate_email("@example.com")
        assert not validate_email("usuario@")
        assert not validate_email("")

    def test_senha_valida(self):
        """Testa validação de senhas válidas"""
        assert validate_password("Senha@123")
        assert validate_password("Test#2024")
        assert validate_password("MyP@ssw0rd")

    def test_senha_invalida(self):
        """Testa validação de senhas inválidas"""
        assert not validate_password("senha")  # Sem maiúscula, número, especial
        assert not validate_password("SENHA123")  # Sem minúscula, especial
        assert not validate_password("Senha123")  # Sem especial
        assert not validate_password("Senha@")  # Sem número
        assert not validate_password("Sen@1")  # Menos de 8 caracteres

    def test_isbn_valido(self):
        """Testa validação de ISBN"""
        assert validate_isbn("978-0132350884")
        assert validate_isbn("9780132350884")
        assert validate_isbn("0-306-40615-2")

    def test_isbn_invalido(self):
        """Testa validação de ISBN inválido"""
        assert not validate_isbn("123")
        assert not validate_isbn("abc-def-ghi")
        assert not validate_isbn("")
```

#### 8.2.3. Testes de Repositories

📁 **Arquivo:** `tests/test_repositories.py`

```python
import pytest
import os
from datetime import datetime
from model.usuario_model import Usuario
from model.livro_model import Livro
import repo.usuario_repo as usuario_repo
import repo.livro_repo as livro_repo
from util.perfis import Perfil
from util.security import hash_password

# Fixture para banco de dados de teste
@pytest.fixture
def setup_test_db():
    """Cria banco de dados de teste"""
    # Usar banco de teste
    test_db = "test_database.db"

    # Criar banco
    from util.database import criar_banco
    criar_banco(test_db)

    yield test_db

    # Limpar após teste
    if os.path.exists(test_db):
        os.remove(test_db)

class TestUsuarioRepo:
    def test_inserir_usuario(self, setup_test_db):
        """Testa inserção de usuário"""
        from dtos.usuario_dto import UsuarioDTO

        usuario_dto = UsuarioDTO(
            nome="Test User",
            email="test@example.com",
            senha=hash_password("Test@123"),
            perfil=Perfil.LEITOR.value
        )

        usuario_id = usuario_repo.inserir(usuario_dto)

        assert usuario_id is not None
        assert usuario_id > 0

    def test_obter_por_email(self, setup_test_db):
        """Testa busca por email"""
        from dtos.usuario_dto import UsuarioDTO

        # Inserir usuário
        usuario_dto = UsuarioDTO(
            nome="Test User",
            email="find@example.com",
            senha=hash_password("Test@123"),
            perfil=Perfil.LEITOR.value
        )
        usuario_repo.inserir(usuario_dto)

        # Buscar
        usuario = usuario_repo.obter_por_email("find@example.com")

        assert usuario is not None
        assert usuario.email == "find@example.com"
        assert usuario.nome == "Test User"

    def test_atualizar_usuario(self, setup_test_db):
        """Testa atualização de usuário"""
        from dtos.usuario_dto import UsuarioDTO

        # Inserir
        usuario_dto = UsuarioDTO(
            nome="Original",
            email="update@example.com",
            senha=hash_password("Test@123"),
            perfil=Perfil.LEITOR.value
        )
        usuario_id = usuario_repo.inserir(usuario_dto)

        # Atualizar
        usuario_dto.id = usuario_id
        usuario_dto.nome = "Atualizado"
        sucesso = usuario_repo.atualizar(usuario_dto)

        assert sucesso

        # Verificar
        usuario = usuario_repo.obter_por_id(usuario_id)
        assert usuario.nome == "Atualizado"

class TestLivroRepo:
    def test_inserir_livro(self, setup_test_db):
        """Testa inserção de livro"""
        from dtos.livro_dto import LivroDTO

        livro_dto = LivroDTO(
            titulo="Test Book",
            isbn="978-0000000000",
            editora="Test Publisher",
            ano_publicacao=2024,
            idioma="Português",
            quantidade_total=10,
            quantidade_disponivel=10
        )

        livro_id = livro_repo.inserir(livro_dto)

        assert livro_id is not None
        assert livro_id > 0

    def test_buscar_livros(self, setup_test_db):
        """Testa busca de livros"""
        from dtos.livro_dto import LivroDTO

        # Inserir livros
        livro_dto = LivroDTO(
            titulo="Python Programming",
            isbn="978-1111111111",
            editora="Tech Books",
            ano_publicacao=2023,
            idioma="Português",
            quantidade_total=5,
            quantidade_disponivel=5
        )
        livro_repo.inserir(livro_dto)

        # Buscar
        resultados = livro_repo.buscar("Python")

        assert len(resultados) > 0
        assert "Python" in resultados[0].titulo
```

---

### 8.3. Testes de Integração

📁 **Arquivo:** `tests/test_integration.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from util.perfis import Perfil

client = TestClient(app)

class TestPublicRoutes:
    def test_catalogo_publico(self):
        """Testa acesso ao catálogo público"""
        response = client.get("/catalogo")
        assert response.status_code == 200
        assert "Catálogo" in response.text

    def test_detalhes_livro_publico(self):
        """Testa visualização de detalhes do livro"""
        # Assumindo que existe livro com ID 1
        response = client.get("/catalogo/livro/1")
        # Pode retornar 200 (se existir) ou redirect (se não existir)
        assert response.status_code in [200, 303]

    def test_pagina_cadastro(self):
        """Testa página de cadastro"""
        response = client.get("/catalogo/cadastro")
        assert response.status_code == 200
        assert "Cadastro" in response.text

class TestAuthRoutes:
    def test_login_page(self):
        """Testa página de login"""
        response = client.get("/login")
        assert response.status_code == 200

    def test_login_invalido(self):
        """Testa login com credenciais inválidas"""
        response = client.post("/login", data={
            "email": "invalido@example.com",
            "senha": "senhaerrada"
        })
        assert response.status_code == 303  # Redirect

    def test_acesso_sem_autenticacao(self):
        """Testa acesso a rota protegida sem autenticação"""
        response = client.get("/leitor/dashboard")
        assert response.status_code == 303  # Redirect para login

class TestAPIEndpoints:
    def test_busca_avancada(self):
        """Testa busca avançada"""
        response = client.get("/catalogo/busca-avancada")
        assert response.status_code == 200

    def test_sobre_page(self):
        """Testa página sobre"""
        response = client.get("/catalogo/sobre")
        assert response.status_code == 200
        assert "Biblix" in response.text
```

---

### 8.4. Testes End-to-End

📁 **Arquivo:** `tests/test_e2e.py`

```python
import pytest
from fastapi.testclient import TestClient
from main import app
from util.security import hash_password
import repo.usuario_repo as usuario_repo
from dtos.usuario_dto import UsuarioDTO
from util.perfis import Perfil

client = TestClient(app)

@pytest.mark.e2e
class TestFluxoCompleto:
    def test_fluxo_cadastro_e_login(self):
        """Testa fluxo completo de cadastro e login"""

        # 1. Acessar página de cadastro
        response = client.get("/catalogo/cadastro")
        assert response.status_code == 200

        # 2. Cadastrar novo usuário
        response = client.post("/catalogo/cadastro", data={
            "nome": "E2E Test User",
            "email": "e2e@example.com",
            "senha": "Test@123456",
            "confirmar_senha": "Test@123456",
        }, follow_redirects=False)

        assert response.status_code == 303  # Redirect

        # 3. Confirmar email (simular)
        usuario = usuario_repo.obter_por_email("e2e@example.com")
        if usuario:
            usuario_repo.confirmar_usuario(usuario.id)

        # 4. Fazer login
        response = client.post("/login", data={
            "email": "e2e@example.com",
            "senha": "Test@123456"
        })

        assert response.status_code == 303

    @pytest.mark.slow
    def test_fluxo_emprestimo_completo(self):
        """Testa fluxo completo de empréstimo"""

        # Este teste requer:
        # 1. Usuário bibliotecário autenticado
        # 2. Livro cadastrado
        # 3. Leitor cadastrado
        # 4. Registrar empréstimo
        # 5. Verificar empréstimo foi criado
        # 6. Registrar devolução

        # Implementar com setup fixtures apropriados
        pass
```

---

### 8.5. Documentação Técnica

#### 8.5.1. README Técnico

📁 **Arquivo:** `docs/README_TECNICO.md`

```markdown
# Biblix - Documentação Técnica

## Arquitetura do Sistema

### Stack Tecnológica
- **Backend:** Python 3.12 + FastAPI
- **Template Engine:** Jinja2
- **Banco de Dados:** SQLite (desenvolvimento) / PostgreSQL (produção)
- **Frontend:** Bootstrap 5, HTML5, CSS3
- **Testes:** Pytest

### Estrutura do Projeto

```
Biblix/
├── model/              # Modelos de dados (dataclasses)
├── repo/               # Camada de acesso a dados (repositories)
├── routes/             # Rotas FastAPI (controllers)
├── templates/          # Templates Jinja2
├── static/             # Arquivos estáticos (CSS, JS, imagens)
├── util/               # Utilitários (validadores, email, etc)
├── dtos/               # Data Transfer Objects
├── sql/                # Scripts SQL
├── tests/              # Testes automatizados
├── backups/            # Backups do banco de dados
└── main.py             # Ponto de entrada da aplicação
```

## Padrões de Código

### Model-Repository-Route Pattern

1. **Models:** Definem estrutura dos dados
2. **Repositories:** Gerenciam acesso ao banco
3. **Routes:** Controlam lógica de negócio e rotas HTTP

### Exemplo de Fluxo

```
Cliente HTTP → Route → Repository → Database
                ↓
            Template ← Route
```

## Banco de Dados

### Tabelas Principais
- `usuario` - Usuários do sistema
- `livro` - Catálogo de livros
- `autor` - Autores
- `categoria` - Categorias
- `emprestimo` - Registro de empréstimos
- `reserva` - Fila de reservas
- `favorito` - Livros favoritos dos leitores
- `mensagem` - Sistema de mensagens internas

### Relacionamentos
- Livro N:N Autor (livro_autor)
- Livro N:N Categoria (livro_categoria)
- Empréstimo N:1 Livro
- Empréstimo N:1 Leitor (Usuario)
- Empréstimo N:1 Bibliotecário (Usuario)

## Sistema de Autenticação

### Perfis de Usuário
1. **Administrador** - Acesso total
2. **Bibliotecário** - Gestão de acervo e empréstimos
3. **Leitor** - Área pessoal e reservas

### Decorador de Autenticação

```python
@auth_decorator(perfil_necessario=Perfil.LEITOR.value)
async def rota_protegida(request: Request):
    # Apenas leitores (ou perfis superiores) podem acessar
    pass
```

## Sistema de Notificações

### Tipos de Notificação
- Empréstimo registrado
- Devolução próxima (3 dias antes)
- Empréstimo atrasado
- Reserva disponível
- Nova mensagem

### Agendamento
- Execução diária às 9h
- Processa lembretes e notificações

## Deploy

### Desenvolvimento

```bash
python -m venv venv
source venv/bin/activate  # Linux/Mac
venv\Scripts\activate     # Windows
pip install -r requirements.txt
python main.py
```

### Produção

```bash
# Com Gunicorn
gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 0.0.0.0:8000

# Com Docker
docker build -t biblix .
docker run -p 8000:8000 biblix
```

## Variáveis de Ambiente

```env
DATABASE_URL=sqlite:///database.db
SECRET_KEY=sua_chave_secreta
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha
```

## Testes

```bash
# Todos os testes
pytest

# Apenas testes unitários
pytest -m unit

# Com cobertura
pytest --cov=. --cov-report=html
```

## Troubleshooting

### Erro: Banco de dados bloqueado
**Solução:** SQLite não suporta alta concorrência. Migrar para PostgreSQL em produção.

### Erro: Email não enviado
**Solução:** Verificar credenciais SMTP e configuração de "apps menos seguros" no Gmail.

### Erro: Permissões de arquivo
**Solução:** Verificar permissões da pasta `backups/` e `static/img/usuarios/`.
```

#### 8.5.2. Guia de API

📁 **Arquivo:** `docs/API.md`

```markdown
# Biblix - Guia de API

## Endpoints Públicos

### Catálogo

#### Listar Livros
```http
GET /catalogo?pagina=1&categoria=5&disponivel=true
```

**Query Parameters:**
- `pagina` (int): Número da página (padrão: 1)
- `categoria` (int): Filtrar por categoria
- `autor` (int): Filtrar por autor
- `busca` (string): Buscar por título
- `disponivel` (bool): Apenas livros disponíveis

**Response:** HTML template

#### Detalhes do Livro
```http
GET /catalogo/livro/{id}
```

**Path Parameters:**
- `id` (int): ID do livro

**Response:** HTML template com detalhes do livro

### Auto-Cadastro

#### Registrar Leitor
```http
POST /catalogo/cadastro
```

**Form Data:**
- `nome` (string, required)
- `email` (string, required)
- `senha` (string, required)
- `confirmar_senha` (string, required)
- `telefone` (string, optional)
- `endereco` (string, optional)
- `data_nascimento` (date, optional)

**Response:** Redirect para /login

## Endpoints Autenticados

### Área do Leitor

#### Dashboard
```http
GET /leitor/dashboard
```

**Auth:** Perfil LEITOR ou superior
**Response:** HTML template com dashboard

#### Empréstimos
```http
GET /leitor/emprestimos
```

**Auth:** Perfil LEITOR ou superior
**Response:** Lista de empréstimos do leitor

#### Criar Reserva
```http
POST /leitor/reservar/{id_livro}
```

**Auth:** Perfil LEITOR ou superior
**Path Parameters:**
- `id_livro` (int): ID do livro a reservar

**Response:** Redirect

### Área do Bibliotecário

#### Registrar Empréstimo
```http
POST /bibliotecario/emprestimos/novo
```

**Auth:** Perfil BIBLIOTECARIO ou superior

**Form Data:**
- `id_livro` (int, required)
- `id_leitor` (int, required)
- `prazo_dias` (int, default: 14)
- `observacoes` (string, optional)

**Response:** Redirect

#### Registrar Devolução
```http
POST /bibliotecario/emprestimos/{id}/devolver
```

**Auth:** Perfil BIBLIOTECARIO ou superior

**Form Data:**
- `observacoes_devolucao` (string, optional)

**Response:** Redirect

### Área Administrativa

#### Criar Backup
```http
POST /admin/backup/criar
```

**Auth:** Perfil ADMIN
**Response:** Redirect com mensagem de sucesso

#### Restaurar Backup
```http
POST /admin/backup/restore/{nome_arquivo}
```

**Auth:** Perfil ADMIN
**Path Parameters:**
- `nome_arquivo` (string): Nome do arquivo de backup

**Response:** Redirect

## Códigos de Status

- `200 OK` - Sucesso
- `303 See Other` - Redirect após POST
- `400 Bad Request` - Dados inválidos
- `401 Unauthorized` - Não autenticado
- `403 Forbidden` - Sem permissão
- `404 Not Found` - Recurso não encontrado
- `500 Internal Server Error` - Erro do servidor
```

---

### 8.6. Otimizações de Performance

#### 8.6.1. Índices do Banco de Dados

📁 **Arquivo:** `sql/indices.sql`

```sql
-- Índices para melhorar performance de consultas

-- Usuários
CREATE INDEX IF NOT EXISTS idx_usuario_email ON usuario(email);
CREATE INDEX IF NOT EXISTS idx_usuario_perfil ON usuario(perfil);

-- Livros
CREATE INDEX IF NOT EXISTS idx_livro_isbn ON livro(isbn);
CREATE INDEX IF NOT EXISTS idx_livro_titulo ON livro(titulo);
CREATE INDEX IF NOT EXISTS idx_livro_ano ON livro(ano_publicacao);
CREATE INDEX IF NOT EXISTS idx_livro_disponibilidade ON livro(quantidade_disponivel);

-- Empréstimos
CREATE INDEX IF NOT EXISTS idx_emprestimo_status ON emprestimo(status);
CREATE INDEX IF NOT EXISTS idx_emprestimo_leitor ON emprestimo(id_leitor);
CREATE INDEX IF NOT EXISTS idx_emprestimo_livro ON emprestimo(id_livro);
CREATE INDEX IF NOT EXISTS idx_emprestimo_data ON emprestimo(data_emprestimo);
CREATE INDEX IF NOT EXISTS idx_emprestimo_devolucao ON emprestimo(data_prevista_devolucao);

-- Reservas
CREATE INDEX IF NOT EXISTS idx_reserva_status ON reserva(status);
CREATE INDEX IF NOT EXISTS idx_reserva_leitor ON reserva(id_leitor);
CREATE INDEX IF NOT EXISTS idx_reserva_livro ON reserva(id_livro);

-- Relacionamentos N:N
CREATE INDEX IF NOT EXISTS idx_livro_autor_livro ON livro_autor(id_livro);
CREATE INDEX IF NOT EXISTS idx_livro_autor_autor ON livro_autor(id_autor);
CREATE INDEX IF NOT EXISTS idx_livro_categoria_livro ON livro_categoria(id_livro);
CREATE INDEX IF NOT EXISTS idx_livro_categoria_categoria ON livro_categoria(id_categoria);
```

#### 8.6.2. Cache de Consultas

📁 **Arquivo:** `util/cache.py`

```python
from functools import lru_cache
from datetime import datetime, timedelta

# Cache simples em memória (para desenvolvimento)
_cache = {}
_cache_timeout = {}

def cache_set(key: str, value, timeout_seconds: int = 300):
    """Define valor no cache com timeout"""
    _cache[key] = value
    _cache_timeout[key] = datetime.now() + timedelta(seconds=timeout_seconds)

def cache_get(key: str):
    """Obtém valor do cache se ainda válido"""
    if key in _cache:
        if datetime.now() < _cache_timeout[key]:
            return _cache[key]
        else:
            # Expirou, remover
            del _cache[key]
            del _cache_timeout[key]
    return None

def cache_clear():
    """Limpa todo o cache"""
    _cache.clear()
    _cache_timeout.clear()

# Uso com decorator
@lru_cache(maxsize=128)
def obter_categorias_cached():
    """Cache de categorias que mudam pouco"""
    import repo.categoria_repo as categoria_repo
    return categoria_repo.obter_todos()
```

---

### 8.7. Configuração de CI/CD

#### 8.7.1. GitHub Actions

📁 **Arquivo:** `.github/workflows/tests.yml`

```yaml
name: Tests

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
    - uses: actions/checkout@v3

    - name: Set up Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.12'

    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install -r requirements-dev.txt

    - name: Run tests
      run: |
        pytest --cov=. --cov-report=xml

    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
```

#### 8.7.2. Docker

📁 **Arquivo:** `Dockerfile`

```dockerfile
FROM python:3.12-slim

WORKDIR /app

# Instalar dependências do sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar requirements
COPY requirements.txt .

# Instalar dependências Python
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY . .

# Criar diretórios necessários
RUN mkdir -p backups static/img/usuarios logs

# Expor porta
EXPOSE 8000

# Comando de inicialização
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

📁 **Arquivo:** `docker-compose.yml`

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    volumes:
      - ./database.db:/app/database.db
      - ./backups:/app/backups
      - ./static:/app/static
    environment:
      - DATABASE_URL=sqlite:///database.db
      - SECRET_KEY=${SECRET_KEY}
      - EMAIL_HOST=${EMAIL_HOST}
      - EMAIL_PORT=${EMAIL_PORT}
      - EMAIL_USER=${EMAIL_USER}
      - EMAIL_PASS=${EMAIL_PASS}
    restart: unless-stopped

  # Opcional: PostgreSQL para produção
  postgres:
    image: postgres:15
    environment:
      - POSTGRES_DB=biblix
      - POSTGRES_USER=biblix
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
```

---

### 8.8. Guia de Deploy

📁 **Arquivo:** `docs/DEPLOY.md`

```markdown
# Guia de Deploy - Biblix

## Pré-requisitos

- Python 3.12+
- Servidor Linux (Ubuntu 22.04 recomendado)
- Nginx (para proxy reverso)
- Supervisor (para gerenciar processo)

## Passo 1: Preparar Servidor

```bash
# Atualizar sistema
sudo apt update && sudo apt upgrade -y

# Instalar Python e dependências
sudo apt install python3.12 python3.12-venv python3-pip nginx supervisor -y
```

## Passo 2: Clonar Projeto

```bash
cd /var/www
sudo git clone https://github.com/seu-usuario/biblix.git
cd biblix
```

## Passo 3: Configurar Ambiente Virtual

```bash
python3.12 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Passo 4: Configurar Variáveis de Ambiente

```bash
# Criar arquivo .env
sudo nano .env
```

```env
DATABASE_URL=sqlite:///database.db
SECRET_KEY=sua_chave_super_secreta_aqui
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USER=seu_email@gmail.com
EMAIL_PASS=sua_senha_app
```

## Passo 5: Inicializar Banco de Dados

```bash
python main.py  # Executa uma vez para criar o banco
```

## Passo 6: Configurar Supervisor

```bash
sudo nano /etc/supervisor/conf.d/biblix.conf
```

```ini
[program:biblix]
directory=/var/www/biblix
command=/var/www/biblix/venv/bin/gunicorn -w 4 -k uvicorn.workers.UvicornWorker main:app --bind 127.0.0.1:8000
user=www-data
autostart=true
autorestart=true
stderr_logfile=/var/log/biblix.err.log
stdout_logfile=/var/log/biblix.out.log
```

```bash
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start biblix
```

## Passo 7: Configurar Nginx

```bash
sudo nano /etc/nginx/sites-available/biblix
```

```nginx
server {
    listen 80;
    server_name seu-dominio.com;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    location /static {
        alias /var/www/biblix/static;
    }
}
```

```bash
sudo ln -s /etc/nginx/sites-available/biblix /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## Passo 8: Configurar SSL (Opcional)

```bash
sudo apt install certbot python3-certbot-nginx -y
sudo certbot --nginx -d seu-dominio.com
```

## Passo 9: Configurar Backup Automático

```bash
sudo nano /etc/cron.daily/biblix-backup
```

```bash
#!/bin/bash
cd /var/www/biblix
source venv/bin/activate
python -c "from util.backup import criar_backup; criar_backup()"
```

```bash
sudo chmod +x /etc/cron.daily/biblix-backup
```

## Manutenção

### Atualizar Aplicação

```bash
cd /var/www/biblix
git pull origin main
source venv/bin/activate
pip install -r requirements.txt
sudo supervisorctl restart biblix
```

### Ver Logs

```bash
# Logs da aplicação
tail -f /var/log/biblix.out.log

# Logs do Nginx
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# Logs do Supervisor
sudo supervisorctl tail -f biblix
```

### Backup Manual

```bash
cd /var/www/biblix
source venv/bin/activate
python -c "from util.backup import criar_backup; criar_backup()"
```
```

---

### 8.9. Checklist de Qualidade

📁 **Arquivo:** `docs/CHECKLIST_QUALIDADE.md`

```markdown
# Checklist de Qualidade - Biblix

## Código

- [ ] Todos os arquivos têm docstrings
- [ ] Variáveis têm nomes descritivos
- [ ] Sem código duplicado
- [ ] Sem imports não utilizados
- [ ] Sem variáveis não utilizadas
- [ ] Type hints em funções críticas
- [ ] Tratamento de erros adequado
- [ ] Logs em operações importantes

## Testes

- [ ] Cobertura de testes > 80%
- [ ] Testes unitários para models
- [ ] Testes unitários para validators
- [ ] Testes unitários para repositories
- [ ] Testes de integração para routes
- [ ] Testes E2E para fluxos principais
- [ ] Todos os testes passando
- [ ] Testes executam em menos de 30s

## Segurança

- [ ] Senhas hasheadas (bcrypt/argon2)
- [ ] Proteção contra SQL Injection
- [ ] Proteção contra XSS
- [ ] Proteção contra CSRF
- [ ] Validação de inputs
- [ ] Rate limiting em rotas críticas
- [ ] HTTPS configurado (produção)
- [ ] Headers de segurança configurados

## Performance

- [ ] Índices criados no banco de dados
- [ ] Queries otimizadas (sem N+1)
- [ ] Paginação implementada
- [ ] Cache em queries pesadas
- [ ] Imagens otimizadas
- [ ] CSS/JS minificados (produção)
- [ ] Lazy loading de imagens
- [ ] Response time < 200ms

## UX/UI

- [ ] Responsivo (mobile, tablet, desktop)
- [ ] Mensagens de erro claras
- [ ] Feedback visual em ações
- [ ] Loading states
- [ ] Validação client-side
- [ ] Acessibilidade (ARIA labels)
- [ ] Contraste adequado
- [ ] Fontes legíveis

## Documentação

- [ ] README completo
- [ ] Documentação técnica
- [ ] Guia de API
- [ ] Guia de deploy
- [ ] Comentários em código complexo
- [ ] Diagramas de arquitetura
- [ ] Changelog atualizado

## Deploy

- [ ] Variáveis de ambiente configuradas
- [ ] Banco de dados migrado
- [ ] Backups automáticos configurados
- [ ] Logs configurados
- [ ] Monitoramento configurado
- [ ] SSL/TLS configurado
- [ ] Firewall configurado
- [ ] Processo de rollback documentado

## Compliance

- [ ] LGPD - Política de privacidade
- [ ] LGPD - Termo de uso
- [ ] LGPD - Consentimento explícito
- [ ] LGPD - Direito ao esquecimento
- [ ] Licença do projeto definida
```

---

### 8.10. Executar Suite de Testes

```bash
# Instalar dependências de teste
pip install -r requirements-dev.txt

# Executar todos os testes
pytest

# Executar com cobertura
pytest --cov=. --cov-report=html

# Executar apenas testes unitários
pytest -m unit

# Executar apenas testes de integração
pytest -m integration

# Executar testes específicos
pytest tests/test_validators.py

# Ver relatório de cobertura
open htmlcov/index.html  # Mac/Linux
start htmlcov/index.html # Windows
```

---

### 8.11. Checklist Sprint 6

- [ ] pytest.ini configurado
- [ ] requirements-dev.txt criado
- [ ] Testes unitários de models
- [ ] Testes unitários de validators
- [ ] Testes unitários de repositories
- [ ] Testes de integração de routes
- [ ] Testes E2E de fluxos principais
- [ ] Cobertura de testes > 80%
- [ ] README_TECNICO.md criado
- [ ] API.md documentado
- [ ] Índices de banco criados (indices.sql)
- [ ] Sistema de cache implementado
- [ ] GitHub Actions configurado
- [ ] Dockerfile criado
- [ ] docker-compose.yml criado
- [ ] DEPLOY.md documentado
- [ ] CHECKLIST_QUALIDADE.md criado
- [ ] Todos os testes passando
- [ ] Performance otimizada
- [ ] Documentação completa
- [ ] Pronto para produção

---

## 🎉 CONCLUSÃO DO PROJETO

Parabéns! Você completou todos os 6 sprints do projeto Biblix.

### Resumo Geral

**Total de Horas:** 234 horas (aproximadamente 6 semanas)

- **Sprint 1:** 40h - Fundação do Sistema
- **Sprint 2:** 40h - Funcionalidades do Leitor
- **Sprint 3:** 48h - Funcionalidades do Bibliotecário
- **Sprint 4:** 40h - Funcionalidades Administrativas
- **Sprint 5:** 36h - Funcionalidades Complementares
- **Sprint 6:** 30h - Qualidade e Testes

### Funcionalidades Implementadas

✅ Sistema completo de autenticação com 3 perfis
✅ Catálogo público com busca avançada
✅ Auto-cadastro de leitores com confirmação por email
✅ Área do Leitor (dashboard, empréstimos, reservas, favoritos)
✅ Área do Bibliotecário (gestão completa de acervo e empréstimos)
✅ Área do Administrador (usuários, backup/restore, relatórios)
✅ Sistema de notificações por email
✅ Paginação e filtros avançados
✅ Relacionamentos N:N (Livro-Autor, Livro-Categoria)
✅ Regras de negócio completas (renovações, reservas, bloqueios)
✅ Testes automatizados (unitários, integração, E2E)
✅ Documentação técnica completa
✅ Configuração de CI/CD
✅ Guia de deploy

### Próximos Passos

1. **Implementar os códigos** seguindo este guia
2. **Executar os testes** e corrigir problemas
3. **Revisar a documentação** e ajustar ao seu contexto
4. **Fazer deploy** em ambiente de staging
5. **Realizar testes de aceitação** com usuários
6. **Deploy em produção**

### Recursos Adicionais

- [FastAPI Documentation](https://fastapi.tiangolo.com/)
- [Jinja2 Documentation](https://jinja.palletsprojects.com/)
- [Bootstrap 5 Documentation](https://getbootstrap.com/docs/5.0/)
- [Pytest Documentation](https://docs.pytest.org/)

### Suporte

Para dúvidas ou problemas, consulte:
- A documentação técnica em `docs/README_TECNICO.md`
- O guia de API em `docs/API.md`
- O checklist de qualidade em `docs/CHECKLIST_QUALIDADE.md`

**Boa sorte com seu projeto Biblix!** 🚀📚

---

## 9. APÊNDICES

### Apêndice A: Comandos Úteis

```bash
# Resetar banco de dados
rm database.db
python main.py  # Recria tudo

# Ver estrutura do banco
sqlite3 database.db .schema

# Backup manual
cp database.db database.backup.db

# Ver logs em tempo real
tail -f logs/app.*.log
```

### Apêndice B: Padrões de Nomenclatura

- **Models:** `nome_model.py` - classe em PascalCase
- **Repositories:** `nome_repo.py` - funções em snake_case
- **Routes:** `nome_routes.py` - funções async
- **Templates:** `pasta/nome.html` - snake_case
- **DTOs:** `nome_dto.py` - classes com sufixo DTO

### Apêndice C: Estrutura de Commit

```
tipo(escopo): mensagem

Exemplos:
feat(livro): adicionar CRUD de livros
fix(emprestimo): corrigir cálculo de prazo
docs(guia): adicionar sprint 2
refactor(repo): simplificar query de autores
test(livro): adicionar testes de repository
```

---

**FIM DO GUIA - SPRINT 1**

**Próximos passos:** Implementar Sprint 2 após completar e validar Sprint 1.

**Dúvidas ou problemas?** Consulte:
- `ANALISE_INICIAL.md` - Visão geral do projeto
- `README.md` - Documentação do boilerplate
- `CLAUDE.md` - Documentação técnica detalhada
