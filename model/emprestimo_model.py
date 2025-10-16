from dataclasses import dataclass
from datetime import datetime


@dataclass
class Emprestimo:
    id_emprestimo: int
    id_livro: int
    id_leitor: int
    data_retirada: datetime
    data_devolucao: datetime