"""Modulo de filas: fila global, tempo real e filas de usuario.

Menor valor de prioridade = maior prioridade no escalonamento.
Tempo real = prioridade 0. Usuario = prioridades 1 (alta), 2 (media), 3 (baixa).
"""

from collections import deque

MAX_PROCESSOS = 1000
LIMIAR_AGING = 5          # ticks de espera antes de promover um processo
PRIORIDADES_USUARIO = (1, 2, 3)


class GerenciadorFilas:
    """Mantem as filas de prontos e classifica os processos por tipo."""

    def __init__(self):
        """Cria a fila de tempo real (FIFO) e as 3 filas de usuario."""
        self.fila_tempo_real = deque()
        self.filas_usuario = {1: deque(), 2: deque(), 3: deque()}
        self.total_admitidos = 0

    def admitir(self, processo):
        """Insere um processo na fila correta conforme sua prioridade.

        Respeita o limite global de MAX_PROCESSOS. Retorna False se o limite
        foi atingido, True caso o processo tenha sido admitido.
        """
        if self.total_admitidos >= MAX_PROCESSOS:
            return False
        processo.tempo_espera = 0
        if processo.eh_tempo_real:
            self.fila_tempo_real.append(processo)
        else:
            prio = processo.prioridade if processo.prioridade in self.filas_usuario else 3
            self.filas_usuario[prio].append(processo)
        self.total_admitidos += 1
        return True

    def tem_tempo_real(self):
        """True se ha algum processo de tempo real esperando."""
        return len(self.fila_tempo_real) > 0

    def proximo_tempo_real(self):
        """Remove e retorna o proximo processo de tempo real (FIFO), ou None."""
        if self.fila_tempo_real:
            return self.fila_tempo_real.popleft()
        return None

    def proximo_usuario(self):
        """Remove e retorna o processo da fila de usuario de maior prioridade.

        Percorre as filas 1, 2, 3 nessa ordem (1 = maior prioridade). Retorna
        None se todas as filas de usuario estiverem vazias.
        """
        for prio in PRIORIDADES_USUARIO:
            if self.filas_usuario[prio]:
                return self.filas_usuario[prio].popleft()
        return None

    def tem_usuario(self):
        """True se ha algum processo de usuario esperando em qualquer fila."""
        return any(self.filas_usuario[prio] for prio in PRIORIDADES_USUARIO)

    def rebaixar(self, processo):
        """Aplica feedback: devolve o processo a uma fila de menor prioridade.

        Se ja esta na fila mais baixa (3), permanece na 3. Zera a espera porque
        ele acabou de rodar.
        """
        nova_prio = min(processo.prioridade + 1, 3)
        processo.prioridade = nova_prio
        processo.tempo_espera = 0
        self.filas_usuario[nova_prio].append(processo)

    def aplicar_aging(self):
        """Incrementa a espera de todos os processos de usuario e promove os antigos.

        Processos que esperam ha LIMIAR_AGING ticks ou mais sobem uma prioridade
        (numero menor). Evita starvation das filas baixas.
        """
        # Percorre da fila mais baixa para a mais alta para promover corretamente.
        for prio in (3, 2):
            fila = self.filas_usuario[prio]
            permanecem = deque()
            while fila:
                processo = fila.popleft()
                processo.tempo_espera += 1
                if processo.tempo_espera >= LIMIAR_AGING:
                    processo.prioridade = prio - 1
                    processo.tempo_espera = 0
                    self.filas_usuario[prio - 1].append(processo)
                else:
                    permanecem.append(processo)
            self.filas_usuario[prio] = permanecem

        # Processos na fila 1 apenas acumulam espera (nao ha para onde subir).
        for processo in self.filas_usuario[1]:
            processo.tempo_espera += 1
