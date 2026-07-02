"""Modulo de E/S: alocacao exclusiva de recursos. Dono: colega bom.

Recursos disponiveis no sistema:
  - 1 scanner
  - 2 impressoras
  - 1 modem
  - 2 dispositivos SATA

Regras a implementar:
  - Cada unidade de recurso e alocada a um processo por vez, sem preempcao:
    o processo so libera ao terminar.
  - Processos de tempo real NAO requisitam recursos de E/S.
  - Alocacao ATOMICA (tudo-ou-nada): so concede se conseguir todas as unidades
    pedidas de uma vez; caso contrario, nao concede nenhuma. Isso evita reter
    recursos parciais e, portanto, evita deadlock.

O escalonador (nucleo) depende dos seguintes membros desta classe:
  - atributo  alocados_por_pid : dict  (pid -> {tipo: quantidade})
  - metodo    pedido_e_possivel(pedido)
  - metodo    tentar_alocar(pid, pedido)
  - metodo    liberar(pid)
Mantenha essas assinaturas para a integracao funcionar sem alteracoes no nucleo.

Implementa a interface GerenciadorES (ver src/interfaces.py).
"""

from src.interfaces import GerenciadorES

RECURSOS_TOTAIS = {"scanner": 1, "impressora": 2, "modem": 1, "sata": 2}


class ES(GerenciadorES):
    """Implementacao do gerenciador de E/S com alocacao atomica. [A IMPLEMENTAR]"""

    def __init__(self):
        """Inicializa os recursos livres e o registro de quem detem o que.

        Sugestao de estruturas:
          self.livres = dict(RECURSOS_TOTAIS)   # unidades disponiveis por tipo
          self.alocados_por_pid = {}            # pid -> {tipo: quantidade}
        O atributo alocados_por_pid E OBRIGATORIO: o escalonador o consulta para
        saber se um processo ja detem recursos.
        """
        self.livres = dict(RECURSOS_TOTAIS)
        self.alocados_por_pid = {}
        raise NotImplementedError("Implementar inicializacao do gerenciador de E/S")

    def pedido_e_possivel(self, pedido):
        """Retorna True se o pedido cabe no TOTAL do sistema (ignorando ocupacao).

        'pedido' e um dict tipo->quantidade. Usado na criacao do processo para
        rejeitar pedidos impossiveis (ex.: 3 impressoras, quando so existem 2).
        """
        raise NotImplementedError

    def tentar_alocar(self, pid, pedido):
        """Tenta conceder TODAS as unidades do pedido de uma vez (atomico).

        Retorna True e efetiva a alocacao se todas couberem nos recursos livres.
        Retorna False sem alocar nada se qualquer recurso faltar.
        """
        raise NotImplementedError

    def requisitar(self, pid, recurso):
        """Compatibilidade com a interface: aloca 1 unidade de um recurso.

        Deve delegar para tentar_alocar(pid, {recurso: 1}).
        """
        raise NotImplementedError

    def liberar(self, pid):
        """Devolve ao pool todos os recursos detidos pelo processo."""
        raise NotImplementedError
