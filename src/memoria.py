"""Modulo de memoria: paginacao com LRU local e contagem de page faults.

Memoria principal de 20 frames (cada frame 1k):
  - 8 frames reservados para processos de tempo real
  - 12 frames para processos de usuario
As areas nunca se misturam. Substituicao por LRU no escopo local de cada processo.
Pre-carga de 1 pagina por processo (nao conta como falta).

Implementa a interface GerenciadorMemoria (ver src/interfaces.py).
"""

from src.interfaces import GerenciadorMemoria

TOTAL_FRAMES = 20
FRAMES_TEMPO_REAL = 8
FRAMES_USUARIO = 12


class Memoria(GerenciadorMemoria):
    """Implementacao concreta do gerenciador de memoria."""

    def __init__(self):
        """Inicializa os pools de frames de tempo real e de usuario."""
        self.frames_livres_rt = FRAMES_TEMPO_REAL
        self.frames_livres_user = FRAMES_USUARIO

        # Estruturas por processo
        self.paginas_por_processo = {}      # pid -> lista de paginas (ordem de uso, LRU no inicio)
        self.faltas_por_processo = {}       # pid -> contador de faltas
        self.working_set_por_processo = {}  # pid -> max_working_set
        self.area_por_processo = {}         # pid -> 'rt' ou 'user'
        self.primeira_referencia = {}       # pid -> bool (True se ainda nao houve referencia)

    def alocar_processo(self, pid, eh_tempo_real, max_working_set):
        """Reserva um frame para a pre-carga e define o working set.
        Retorna False se nao houver pelo menos 1 frame livre na area correta.
        """
        # Verifica se ha pelo menos 1 frame livre na area apropriada
        if eh_tempo_real:
            if self.frames_livres_rt < 1:
                return False
            self.area_por_processo[pid] = 'rt'
            # Nao subtraimos frames agora, pois a alocacao e sob demanda
        else:
            if self.frames_livres_user < 1:
                return False
            self.area_por_processo[pid] = 'user'

        self.paginas_por_processo[pid] = []    # lista vazia, a pre-carga sera feita no primeiro acesso
        self.faltas_por_processo[pid] = 0
        self.working_set_por_processo[pid] = max_working_set
        self.primeira_referencia[pid] = True   # aguardando a primeira pagina

        return True

    def referenciar_pagina(self, pid, pagina):
        """Acessa uma pagina; aplica LRU local e retorna True se houve page fault.
        A primeira referencia de cada processo e uma pre-carga e nao conta como falta.
        """
        if pid not in self.paginas_por_processo:
            return False  # processo nao alocado

        paginas = self.paginas_por_processo[pid]
        working_set = self.working_set_por_processo[pid]

        # Se for a primeira referencia, faz a pre-carga sem contar falta
        if self.primeira_referencia.get(pid, False):
            self.primeira_referencia[pid] = False
            # Carrega a pagina (se nao estiver ja, mas como a lista esta vazia, adiciona)
            paginas.append(pagina)
            # Nao incrementa faltas
            return False  # hit (pre-carga)

        # Caso normal: verifica se a pagina ja esta na memoria
        if pagina in paginas:
            # Hit: move para o final (mais recente)
            paginas.remove(pagina)
            paginas.append(pagina)
            return False

        # Page fault
        self.faltas_por_processo[pid] += 1

        if len(paginas) < working_set:
            # Ainda ha espaco no working set
            paginas.append(pagina)
        else:
            # Working set cheio: substitui a pagina menos recente (LRU)
            paginas.pop(0)      # remove a mais antiga
            paginas.append(pagina)

        return True

    def liberar_processo(self, pid):
        """Devolve os frames do processo ao pool ao final da execucao."""
        if pid not in self.paginas_por_processo:
            return

        # Remove todas as referencias ao processo
        del self.paginas_por_processo[pid]
        del self.faltas_por_processo[pid]
        del self.working_set_por_processo[pid]
        del self.area_por_processo[pid]
        if pid in self.primeira_referencia:
            del self.primeira_referencia[pid]

    def total_faltas(self, pid):
        """Retorna o total de page faults do processo."""
        return self.faltas_por_processo.get(pid, 0)