"""Modulo de memoria: paginacao com LRU local e contagem de page faults.

Memoria principal de 20 frames, cada frame com 1 KiB.

A politica usada aqui e LRU LOCAL: cada processo possui seu proprio conjunto de
paginas residentes, limitado pelo max_working_set informado em processes.txt.

A alocacao registra o processo sempre que o working set e valido e cabe no total
fisico de frames. Assim, processos como P4, P5, P10 etc. continuam tendo suas
referencias de pagina contabilizadas corretamente.
"""

from src.interfaces import GerenciadorMemoria


TOTAL_FRAMES = 20


class Memoria(GerenciadorMemoria):
    """Gerenciador de memoria virtual paginada do pseudo-SO."""

    def __init__(self):
        """Inicializa as estruturas de controle por processo."""

        # Paginas residentes por processo.
        # Ordem da lista: menos recente no indice 0 e mais recente no final.
        self.paginas_por_processo = {}

        # Working set maximo de cada processo.
        self.working_set_por_processo = {}

        # Frames concedidos para cada processo.
        self.frames_alocados_por_processo = {}

        # Controle para a primeira referencia de cada processo.
        # A primeira pagina e tratada como pre-carga e nao conta page fault.
        self.primeira_referencia = {}

        # Historico de faltas preservado mesmo depois que o processo termina.
        self.faltas_por_processo = {}

    def alocar_processo(self, pid, eh_tempo_real, max_working_set):
        """Registra um processo na memoria.

        Retorna:
            - quantidade de frames concedida, se o pedido for valido;
            - False, se o pedido for invalido ou maior que a memoria fisica.

        Observacao:
        O parametro eh_tempo_real e mantido para compatibilidade com o restante
        do projeto, mas aqui a paginacao usa LRU local por processo.
        """

        try:
            max_working_set = int(max_working_set)
        except (TypeError, ValueError):
            self.faltas_por_processo.setdefault(pid, 0)
            return False

        if max_working_set <= 0 or max_working_set > TOTAL_FRAMES:
            self.faltas_por_processo.setdefault(pid, 0)
            return False

        # Se o processo ja foi registrado, apenas retorna os frames dele.
        if pid in self.frames_alocados_por_processo:
            return self.frames_alocados_por_processo[pid]

        self.frames_alocados_por_processo[pid] = max_working_set
        self.working_set_por_processo[pid] = max_working_set
        self.paginas_por_processo[pid] = []
        self.primeira_referencia[pid] = True
        self.faltas_por_processo.setdefault(pid, 0)

        return max_working_set

    def referenciar_pagina(self, pid, pagina):
        """Referencia uma pagina do processo aplicando LRU local.

        Retorna:
            - True, se houve page fault;
            - False, se houve hit ou se foi a primeira referencia/pre-carga.
        """

        if pid not in self.paginas_por_processo:
            # Processo nao registrado por pedido realmente invalido.
            # Mantem a saida final estavel.
            self.faltas_por_processo.setdefault(pid, 0)
            return False

        paginas = self.paginas_por_processo[pid]
        working_set = self.working_set_por_processo[pid]

        # Primeira referencia: pre-carga, nao conta falta de pagina.
        if self.primeira_referencia.get(pid, False):
            self.primeira_referencia[pid] = False
            paginas.append(pagina)
            return False

        # Hit: pagina ja esta residente.
        # Move para o final para marcar como mais recentemente usada.
        if pagina in paginas:
            paginas.remove(pagina)
            paginas.append(pagina)
            return False

        # Miss: houve page fault.
        self.faltas_por_processo[pid] = self.faltas_por_processo.get(pid, 0) + 1

        # Se ainda cabe no working set, apenas adiciona.
        if len(paginas) < working_set:
            paginas.append(pagina)
        else:
            # LRU local: remove a pagina menos recentemente usada do proprio processo.
            paginas.pop(0)
            paginas.append(pagina)

        return True

    def liberar_processo(self, pid):
        """Libera as estruturas volateis do processo.

        O total de faltas de pagina nao e apagado, pois precisa ser impresso
        no final da simulacao.
        """

        self.frames_alocados_por_processo.pop(pid, None)
        self.paginas_por_processo.pop(pid, None)
        self.working_set_por_processo.pop(pid, None)
        self.primeira_referencia.pop(pid, None)

    def total_faltas(self, pid):
        """Retorna o total de page faults contabilizados para um processo."""

        return self.faltas_por_processo.get(pid, 0)

    def total_faltas_por_processo(self):
        """Retorna uma copia do historico de faltas por processo."""

        return dict(self.faltas_por_processo)