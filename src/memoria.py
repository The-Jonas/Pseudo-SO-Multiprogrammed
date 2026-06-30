"""Modulo de memoria: paginacao com LRU local e contagem de page faults.

Memoria principal de 20 frames (cada frame 1k):
  - 8 frames reservados para processos de tempo real
  - 12 frames para processos de usuario
As areas nunca se misturam. Substituicao por LRU no escopo local de cada processo.
Pre-carga de 1 pagina por processo.

Implementa a interface GerenciadorMemoria (ver src/interfaces.py).
Validacao: com o string.txt de exemplo, P0 deve dar 6 faltas e P1, 14 faltas.
"""

from src.interfaces import GerenciadorMemoria

TOTAL_FRAMES = 20
FRAMES_TEMPO_REAL = 8
FRAMES_USUARIO = 12


class Memoria(GerenciadorMemoria):
    """Implementacao concreta do gerenciador de memoria."""

    def __init__(self):
        """Inicializa os pools de frames de tempo real e de usuario."""
        # TODO: estruturas de frames por area e contadores de falta por pid
        raise NotImplementedError

    def alocar_processo(self, pid, eh_tempo_real, max_working_set):
        """Reserva frames na area correta e pre-carrega 1 pagina."""
        # TODO
        raise NotImplementedError

    def referenciar_pagina(self, pid, pagina):
        """Acessa uma pagina; aplica LRU local e retorna True se houve page fault."""
        # TODO
        raise NotImplementedError

    def liberar_processo(self, pid):
        """Devolve os frames do processo ao pool."""
        # TODO
        raise NotImplementedError

    def total_faltas(self, pid):
        """Retorna o total de page faults do processo."""
        # TODO
        raise NotImplementedError