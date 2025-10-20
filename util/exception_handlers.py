from fastapi import Request, status
from fastapi.responses import RedirectResponse, Response
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from util.template_util import criar_templates
from util.flash_messages import informar_erro, informar_aviso
from util.logger_config import logger
from util.config import IS_DEVELOPMENT
import traceback

# Configurar templates de erro
templates = criar_templates("templates")


async def http_exception_handler(request: Request, exc: StarletteHTTPException) -> Response:
    """
    Handler para exceções HTTP do Starlette/FastAPI

    - 401 (Unauthorized): Redireciona para login com mensagem
    - 403 (Forbidden): Redireciona para login com mensagem
    - 404 (Not Found): Exibe página de erro 404
    - Outros: Loga e retorna página de erro genérica
    """
    status_code = exc.status_code

    # Extensões de arquivos estáticos opcionais que não devem gerar warnings
    STATIC_OPTIONAL_EXTENSIONS = ('.map', '.ico', '.woff', '.woff2', '.ttf', '.eot')

    # Determinar nível de log baseado no tipo de recurso
    path_lower = request.url.path.lower()
    is_optional_static = status_code == 404 and path_lower.endswith(STATIC_OPTIONAL_EXTENSIONS)

    # Log da exceção com nível apropriado
    log_message = (
        f"HTTPException {status_code}: {exc.detail} - "
        f"Path: {request.url.path} - "
        f"IP: {request.client.host if request.client else 'unknown'}"
    )

    if is_optional_static:
        logger.debug(log_message)
    else:
        logger.warning(log_message)

    # 401 - Não autenticado
    if status_code == status.HTTP_401_UNAUTHORIZED:
        informar_erro(request, "Você precisa estar autenticado para acessar esta página.")
        return RedirectResponse(
            f"/login?redirect={request.url.path}",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 403 - Sem permissão
    if status_code == status.HTTP_403_FORBIDDEN:
        informar_erro(request, "Você não tem permissão para acessar esta página.")
        return RedirectResponse(
            "/login",
            status_code=status.HTTP_303_SEE_OTHER
        )

    # 404 - Não encontrado
    if status_code == status.HTTP_404_NOT_FOUND:
        return templates.TemplateResponse(
            "errors/404.html",
            {"request": request},
            status_code=status.HTTP_404_NOT_FOUND
        )

    # Outros erros HTTP - página de erro genérica
    context = {
        "request": request,
        "error_code": status_code,
        "error_message": exc.detail if IS_DEVELOPMENT else "Ocorreu um erro ao processar sua solicitação."
    }

    # Em desenvolvimento, adicionar detalhes técnicos
    if IS_DEVELOPMENT:
        context["error_details"] = {
            "type": type(exc).__name__,
            "detail": str(exc.detail),
            "path": request.url.path,
            "method": request.method
        }

    return templates.TemplateResponse(
        "errors/500.html",
        context,
        status_code=status_code
    )


async def validation_exception_handler(request: Request, exc: RequestValidationError) -> Response:
    """
    Handler para erros de validação do Pydantic
    Loga o erro e exibe mensagem amigável
    """
    logger.warning(
        f"Erro de validação: {exc.errors()} - "
        f"Path: {request.url.path} - "
        f"Body: {exc.body}"
    )

    # Extrair mensagens de erro
    erros = []
    for error in exc.errors():
        campo = " -> ".join(str(loc) for loc in error["loc"] if loc != "body")
        mensagem = error["msg"]
        erros.append(f"{campo}: {mensagem}" if campo else mensagem)

    # Mensagem amigável ou técnica dependendo do modo
    if IS_DEVELOPMENT:
        mensagem_flash = f"Dados inválidos: {'; '.join(erros)}"
        error_message = f"Erro de validação: {'; '.join(erros)}"
    else:
        mensagem_flash = "Os dados fornecidos são inválidos. Por favor, verifique e tente novamente."
        error_message = "Erro de validação de dados"

    informar_erro(request, mensagem_flash)

    context = {
        "request": request,
        "error_code": 422,
        "error_message": error_message
    }

    # Em desenvolvimento, adicionar detalhes técnicos
    if IS_DEVELOPMENT:
        context["error_details"] = {
            "type": "RequestValidationError",
            "errors": exc.errors(),
            "body": str(exc.body),
            "path": request.url.path,
            "method": request.method
        }

    return templates.TemplateResponse(
        "errors/500.html",
        context,
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY
    )


async def generic_exception_handler(request: Request, exc: Exception) -> Response:
    """
    Handler genérico para todas as exceções não tratadas
    Loga o erro completo e exibe página de erro amigável
    """
    # Sempre logar o erro completo (independente do modo)
    logger.error(
        f"Exceção não tratada: {type(exc).__name__}: {str(exc)} - "
        f"Path: {request.url.path} - "
        f"IP: {request.client.host if request.client else 'unknown'}",
        exc_info=True
    )

    # Definir mensagem baseada no modo de execução
    if IS_DEVELOPMENT:
        error_message = f"{type(exc).__name__}: {str(exc)}"
    else:
        error_message = "Erro interno do servidor. Nossa equipe foi notificada."

    context = {
        "request": request,
        "error_code": 500,
        "error_message": error_message
    }

    # Em desenvolvimento, adicionar detalhes técnicos completos
    if IS_DEVELOPMENT:
        context["error_details"] = {
            "type": type(exc).__name__,
            "message": str(exc),
            "traceback": traceback.format_exc(),
            "path": request.url.path,
            "method": request.method,
            "ip": request.client.host if request.client else 'unknown'
        }

    return templates.TemplateResponse(
        "errors/500.html",
        context,
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
    )
