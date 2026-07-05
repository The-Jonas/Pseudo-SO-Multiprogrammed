"""Contratos (interfaces) dos gerenciadores do pseudo-SO.

Define as assinaturas que cada modulo deve implementar.
NAO contem logica: apenas assinaturas e documentacao.
"""


class GerenciadorMemoria:
    """Gerencia memoria virtual por paginacao."""

    def alocar_processo(self, pid, eh_tempo_real, max_working_set):
        """Reserva frames para o processo na area correta (tempo real ou usuario).

        Retorna a quantidade de frames alocada, ou False se nao houver espaco.
        """
        raise NotImplementedError

    def referenciar_pagina(self, pid, pagina):
        """Acessa uma pagina do processo aplicando LRU local.

        Retorna True se houve page fault, False se hit ou pre-carga.
        """
        raise NotImplementedError

    def liberar_processo(self, pid):
        """Devolve os frames do processo ao pool ao final da execucao."""
        raise NotImplementedError

    def total_faltas(self, pid):
        """Retorna o total de page faults contabilizados para o processo."""
        raise NotImplementedError


class GerenciadorES:
    """Gerencia alocacao exclusiva e atomica de recursos de E/S."""

    def pedido_e_possivel(self, pedido):
        """True se o pedido (dict tipo->qtd) nao excede o total fisico do sistema."""
        raise NotImplementedError

    def tentar_alocar(self, pid, pedido):
        """Concede TODAS as unidades do pedido de uma vez, ou nenhuma (atomico).

        Retorna True se alocou tudo, False se faltou qualquer recurso.
        """
        raise NotImplementedError

    def requisitar(self, pid, recurso):
        """Aloca 1 unidade de um recurso. Deve delegar para tentar_alocar."""
        raise NotImplementedError

    def liberar(self, pid):
        """Libera todos os recursos que o processo detinha."""
        raise NotImplementedError


class GerenciadorArquivos:
    """Gerencia o sistema de arquivos em disco."""

    def executar_operacao(self, pid, codigo, nome, blocos, eh_tempo_real):
        """Executa create (0) ou delete (1) e imprime a mensagem de resultado.

        codigo 0 = criar (usa 'blocos'), codigo 1 = deletar (ignora 'blocos').
        eh_tempo_real determina as permissoes de delete.
        """
        raise NotImplementedError

    def imprimir_mapa(self):
        """Imprime o mapa de ocupacao do disco ao final da execucao."""
        raise NotImplementedError
