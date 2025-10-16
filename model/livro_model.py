from dataclasses import dataclass
from datetime import datetime


@dataclass
class Livro:
    id_livro: int
    titulo: str
    data_publicacao: datetime
    sinopse: str
