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

    def admitir_chegadas(self, processos):
        """Admite nas filas os processos cujo tempo de inicializacao ja chegou."""
        # TODO
        raise NotImplementedError

    def executar_tempo_real(self):
        """Executa ate o fim todos os processos de tempo real (FIFO, sem preempcao)."""
        # TODO: para cada processo, referenciar paginas via self.memoria
        raise NotImplementedError

    def executar_usuario(self):
        """Executa um processo de usuario por 1 quantum, aplicando feedback e aging."""
        # TODO: requisitar/liberar E/S, referenciar paginas, rebaixar se nao terminou
        raise NotImplementedError

    def rodar(self, processos):
        """Loop principal: avanca os ticks ate todos os processos terminarem."""
        # TODO: enquanto houver processos pendentes ou nas filas, avancar o tick
        raise NotImplementedError