"""Modulo de processos: estrutura de dados de um processo."""

class Processo:
    """Mantem as informacoes especificas de um processo do pseudo-SO."""

    def __init__(self, pid, tempo_inicializacao, prioridade, tempo_processador,
                 max_working_set, req_impressora, req_scanner, req_modem, req_sata,
                 string_paginas=None):
        """Inicializa um processo a partir dos campos lidos do processes.txt.

        prioridade 0 indica processo de tempo real. string_paginas e a sequencia
        de paginas referenciadas (vinda do string.txt).
        """
        self.pid = pid
        self.tempo_inicializacao = tempo_inicializacao
        self.prioridade = prioridade
        self.tempo_processador = tempo_processador
        self.tempo_restante = tempo_processador
        self.max_working_set = max_working_set
        self.req_impressora = req_impressora
        self.req_scanner = req_scanner
        self.req_modem = req_modem
        self.req_sata = req_sata
        self.string_paginas = string_paginas or []

    @property
    def eh_tempo_real(self):
        """True se o processo e de tempo real (prioridade 0)."""
        return self.prioridade == 0

    def __repr__(self):
        """Representacao curta para depuração."""
        return f"Processo(pid={self.pid}, prioridade={self.prioridade})"