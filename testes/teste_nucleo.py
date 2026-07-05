"""Teste isolado do NUCLEO (filas + escalonador), dono: voce.

Usa stubs LOCAIS de memoria e E/S definidos aqui dentro, para testar a sua
parte sem depender da implementacao real dos colegas. Nao faz parte da entrega
funcional: e apenas um andaime de desenvolvimento.

Executar da raiz do projeto:
    python3 testes/teste_nucleo.py
"""

import sys
import os

# Garante que a raiz do projeto esta no path (para importar 'src').
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processo import Processo
from src.filas import GerenciadorFilas
from src.escalonador import Escalonador


class MemoriaStub:
    """Stub de memoria: aloca frames fixos e conta cada referencia como falta."""

    def __init__(self):
        """Inicializa o dicionario de faltas por pid."""
        self.faltas = {}

    def alocar_processo(self, pid, eh_tempo_real, max_working_set):
        """Devolve os frames pedidos, sem logica de area."""
        self.faltas[pid] = 0
        return max_working_set

    def referenciar_pagina(self, pid, pagina):
        """Conta toda referencia como falta (stub, nao implementa LRU)."""
        self.faltas[pid] = self.faltas.get(pid, 0) + 1
        return True

    def liberar_processo(self, pid):
        """Nao faz nada no stub."""
        pass

    def total_faltas(self, pid):
        """Retorna o total de faltas contabilizadas."""
        return self.faltas.get(pid, 0)


class ESStub:
    """Stub de E/S com alocacao atomica minima, so para testar o nucleo."""

    RECURSOS = {"impressora": 2, "scanner": 1, "modem": 1, "sata": 2}

    def __init__(self):
        """Inicializa recursos livres e o registro de alocacao por pid."""
        self.livres = dict(self.RECURSOS)
        self.alocados_por_pid = {}

    def pedido_e_possivel(self, pedido):
        """True se o pedido cabe no total do sistema."""
        return all(q <= self.RECURSOS.get(t, 0) for t, q in pedido.items())

    def tentar_alocar(self, pid, pedido):
        """Aloca tudo-ou-nada."""
        if any(self.livres.get(t, 0) < q for t, q in pedido.items()):
            return False
        for t, q in pedido.items():
            self.livres[t] -= q
        self.alocados_por_pid[pid] = dict(pedido)
        return True

    def requisitar(self, pid, recurso):
        """Aloca 1 unidade, delegando para tentar_alocar."""
        return self.tentar_alocar(pid, {recurso: 1})

    def liberar(self, pid):
        """Devolve os recursos do processo ao pool."""
        for t, q in self.alocados_por_pid.pop(pid, {}).items():
            self.livres[t] += q


def cenario_tempo_real():
    """Dois processos de tempo real: devem rodar ate o fim, sem intercalar."""
    print("=== TEMPO REAL (FIFO, sem preempcao) ===")
    processos = [
        Processo(0, 2, 0, 3, 4, 0, 0, 0, 0, [1, 2, 3, 4, 1, 2]),
        Processo(1, 8, 0, 2, 8, 0, 0, 0, 0, [7, 0, 1, 2]),
    ]
    esc = Escalonador(GerenciadorFilas(), MemoriaStub(), ESStub())
    esc.rodar(processos)


def cenario_usuario():
    """Tres processos de usuario: devem intercalar por quantum e todos terminar."""
    print("=== USUARIO (quantum, feedback, aging) ===")
    processos = [
        Processo(0, 0, 1, 4, 3, 0, 0, 0, 0, [1, 2, 3, 1]),
        Processo(1, 0, 2, 3, 2, 0, 0, 0, 0, [5, 6, 5]),
        Processo(2, 1, 3, 5, 5, 0, 0, 0, 0, [1, 1, 2, 2, 3]),
    ]
    esc = Escalonador(GerenciadorFilas(), MemoriaStub(), ESStub())
    esc.rodar(processos)


def cenario_recursos():
    """Contencao (disputa da impressora) e rejeicao (pedido impossivel)."""
    print("=== RECURSOS: contencao + rejeicao ===")
    processos = [
        Processo(0, 0, 1, 2, 3, 2, 0, 0, 0, [1, 2]),   # pede 2 impressoras
        Processo(1, 0, 1, 2, 3, 2, 0, 0, 0, [3, 4]),   # tambem pede 2 -> espera
        Processo(2, 0, 1, 1, 3, 3, 0, 0, 0, [9]),      # pede 3 -> rejeitado
    ]
    esc = Escalonador(GerenciadorFilas(), MemoriaStub(), ESStub())
    esc.rodar(processos)


if __name__ == "__main__":
    cenario_tempo_real()
    cenario_usuario()
    cenario_recursos()
    print("Todos os cenarios rodaram sem erro.")
