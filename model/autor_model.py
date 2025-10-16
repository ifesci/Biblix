from dataclasses import dataclass
from datetime import datetime


@dataclass
class Autor:
    id_autor: int
    nome: str
    biografia: str
    data_nascimento: datetime
