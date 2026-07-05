"""Modulo do escalonador: loop de ticks que orquestra a simulacao.

Tempo real e escalonado primeiro (FIFO, sem preempcao). Depois os processos de
usuario, com quantum de 1ms, preempcao, feedback e aging.

Sobre a string de referencia de paginas:
  O processo percorre a string INTEIRA durante sua execucao, independente do
  tempo_processador. O tempo_processador controla quantas instrucoes o processo
  executa (quanto tempo de CPU ele ocupa). A string determina quais paginas ele
  acessa — as duas dimensoes sao independentes, conforme a especificacao.
"""

QUANTUM_MS = 1


class Escalonador:
    """Coordena a execucao dos processos usando um relogio logico de ticks."""

    def __init__(self, gerenciador_filas, gerenciador_memoria, gerenciador_es):
        """Recebe as dependencias ja instanciadas (filas, memoria, E/S)."""
        self.filas = gerenciador_filas
        self.memoria = gerenciador_memoria
        self.es = gerenciador_es
        self.tick_atual = 0
        self._contador_bloqueios = 0

    def admitir_chegadas(self, pendentes):
        """Move para as filas os processos cujo tempo de inicializacao ja chegou.

        Antes de admitir, valida recursos, aloca memoria e imprime a identificacao.
        Retorna a lista dos processos que ainda nao chegaram.
        """
        ainda_pendentes = []
        for processo in pendentes:
            if processo.tempo_inicializacao <= self.tick_atual:
                pedido = self._montar_pedido(processo)
                if pedido and not self.es.pedido_e_possivel(pedido):
                    print(f"dispatcher => PID {processo.pid} REJEITADO: "
                          f"pedido de recursos excede o total do sistema {pedido}")
                    print()
                    continue
                frames = self.memoria.alocar_processo(
                    processo.pid, processo.eh_tempo_real, processo.max_working_set
                )
                self._imprimir_identificacao(processo, frames)
                self.filas.admitir(processo)
            else:
                ainda_pendentes.append(processo)
        return ainda_pendentes

    def _imprimir_identificacao(self, processo, frames):
        """Imprime o bloco 'dispatcher =>' de um processo recem-admitido.

        Recursos exibidos como flag 0/1: 1 se usa (qualquer quantidade), 0 se nao usa.
        """
        print("dispatcher =>")
        print(f"  PID: {processo.pid}")
        print(f"  frames: {frames}")
        print(f"  priority: {processo.prioridade}")
        print(f"  time: {processo.tempo_processador}")
        print(f"  printers: {1 if processo.req_impressora > 0 else 0}")
        print(f"  scanners: {1 if processo.req_scanner > 0 else 0}")
        print(f"  modems: {1 if processo.req_modem > 0 else 0}")
        print(f"  drives: {1 if processo.req_sata > 0 else 0}")
        print()

    def executar_tempo_real(self, processo):
        """Executa um processo de tempo real ate o fim (FIFO, sem preempcao).

        Referencia TODAS as paginas da string do processo durante a execucao,
        independente do tempo_processador. Tempo real nao usa recursos de E/S.
        """
        print(f"process {processo.pid} =>")
        print(f"P{processo.pid} STARTED")

        # Referencia todas as paginas da string antes de executar as instrucoes.
        pagina = processo.proxima_pagina()
        while pagina is not None:
            self.memoria.referenciar_pagina(processo.pid, pagina)
            pagina = processo.proxima_pagina()

        for i in range(processo.tempo_restante):
            print(f"P{processo.pid} instruction {i + 1}")
            self.tick_atual += 1

        processo.tempo_restante = 0
        print(f"P{processo.pid} return SIGINT")
        print()
        self.memoria.liberar_processo(processo.pid)

    def executar_usuario(self, processo):
        """Executa um processo de usuario por 1 quantum (preemptivo).

        A cada quantum, referencia a proxima pagina da string (ponteiro proprio
        por processo, continua de onde parou). O processo percorre a string
        inteira ao longo de todos os seus quanta combinados.

        Retorna True se executou, False se voltou a fila por falta de recursos.
        """
        pedido = self._montar_pedido(processo)
        ja_tem_recursos = processo.pid in self.es.alocados_por_pid

        if pedido and not ja_tem_recursos:
            if not self.es.tentar_alocar(processo.pid, pedido):
                self.filas.filas_usuario[processo.prioridade].append(processo)
                return False

        # Referencia a proxima pagina da string (avanca o ponteiro).
        pagina = processo.proxima_pagina()
        if pagina is not None:
            self.memoria.referenciar_pagina(processo.pid, pagina)

        instrucao_atual = processo.tempo_processador - processo.tempo_restante + 1
        print(f"P{processo.pid} instruction {instrucao_atual}")
        processo.tempo_restante -= 1
        self.tick_atual += 1

        if processo.tempo_restante == 0:
            # Esgotou o tempo de CPU: referencia o restante da string antes de sair.
            pagina = processo.proxima_pagina()
            while pagina is not None:
                self.memoria.referenciar_pagina(processo.pid, pagina)
                pagina = processo.proxima_pagina()
            print(f"P{processo.pid} return SIGINT")
            print()
            self.es.liberar(processo.pid)
            self.memoria.liberar_processo(processo.pid)
        else:
            self.filas.rebaixar(processo)
        return True

    def _montar_pedido(self, processo):
        """Monta o dict tipo->quantidade dos recursos que o processo pediu (>0)."""
        bruto = {
            "impressora": processo.req_impressora,
            "scanner":    processo.req_scanner,
            "modem":      processo.req_modem,
            "sata":       processo.req_sata,
        }
        return {tipo: qtd for tipo, qtd in bruto.items() if qtd > 0}

    def rodar(self, processos):
        """Loop principal: avanca os ticks ate todos os processos terminarem."""
        pendentes = list(processos)

        while pendentes or self.filas.tem_tempo_real() or self.filas.tem_usuario():
            pendentes = self.admitir_chegadas(pendentes)

            if self.filas.tem_tempo_real():
                processo = self.filas.proximo_tempo_real()
                self.executar_tempo_real(processo)
            elif self.filas.tem_usuario():
                processo = self.filas.proximo_usuario()
                executou = self.executar_usuario(processo)
                self.filas.aplicar_aging()
                if not executou:
                    self._contador_bloqueios += 1
                    if self._contador_bloqueios > self.filas.total_admitidos:
                        self.tick_atual += 1
                        self._contador_bloqueios = 0
                else:
                    self._contador_bloqueios = 0
            else:
                self.tick_atual += 1
