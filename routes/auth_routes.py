from fastapi import APIRouter, Form, Request, status
from fastapi.responses import RedirectResponse
from pydantic import ValidationError
from datetime import datetime

from dtos.auth_dto import LoginDTO, CadastroDTO, RecuperacaoSenhaDTO, RedefinirSenhaDTO
from model.usuario_model import Usuario
from repo import usuario_repo
from util.security import criar_hash_senha, verificar_senha, gerar_token_redefinicao, obter_data_expiracao_token
from util.email_service import email_service
from util.flash_messages import informar_sucesso, informar_erro
from util.template_util import criar_templates
from util.logger_config import logger
from util.perfis import Perfil
from util.config import (
    RATE_LIMIT_LOGIN_MAX,
    RATE_LIMIT_LOGIN_MINUTOS,
    RATE_LIMIT_CADASTRO_MAX,
    RATE_LIMIT_CADASTRO_MINUTOS,
    RATE_LIMIT_ESQUECI_SENHA_MAX,
    RATE_LIMIT_ESQUECI_SENHA_MINUTOS
)

router = APIRouter()
templates = criar_templates("templates/auth")

# Rate limiter simples - em produção usar biblioteca especializada
from collections import defaultdict
from datetime import datetime, timedelta

class SimpleRateLimiter:
    def __init__(self, max_tentativas: int = 5, janela_minutos: int = 5):
        self.max_tentativas = max_tentativas
        self.janela = timedelta(minutes=janela_minutos)
        self.tentativas: defaultdict[str, list[datetime]] = defaultdict(list)

    def verificar(self, identificador: str) -> bool:
        """Retorna True se dentro do limite, False se excedido"""
        agora = datetime.now()

        # Limpar tentativas antigas
        self.tentativas[identificador] = [
            t for t in self.tentativas[identificador]
            if agora - t < self.janela
        ]

        # Verificar limite
        if len(self.tentativas[identificador]) >= self.max_tentativas:
            return False

        # Registrar tentativa
        self.tentativas[identificador].append(agora)
        return True

    def limpar(self):
        """Limpa todas as tentativas registradas (útil para testes)"""
        self.tentativas.clear()

login_limiter = SimpleRateLimiter(
    max_tentativas=RATE_LIMIT_LOGIN_MAX,
    janela_minutos=RATE_LIMIT_LOGIN_MINUTOS
)
cadastro_limiter = SimpleRateLimiter(
    max_tentativas=RATE_LIMIT_CADASTRO_MAX,
    janela_minutos=RATE_LIMIT_CADASTRO_MINUTOS
)
esqueci_senha_limiter = SimpleRateLimiter(
    max_tentativas=RATE_LIMIT_ESQUECI_SENHA_MAX,
    janela_minutos=RATE_LIMIT_ESQUECI_SENHA_MINUTOS
)

