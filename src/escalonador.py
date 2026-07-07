"""Modulo do escalonador: loop de ticks que orquestra a simulacao.

Tempo real e escalonado primeiro (FIFO, sem preempcao). Depois os processos de
usuario, com quantum de 1ms, preempcao, feedback e aging.

Ciclo de vida de um processo:
  NOVO       → chegou, aguarda na fila global
  PRONTO     → alocou memoria E recursos de E/S, esta na fila de escalonamento
  EXECUTANDO → esta rodando na CPU
  TERMINADO  → concluiu execucao, liberou memoria e recursos
  REJEITADO  → pedido impossivel, nunca sera executado
"""

from src.processo import Processo

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
        self.pids_rejeitados = set()
        self.pids_executados = set()

    def _validar_processo(self, processo):
        """Verifica se o processo tem valores validos e pedido de recursos possivel.

        Retorna (True, None) se valido, (False, motivo) se invalido.
        """
        motivo = processo.tem_valores_invalidos()
        if motivo:
            return False, motivo

        pedido = self._montar_pedido(processo)
        if pedido and not self.es.pedido_e_possivel(pedido):
            return False, f"pedido de E/S impossivel {pedido}"

        from src.memoria import FRAMES_TEMPO_REAL, FRAMES_USUARIO
        limite = FRAMES_TEMPO_REAL if processo.eh_tempo_real else FRAMES_USUARIO
        if processo.max_working_set > limite:
            return False, (f"max_working_set ({processo.max_working_set}) "
                           f"excede o maximo da area ({limite} frames)")
        return True, None

    def _tentar_tornar_pronto(self, processo):
        """Tenta alocar memoria E recursos de E/S para o processo.

        So transita para PRONTO se conseguir AMBOS de uma vez.
        Se a memoria falhar, nao tenta recursos.
        Se a memoria funcionar mas os recursos falharem, devolve a memoria.
        Retorna True se ficou PRONTO, False se deve continuar esperando.
        """
        # Tenta alocar memoria primeiro
        frames = self.memoria.alocar_processo(
            processo.pid, processo.eh_tempo_real, processo.max_working_set
        )
        if frames is False:
            return False  

        # Tenta alocar recursos de E/S (se o processo precisar de algum)
        pedido = self._montar_pedido(processo)
        if pedido:
            if not self.es.tentar_alocar(processo.pid, pedido):
                # Recursos ocupados: devolve a memoria e aguarda
                self.memoria.liberar_processo(processo.pid)
                return False

        # Conseguiu tudo: processo esta PRONTO
        processo.estado = Processo.ESTADO_PRONTO
        self._imprimir_identificacao(processo, frames)
        self.filas.admitir(processo)
        return True

    def processar_fila_global(self, fila_global):
        """Processa a fila global: valida, rejeita impossiveis, torna prontos os que conseguem.

        Tempo real tem prioridade: processos TR sao processados antes dos de usuario.
        Retorna a fila global atualizada.
        """
        chegaram = [p for p in fila_global if p.tempo_inicializacao <= self.tick_atual]
        nao_chegaram = [p for p in fila_global if p.tempo_inicializacao > self.tick_atual]

        # Tempo real primeiro, depois usuario
        tr  = [p for p in chegaram if p.eh_tempo_real]
        usr = [p for p in chegaram if not p.eh_tempo_real]

        ainda_esperando = []
        for processo in tr + usr:
            # Valida uma unica vez quando o processo chega pela primeira vez
            if processo.estado == Processo.ESTADO_NOVO:
                valido, motivo = self._validar_processo(processo)
                if not valido:
                    processo.estado = Processo.ESTADO_REJEITADO
                    self.pids_rejeitados.add(processo.pid)
                    print(f"dispatcher => PID {processo.pid} REJEITADO: {motivo}")
                    print()
                    continue

            # Tenta alocar memoria E recursos juntos
            if not self._tentar_tornar_pronto(processo):
                ainda_esperando.append(processo)

        return ainda_esperando + nao_chegaram

    def _imprimir_identificacao(self, processo, frames):
        """Imprime o bloco 'dispatcher =>' de um processo recem-admitido."""
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

        Recursos ja foram alocados quando o processo ficou PRONTO.
        Tempo real nao usa E/S, entao nao ha recursos para liberar.
        """
        processo.estado = Processo.ESTADO_EXECUTANDO
        print(f"process {processo.pid} =>")
        print(f"P{processo.pid} STARTED")

        pagina = processo.proxima_pagina()
        while pagina is not None:
            self.memoria.referenciar_pagina(processo.pid, pagina)
            pagina = processo.proxima_pagina()

        for i in range(processo.tempo_restante):
            print(f"P{processo.pid} instruction {i + 1}")
            self.tick_atual += 1

        processo.tempo_restante = 0
        processo.estado = Processo.ESTADO_TERMINADO
        self.pids_executados.add(processo.pid)
        print(f"P{processo.pid} return SIGINT")
        print()
        self.memoria.liberar_processo(processo.pid)

    def executar_usuario(self, processo):
        """Executa um processo de usuario por 1 quantum (preemptivo).

        Recursos ja foram alocados quando o processo ficou PRONTO — nao tenta
        alocar novamente aqui. Libera tudo apenas ao terminar.
        """
        processo.estado = Processo.ESTADO_EXECUTANDO

        pagina = processo.proxima_pagina()
        if pagina is not None:
            self.memoria.referenciar_pagina(processo.pid, pagina)

        instrucao_atual = processo.tempo_processador - processo.tempo_restante + 1
        print(f"P{processo.pid} instruction {instrucao_atual}")
        processo.tempo_restante -= 1
        self.tick_atual += 1

        if processo.tempo_restante == 0:
            pagina = processo.proxima_pagina()
            while pagina is not None:
                self.memoria.referenciar_pagina(processo.pid, pagina)
                pagina = processo.proxima_pagina()
            processo.estado = Processo.ESTADO_TERMINADO
            self.pids_executados.add(processo.pid)
            print(f"P{processo.pid} return SIGINT")
            print()
            self.es.liberar(processo.pid)
            self.memoria.liberar_processo(processo.pid)
        else:
            processo.estado = Processo.ESTADO_PRONTO
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
        """Loop principal com fila global.

        Retorna o conjunto de PIDs rejeitados para uso do dispatcher.
        """
        fila_global = list(processos)

        while (fila_global or
               self.filas.tem_tempo_real() or
               self.filas.tem_usuario()):

            fila_global = self.processar_fila_global(fila_global)

            if self.filas.tem_tempo_real():
                processo = self.filas.proximo_tempo_real()
                self.executar_tempo_real(processo)
            elif self.filas.tem_usuario():
                processo = self.filas.proximo_usuario()
                self.executar_usuario(processo)
                self.filas.aplicar_aging()
            else:
                self.tick_atual += 1

        return self.pids_rejeitados