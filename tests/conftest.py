"""
Configurações e fixtures para testes pytest
"""
import pytest
from fastapi.testclient import TestClient
import os
import tempfile
from util.perfis import Perfil

# Configurar banco de dados de teste ANTES de importar a aplicação
@pytest.fixture(scope="session", autouse=True)
def setup_test_database():
    """Configura banco de dados de teste em memória para toda a sessão"""
    # Criar arquivo temporário para o banco de testes
    test_db = tempfile.NamedTemporaryFile(mode='w', delete=False, suffix='.db')
    test_db_path = test_db.name
    test_db.close()

    # Configurar variável de ambiente para usar DB de teste
    os.environ['DATABASE_PATH'] = test_db_path

    # Desabilitar envio de e-mails durante testes
    os.environ['RESEND_API_KEY'] = ''

    # Configurar nível de log para testes
    os.environ['LOG_LEVEL'] = 'ERROR'

    yield test_db_path

    # Limpar: remover arquivo de banco após todos os testes
    try:
        os.unlink(test_db_path)
    except:
        pass


@pytest.fixture(scope="function", autouse=True)
def limpar_rate_limiter():
    """Limpa o rate limiter antes de cada teste para evitar bloqueios"""
    # Importar após configuração do banco de dados
    from routes.auth_routes import login_limiter

    # Limpar antes do teste
    login_limiter.limpar()
    yield
    # Limpar depois do teste também
    login_limiter.limpar()


@pytest.fixture(scope="function")
def client():
    """
    Cliente de teste FastAPI com sessão limpa para cada teste
    Importa app DEPOIS de configurar o banco de dados
    """
    # Importar aqui para garantir que as configurações de teste sejam aplicadas
    from main import app

    # Criar cliente de teste
    with TestClient(app) as test_client:
        yield test_client


@pytest.fixture
def usuario_teste():
    """Dados de um usuário de teste padrão"""
    return {
        "nome": "Usuario Teste",
        "email": "teste@example.com",
        "senha": "Senha@123",
        "perfil": Perfil.CLIENTE.value  # Usa Enum Perfil
    }


@pytest.fixture
def admin_teste():
    """Dados de um admin de teste"""
    return {
        "nome": "Admin Teste",
        "email": "admin@example.com",
        "senha": "Admin@123",
        "perfil": Perfil.ADMIN.value  # Usa Enum Perfil
    }


@pytest.fixture
def criar_usuario(client):
    """
    Fixture que retorna uma função para criar usuários
    Útil para criar múltiplos usuários em um teste
    """
    def _criar_usuario(nome: str, email: str, senha: str):
        """Cadastra um usuário via endpoint de cadastro"""
        response = client.post("/cadastrar", data={
            "nome": nome,
            "email": email,
            "senha": senha,
            "confirmar_senha": senha
        }, follow_redirects=False)
        return response

    return _criar_usuario


@pytest.fixture
def fazer_login(client):
    """
    Fixture que retorna uma função para fazer login
    Retorna o cliente já autenticado
    """
    def _fazer_login(email: str, senha: str):
        """Faz login e retorna o cliente autenticado"""
        response = client.post("/login", data={
            "email": email,
            "senha": senha
        }, follow_redirects=False)
        return response

    return _fazer_login


@pytest.fixture
def cliente_autenticado(client, criar_usuario, fazer_login, usuario_teste):
    """
    Fixture que retorna um cliente já autenticado
    Cria um usuário e faz login automaticamente
    """
    # Criar usuário
    criar_usuario(
        usuario_teste["nome"],
        usuario_teste["email"],
        usuario_teste["senha"]
    )

    # Fazer login
    fazer_login(usuario_teste["email"], usuario_teste["senha"])

    # Retornar cliente autenticado
    return client


@pytest.fixture
def admin_autenticado(client, criar_usuario, fazer_login, admin_teste):
    """
    Fixture que retorna um cliente autenticado como admin
    """
    # Importar para manipular diretamente o banco
    from repo import usuario_repo
    from model.usuario_model import Usuario
    from util.security import criar_hash_senha

    # Criar admin diretamente no banco (pular validações de cadastro público)
    admin = Usuario(
        id=0,
        nome=admin_teste["nome"],
        email=admin_teste["email"],
        senha=criar_hash_senha(admin_teste["senha"]),
        perfil=Perfil.ADMIN.value  # Usa Enum Perfil
    )
    usuario_repo.inserir(admin)

    # Fazer login
    fazer_login(admin_teste["email"], admin_teste["senha"])

    # Retornar cliente autenticado
    return client


@pytest.fixture
def tarefa_teste():
    """Dados de uma tarefa de teste"""
    return {
        "titulo": "Tarefa de Teste",
        "descricao": "Descrição da tarefa de teste"
    }


@pytest.fixture
def criar_tarefa(cliente_autenticado):
    """
    Fixture que retorna uma função para criar tarefas
    Requer cliente autenticado
    """
    def _criar_tarefa(titulo: str, descricao: str = ""):
        """Cria uma tarefa via endpoint"""
        response = cliente_autenticado.post("/tarefas/cadastrar", data={
            "titulo": titulo,
            "descricao": descricao
        }, follow_redirects=False)
        return response

    return _criar_tarefa
