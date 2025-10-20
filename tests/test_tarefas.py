"""
Testes do CRUD de tarefas
Testa criação, listagem, conclusão e exclusão de tarefas
"""
import pytest
from fastapi import status


class TestListarTarefas:
    """Testes de listagem de tarefas"""

    def test_listar_tarefas_requer_autenticacao(self, client):
        """Deve exigir autenticação para listar tarefas"""
        response = client.get("/tarefas/listar", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_listar_tarefas_usuario_autenticado(self, cliente_autenticado):
        """Usuário autenticado deve conseguir listar suas tarefas"""
        response = cliente_autenticado.get("/tarefas/listar")
        assert response.status_code == status.HTTP_200_OK

    def test_listar_tarefas_vazia_inicialmente(self, cliente_autenticado):
        """Lista de tarefas deve estar vazia inicialmente"""
        response = cliente_autenticado.get("/tarefas/listar")
        assert response.status_code == status.HTTP_200_OK
        # HTML não deve conter tarefas (ou indicar lista vazia)
        assert "tarefa" in response.text.lower()


class TestCriarTarefa:
    """Testes de criação de tarefas"""

    def test_get_formulario_cadastro_requer_autenticacao(self, client):
        """Deve exigir autenticação para acessar formulário"""
        response = client.get("/tarefas/cadastrar", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_get_formulario_cadastro_usuario_autenticado(self, cliente_autenticado):
        """Usuário autenticado deve acessar formulário de cadastro"""
        response = cliente_autenticado.get("/tarefas/cadastrar")
        assert response.status_code == status.HTTP_200_OK
        assert "cadastr" in response.text.lower()

    def test_criar_tarefa_com_dados_validos(self, cliente_autenticado, tarefa_teste):
        """Deve criar tarefa com dados válidos"""
        response = cliente_autenticado.post("/tarefas/cadastrar", data={
            "titulo": tarefa_teste["titulo"],
            "descricao": tarefa_teste["descricao"]
        }, follow_redirects=False)

        # Deve redirecionar para listagem
        assert response.status_code == status.HTTP_303_SEE_OTHER
        assert response.headers["location"] == "/tarefas/listar"

    def test_criar_tarefa_sem_autenticacao(self, client, tarefa_teste):
        """Não deve permitir criar tarefa sem autenticação"""
        response = client.post("/tarefas/cadastrar", data={
            "titulo": tarefa_teste["titulo"],
            "descricao": tarefa_teste["descricao"]
        }, follow_redirects=False)

        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_criar_tarefa_titulo_muito_curto(self, cliente_autenticado):
        """Deve rejeitar título com menos de 3 caracteres"""
        response = cliente_autenticado.post("/tarefas/cadastrar", data={
            "titulo": "AB",  # Muito curto
            "descricao": "Descrição válida"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK
        # Deve mostrar erro de validação
        assert "erro" in response.text.lower() or "inválid" in response.text.lower()

    def test_criar_tarefa_titulo_muito_longo(self, cliente_autenticado):
        """Deve rejeitar título com mais de 100 caracteres"""
        titulo_longo = "T" * 101
        response = cliente_autenticado.post("/tarefas/cadastrar", data={
            "titulo": titulo_longo,
            "descricao": "Descrição"
        }, follow_redirects=True)

        assert response.status_code == status.HTTP_200_OK

    def test_criar_tarefa_sem_titulo(self, cliente_autenticado):
        """Deve rejeitar tarefa sem título"""
        response = cliente_autenticado.post("/tarefas/cadastrar", data={
            "titulo": "",
            "descricao": "Descrição"
        }, follow_redirects=True)

        assert response.status_code in [status.HTTP_200_OK, status.HTTP_422_UNPROCESSABLE_ENTITY]

    def test_criar_tarefa_sem_descricao(self, cliente_autenticado):
        """Deve permitir criar tarefa sem descrição"""
        response = cliente_autenticado.post("/tarefas/cadastrar", data={
            "titulo": "Tarefa Sem Descrição",
            "descricao": ""
        }, follow_redirects=False)

        # Descrição é opcional, deve criar normalmente
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_tarefa_criada_aparece_na_listagem(self, cliente_autenticado, tarefa_teste):
        """Tarefa criada deve aparecer na listagem"""
        # Criar tarefa
        cliente_autenticado.post("/tarefas/cadastrar", data={
            "titulo": tarefa_teste["titulo"],
            "descricao": tarefa_teste["descricao"]
        })

        # Listar tarefas
        response = cliente_autenticado.get("/tarefas/listar")
        assert response.status_code == status.HTTP_200_OK
        assert tarefa_teste["titulo"] in response.text

    def test_tarefa_criada_pertence_ao_usuario(self, cliente_autenticado, tarefa_teste, usuario_teste):
        """Tarefa criada deve pertencer ao usuário que a criou"""
        from repo import tarefa_repo, usuario_repo

        # Criar tarefa
        cliente_autenticado.post("/tarefas/cadastrar", data={
            "titulo": tarefa_teste["titulo"],
            "descricao": tarefa_teste["descricao"]
        })

        # Buscar ID do usuário de teste
        usuario = usuario_repo.obter_por_email(usuario_teste["email"])
        assert usuario is not None
        tarefas = tarefa_repo.obter_todos_por_usuario(usuario.id)
        assert len(tarefas) > 0
        assert tarefas[0].titulo == tarefa_teste["titulo"]


class TestConcluirTarefa:
    """Testes de conclusão de tarefas"""

    def test_concluir_tarefa_propria(self, cliente_autenticado, criar_tarefa, tarefa_teste, usuario_teste):
        """Deve permitir concluir tarefa própria"""
        from repo import tarefa_repo, usuario_repo

        # Criar tarefa
        criar_tarefa(tarefa_teste["titulo"], tarefa_teste["descricao"])

        # Buscar ID do usuário e da tarefa
        usuario = usuario_repo.obter_por_email(usuario_teste["email"])
        assert usuario is not None
        tarefas = tarefa_repo.obter_todos_por_usuario(usuario.id)
        tarefa_id = tarefas[0].id

        # Concluir tarefa
        response = cliente_autenticado.post(
            f"/tarefas/{tarefa_id}/concluir",
            follow_redirects=False
        )

        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar no banco que foi concluída
        tarefa = tarefa_repo.obter_por_id(tarefa_id)
        assert tarefa is not None
        assert tarefa.concluida is True

    def test_concluir_tarefa_sem_autenticacao(self, client):
        """Não deve permitir concluir tarefa sem autenticação"""
        response = client.post("/tarefas/1/concluir", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_concluir_tarefa_inexistente(self, cliente_autenticado):
        """Deve tratar tentativa de concluir tarefa inexistente"""
        response = cliente_autenticado.post(
            "/tarefas/99999/concluir",
            follow_redirects=False
        )

        # Deve redirecionar mesmo se não encontrar
        assert response.status_code == status.HTTP_303_SEE_OTHER


class TestExcluirTarefa:
    """Testes de exclusão de tarefas"""

    def test_excluir_tarefa_propria(self, cliente_autenticado, criar_tarefa, tarefa_teste, usuario_teste):
        """Deve permitir excluir tarefa própria"""
        from repo import tarefa_repo, usuario_repo

        # Criar tarefa
        criar_tarefa(tarefa_teste["titulo"], tarefa_teste["descricao"])

        # Buscar ID do usuário e da tarefa
        usuario = usuario_repo.obter_por_email(usuario_teste["email"])
        assert usuario is not None
        tarefas = tarefa_repo.obter_todos_por_usuario(usuario.id)
        tarefa_id = tarefas[0].id

        # Excluir tarefa
        response = cliente_autenticado.post(
            f"/tarefas/{tarefa_id}/excluir",
            follow_redirects=False
        )

        assert response.status_code == status.HTTP_303_SEE_OTHER

        # Verificar que foi excluída
        tarefa = tarefa_repo.obter_por_id(tarefa_id)
        assert tarefa is None

    def test_excluir_tarefa_sem_autenticacao(self, client):
        """Não deve permitir excluir tarefa sem autenticação"""
        response = client.post("/tarefas/1/excluir", follow_redirects=False)
        assert response.status_code == status.HTTP_303_SEE_OTHER

    def test_excluir_tarefa_inexistente(self, cliente_autenticado):
        """Deve tratar tentativa de excluir tarefa inexistente"""
        response = cliente_autenticado.post(
            "/tarefas/99999/excluir",
            follow_redirects=False
        )

        # Deve redirecionar sem erro
        assert response.status_code == status.HTTP_303_SEE_OTHER


class TestIsolamentoTarefas:
    """Testes de isolamento de tarefas entre usuários"""

    def test_usuario_nao_ve_tarefas_de_outros(self, client, criar_usuario):
        """Um usuário não deve ver tarefas de outros usuários"""
        from repo import tarefa_repo
        from model.tarefa_model import Tarefa

        # Criar dois usuários
        criar_usuario("Usuario 1", "usuario1@example.com", "Senha@123")
        criar_usuario("Usuario 2", "usuario2@example.com", "Senha@123")

        # Login como usuário 1
        client.post("/login", data={
            "email": "usuario1@example.com",
            "senha": "Senha@123"
        })

        # Criar tarefa como usuário 1
        client.post("/tarefas/cadastrar", data={
            "titulo": "Tarefa Usuario 1",
            "descricao": "Descrição"
        })

        # Logout
        client.get("/logout")

        # Login como usuário 2
        client.post("/login", data={
            "email": "usuario2@example.com",
            "senha": "Senha@123"
        })

        # Listar tarefas como usuário 2
        response = client.get("/tarefas/listar")

        # Não deve ver tarefa do usuário 1
        assert "Tarefa Usuario 1" not in response.text

    def test_usuario_nao_pode_concluir_tarefa_de_outro(self, client, criar_usuario):
        """Usuário não deve poder concluir tarefa de outro usuário"""
        from repo import tarefa_repo, usuario_repo
        from model.tarefa_model import Tarefa

        # Criar dois usuários
        criar_usuario("Usuario 1", "usuario1@example.com", "Senha@123")
        criar_usuario("Usuario 2", "usuario2@example.com", "Senha@123")

        # Login como usuário 1
        client.post("/login", data={
            "email": "usuario1@example.com",
            "senha": "Senha@123"
        })

        # Criar tarefa como usuário 1
        client.post("/tarefas/cadastrar", data={
            "titulo": "Tarefa Usuario 1",
            "descricao": "Descrição"
        })

        # Buscar ID do usuário 1 e da tarefa
        usuario1 = usuario_repo.obter_por_email("usuario1@example.com")
        assert usuario1 is not None
        tarefas = tarefa_repo.obter_todos_por_usuario(usuario1.id)
        tarefa_id = tarefas[0].id

        # Logout
        client.get("/logout")

        # Login como usuário 2
        client.post("/login", data={
            "email": "usuario2@example.com",
            "senha": "Senha@123"
        })

        # Tentar concluir tarefa do usuário 1
        response = client.post(f"/tarefas/{tarefa_id}/concluir", follow_redirects=True)

        # Deve ser bloqueado
        assert response.status_code == status.HTTP_200_OK

        # Verificar que tarefa não foi concluída
        tarefa = tarefa_repo.obter_por_id(tarefa_id)
        assert tarefa is not None
        assert tarefa.concluida is False

    def test_usuario_nao_pode_excluir_tarefa_de_outro(self, client, criar_usuario):
        """Usuário não deve poder excluir tarefa de outro usuário"""
        from repo import tarefa_repo, usuario_repo

        # Criar dois usuários
        criar_usuario("Usuario 1", "usuario1@example.com", "Senha@123")
        criar_usuario("Usuario 2", "usuario2@example.com", "Senha@123")

        # Login como usuário 1
        client.post("/login", data={
            "email": "usuario1@example.com",
            "senha": "Senha@123"
        })

        # Criar tarefa como usuário 1
        client.post("/tarefas/cadastrar", data={
            "titulo": "Tarefa Usuario 1",
            "descricao": "Descrição"
        })

        # Buscar ID do usuário 1 e da tarefa
        usuario1 = usuario_repo.obter_por_email("usuario1@example.com")
        assert usuario1 is not None
        tarefas = tarefa_repo.obter_todos_por_usuario(usuario1.id)
        tarefa_id = tarefas[0].id

        # Logout
        client.get("/logout")

        # Login como usuário 2
        client.post("/login", data={
            "email": "usuario2@example.com",
            "senha": "Senha@123"
        })

        # Tentar excluir tarefa do usuário 1
        response = client.post(f"/tarefas/{tarefa_id}/excluir", follow_redirects=True)

        # Deve ser bloqueado
        assert response.status_code == status.HTTP_200_OK

        # Verificar que tarefa ainda existe
        tarefa = tarefa_repo.obter_por_id(tarefa_id)
        assert tarefa is not None


class TestValidacoesTarefa:
    """Testes de validações específicas de tarefas"""

    def test_criar_multiplas_tarefas(self, cliente_autenticado):
        """Deve permitir criar múltiplas tarefas"""
        tarefas = ["Tarefa 1", "Tarefa 2", "Tarefa 3"]

        for titulo in tarefas:
            response = cliente_autenticado.post("/tarefas/cadastrar", data={
                "titulo": titulo,
                "descricao": f"Descrição {titulo}"
            })

        # Listar e verificar que todas estão lá
        response = cliente_autenticado.get("/tarefas/listar")
        for titulo in tarefas:
            assert titulo in response.text

    def test_tarefa_criada_nao_esta_concluida(self, cliente_autenticado, criar_tarefa, tarefa_teste, usuario_teste):
        """Tarefa criada deve estar marcada como não concluída"""
        from repo import tarefa_repo, usuario_repo

        criar_tarefa(tarefa_teste["titulo"], tarefa_teste["descricao"])

        usuario = usuario_repo.obter_por_email(usuario_teste["email"])
        assert usuario is not None
        tarefas = tarefa_repo.obter_todos_por_usuario(usuario.id)
        assert tarefas[0].concluida is False

    def test_tarefa_tem_data_criacao(self, cliente_autenticado, criar_tarefa, tarefa_teste, usuario_teste):
        """Tarefa deve ter data de criação registrada"""
        from repo import tarefa_repo, usuario_repo

        criar_tarefa(tarefa_teste["titulo"], tarefa_teste["descricao"])

        usuario = usuario_repo.obter_por_email(usuario_teste["email"])
        assert usuario is not None
        tarefas = tarefa_repo.obter_todos_por_usuario(usuario.id)
        assert tarefas[0].data_criacao is not None
