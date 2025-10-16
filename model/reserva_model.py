from dataclasses import dataclass
from datetime import datetime


@dataclass
class Reserva:
    id_reserva: int
    id_livro: int
    id_leitor: int
    data_cadastro: datetime
    data_reserva: datetime
    status: str