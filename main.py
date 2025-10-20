import uvicorn
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.exceptions import RequestValidationError
from starlette.middleware.sessions import SessionMiddleware
from starlette.exceptions import HTTPException as StarletteHTTPException
from pathlib import Path

# Configurações
from util.config import APP_NAME, SECRET_KEY, HOST, PORT, RELOAD, VERSION

# Logger
from util.logger_config import logger

# Exception Handlers
from util.exception_handlers import (
    http_exception_handler,
    validation_exception_handler,
    generic_exception_handler
)

# Repositórios
from repo import usuario_repo, configuracao_repo, tarefa_repo

# Rotas
from routes.auth_routes import router as auth_router
from routes.tarefas_routes import router as tarefas_router
from routes.admin_usuarios_routes import router as admin_usuarios_router
from routes.admin_configuracoes_routes import router as admin_config_router
from routes.perfil_routes import router as perfil_router
from routes.usuario_routes import router as usuario_router
from routes.public_routes import router as public_router
from routes.examples_routes import router as examples_router

# Seeds
from util.seed_data import inicializar_dados

# Criar aplicação FastAPI
app = FastAPI(title=APP_NAME, version=VERSION)

# Configurar SessionMiddleware
app.add_middleware(SessionMiddleware, secret_key=SECRET_KEY)

# Registrar Exception Handlers
app.add_exception_handler(StarletteHTTPException, http_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(RequestValidationError, validation_exception_handler)  # type: ignore[arg-type]
app.add_exception_handler(Exception, generic_exception_handler)
logger.info("Exception handlers registrados")

# Montar arquivos estáticos
static_path = Path("static")
if static_path.exists():
    app.mount("/static", StaticFiles(directory="static"), name="static")
    logger.info("Arquivos estáticos montados em /static")

# Criar tabelas do banco de dados
logger.info("Criando tabelas do banco de dados...")
try:
    usuario_repo.criar_tabela()
    logger.info("Tabela 'usuario' criada/verificada")

    configuracao_repo.criar_tabela()
    logger.info("Tabela 'configuracao' criada/verificada")

    tarefa_repo.criar_tabela()
    logger.info("Tabela 'tarefa' criada/verificada")

except Exception as e:
    logger.error(f"Erro ao criar tabelas: {e}")
    raise

# Inicializar dados seed
try:
    inicializar_dados()
except Exception as e:
    logger.error(f"Erro ao inicializar dados seed: {e}", exc_info=True)

# Incluir routers
# IMPORTANTE: public_router deve ser incluído por último para que a rota "/" funcione corretamente
app.include_router(auth_router, tags=["Autenticação"])
logger.info("Router de autenticação incluído")

app.include_router(perfil_router, tags=["Perfil"])
logger.info("Router de perfil incluído")

app.include_router(tarefas_router, tags=["Tarefas"])
logger.info("Router de tarefas incluído")

app.include_router(admin_usuarios_router, tags=["Admin - Usuários"])
logger.info("Router admin de usuários incluído")

app.include_router(admin_config_router, tags=["Admin - Configurações"])
logger.info("Router admin de configurações incluído")

app.include_router(usuario_router, tags=["Usuário"])
logger.info("Router de usuário incluído")

# Rotas públicas (deve ser por último para não sobrescrever outras rotas)
app.include_router(public_router, tags=["Público"])
logger.info("Router público incluído")

# Rotas públicas (deve ser por último para não sobrescrever outras rotas)
app.include_router(examples_router, tags=["Exemplos"])
logger.info("Router de exemplos incluído")

@app.get("/health")
async def health_check():
    """Endpoint de health check"""
    return {"status": "healthy"}

if __name__ == "__main__":
    logger.info("=" * 60)
    logger.info(f"Iniciando {APP_NAME} v{VERSION}")
    logger.info("=" * 60)

    logger.info(f"Servidor rodando em http://{HOST}:{PORT}")
    logger.info(f"Hot reload: {'Ativado' if RELOAD else 'Desativado'}")
    logger.info(f"Documentação API: http://{HOST}:{PORT}/docs")
    logger.info("=" * 60)

    try:
        uvicorn.run(
            "main:app",
            host=HOST,
            port=PORT,
            reload=RELOAD,
            log_level="info"
        )
    except KeyboardInterrupt:
        logger.info("Servidor encerrado pelo usuário")
    except Exception as e:
        logger.error(f"Erro ao iniciar servidor: {e}")
        raise
