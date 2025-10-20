import logging
from logging.handlers import TimedRotatingFileHandler
import os
from pathlib import Path
from datetime import datetime
import time


class DailyRotatingFileHandler(TimedRotatingFileHandler):
    """Handler customizado que cria arquivos com data no nome desde o início"""

    def __init__(self, log_dir='logs', when='midnight', interval=1, backupCount=30):
        self.log_dir = log_dir
        Path(log_dir).mkdir(exist_ok=True)

        # Nome do arquivo com data de hoje
        filename = self._get_filename_for_date(datetime.now())

        super().__init__(
            filename=filename,
            when=when,
            interval=interval,
            backupCount=backupCount
        )

    def _get_filename_for_date(self, dt):
        """Gera nome do arquivo no formato app.YYYY.MM.DD.log"""
        return os.path.join(
            self.log_dir,
            f"app.{dt.strftime('%Y.%m.%d')}.log"
        )

    def doRollover(self):
        """Override do rollover para criar novo arquivo com nome correto"""
        if self.stream:
            self.stream.close()
            self.stream = None  # type: ignore[assignment]

        # Novo arquivo com data atual (após meia-noite)
        self.baseFilename = self._get_filename_for_date(datetime.now())

        # Deletar arquivos antigos além do backupCount
        if self.backupCount > 0:
            for s in self.getFilesToDelete():
                os.remove(s)

        # Atualizar próximo rollover
        currentTime = int(time.time())
        newRolloverAt = self.computeRollover(currentTime)
        while newRolloverAt <= currentTime:
            newRolloverAt = newRolloverAt + self.interval
        self.rolloverAt = newRolloverAt

        # Abrir novo arquivo
        if not self.delay:
            self.stream = self._open()


def configurar_logger():
    """Configura sistema de logging profissional com rotação diária"""
    # Configurar formato
    formato = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Obter configuração de retenção de logs (padrão: 30 dias)
    retention_days = int(os.getenv('LOG_RETENTION_DAYS', '30'))

    # Handler customizado que cria arquivos com data desde o início
    file_handler = DailyRotatingFileHandler(
        log_dir='logs',
        when='midnight',
        interval=1,
        backupCount=retention_days
    )
    file_handler.setFormatter(formato)

    # Handler para console
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formato)

    # Configurar logger raiz
    logger = logging.getLogger()
    nivel = os.getenv('LOG_LEVEL', 'INFO')
    logger.setLevel(getattr(logging, nivel))
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger

# Logger global para importação
logger = configurar_logger()
