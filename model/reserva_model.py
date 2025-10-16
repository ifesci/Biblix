from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from model.livro_model import Livro
from model.usuario_model import Usuario


@dataclass
class Reserva:
    id_reserva: int
    id_livro: int
    id_leitor: int
    data_cadastro: datetime
    data_reserva: datetime
    status: str
    # Relacionamentos
    livro: Optional[Livro]
    leitor: Optional[Usuario]