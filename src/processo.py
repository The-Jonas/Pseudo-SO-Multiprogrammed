"""Modulo de processos: estrutura de dados de um processo."""


class Processo:
    """Mantem as informacoes especificas de um processo do pseudo-SO."""

    def __init__(self, pid, tempo_inicializacao, prioridade, tempo_processador,
                 max_working_set, req_impressora, req_scanner, req_modem, req_sata,
                 string_paginas=None):
        """Inicializa um processo a partir dos campos lidos do processes.txt.

        prioridade 0 indica processo de tempo real. string_paginas e a sequencia
        completa de paginas referenciadas (vinda do string.txt). O processo
        percorre a string inteira durante sua execucao, independente do
        tempo_processador — as duas dimensoes sao independentes.
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
        self.tempo_espera = 0       # ticks esperando na fila (usado pelo aging)
        self.ponteiro_pagina = 0    # proxima pagina a referenciar na string

    @property
    def eh_tempo_real(self):
        """True se o processo e de tempo real (prioridade 0)."""
        return self.prioridade == 0

    def proxima_pagina(self):
        """Retorna a proxima pagina da string e avanca o ponteiro.

        Retorna None quando a string ja foi percorrida por completo.
        """
        if self.ponteiro_pagina < len(self.string_paginas):
            pagina = self.string_paginas[self.ponteiro_pagina]
            self.ponteiro_pagina += 1
            return pagina
        return None

    def __repr__(self):
        """Representacao curta para depuracao."""
        return f"Processo(pid={self.pid}, prioridade={self.prioridade})"
