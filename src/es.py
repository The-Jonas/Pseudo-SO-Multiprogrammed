"""Modulo de E/S: alocacao exclusiva e atomica de recursos.

Recursos disponiveis, conforme a especificacao do pseudo-SO:
  - 1 scanner
  - 2 impressoras
  - 1 modem
  - 2 dispositivos SATA

Cada recurso e alocado a processos de usuario de forma exclusiva e sem
preempcao. Processos de tempo real nao devem requisitar E/S.

Alocacao ATOMICA (tudo-ou-nada): so concede se conseguir todas as unidades
pedidas de uma vez; caso contrario, nao concede nenhuma. Isso evita reter
recursos parciais e, portanto, evita deadlock.
"""

from src.interfaces import GerenciadorES


RECURSOS_DISPONIVEIS = {
    "scanner":    1,
    "impressora": 2,
    "modem":      1,
    "sata":       2,
}


class ES(GerenciadorES):
    """Gerenciador de recursos de E/S do pseudo-SO com alocacao atomica."""

    def __init__(self):
        """Inicializa os recursos livres e o registro de alocacao por pid."""
        self.disponiveis = RECURSOS_DISPONIVEIS.copy()
        self.alocados_por_pid = {}

    def pedido_e_possivel(self, pedido):
        """Retorna True se o pedido nao excede o total fisico do sistema.

        Usado para rejeitar pedidos impossiveis (ex: 3 impressoras quando
        so existem 2). Nao considera o que esta ocupado agora.
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

        Retorna True e efetiva a alocacao se todos os recursos couberem.
        Retorna False sem alocar nada se qualquer recurso faltar.
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
        """Aloca 1 unidade de recurso. Delega para tentar_alocar."""
        return self.tentar_alocar(pid, {recurso: 1})

    def liberar(self, pid):
        """Libera todos os recursos alocados para pid."""
        alocados = self.alocados_por_pid.pop(pid, None)
        if not alocados:
            return
        for recurso, quantidade in alocados.items():
            if recurso in self.disponiveis:
                self.disponiveis[recurso] += quantidade
                if self.disponiveis[recurso] > RECURSOS_DISPONIVEIS[recurso]:
                    self.disponiveis[recurso] = RECURSOS_DISPONIVEIS[recurso]

    def _normalizar_pedido(self, pedido):
        """Remove quantidades zero e valida tipo basico do pedido."""
        if not isinstance(pedido, dict):
            return {}
        normalizado = {}
        for recurso, quantidade in pedido.items():
            try:
                quantidade = int(quantidade)
            except (TypeError, ValueError):
                continue
            if quantidade > 0:
                normalizado[recurso] = quantidade
        return normalizado