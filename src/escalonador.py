"""Modulo do escalonador: loop de ticks que orquestra a simulacao. Dono: nucleo (voce).

Tempo real e escalonado primeiro (FIFO, sem preempcao). Depois os processos de
usuario, com quantum de 1ms, preempcao, feedback e aging. A cada execucao,
chama os gerenciadores de memoria, E/S e arquivos.
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

    def admitir_chegadas(self, pendentes):
        """Move para as filas os processos cujo tempo de inicialização já chegou.
        'pendentes' e a lista de processos que ainda não entraram no sistema.
        Remove dela os que foram admitidos. Antes de admitir, aloca memória e
        imprime a identificação (papel do despachante).
        """
        ainda_pendentes = []
        for processo in ainda_pendentes:
            if processo.tempo_inicializacao <= self.tick_atual: 
                #Rejeita pedidos de recursos impossíveis (mais do que existe no sistema)
                pedido = self.montar_pedido(processo)
                if pedido and not self.es_pedido_e_possivel(pedido):
                    print(f"dispatcher => PID {processo.pid} REJEITADO: "
                          f"pedido de recursos excede o total do sistema {pedido}")
                    print()
                    continue # Ou seja, não cria e nem admite esse processo
                frames = self.memoria.alocar_processo(
                    processo.pid, processo.eh_tempo_real, processo.max_working_set
                )
                self._imprimir_identificacao(processo, frames)
                self.filas_admitir(processo)
            else:
                ainda_pendentes.append(processo)
        return ainda_pendentes        

    def executar_tempo_real(self, processo, frames):
        """Imprime o bloco 'dispatcher =>' de um processo recém-admitido.
        
        Os campos de recurso são exibidos como flag binária: 1 se o processo usa
        aquele recurso (em qualquer quantidade que seja), 0 se não usa. A quantidade real
        segue registrada internamente para alocação."""

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
        """Executa um processo de tempo real até o fim (FIFO, sem preempção)
        
        Consome todo o tempo restante de uma vez. Referencia as páginas do
        processo na memória (contabilizando page faults) e libera a memória ao fim
        Tempo real não usa recursos de E/S."""
        
        print(f"process {processo.pid} =>")
        print(f"P{processo.pid} STARTED")
        for i in range(processo.tempo_restante):
            # Cada 'instrução' referencia a próxima página da string do processo
            if i < len(processo.string_paginas):
                self.memoria.referenciar_pagina(processo.pid, processo.string_paginas[i])
            print(f"P{processo.pid} instruction {i + 1}")
            self.tick_atual += 1
        processo.tempo_restante = 0
        print(f"P{processo.pid} return SIGINT")
        print()
        self.memoria.liberar_processo(processo.pid)

    def executar_usuario(self, processo):
        """Executa um processo de usuario por 1 quantum (preemptivo).
        
        Antes de rodar, garante posse de TODOS os recursos pedidos (alocação
        atômica). Se ainda não os tem e não consegue todos agora, devolve o processo a fila
        sem executar (passa a vez, sem reter nada). Se já os detém (de um quantum anterior),
        executa direto. Ao terminar, libera tudo.
        
        Returna True se o processo executou neste quantum, False se só voltou a fila"""
        
        pedido = self.montar_pedido(processo)
        ja_tem_recursos = processo.pid in self.es.alocados_por_pid
        
        if pedido and not ja_tem_recursos:
            if not self.es.tentar_alocar(processo.pid, pedido):
                # Recursos ocupados por outro processo : não executa agora
                # devolve a fila na mesma prioridade e tenta de novo depois.
                self.filas.filas_usuario[processo.prioridade].append(processo)
                return False
        
        indice = processo.tempo_processador - processo.tempo_restante
        if indice < len(processo.string_paginas):
            self.memoria.referenciar_pagina(processo.pid, processo.string_paginas[indice])
        
        print(f"P{processo.pid} instruction {indice + 1}")
        processo.tempo_restante -= 1
        self.tick_atual += 1
        
        if processo.tempo_restante == 0:
            print(f"P{processo.pid} return SIGINT")
            print()
            self.es_liberar(processo.pid)
            self.memoria.liberar_processo(processo.pid)
        else:
            # Preempção: Não terminou no quantum, volta para uma fila menor
            # Mantém os recursos (sem preempção de E/S) até finalizar
            self.filas.rebaixar(processo)
        return True        
    
    def _montar_pedido(self, processo):
        """Monta o dict tipo->quantidade dos recursos que o processo pediu (>0)."""
        bruto = {
            "impressora": processo.req_impressora,
            "scanner"   : processo.req_scanner,
            "modem"     : processo.req_modem,
            "sata"      : processo.req_sata,
        }
        return {tipo: qtd for tipo, qtd in bruto.items() if qtd > 0}

    def rodar(self, processos):
        """Loop principal: avança os ticks até todos os processos terminarem.
        
        'processos' e a lista completa de processos criados (ordenada por chegada).
        Encerra quando não há mais pendentes, nem processos nas filas."""
        
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
                    # Ninguém conseguiu recursos neste passo: avança o tempo para
                    # não girar em falso. (Recursos só se liberam quando um processo
                    # que os detém termina, o que ocorre em outro tick).
                    self.contador_bloqueios = getattr(self, "_contador_bloqueios", 0) + 1
                    if self._contador_bloqueios > self.filas.total_admitidos:
                        self.tick_atual += 1
                        self._contador_bloqueios = 0
                else:
                    self._contador_bloqueios = 0
            else:
                # Nenhum processo pronto ainda: avança o tempo até a próxima chegada
                self.tick_atual += 1