"""Teste de integracao: roda o dispatcher com o exemplo da spec e verifica a saida.

Compara linha a linha com o gabarito esperado (paginas 6-7 da especificacao).
Se qualquer linha divergir, o teste falha e mostra exatamente onde.

Executar da raiz do projeto:
    python testes/teste_integracao.py
"""

import sys
import os
import io
import contextlib

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.processo import Processo
from src.filas import GerenciadorFilas
from src.escalonador import Escalonador
from src.memoria import Memoria
from src.es import ES
from src.arquivos import Arquivos


# ---------------------------------------------------------------------------
# Gabarito exato da especificacao (paginas 6-7), ignorando espacos extras
# ---------------------------------------------------------------------------
SAIDA_ESPERADA = """
dispatcher =>
  PID: 0
  frames: 4
  priority: 0
  time: 3
  printers: 0
  scanners: 0
  modems: 0
  drives: 0

process 0 =>
P0 STARTED
P0 instruction 1
P0 instruction 2
P0 instruction 3
P0 return SIGINT

dispatcher =>
  PID: 1
  frames: 8
  priority: 0
  time: 2
  printers: 0
  scanners: 0
  modems: 0
  drives: 0

process 1 =>
P1 STARTED
P1 instruction 1
P1 instruction 2
P1 return SIGINT

Sistema de arquivos =>

Operação 1 => Falha
O processo 0 não pode criar o arquivo A (falta de espaço).

Operação 2 => Sucesso
O processo 0 deletou o arquivo X.

Operação 3 => Falha
O processo 2 não existe.

Operação 4 => Sucesso
O processo 0 criou o arquivo D (blocos 0, 1 e 2).

Operação 5 => Falha
O processo 1 não pode deletar o arquivo E porque ele não existe.

Mapa de ocupação do disco:
D D D Y 0 Z Z Z 0 0

Número de Faltas de Páginas por processo:
P0 = 7 faltas de páginas
P1 = 14 faltas de páginas
""".strip()


def rodar_simulacao():
    """Executa a simulacao completa e retorna a saida como string."""

    processos = [
        Processo(0, 2, 0, 3, 4, 0, 0, 0, 0, [1,2,3,4,1,2,5,1,2,3,4,5]),
        Processo(1, 8, 0, 2, 8, 0, 0, 0, 0, [7,0,1,2,0,3,0,4,2,3,0,3,1,0,2,8,9,10,11,12,9,7,8,3,0,1]),
    ]

    segmentos = [("X", 0, 2), ("Y", 3, 1), ("Z", 5, 3)]

    operacoes = [
        (0, 0, "A", 5),   # processo 0 cria A com 5 blocos
        (0, 1, "X", None),# processo 0 deleta X
        (2, 0, "B", 2),   # processo 2 (nao existe) cria B
        (0, 0, "D", 3),   # processo 0 cria D com 3 blocos
        (1, 1, "E", None),# processo 1 deleta E (nao existe)
    ]

    memoria  = Memoria()
    es       = ES()
    filas    = GerenciadorFilas()
    arquivos = Arquivos(10, segmentos, len(processos))

    buffer = io.StringIO()
    with contextlib.redirect_stdout(buffer):
        escalonador = Escalonador(filas, memoria, es)
        escalonador.rodar(processos)

        print("Sistema de arquivos =>")
        print()
        for numero, (pid, codigo, nome, blocos) in enumerate(operacoes, start=1):
            eh_tr = processos[pid].eh_tempo_real if pid < len(processos) else False
            blocos_val = blocos if blocos is not None else 0

            buf2 = io.StringIO()
            with contextlib.redirect_stdout(buf2):
                arquivos.executar_operacao(pid, codigo, nome, blocos_val, eh_tr)
            mensagem = buf2.getvalue().strip()

            status = "Sucesso" if ("criou" in mensagem or "deletou" in mensagem) else "Falha"
            print(f"Operação {numero} => {status}")
            print(mensagem)
            print()

        arquivos.imprimir_mapa()
        print()

        print("Número de Faltas de Páginas por processo:")
        for p in processos:
            print(f"P{p.pid} = {memoria.total_faltas(p.pid)} faltas de páginas")

    return buffer.getvalue().strip()


def comparar(saida_real, saida_esperada):
    """Compara linha a linha e imprime as divergencias encontradas."""
    linhas_real     = saida_real.splitlines()
    linhas_esperada = saida_esperada.splitlines()

    falhas = []
    for i, (real, esperada) in enumerate(zip(linhas_real, linhas_esperada), start=1):
        if real.strip() != esperada.strip():
            falhas.append((i, esperada.strip(), real.strip()))

    if len(linhas_real) != len(linhas_esperada):
        falhas.append((
            "total de linhas",
            f"esperado {len(linhas_esperada)}",
            f"obtido {len(linhas_real)}"
        ))

    return falhas


def main():
    print("Rodando simulacao com o exemplo da especificacao...")
    saida_real = rodar_simulacao()
    falhas = comparar(saida_real, SAIDA_ESPERADA)

    if not falhas:
        print("PASSOU — saida identica ao gabarito da especificacao.")
    else:
        print(f"FALHOU — {len(falhas)} divergencia(s) encontrada(s):\n")
        for linha, esperada, obtida in falhas:
            print(f"  Linha {linha}:")
            print(f"    esperado : {esperada!r}")
            print(f"    obtido   : {obtida!r}")
        sys.exit(1)


if __name__ == "__main__":
    main()
