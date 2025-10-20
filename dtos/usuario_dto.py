from pydantic import BaseModel, field_validator
from util.perfis import Perfil
from dtos.validators import (
    validar_email,
    validar_senha_forte,
    validar_nome_pessoa,
    validar_id_positivo,
    validar_perfil_usuario,
)


class CriarUsuarioDTO(BaseModel):
    """DTO para criação de usuário"""

    nome: str
    email: str
    senha: str
    perfil: str

    _validar_nome = field_validator("nome")(validar_nome_pessoa())
    _validar_email = field_validator("email")(validar_email())
    _validar_senha = field_validator("senha")(validar_senha_forte())
    _validar_perfil = field_validator("perfil")(validar_perfil_usuario(Perfil))


class AlterarUsuarioDTO(BaseModel):
    """DTO para alteração de usuário"""

    id: int
    nome: str
    email: str
    perfil: str

    _validar_id = field_validator("id")(validar_id_positivo())
    _validar_nome = field_validator("nome")(validar_nome_pessoa())
    _validar_email = field_validator("email")(validar_email())
    _validar_perfil = field_validator("perfil")(validar_perfil_usuario(Perfil))
