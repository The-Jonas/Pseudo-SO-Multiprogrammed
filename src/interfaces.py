"""Contratos (interfaces) dos gerenciadores do pseudo-SO.

Define as assinaturas que cada modulo deve implementar. Cada membro programa
contra estas interfaces, usando stubs dos modulos dos colegas ate a integracao.
NAO contem logica: apenas as assinaturas e a documentacao de cada metodo.
"""

class GerenciadorMemoria:
    """Gerencia memoria virtual por paginacao. Dono: colega bom."""

    def alocar_processo(self, pid, eh_tempo_real, max_working_set):
        """Reserva frames para o processo na area correta (tempo real ou usuario).

        Retorna False se nao houver frames livres suficientes na area dele.
        Faz a pre-carga de 1 pagina.
        """
        raise NotImplementedError

    def referenciar_pagina(self, pid, pagina):
        """Acessa uma pagina do processo, aplicando LRU no escopo local.

        Retorna True se houve page fault (pagina nao estava carregada), False se hit.
        """
        raise NotImplementedError

    def liberar_processo(self, pid):
        """Devolve os frames do processo ao pool ao final da execucao."""
        raise NotImplementedError

    def total_faltas(self, pid):
        """Retorna o total de page faults contabilizados para o processo."""
        raise NotImplementedError


class GerenciadorES:
    """Gerencia alocacao exclusiva de recursos de E/S. Dono: colega bom."""

    def requisitar(self, pid, recurso):
        """Tenta alocar um recurso exclusivo para o processo.

        'recurso' e uma string: 'scanner', 'impressora', 'modem' ou 'sata'.
        Retorna False se o recurso ja estiver ocupado. Processos de tempo real
        nunca requisitam E/S.
        """
        raise NotImplementedError

    def liberar(self, pid):
        """Libera todos os recursos que o processo detinha."""
        raise NotImplementedError


class GerenciadorArquivos:
    """Gerencia o sistema de arquivos em disco. Dono: colega fraco."""

    def executar_operacao(self, pid, codigo, nome, blocos):
        """Executa uma operacao de arquivo.

        codigo 0 = criar (usa 'blocos'), codigo 1 = deletar (ignora 'blocos').
        Aplica as regras de permissao (tempo real x usuario) e a alocacao
        contigua com first-fit. Retorna a mensagem de sucesso ou falha.
        """
        raise NotImplementedError

    def imprimir_mapa(self):
        """Imprime o mapa de ocupacao do disco ao final da execucao."""
        raise NotImplementedError