@router.get("/login")
async def get_login(request: Request):
    """Exibe formulário de login"""
    # Se já estiver logado, redireciona
    if request.session.get("usuario_logado"):
        return RedirectResponse("/usuario", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("auth/login.html", {"request": request})

@router.post("/login")
async def post_login(
    request: Request,
    email: str = Form(...),
    senha: str = Form(...)
):
    """Processa login do usuário"""
    try:
        # Rate limiting por IP
        ip = request.client.host if request.client else "unknown"
        if not login_limiter.verificar(ip):
            informar_erro(request, "Muitas tentativas de login. Aguarde alguns minutos.")
            logger.warning(f"Rate limit excedido para IP: {ip}")
            return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
        
        # Armazena os dados do formulário para reexibição em caso de erro
        dados_formulario = {"email": email}

        # Validar dados com DTO
        dto = LoginDTO(email=email, senha=senha)        

        # Buscar usuário
        usuario = usuario_repo.obter_por_email(dto.email)

        # Verificar credenciais
        if not usuario or not verificar_senha(dto.senha, usuario.senha):
            informar_erro(request, "E-mail ou senha inválidos")
            logger.warning(f"Tentativa de login falhou para: {dto.email}")
            return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

        # Salvar sessão
        request.session["usuario_logado"] = {
            "id": usuario.id,
            "nome": usuario.nome,
            "email": usuario.email,
            "perfil": usuario.perfil
        }

        logger.info(f"Usuário {usuario.email} autenticado com sucesso")
        informar_sucesso(request, f"Bem-vindo(a), {usuario.nome}!")
        return RedirectResponse("/usuario", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = { erro["loc"][-1]: erro['msg'].replace("Value error, ", "") for erro in e.errors() }
        informar_erro(request, "Há campos com erros de validação.")
        return templates.TemplateResponse(
            "auth/login.html",
            {"request": request, "dados": dados_formulario, "erros": erros}
        )

@router.get("/logout")
async def logout(request: Request):
    """Faz logout do usuário"""
    usuario_email = request.session.get("usuario_logado", {}).get("email", "Usuário")
    request.session.clear()
    logger.info(f"Usuário {usuario_email} fez logout")
    informar_sucesso(request, "Logout realizado com sucesso!")
    return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

@router.get("/cadastrar")
async def get_cadastrar(request: Request):
    """Exibe formulário de cadastro"""
    # Se já estiver logado, redireciona
    if request.session.get("usuario_logado"):
        return RedirectResponse("/usuario", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse("auth/cadastro.html", {"request": request})

@router.post("/cadastrar")
async def post_cadastrar(
    request: Request,
    perfil: str = Form(...),
    nome: str = Form(...),
    email: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...)
):
    """Processa cadastro de novo usuário"""
    try:
        # Rate limiting por IP
        ip = request.client.host if request.client else "unknown"
        if not cadastro_limiter.verificar(ip):
            informar_erro(
                request,
                f"Muitas tentativas de cadastro. Aguarde {RATE_LIMIT_CADASTRO_MINUTOS} minuto(s)."
            )
            logger.warning(f"Rate limit de cadastro excedido para IP: {ip}")
            return RedirectResponse("/cadastrar", status_code=status.HTTP_303_SEE_OTHER)

        # Validar dados com DTO
        dto = CadastroDTO(
            perfil=perfil,
            nome=nome,
            email=email,
            senha=senha,
            confirmar_senha=confirmar_senha
        )

        # Verificar se e-mail já existe
        if usuario_repo.obter_por_email(dto.email):
            informar_erro(request, "Este e-mail já está cadastrado")
            return templates.TemplateResponse(
                "auth/cadastro.html",
                {"request": request, "perfil": perfil, "nome": nome, "email": email}
            )

        # Criar usuário com perfil escolhido
        usuario = Usuario(
            id=0,
            nome=dto.nome,
            email=dto.email,
            senha=criar_hash_senha(dto.senha),
            perfil=dto.perfil
        )

        # Inserir no banco
        usuario_id = usuario_repo.inserir(usuario)

        if usuario_id:
            logger.info(f"Novo usuário cadastrado: {usuario.email}")

            # Enviar e-mail de boas-vindas
            email_service.enviar_boas_vindas(usuario.email, usuario.nome)

            informar_sucesso(request, "Cadastro realizado com sucesso! Faça login para continuar.")
            return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)
        else:
            informar_erro(request, "Erro ao realizar cadastro. Tente novamente.")
            return templates.TemplateResponse(
                "auth/cadastro.html",
                {"request": request, "nome": nome, "email": email}
            )

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        return templates.TemplateResponse(
            "auth/cadastro.html",
            {"request": request, "perfil": perfil, "nome": nome, "email": email}
        )

@router.get("/esqueci-senha")
async def get_esqueci_senha(request: Request):
    """Exibe formulário de recuperação de senha"""
    return templates.TemplateResponse("auth/esqueci_senha.html", {"request": request})

@router.post("/esqueci-senha")
async def post_esqueci_senha(
    request: Request,
    email: str = Form(...)
):
    """Processa solicitação de recuperação de senha"""
    try:
        # Rate limiting por IP
        ip = request.client.host if request.client else "unknown"
        if not esqueci_senha_limiter.verificar(ip):
            informar_erro(
                request,
                f"Muitas tentativas de recuperação de senha. Aguarde {RATE_LIMIT_ESQUECI_SENHA_MINUTOS} minuto(s)."
            )
            logger.warning(f"Rate limit de recuperação de senha excedido para IP: {ip}")
            return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)

        # Validar e-mail com DTO
        dto = RecuperacaoSenhaDTO(email=email)

        # Buscar usuário
        usuario = usuario_repo.obter_por_email(dto.email)

        if usuario:
            # Gerar token de redefinição
            token = gerar_token_redefinicao()
            data_expiracao = obter_data_expiracao_token(horas=1)

            # Salvar token no banco
            usuario_repo.atualizar_token(usuario.email, token, data_expiracao)

            # Enviar e-mail com link de recuperação
            email_enviado = email_service.enviar_recuperacao_senha(
                usuario.email,
                usuario.nome,
                token
            )

            if email_enviado:
                logger.info(f"E-mail de recuperação enviado para: {usuario.email}")
            else:
                logger.error(f"Falha ao enviar e-mail de recuperação para: {usuario.email}")

        # Sempre retornar mesma mensagem (segurança)
        informar_sucesso(
            request,
            "Se o e-mail estiver cadastrado, você receberá instruções para recuperação de senha."
        )
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        return templates.TemplateResponse(
            "auth/esqueci_senha.html",
            {"request": request, "email": email}
        )

