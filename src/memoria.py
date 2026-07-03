"""Modulo de memoria: paginacao com LRU local e contagem de page faults.

Memoria principal de 20 frames, cada frame com 1 KiB:
  - 8 frames reservados para processos de tempo real
  - 12 frames reservados para processos de usuario

As duas areas nunca se misturam. A substituicao de paginas usa LRU no escopo
local de cada processo. A primeira pagina referenciada por cada processo e
tratada como pre-carga e nao contabiliza page fault.
"""

from src.interfaces import GerenciadorMemoria


TOTAL_FRAMES = 20
FRAMES_TEMPO_REAL = 8
FRAMES_USUARIO = 12


class Memoria(GerenciadorMemoria):
    """Gerenciador de memoria virtual paginada do pseudo-SO."""

    def __init__(self):
        self.frames_livres_rt = FRAMES_TEMPO_REAL
        self.frames_livres_user = FRAMES_USUARIO

        # Estado dos processos ativos.
        # A lista guarda as paginas do menos recente para o mais recente.
        self.paginas_por_processo = {}
        self.working_set_por_processo = {}
        self.frames_alocados_por_processo = {}
        self.area_por_processo = {}
        self.primeira_referencia = {}

        # Historico preservado mesmo apos liberar o processo, pois a
        # especificacao pede imprimir as faltas de pagina ao final da execucao.
        self.faltas_por_processo = {}

    def alocar_processo(self, pid, eh_tempo_real, max_working_set):
        """Reserva frames para um processo na area correta.

        Retorna a quantidade de frames alocada quando a alocacao for possivel.
        Retorna False quando o pedido for invalido ou nao houver frames livres
        suficientes. A pre-carga e feita no primeiro acesso de pagina.
        """
        try:
            max_working_set = int(max_working_set)
        except (TypeError, ValueError):
            return False

        if max_working_set <= 0:
            return False

        # Evita dupla alocacao do mesmo PID.
        if pid in self.frames_alocados_por_processo:
            return self.frames_alocados_por_processo[pid]

        if eh_tempo_real:
            if max_working_set > FRAMES_TEMPO_REAL:
                return False
            if self.frames_livres_rt < max_working_set:
                return False
            self.frames_livres_rt -= max_working_set
            area = "rt"
        else:
            if max_working_set > FRAMES_USUARIO:
                return False
            if self.frames_livres_user < max_working_set:
                return False
            self.frames_livres_user -= max_working_set
            area = "user"

        self.area_por_processo[pid] = area
        self.frames_alocados_por_processo[pid] = max_working_set
        self.working_set_por_processo[pid] = max_working_set
        self.paginas_por_processo[pid] = []
        self.primeira_referencia[pid] = True
        self.faltas_por_processo.setdefault(pid, 0)

        return max_working_set

    def referenciar_pagina(self, pid, pagina):
        """Referencia uma pagina do processo.

        Retorna True quando ocorre page fault e False quando ocorre hit ou
        pre-carga. A substituicao e LRU local: somente paginas do proprio
        processo podem ser removidas.
        """
        if pid not in self.paginas_por_processo:
            return False

        paginas = self.paginas_por_processo[pid]
        working_set = self.working_set_por_processo[pid]

        if self.primeira_referencia.get(pid, False):
            self.primeira_referencia[pid] = False
            paginas.append(pagina)
            return False

        if pagina in paginas:
            paginas.remove(pagina)
            paginas.append(pagina)
            return False

        self.faltas_por_processo[pid] = self.faltas_por_processo.get(pid, 0) + 1

        if len(paginas) < working_set:
            paginas.append(pagina)
        else:
            paginas.pop(0)
            paginas.append(pagina)

        return True

    def liberar_processo(self, pid):
        """Libera os frames reservados pelo processo.

        O historico de faltas de pagina nao e apagado.
        """
        if pid not in self.frames_alocados_por_processo:
            return

        frames = self.frames_alocados_por_processo.pop(pid)
        area = self.area_por_processo.pop(pid)

        if area == "rt":
            self.frames_livres_rt += frames
            if self.frames_livres_rt > FRAMES_TEMPO_REAL:
                self.frames_livres_rt = FRAMES_TEMPO_REAL
        else:
            self.frames_livres_user += frames
            if self.frames_livres_user > FRAMES_USUARIO:
                self.frames_livres_user = FRAMES_USUARIO

        self.paginas_por_processo.pop(pid, None)
        self.working_set_por_processo.pop(pid, None)
        self.primeira_referencia.pop(pid, None)

    def total_faltas(self, pid):
        """Retorna o total de page faults contabilizados para ``pid``."""
        return self.faltas_por_processo.get(pid, 0)

    def total_faltas_por_processo(self):
        """Retorna uma copia do historico de faltas por processo."""
        return dict(self.faltas_por_processo)
