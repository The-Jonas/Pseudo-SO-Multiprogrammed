"""Modulo de filas: fila global, tempo real e filas de usuario. Dono: nucleo (voce).

Menor valor de prioridade = maior prioridade no escalonamento.
Tempo real = prioridade 0. Usuario = prioridades 1 (alta), 2 (media), 3 (baixa).
"""

from collections import deque

MAX_PROCESSOS = 1000


class GerenciadorFilas:
    """Mantem as filas de prontos e classifica os processos por tipo."""

    def __init__(self):
        """Cria a fila de tempo real (FIFO) e as 3 filas de usuario."""
        self.fila_tempo_real = deque()
        self.filas_usuario = {1: deque(), 2: deque(), 3: deque()}
        self.total_admitidos = 0

    def admitir(self, processo):
        """Insere um processo na fila correta conforme sua prioridade.

        Respeita o limite global de MAX_PROCESSOS. Retorna False se o limite
        foi atingido.
        """
        # TODO: classificar entre tempo real e usuario, respeitar o limite
        raise NotImplementedError

    def proximo_tempo_real(self):
        """Retorna o proximo processo de tempo real (FIFO), ou None se vazio."""
        # TODO
        raise NotImplementedError

    def proximo_usuario(self):
        """Retorna o proximo processo de usuario da fila de maior prioridade nao vazia."""
        # TODO
        raise NotImplementedError

    def rebaixar(self, processo):
        """Aplica feedback: devolve o processo a uma fila de menor prioridade."""
        # TODO
        raise NotImplementedError

    def aplicar_aging(self):
        """Sobe a prioridade de processos que esperam ha muito tempo (evita starvation)."""
        # TODO
        raise NotImplementedError