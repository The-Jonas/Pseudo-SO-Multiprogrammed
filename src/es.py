"""Modulo de E/S: alocacao exclusiva de recursos. 

Recursos disponiveis:
  - 1 scanner
  - 2 impressoras
  - 1 modem
  - 2 dispositivos SATA
Cada recurso e alocado a um processo por vez, sem preempcao. Processos de
tempo real nao requisitam recursos de E/S.

Implementa a interface GerenciadorES (ver src/interfaces.py).
"""

from src.interfaces import GerenciadorES

RECURSOS_DISPONIVEIS = {"scanner": 1, "impressora": 2, "modem": 1, "sata": 2}


class ES(GerenciadorES):
    """Implementacao concreta do gerenciador de E/S."""

    def __init__(self):
        """Inicializa os contadores de disponibilidade de cada recurso."""
        # TODO: controlar quantos de cada recurso estao livres e quem detem o que
        raise NotImplementedError

    def requisitar(self, pid, recurso):
        """Aloca um recurso exclusivo, se disponivel. Retorna False se ocupado."""
        # TODO
        raise NotImplementedError

    def liberar(self, pid):
        """Libera todos os recursos detidos pelo processo."""
        # TODO
        raise NotImplementedError
