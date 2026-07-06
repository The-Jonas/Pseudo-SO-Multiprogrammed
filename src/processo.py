"""Modulo de processos: estrutura de dados de um processo."""


class Processo:
    """Mantem as informacoes especificas de um processo do pseudo-SO."""

    # Estados possiveis do processo
    ESTADO_NOVO       = "NOVO"       # chegou mas ainda nao foi validado
    ESTADO_PRONTO     = "PRONTO"     # alocou memoria e recursos, esta na fila de escalonamento
    ESTADO_EXECUTANDO = "EXECUTANDO" # esta rodando na CPU
    ESTADO_TERMINADO  = "TERMINADO"  # concluiu execucao
    ESTADO_REJEITADO  = "REJEITADO"  # pedido impossivel, nao sera executado

    def __init__(self, pid, tempo_inicializacao, prioridade, tempo_processador,
                 max_working_set, req_impressora, req_scanner, req_modem, req_sata,
                 string_paginas=None):
        """Inicializa um processo a partir dos campos lidos do processes.txt.

        Valores negativos em tempo_processador, max_working_set ou recursos
        sao tratados como invalidos e o processo sera rejeitado pelo escalonador.
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
        self.estado = self.ESTADO_NOVO

    @property
    def eh_tempo_real(self):
        """True se o processo e de tempo real (prioridade 0)."""
        return self.prioridade == 0

    def tem_valores_invalidos(self):
        """Retorna mensagem de erro se algum campo critico for invalido, None caso contrario.

        Valores invalidos: tempo_processador <= 0, max_working_set <= 0,
        ou qualquer requisicao de recurso negativa.
        """
        if self.tempo_processador <= 0:
            return f"tempo_processador invalido ({self.tempo_processador})"
        if self.max_working_set <= 0:
            return f"max_working_set invalido ({self.max_working_set})"
        for nome, val in [("impressora", self.req_impressora),
                          ("scanner",    self.req_scanner),
                          ("modem",      self.req_modem),
                          ("sata",       self.req_sata)]:
            if val < 0:
                return f"requisicao de {nome} invalida ({val})"
        return None

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
        return f"Processo(pid={self.pid}, prio={self.prioridade}, estado={self.estado})"