@router.get("/redefinir-senha")
async def get_redefinir_senha(request: Request, token: str):
    """Exibe formulário de redefinição de senha"""
    # Validar token
    usuario = usuario_repo.obter_por_token(token)

    if not usuario or not usuario.data_token:
        informar_erro(request, "Token inválido ou expirado")
        return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)

    # Verificar expiração
    try:
        data_token = datetime.fromisoformat(usuario.data_token)
        if datetime.now() > data_token:
            informar_erro(request, "Token expirado. Solicite uma nova recuperação de senha.")
            return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)
    except:
        informar_erro(request, "Token inválido")
        return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)

    return templates.TemplateResponse(
        "auth/redefinir_senha.html",
        {"request": request, "token": token}
    )

@router.post("/redefinir-senha")
async def post_redefinir_senha(
    request: Request,
    token: str = Form(...),
    senha: str = Form(...),
    confirmar_senha: str = Form(...)
):
    """Processa redefinição de senha"""
    try:
        # Validar dados com DTO
        dto = RedefinirSenhaDTO(
            token=token,
            senha=senha,
            confirmar_senha=confirmar_senha
        )

        # Validar token e expiração
        usuario = usuario_repo.obter_por_token(dto.token)

        if not usuario or not usuario.data_token:
            informar_erro(request, "Token inválido")
            return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)

        try:
            data_token = datetime.fromisoformat(usuario.data_token)
            if datetime.now() > data_token:
                informar_erro(request, "Token expirado")
                return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)
        except:
            informar_erro(request, "Token inválido")
            return RedirectResponse("/esqueci-senha", status_code=status.HTTP_303_SEE_OTHER)

        # Atualizar senha
        senha_hash = criar_hash_senha(dto.senha)
        usuario_repo.atualizar_senha(usuario.id, senha_hash)

        # Limpar token
        usuario_repo.limpar_token(usuario.id)

        logger.info(f"Senha redefinida com sucesso para usuário: {usuario.email}")
        informar_sucesso(request, "Senha redefinida com sucesso! Faça login com sua nova senha.")
        return RedirectResponse("/login", status_code=status.HTTP_303_SEE_OTHER)

    except ValidationError as e:
        erros = [erro['msg'] for erro in e.errors()]
        informar_erro(request, " | ".join(erros))
        return RedirectResponse(
            f"/redefinir-senha?token={token}",
            status_code=status.HTTP_303_SEE_OTHER
        )
