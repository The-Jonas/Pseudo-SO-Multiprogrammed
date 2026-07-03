"""Modulo de E/S: alocacao exclusiva e atomica de recursos.

Recursos disponiveis, conforme a especificacao do pseudo-SO:
  - 1 scanner
  - 2 impressoras
  - 1 modem
  - 2 dispositivos SATA

Cada recurso e alocado a processos de usuario de forma exclusiva e sem
preempcao. Processos de tempo real nao devem requisitar E/S.

Este modulo mantem compatibilidade com duas formas de uso:
  1. interface simples: requisitar(pid, recurso) e liberar(pid)
  2. integracao com escalonador: tentar_alocar(pid, pedido_dict)
"""

from src.interfaces import GerenciadorES


RECURSOS_DISPONIVEIS = {
    "scanner": 1,
    "impressora": 2,
    "modem": 1,
    "sata": 2,
}


class ES(GerenciadorES):
    """Gerenciador de recursos de E/S do pseudo-SO.

    A estrutura principal e ``alocados_por_pid``:
        pid -> {recurso: quantidade_alocada}

    O atributo ``alocados_por_processo`` aponta para a mesma estrutura para
    manter compatibilidade com codigos que usavam o nome antigo.
    """

    def __init__(self):
        self.disponiveis = RECURSOS_DISPONIVEIS.copy()
        self.alocados_por_pid = {}
        self.alocados_por_processo = self.alocados_por_pid

    def pedido_e_possivel(self, pedido):
        """Retorna True se o pedido nao excede o total fisico do sistema.

        Isso serve para rejeitar pedidos impossiveis, como 3 impressoras quando
        o sistema possui apenas 2. Nao considera o que esta ocupado agora; para
        isso use ``tentar_alocar``.
        """
        if not isinstance(pedido, dict):
            return False

        for recurso, quantidade in pedido.items():
            if recurso not in RECURSOS_DISPONIVEIS:
                return False
            if quantidade is None or quantidade < 0:
                return False
            if quantidade > RECURSOS_DISPONIVEIS[recurso]:
                return False
        return True

    def pode_alocar_agora(self, pedido):
        """Retorna True se todos os recursos do pedido estao livres agora."""
        if not self.pedido_e_possivel(pedido):
            return False

        for recurso, quantidade in pedido.items():
            if self.disponiveis.get(recurso, 0) < quantidade:
                return False
        return True

    def tentar_alocar(self, pid, pedido):
        """Tenta alocar varios recursos de uma vez, de forma atomica.

        ``pedido`` deve ser um dicionario, por exemplo:
            {"impressora": 2, "scanner": 1}

        A alocacao e atomica: se qualquer recurso estiver indisponivel, nada e
        alocado e o metodo retorna False. Se der certo, retorna True.
        """
        pedido = self._normalizar_pedido(pedido)
        if not pedido:
            return True

        if not self.pode_alocar_agora(pedido):
            return False

        for recurso, quantidade in pedido.items():
            self.disponiveis[recurso] -= quantidade

        alocados = self.alocados_por_pid.setdefault(pid, {})
        for recurso, quantidade in pedido.items():
            alocados[recurso] = alocados.get(recurso, 0) + quantidade

        return True

    def requisitar(self, pid, recurso):
        """Tenta alocar uma unidade de ``recurso`` para ``pid``.

        Metodo exigido pela interface original. Internamente usa a mesma logica
        atomica de ``tentar_alocar``.
        """
        return self.tentar_alocar(pid, {recurso: 1})

    def liberar(self, pid):
        """Libera todos os recursos alocados para ``pid``."""
        alocados = self.alocados_por_pid.pop(pid, None)
        if not alocados:
            return

        for recurso, quantidade in alocados.items():
            if recurso in self.disponiveis:
                self.disponiveis[recurso] += quantidade
                if self.disponiveis[recurso] > RECURSOS_DISPONIVEIS[recurso]:
                    self.disponiveis[recurso] = RECURSOS_DISPONIVEIS[recurso]

    def possui_recursos(self, pid):
        """Retorna True se o processo ja possui algum recurso de E/S."""
        return pid in self.alocados_por_pid

    def recursos_do_processo(self, pid):
        """Retorna uma copia dos recursos alocados para um processo."""
        return dict(self.alocados_por_pid.get(pid, {}))

    def _normalizar_pedido(self, pedido):
        """Remove quantidades zero e valida tipo basico do pedido."""
        if pedido is None:
            return {}
        if not isinstance(pedido, dict):
            return {}

        normalizado = {}
        for recurso, quantidade in pedido.items():
            try:
                quantidade = int(quantidade)
            except (TypeError, ValueError):
                normalizado[recurso] = -1
                continue

            if quantidade > 0:
                normalizado[recurso] = quantidade

        return normalizado
