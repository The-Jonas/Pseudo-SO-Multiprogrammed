"""Modulo de E/S: alocacao exclusiva de recursos.

Recursos disponiveis:
  - 1 scanner
  - 2 impressoras
  - 1 modem
  - 2 dispositivos SATA
Cada recurso e alocado a um processo por vez, sem preempcao.
Processos de tempo real nao requisitam recursos de E/S.

Implementa a interface GerenciadorES (ver src/interfaces.py).
"""

from src.interfaces import GerenciadorES

RECURSOS_DISPONIVEIS = {"scanner": 1, "impressora": 2, "modem": 1, "sata": 2}


class ES(GerenciadorES):
    """Implementacao concreta do gerenciador de E/S."""

    def __init__(self):
        self.disponiveis = RECURSOS_DISPONIVEIS.copy()
        self.alocados_por_processo = {}

    def requisitar(self, pid, recurso):
        if recurso not in self.disponiveis:
            return False
        if self.disponiveis[recurso] <= 0:
            return False
        self.disponiveis[recurso] -= 1
        if pid not in self.alocados_por_processo:
            self.alocados_por_processo[pid] = []
        self.alocados_por_processo[pid].append(recurso)
        return True

    def liberar(self, pid):
        if pid not in self.alocados_por_processo:
            return
        for recurso in self.alocados_por_processo[pid]:
            self.disponiveis[recurso] += 1
        del self.alocados_por_processo[pid]